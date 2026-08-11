import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def get_store_diagnostic_metrics(store_id: str):
    """
    Q8 Tool: Detailed diagnostic decomposition of a single declining store
    by calculating trend data, channel shifts, SKU drops, and weekday/weekend changes.
    Determines driver scores deterministically.
    """
    start_date, end_date, _ = resolve_period_last_n_months(3)
    
    # 1. Monthly Trend Data (May, June, July 2026)
    query_monthly = """
        SELECT 
            c.YEAR as year,
            c.MONTH as month,
            c.MONTH_NO as month_no,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue,
            COUNT(o.ORDER_ID) as orders,
            CASE WHEN COUNT(o.ORDER_ID) > 0 THEN SUM(o.NET_REVENUE) / COUNT(o.ORDER_ID) ELSE 0.0 END as aov
        FROM Calendar c
        LEFT JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE AND o.STORE_ID = ?
        WHERE c.DATE >= ? AND c.DATE <= ?
        GROUP BY c.YEAR, c.MONTH, c.MONTH_NO
        ORDER BY c.YEAR ASC, c.MONTH_NO ASC
    """
    monthly_data = DatabaseManager.execute_query(query_monthly, [store_id, start_date, end_date])
    
    if len(monthly_data) < 3:
        return {"error": f"Insufficient historical data for store {store_id}"}
        
    m1 = monthly_data[0] # May
    m2 = monthly_data[1] # June
    m3 = monthly_data[2] # July
    
    rev_may, rev_jul = m1["revenue"], m3["revenue"]
    orders_may, orders_jul = m1["orders"], m3["orders"]
    aov_may, aov_jul = m1["aov"], m3["aov"]
    
    total_rev_drop = rev_jul - rev_may # Negative if declined
    pct_rev_drop = (total_rev_drop / rev_may * 100) if rev_may > 0 else 0.0
    
    total_ord_drop = orders_jul - orders_may
    pct_ord_drop = (total_ord_drop / orders_may * 100) if orders_may > 0 else 0.0
    
    total_aov_drop = aov_jul - aov_may
    pct_aov_drop = (total_aov_drop / aov_may * 100) if aov_may > 0 else 0.0

    # 2. Channel Performance Change (May vs July)
    query_channel = """
        SELECT 
            o.CHANNEL as channel,
            SUM(CASE WHEN c.MONTH_NO = 5 THEN o.NET_REVENUE ELSE 0.0 END) as revenue_may,
            SUM(CASE WHEN c.MONTH_NO = 7 THEN o.NET_REVENUE ELSE 0.0 END) as revenue_jul
        FROM Calendar c
        JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE o.STORE_ID = ? AND c.DATE >= ? AND c.DATE <= ?
        GROUP BY o.CHANNEL
    """
    channel_data = DatabaseManager.execute_query(query_channel, [store_id, start_date, end_date])
    
    channel_shifts = []
    max_channel_rev_drop = 0.0
    max_channel_name = "None"
    
    for row in channel_data:
        chan = row["channel"]
        c_may = row["revenue_may"] or 0.0
        c_jul = row["revenue_jul"] or 0.0
        c_drop = c_jul - c_may
        c_pct = (c_drop / c_may * 100) if c_may > 0 else 0.0
        
        if c_drop < max_channel_rev_drop:
            max_channel_rev_drop = c_drop
            max_channel_name = chan
            
        channel_shifts.append({
            "channel": chan,
            "revenue_may": round(c_may, 2),
            "revenue_jul": round(c_jul, 2),
            "revenue_drop": round(c_drop, 2),
            "pct_change": round(c_pct, 2)
        })

    # 3. Product SKU Decline (May vs July)
    query_skus = """
        SELECT 
            p.SKU_ID as sku_id,
            p.SKU_NAME as sku_name,
            SUM(CASE WHEN c.MONTH_NO = 5 THEN od.LINE_NET_VALUE ELSE 0.0 END) as rev_may,
            SUM(CASE WHEN c.MONTH_NO = 7 THEN od.LINE_NET_VALUE ELSE 0.0 END) as rev_jul
        FROM Calendar c
        JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        JOIN Order_Details od ON od.ORDER_ID = o.ORDER_ID
        JOIN Product_Master p ON p.SKU_ID = od.SKU_ID
        WHERE o.STORE_ID = ? AND c.DATE >= ? AND c.DATE <= ?
        GROUP BY p.SKU_ID, p.SKU_NAME
    """
    sku_data = DatabaseManager.execute_query(query_skus, [store_id, start_date, end_date])
    
    sku_shifts = []
    for row in sku_data:
        s_may = row["rev_may"] or 0.0
        s_jul = row["rev_jul"] or 0.0
        s_drop = s_jul - s_may
        s_pct = (s_drop / s_may * 100) if s_may > 0 else 0.0
        
        if s_drop < 0:
            sku_shifts.append({
                "sku_id": row["sku_id"],
                "sku_name": row["sku_name"],
                "rev_may": round(s_may, 2),
                "rev_jul": round(s_jul, 2),
                "rev_drop": round(s_drop, 2),
                "pct_change": round(s_pct, 2)
            })
            
    sku_shifts.sort(key=lambda x: x["rev_drop"]) # Most negative first
    top_declining_skus = sku_shifts[:5]

    # 4. Day Type Performance Change (May vs July)
    query_daytype = """
        SELECT 
            c.DAY_TYPE as day_type,
            SUM(CASE WHEN c.MONTH_NO = 5 THEN o.NET_REVENUE ELSE 0.0 END) as rev_may,
            SUM(CASE WHEN c.MONTH_NO = 7 THEN o.NET_REVENUE ELSE 0.0 END) as rev_jul
        FROM Calendar c
        JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE o.STORE_ID = ? AND c.DATE >= ? AND c.DATE <= ?
        GROUP BY c.DAY_TYPE
    """
    daytype_data = DatabaseManager.execute_query(query_daytype, [store_id, start_date, end_date])
    
    daytype_shifts = {}
    for row in daytype_data:
        dtype = row["day_type"]
        dt_may = row["rev_may"] or 0.0
        dt_jul = row["rev_jul"] or 0.0
        dt_drop = dt_jul - dt_may
        dt_pct = (dt_drop / dt_may * 100) if dt_may > 0 else 0.0
        
        daytype_shifts[dtype] = {
            "rev_may": round(dt_may, 2),
            "rev_jul": round(dt_jul, 2),
            "revenue_drop": round(dt_drop, 2),
            "pct_change": round(dt_pct, 2)
        }

    # 5. Deterministic Driver Scores
    # Order volume score
    if pct_ord_drop <= -15.0:
        ord_score = "HIGH"
    elif pct_ord_drop <= -5.0:
        ord_score = "MEDIUM"
    else:
        ord_score = "LOW"
        
    # AOV score
    if pct_aov_drop <= -10.0:
        aov_score = "HIGH"
    elif pct_aov_drop <= -3.0:
        aov_score = "MEDIUM"
    else:
        aov_score = "LOW"
        
    # Channel shift contribution: check if the largest declining channel is a major driver
    chan_contrib_pct = (max_channel_rev_drop / total_rev_drop * 100) if total_rev_drop < 0 else 0.0
    if chan_contrib_pct >= 40.0 and max_channel_rev_drop < -10000:
        chan_score = "HIGH"
    elif chan_contrib_pct >= 20.0:
        chan_score = "MEDIUM"
    else:
        chan_score = "LOW"
        
    # SKU mix deterioration: check sum of decline of top declining SKUs relative to total drop
    top_sku_drop_sum = sum(s["rev_drop"] for s in top_declining_skus)
    sku_contrib_pct = (top_sku_drop_sum / total_rev_drop * 100) if total_rev_drop < 0 else 0.0
    if sku_contrib_pct >= 40.0:
        sku_score = "HIGH"
    elif sku_contrib_pct >= 15.0:
        sku_score = "MEDIUM"
    else:
        sku_score = "LOW"

    return {
        "store_id": store_id,
        "revenue_change_pct": round(pct_rev_drop, 2),
        "revenue_change_val": round(total_rev_drop, 2),
        "monthly_trend": [
            {
                "month": f"{r['month']} {r['year']}",
                "revenue": round(r['revenue'], 2),
                "orders": int(r['orders']),
                "aov": round(r['aov'], 2)
            } for r in monthly_data
        ],
        "channel_shifts": channel_shifts,
        "top_declining_skus": top_declining_skus,
        "daytype_shifts": daytype_shifts,
        "drivers": {
            "order_volume_decline": {
                "score": ord_score,
                "pct_change": round(pct_ord_drop, 2),
                "details": f"Order volume decreased by {abs(round(pct_ord_drop, 1))}%"
            },
            "aov_decline": {
                "score": aov_score,
                "pct_change": round(pct_aov_drop, 2),
                "details": f"Average order value changed by {round(pct_aov_drop, 1)}%"
            },
            "channel_degradation": {
                "score": chan_score,
                "primary_channel": max_channel_name,
                "pct_contribution": round(chan_contrib_pct, 2),
                "details": f"{max_channel_name} revenue dropped by {abs(round(max_channel_rev_drop, 0))} INR ({round(chan_contrib_pct, 1)}% of total drop)"
            },
            "sku_mix_deterioration": {
                "score": sku_score,
                "pct_contribution": round(sku_contrib_pct, 2),
                "details": f"Top declining menu items contributed to {round(sku_contrib_pct, 1)}% of total drop"
            }
        }
    }
