"""
Multi-Store Comparative Analysis Engine
Side-by-side comparison across any metric with performance scoring and gap analysis.
"""
import math
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def compare_stores(store_ids: list, n_months: int = 3) -> dict:
    """
    Compare multiple stores side-by-side across revenue, orders, AOV, and growth rate.
    Calculates a Performance Score (0-100) and gap-to-best for each metric.
    """
    start_date, end_date, label = resolve_period_last_n_months(n_months)
    
    if not store_ids:
        # Default: compare top 5 vs bottom 5
        query = """
            SELECT s.STORE_ID FROM Store_Master s
            JOIN Orders o ON o.STORE_ID = s.STORE_ID
            WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
            GROUP BY s.STORE_ID ORDER BY SUM(o.NET_REVENUE) DESC LIMIT 10
        """
        res = DatabaseManager.execute_query(query, [start_date, end_date])
        store_ids = [r["STORE_ID"] for r in res]

    placeholders = ",".join(["?" for _ in store_ids])
    
    # Current period metrics
    query = f"""
        SELECT s.STORE_ID as store_id, s.STORE_NAME as store_name, s.CITY as city,
               s.STORE_FORMAT as store_format,
               COALESCE(SUM(o.NET_REVENUE), 0) as revenue,
               COUNT(o.ORDER_ID) as orders,
               CASE WHEN COUNT(o.ORDER_ID) > 0 THEN SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) ELSE 0 END as aov
        FROM Store_Master s
        LEFT JOIN Orders o ON o.STORE_ID = s.STORE_ID
            AND CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
        WHERE s.STORE_ID IN ({placeholders})
        GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT
    """
    current = DatabaseManager.execute_query(query, [start_date, end_date] + store_ids)
    
    # Monthly breakdown for growth rate calc
    monthly_query = f"""
        SELECT s.STORE_ID as store_id, c.MONTH_NO as month_no,
               COALESCE(SUM(o.NET_REVENUE), 0) as revenue
        FROM Store_Master s
        JOIN Orders o ON o.STORE_ID = s.STORE_ID
        JOIN Calendar c ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE c.DATE >= ? AND c.DATE <= ? AND s.STORE_ID IN ({placeholders})
        GROUP BY s.STORE_ID, c.MONTH_NO ORDER BY s.STORE_ID, c.MONTH_NO
    """
    monthly = DatabaseManager.execute_query(monthly_query, [start_date, end_date] + store_ids)
    
    # Build monthly map
    monthly_map = {}
    for row in monthly:
        sid = row["store_id"]
        if sid not in monthly_map:
            monthly_map[sid] = []
        monthly_map[sid].append(row["revenue"])
    
    # Calculate growth rates
    growth_rates = {}
    for sid, revs in monthly_map.items():
        if len(revs) >= 2 and revs[0] > 0:
            growth_rates[sid] = round(((revs[-1] - revs[0]) / revs[0]) * 100, 2)
        else:
            growth_rates[sid] = 0.0
    
    # Calculate averages for benchmarking
    if not current:
        return {"stores": [], "period": {"start": str(start_date), "end": str(end_date), "label": label}}
    
    avg_revenue = sum(s["revenue"] for s in current) / len(current)
    avg_orders = sum(s["orders"] for s in current) / len(current)
    avg_aov = sum(s["aov"] for s in current) / len(current)
    avg_growth = sum(growth_rates.get(s["store_id"], 0) for s in current) / len(current) if growth_rates else 0
    
    max_revenue = max(s["revenue"] for s in current)
    max_orders = max(s["orders"] for s in current)
    max_aov = max(s["aov"] for s in current)
    
    # Build comparison rows with performance scores
    comparison = []
    for store in current:
        sid = store["store_id"]
        gr = growth_rates.get(sid, 0.0)
        
        # Performance Score (0-100): weighted composite
        rev_score = min((store["revenue"] / max_revenue) * 100, 100) if max_revenue > 0 else 0
        ord_score = min((store["orders"] / max_orders) * 100, 100) if max_orders > 0 else 0
        aov_score = min((store["aov"] / max_aov) * 100, 100) if max_aov > 0 else 0
        growth_score = max(min(50 + gr, 100), 0)  # Center at 50, cap 0-100
        
        perf_score = round(rev_score * 0.4 + ord_score * 0.25 + aov_score * 0.2 + growth_score * 0.15, 1)
        
        comparison.append({
            "store_id": sid,
            "store_name": store["store_name"],
            "city": store["city"],
            "store_format": store["store_format"],
            "revenue": round(store["revenue"], 2),
            "orders": int(store["orders"]),
            "aov": round(store["aov"], 2),
            "growth_rate": gr,
            "performance_score": perf_score,
            "vs_avg": {
                "revenue": round(((store["revenue"] - avg_revenue) / avg_revenue) * 100, 1) if avg_revenue > 0 else 0,
                "orders": round(((store["orders"] - avg_orders) / avg_orders) * 100, 1) if avg_orders > 0 else 0,
                "aov": round(((store["aov"] - avg_aov) / avg_aov) * 100, 1) if avg_aov > 0 else 0,
            },
            "gap_to_best": {
                "revenue": round(max_revenue - store["revenue"], 2),
                "orders": int(max_orders - store["orders"]),
                "aov": round(max_aov - store["aov"], 2),
            }
        })
    
    comparison.sort(key=lambda x: x["performance_score"], reverse=True)
    
    # Mark best-in-class
    if comparison:
        comparison[0]["best_in_class"] = True
    
    return {
        "stores": comparison,
        "benchmarks": {
            "avg_revenue": round(avg_revenue, 2),
            "avg_orders": round(avg_orders, 0),
            "avg_aov": round(avg_aov, 2),
            "avg_growth": round(avg_growth, 2)
        },
        "period": {"start": str(start_date), "end": str(end_date), "label": label}
    }
