"""
Smart Recommendation Engine
Generates actionable recommendations for declining stores/channels with estimated impact.
Uses rule-based logic + data-driven impact estimation.
"""
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def _get_channel_metrics(store_id: str, start_date, end_date) -> list:
    """Get channel-level metrics for a store."""
    query = """
        SELECT CHANNEL as channel, SUM(NET_REVENUE) as revenue, COUNT(ORDER_ID) as orders,
               SUM(NET_REVENUE)/COUNT(ORDER_ID) as aov
        FROM Orders WHERE STORE_ID = ? AND CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ?
        GROUP BY CHANNEL ORDER BY revenue DESC
    """
    return DatabaseManager.execute_query(query, [store_id, start_date, end_date])

def _get_product_metrics(store_id: str, start_date, end_date) -> list:
    """Get product performance for a store."""
    query = """
        SELECT p.CATEGORY, SUM(od.QUANTITY) as qty, SUM(od.LINE_NET_VALUE) as revenue,
               SUM(od.LINE_NET_VALUE)/SUM(od.QUANTITY) as avg_price
        FROM Product_Master p JOIN Order_Details od ON od.SKU_ID = p.SKU_ID
        JOIN Orders o ON o.ORDER_ID = od.ORDER_ID
        WHERE o.STORE_ID = ? AND CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
        GROUP BY p.CATEGORY ORDER BY revenue DESC
    """
    return DatabaseManager.execute_query(query, [store_id, start_date, end_date])

def _get_rejection_rate(store_id: str, start_date, end_date) -> float:
    """Calculate discount rate for a store based on real dataset columns."""
    query = """
        SELECT COALESCE(SUM(DISCOUNT_AMOUNT), 0) * 100.0 / NULLIF(SUM(NET_REVENUE + DISCOUNT_AMOUNT), 0) as discount_rate
        FROM Orders WHERE STORE_ID = ? AND CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ?
    """
    res = DatabaseManager.execute_query(query, [store_id, start_date, end_date])
    return res[0]["discount_rate"] if res and res[0]["discount_rate"] is not None else 0.0



def _get_channel_change(store_id: str, n_months: int = 3) -> list:
    """Get channel-level period-over-period change."""
    start_date, end_date, _ = resolve_period_last_n_months(n_months)
    prev_start, prev_end, _ = resolve_period_last_n_months(n_months * 2)
    
    query = """
        SELECT CHANNEL as channel,
               SUM(CASE WHEN CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ? THEN NET_REVENUE ELSE 0 END) as current_rev,
               SUM(CASE WHEN CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) < ? THEN NET_REVENUE ELSE 0 END) as prev_rev
        FROM Orders WHERE STORE_ID = ?
        GROUP BY CHANNEL
    """
    return DatabaseManager.execute_query(query, [start_date, end_date, prev_start, start_date, store_id])

def generate_recommendations(store_id: str, n_months: int = 3) -> dict:
    """
    Generate 3-5 actionable recommendations for a store with estimated impact.
    """
    start_date, end_date, label = resolve_period_last_n_months(n_months)
    
    channels = _get_channel_metrics(store_id, start_date, end_date)
    products = _get_product_metrics(store_id, start_date, end_date)
    rejection_rate = _get_rejection_rate(store_id, start_date, end_date)
    channel_changes = _get_channel_change(store_id, n_months)
    
    total_revenue = sum(ch["revenue"] for ch in channels) if channels else 0
    recommendations = []
    
    # Rule 1: Channel optimization — identify declining channels
    for ch in channel_changes:
        if ch["prev_rev"] > 0:
            change_pct = ((ch["current_rev"] - ch["prev_rev"]) / ch["prev_rev"]) * 100
            if change_pct < -10:
                channel_share = (ch["current_rev"] / total_revenue * 100) if total_revenue > 0 else 0
                recovery_amount = abs(ch["current_rev"] - ch["prev_rev"]) * 0.5
                recommendations.append({
                    "category": "Channel Optimization",
                    "action": f"Increase {ch['channel']} visibility & promotional spend by 15-20%",
                    "estimated_impact": f"+₹{recovery_amount:,.0f}",
                    "impact_percent": f"+{abs(change_pct) * 0.5:.1f}%",
                    "effort": "medium",
                    "timeline": "7-14 days",
                    "success_probability": "72%",
                    "risks": ["May reduce margin if not optimized", "ROI depends on market saturation"],
                    "rationale": f"{ch['channel']} revenue dropped {change_pct:.1f}% ({channel_share:.0f}% channel share). "
                                 f"Recovering 50% of lost volume is achievable through increased platform spend."
                })
    
    # Rule 2: High discount leakage / margin erosion
    if rejection_rate > 5:
        estimated_recovery = total_revenue * (rejection_rate / 100) * 0.4
        recommendations.append({
            "category": "Operational Fix",
            "action": "Optimize discount threshold to prevent margin erosion and uncalculated promo leakage",
            "estimated_impact": f"+₹{estimated_recovery:,.0f}",
            "impact_percent": f"+{rejection_rate * 0.4:.1f}%",
            "effort": "low",
            "timeline": "3-5 days",
            "success_probability": "85%",
            "risks": ["May temporarily lower coupon redemptions"],
            "rationale": f"Current promo discount rate is {rejection_rate:.1f}%. Industry benchmark is <5%. "
                         f"Tighter discounting parameters directly recover lost net revenue."
        })

    
    # Rule 3: Menu engineering — promote high-margin categories
    if len(products) >= 2:
        top_cat = products[0]
        low_cats = [p for p in products if p["revenue"] < top_cat["revenue"] * 0.3]
        if low_cats:
            low_cat = low_cats[0]
            cross_sell_impact = total_revenue * 0.03  # 3% uplift from cross-sell
            recommendations.append({
                "category": "Menu Engineering",
                "action": f"Create combo offers bundling {top_cat['CATEGORY']} with {low_cat['CATEGORY']} to boost low-performing categories",
                "estimated_impact": f"+₹{cross_sell_impact:,.0f}",
                "impact_percent": "+3-5%",
                "effort": "low",
                "timeline": "3-7 days",
                "success_probability": "68%",
                "risks": ["May cannibalize individual item sales", "Requires menu redesign"],
                "rationale": f"{low_cat['CATEGORY']} contributes only ₹{low_cat['revenue']:,.0f} vs {top_cat['CATEGORY']} at ₹{top_cat['revenue']:,.0f}. "
                             f"Combo offers can increase basket size and overall AOV."
            })
    
    # Rule 4: AOV improvement — upselling
    if channels:
        avg_aov = sum(ch["aov"] for ch in channels) / len(channels)
        if avg_aov < 700:
            aov_uplift_impact = total_revenue * 0.05  # 5% from AOV uplift
            recommendations.append({
                "category": "Pricing Strategy",
                "action": "Implement suggestive upselling — add-on recommendations at checkout for beverages and sides",
                "estimated_impact": f"+₹{aov_uplift_impact:,.0f}",
                "impact_percent": "+5-8%",
                "effort": "low",
                "timeline": "1-3 days",
                "success_probability": "75%",
                "risks": ["May slow checkout flow if poorly implemented"],
                "rationale": f"Current AOV (₹{avg_aov:.0f}) is below ₹700 benchmark. "
                             f"Industry data shows suggestive selling lifts AOV by 8-15%."
            })
    
    # Rule 5: Peak-hour optimization
    peak_query = """
        SELECT EXTRACT(HOUR FROM CAST(ORDER_DATETIME AS TIMESTAMP)) as hour,
               COUNT(ORDER_ID) as orders, SUM(NET_REVENUE) as revenue
        FROM Orders WHERE STORE_ID = ? AND CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ?
        GROUP BY hour ORDER BY revenue DESC
    """
    hourly = DatabaseManager.execute_query(peak_query, [store_id, start_date, end_date])
    if len(hourly) >= 3:
        peak_hours = hourly[:3]
        off_peak = hourly[-3:]
        off_peak_rev = sum(h["revenue"] for h in off_peak)
        if off_peak_rev > 0:
            promotion_impact = off_peak_rev * 0.2  # 20% uplift on off-peak
            peak_labels = ", ".join([f"{int(h['hour'])}:00" for h in peak_hours])
            recommendations.append({
                "category": "Promotional Tactics",
                "action": f"Launch happy hour promotions during off-peak hours to redistribute demand from peak ({peak_labels})",
                "estimated_impact": f"+₹{promotion_impact:,.0f}",
                "impact_percent": "+2-4%",
                "effort": "medium",
                "timeline": "5-10 days",
                "success_probability": "65%",
                "risks": ["Discounts may reduce margin", "Peak demand may not shift easily"],
                "rationale": f"Off-peak hours generate significantly lower revenue. "
                             f"Targeted promotions can redistribute 10-20% of demand."
            })
    
    # Sort by ROI/effort ratio
    effort_map = {"low": 1, "medium": 2, "high": 3}
    recommendations.sort(key=lambda r: float(r["success_probability"].rstrip("%")) / effort_map.get(r["effort"], 2), reverse=True)
    
    return {
        "store_id": store_id,
        "recommendations": recommendations[:5],
        "total_recommendations": len(recommendations),
        "period": {"start": str(start_date), "end": str(end_date), "label": label},
        "context": {
            "total_revenue": round(total_revenue, 2),
            "channels": len(channels),
            "rejection_rate": round(rejection_rate, 2)
        }
    }
