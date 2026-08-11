import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months, get_previous_period

def get_last_n_month_metrics(n_months: int = 3):
    """
    Q1: Returns total revenue, orders, and AOV for the last N months,
    along with month-over-month breakdown and comparison to the previous period.
    """
    start_date, end_date, label = resolve_period_last_n_months(n_months)
    
    # Query current period metrics
    query = """
        SELECT 
            COALESCE(SUM(NET_REVENUE), 0.0) as revenue,
            COUNT(ORDER_ID) as orders,
            CASE WHEN COUNT(ORDER_ID) > 0 THEN SUM(NET_REVENUE) / COUNT(ORDER_ID) ELSE 0.0 END as aov
        FROM Orders
        WHERE CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ?
    """
    curr_res = DatabaseManager.execute_query(query, [start_date, end_date])[0]
    
    # Query previous period metrics
    prev_start, prev_end = get_previous_period(start_date, end_date)
    prev_res = DatabaseManager.execute_query(query, [prev_start, prev_end])[0]
    
    # Monthly breakdown for chart
    monthly_query = """
        SELECT 
            c.YEAR as year,
            c.MONTH as month,
            c.MONTH_NO as month_no,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue,
            COUNT(o.ORDER_ID) as orders,
            CASE WHEN COUNT(o.ORDER_ID) > 0 THEN SUM(o.NET_REVENUE) / COUNT(o.ORDER_ID) ELSE 0.0 END as aov
        FROM Calendar c
        LEFT JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE c.DATE >= ? AND c.DATE <= ?
        GROUP BY c.YEAR, c.MONTH, c.MONTH_NO
        ORDER BY c.YEAR ASC, c.MONTH_NO ASC
    """
    monthly_breakdown = DatabaseManager.execute_query(monthly_query, [start_date, end_date])
    
    # Calculate percentage changes
    rev_change = 0.0
    if prev_res['revenue'] > 0:
        rev_change = ((curr_res['revenue'] - prev_res['revenue']) / prev_res['revenue']) * 100
        
    orders_change = 0.0
    if prev_res['orders'] > 0:
        orders_change = ((curr_res['orders'] - prev_res['orders']) / prev_res['orders']) * 100
        
    aov_change = 0.0
    if prev_res['aov'] > 0:
        aov_change = ((curr_res['aov'] - prev_res['aov']) / prev_res['aov']) * 100

    return {
        "period": {
            "start": str(start_date),
            "end": str(end_date),
            "label": label
        },
        "revenue": round(curr_res['revenue'], 2),
        "orders": int(curr_res['orders']),
        "aov": round(curr_res['aov'], 2),
        "changes": {
            "revenue_pct": round(rev_change, 2),
            "orders_pct": round(orders_change, 2),
            "aov_pct": round(aov_change, 2)
        },
        "monthly_data": [
            {
                "label": f"{row['month']} {row['year']}",
                "revenue": round(row['revenue'], 2),
                "orders": int(row['orders']),
                "aov": round(row['aov'], 2)
            } for row in monthly_breakdown
        ]
    }
