import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def compare_weekend_weekday(start_date=None, end_date=None):
    """
    Q6: Compare weekend vs weekday performance: total revenue, order count, AOV,
    and daily averages (normalized by number of days of each type in the period).
    """
    if not start_date or not end_date:
        start_date, end_date, _ = resolve_period_last_n_months(3)
        
    # Query performance metrics by day type
    query = """
        SELECT 
            c.DAY_TYPE as day_type,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue,
            COUNT(o.ORDER_ID) as orders,
            CASE WHEN COUNT(o.ORDER_ID) > 0 THEN SUM(o.NET_REVENUE) / COUNT(o.ORDER_ID) ELSE 0.0 END as aov,
            COUNT(DISTINCT c.DATE) as days_count
        FROM Calendar c
        LEFT JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE c.DATE >= ? AND c.DATE <= ?
        GROUP BY c.DAY_TYPE
    """
    db_results = DatabaseManager.execute_query(query, [start_date, end_date])
    
    formatted_results = {}
    for row in db_results:
        dtype = row["day_type"]
        days = int(row["days_count"])
        rev = row["revenue"]
        ord_cnt = row["orders"]
        
        formatted_results[dtype] = {
            "total_revenue": round(rev, 2),
            "total_orders": int(ord_cnt),
            "aov": round(row["aov"], 2),
            "days_count": days,
            "avg_daily_revenue": round(rev / days, 2) if days > 0 else 0.0,
            "avg_daily_orders": round(ord_cnt / days, 2) if days > 0 else 0.0
        }
        
    # Ensure both Weekday and Weekend keys exist
    for key in ["Weekday", "Weekend"]:
        if key not in formatted_results:
            formatted_results[key] = {
                "total_revenue": 0.0,
                "total_orders": 0,
                "aov": 0.0,
                "days_count": 0,
                "avg_daily_revenue": 0.0,
                "avg_daily_orders": 0.0
            }
            
    return formatted_results

def compare_festive_normal(start_date=None, end_date=None):
    """
    Q7: Compare festive-period vs normal-period performance.
    """
    if not start_date or not end_date:
        start_date, end_date, _ = resolve_period_last_n_months(3)
        
    query = """
        SELECT 
            c.FESTIVE_PERIOD as festive_period,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue,
            COUNT(o.ORDER_ID) as orders,
            CASE WHEN COUNT(o.ORDER_ID) > 0 THEN SUM(o.NET_REVENUE) / COUNT(o.ORDER_ID) ELSE 0.0 END as aov,
            COUNT(DISTINCT c.DATE) as days_count
        FROM Calendar c
        LEFT JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE c.DATE >= ? AND c.DATE <= ?
        GROUP BY c.FESTIVE_PERIOD
    """
    db_results = DatabaseManager.execute_query(query, [start_date, end_date])
    
    results = []
    for row in db_results:
        days = int(row["days_count"])
        rev = row["revenue"]
        ord_cnt = row["orders"]
        
        results.append({
            "period_type": row["festive_period"],
            "total_revenue": round(rev, 2),
            "total_orders": int(ord_cnt),
            "aov": round(row["aov"], 2),
            "days_count": days,
            "avg_daily_revenue": round(rev / days, 2) if days > 0 else 0.0,
            "avg_daily_orders": round(ord_cnt / days, 2) if days > 0 else 0.0
        })
        
    # Sort results so Normal is first
    results.sort(key=lambda x: 0 if x["period_type"] == "Normal" else 1)
    
    return {
        "periods": results
    }
