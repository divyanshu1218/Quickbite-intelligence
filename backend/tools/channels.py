import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def get_channel_performance(start_date=None, end_date=None):
    """
    Q3: Channel performance breakdown: revenue, orders, AOV, and revenue share.
    """
    if not start_date or not end_date:
        start_date, end_date, _ = resolve_period_last_n_months(3)
        
    query = """
        SELECT 
            CHANNEL as channel,
            COALESCE(SUM(NET_REVENUE), 0.0) as revenue,
            COUNT(ORDER_ID) as orders,
            CASE WHEN COUNT(ORDER_ID) > 0 THEN SUM(NET_REVENUE) / COUNT(ORDER_ID) ELSE 0.0 END as aov
        FROM Orders
        WHERE CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ?
        GROUP BY CHANNEL
        ORDER BY revenue DESC
    """
    channel_data = DatabaseManager.execute_query(query, [start_date, end_date])
    
    total_revenue = sum(row["revenue"] for row in channel_data)
    total_orders = sum(row["orders"] for row in channel_data)
    
    results = []
    for row in channel_data:
        share_pct = (row["revenue"] / total_revenue) * 100 if total_revenue > 0 else 0.0
        results.append({
            "channel": row["channel"],
            "revenue": round(row["revenue"], 2),
            "orders": int(row["orders"]),
            "aov": round(row["aov"], 2),
            "share_pct": round(share_pct, 2)
        })
        
    return {
        "channels": results,
        "total_revenue": round(total_revenue, 2),
        "total_orders": int(total_orders)
    }
