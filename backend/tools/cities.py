import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def get_city_revenue_trend(start_date=None, end_date=None):
    """
    Q5: Cities with declining revenue over the last 3 months.
    Includes monthly data points, overall decline rate, and consistency checks.
    """
    start_date, end_date, _ = resolve_period_last_n_months(3)
    
    query = """
        SELECT 
            s.CITY as city,
            c.YEAR as year,
            c.MONTH as month,
            c.MONTH_NO as month_no,
            COALESCE(SUM(o.NET_REVENUE), 0.0) as revenue
        FROM Store_Master s
        JOIN Orders o ON o.STORE_ID = s.STORE_ID
        JOIN Calendar c ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
        WHERE c.DATE >= ? AND c.DATE <= ?
        GROUP BY s.CITY, c.YEAR, c.MONTH, c.MONTH_NO
        ORDER BY s.CITY, c.YEAR ASC, c.MONTH_NO ASC
    """
    city_data = DatabaseManager.execute_query(query, [start_date, end_date])
    
    city_months = {}
    for row in city_data:
        city = row["city"]
        if city not in city_months:
            city_months[city] = []
        city_months[city].append({
            "label": f"{row['month']} {row['year']}",
            "revenue": row["revenue"]
        })
        
    declining_cities = []
    stable_growing_cities = []
    
    for city, months in city_months.items():
        if len(months) == 3:
            m1_rev = months[0]["revenue"]
            m2_rev = months[1]["revenue"]
            m3_rev = months[2]["revenue"]
            
            total_change = m3_rev - m1_rev
            pct_change = (total_change / m1_rev) * 100 if m1_rev > 0 else 0.0
            
            is_consistent = (m1_rev > m2_rev) and (m2_rev > m3_rev)
            is_declining = m3_rev < m1_rev # Overall decline
            
            city_report = {
                "city": city,
                "monthly_revenue": [
                    {"month": months[0]["label"], "revenue": round(m1_rev, 2)},
                    {"month": months[1]["label"], "revenue": round(m2_rev, 2)},
                    {"month": months[2]["label"], "revenue": round(m3_rev, 2)}
                ],
                "revenue_change": round(total_change, 2),
                "pct_change": round(pct_change, 2),
                "is_consistent": is_consistent
            }
            
            if is_declining:
                declining_cities.append(city_report)
            else:
                stable_growing_cities.append(city_report)
                
    # Sort declining cities by percentage decline (largest decline first)
    declining_cities.sort(key=lambda x: x["pct_change"])
    stable_growing_cities.sort(key=lambda x: x["pct_change"], reverse=True)
    
    return {
        "declining_cities": declining_cities,
        "stable_growing_cities": stable_growing_cities
    }
