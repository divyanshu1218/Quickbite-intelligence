import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def get_store_rankings(top_n: int = 5, bottom_n: int = 5, start_date=None, end_date=None):
    """
    Q2: Top N and Bottom N stores by revenue.
    """
    if not start_date or not end_date:
        start_date, end_date, _ = resolve_period_last_n_months(3)
        
    query = """
        SELECT 
            s.STORE_ID as store_id,
            s.STORE_NAME as store_name,
            s.CITY as city,
            s.STORE_FORMAT as store_format,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue,
            COUNT(o.ORDER_ID) as orders,
            CASE WHEN COUNT(o.ORDER_ID) > 0 THEN SUM(o.NET_REVENUE) / COUNT(o.ORDER_ID) ELSE 0.0 END as aov
        FROM Store_Master s
        JOIN Orders o ON o.STORE_ID = s.STORE_ID
        WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
        GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT
        ORDER BY revenue DESC
    """
    all_stores = DatabaseManager.execute_query(query, [start_date, end_date])
    
    if not all_stores:
        return {"top_stores": [], "bottom_stores": [], "all_stores": []}
        
    top_stores = all_stores[:top_n]
    bottom_stores = all_stores[-bottom_n:][::-1] # Reverse bottom so lowest is first or last as preferred. Let's keep it sorted ascending for bottom.
    
    # Format list
    def format_row(row, rank):
        return {
            "rank": rank,
            "store_id": row["store_id"],
            "store_name": row["store_name"],
            "city": row["city"],
            "store_format": row["store_format"],
            "revenue": round(row["revenue"], 2),
            "orders": int(row["orders"]),
            "aov": round(row["aov"], 2)
        }
        
    return {
        "top_stores": [format_row(row, i+1) for i, row in enumerate(top_stores)],
        "bottom_stores": [format_row(row, len(all_stores) - i) for i, row in enumerate(bottom_stores)],
        "all_stores": [format_row(row, i+1) for i, row in enumerate(all_stores)]
    }

def get_consistently_declining_stores(n_months: int = 3):
    """
    Q8: Stores consistently declining over the last 3 months.
    Declining = Month1 > Month2 > Month3.
    """
    start_date, end_date, _ = resolve_period_last_n_months(n_months)
    
    # Query monthly revenue for each store
    query = """
        SELECT 
            s.STORE_ID as store_id,
            s.STORE_NAME as store_name,
            s.CITY as city,
            c.YEAR as year,
            c.MONTH as month,
            c.MONTH_NO as month_no,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue
        FROM Store_Master s
        JOIN Orders o ON o.STORE_ID = s.STORE_ID
        JOIN Calendar c ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE c.DATE >= ? AND c.DATE <= ?
        GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY, c.YEAR, c.MONTH, c.MONTH_NO
        ORDER BY s.STORE_ID, c.YEAR ASC, c.MONTH_NO ASC
    """
    monthly_data = DatabaseManager.execute_query(query, [start_date, end_date])
    
    # Group by store_id
    store_months = {}
    for row in monthly_data:
        sid = row["store_id"]
        if sid not in store_months:
            store_months[sid] = {
                "store_name": row["store_name"],
                "city": row["city"],
                "months": []
            }
        store_months[sid]["months"].append({
            "label": f"{row['month']} {row['year']}",
            "revenue": row["revenue"]
        })
        
    declining_stores = []
    for sid, info in store_months.items():
        months = info["months"]
        if len(months) == 3:
            m1_rev = months[0]["revenue"]
            m2_rev = months[1]["revenue"]
            m3_rev = months[2]["revenue"]
            
            # Mathematical condition: May > June AND June > July
            if m1_rev > m2_rev and m2_rev > m3_rev:
                # Calculate decline details
                total_decline = m3_rev - m1_rev
                pct_decline = (total_decline / m1_rev) * 100 if m1_rev > 0 else 0
                
                # Check magnitude: categorise if high priority (e.g. > 5% decline)
                priority = "HIGH" if abs(pct_decline) >= 10.0 else "MEDIUM"
                
                declining_stores.append({
                    "store_id": sid,
                    "store_name": info["store_name"],
                    "city": info["city"],
                    "monthly_revenue": [
                        {"month": months[0]["label"], "revenue": round(m1_rev, 2)},
                        {"month": months[1]["label"], "revenue": round(m2_rev, 2)},
                        {"month": months[2]["label"], "revenue": round(m3_rev, 2)}
                    ],
                    "total_decline": round(total_decline, 2),
                    "pct_decline": round(pct_decline, 2),
                    "priority_level": priority
                })
                
    # Sort by percentage decline descending (most negative first)
    declining_stores.sort(key=lambda x: x["pct_decline"])
    return declining_stores
