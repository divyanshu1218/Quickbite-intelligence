from backend.tools.revenue import get_last_n_month_metrics
from backend.tools.stores import get_store_rankings, get_consistently_declining_stores
from backend.tools.channels import get_channel_performance
from backend.tools.products import get_top_skus
from backend.tools.cities import get_city_revenue_trend
from backend.tools.periods import compare_weekend_weekday, compare_festive_normal
from backend.tools.diagnostics import get_store_diagnostic_metrics
from backend.tools.recommendations import generate_recommendations

def analyze_data(intent: str, params: dict, period: dict) -> dict:
    """
    Data Analyst Agent Node:
    Calls appropriate deterministic tools and populates raw analytical metrics.
    """
    trace_logs = []
    metrics_data = {}
    diagnostic_data = {}
    
    n_months = params.get("n_months", 3)
    top_n = params.get("top_n", 5)
    store_id = params.get("store_id")
    city = params.get("city")
    
    trace_logs.append("✓ Accessing QSR analytical database.")
    
    if intent == "revenue_overview":
        trace_logs.append(f"✓ Running revenue metrics query for last {n_months} months.")
        metrics_data = get_last_n_month_metrics(n_months)
        
    elif intent == "store_rankings":
        trace_logs.append(f"✓ Running store rankings query (top/bottom {top_n}).")
        metrics_data = get_store_rankings(top_n=top_n, bottom_n=top_n)
        
    elif intent == "channel_performance":
        trace_logs.append("✓ Running sales channel contribution analysis.")
        metrics_data = get_channel_performance()
        
    elif intent == "sku_rankings":
        trace_logs.append(f"✓ Running SKU rankings query (top {top_n}).")
        metrics_data = get_top_skus(top_n=top_n)
        
    elif intent == "city_decline":
        trace_logs.append("✓ Analyzing cities MoM growth and decline trends.")
        metrics_data = get_city_revenue_trend()
        
    elif intent == "period_weekend_weekday":
        trace_logs.append("✓ Comparing weekend vs weekday performance metrics.")
        metrics_data = compare_weekend_weekday()
        
    elif intent == "period_festive_normal":
        trace_logs.append("✓ Comparing festive seasonal period vs normal period performance.")
        metrics_data = compare_festive_normal()
        
    elif intent == "store_diagnostic":
        if store_id:
            # Diagnostic for a single store
            trace_logs.append(f"✓ Compiling diagnostic metrics for store {store_id}.")
            diagnostic_data = get_store_diagnostic_metrics(store_id)
            metrics_data = {
                "store_id": store_id,
                "revenue_change_pct": diagnostic_data.get("revenue_change_pct", 0.0),
                "revenue_change_val": diagnostic_data.get("revenue_change_val", 0.0)
            }
        else:
            # Get list of consistently declining stores
            trace_logs.append("✓ Identifying stores with consistent monthly decline.")
            declining_list = get_consistently_declining_stores()
            metrics_data = {"declining_stores": declining_list}
            
            # If there's a specific decline target that was queried (e.g. Hyderabad city or first store in list)
            if declining_list:
                first_store_id = declining_list[0]["store_id"]
                trace_logs.append(f"✓ Extracting deep diagnostic metrics for representative store {first_store_id}.")
                diagnostic_data = get_store_diagnostic_metrics(first_store_id)
            else:
                trace_logs.append("✓ No consistently declining stores found.")
                
    elif intent == "revenue_growth_advisory":
        trace_logs.append("✓ Pulling revenue overview, declining stores, channel mix and top SKUs for advisory.")
        metrics_data = get_last_n_month_metrics(n_months)
        declining_stores = get_consistently_declining_stores()
        rankings = get_store_rankings(top_n=5, bottom_n=5)
        channels = get_channel_performance()
        # Grab recommendations for the worst-performing store
        recs = {}
        if declining_stores:
            worst_id = declining_stores[0]["store_id"]
            trace_logs.append(f"✓ Generating targeted recommendations for worst store {worst_id}.")
            recs = generate_recommendations(store_id=worst_id, n_months=n_months)
        metrics_data["declining_stores"] = declining_stores
        metrics_data["bottom_stores"] = rankings.get("bottom_stores", [])
        metrics_data["top_stores"] = rankings.get("top_stores", [])
        metrics_data["channels"] = channels.get("channels", [])
        metrics_data["recommendations"] = recs.get("recommendations", [])

    elif intent == "unsupported":
        trace_logs.append("⚠ Query intent classified as outside analytical scope.")

    elif intent == "ambiguous":
        trace_logs.append("⚠ Ambiguous parameters detected.")
        
    return {
        "metrics_data": metrics_data,
        "diagnostic_data": diagnostic_data,
        "trace_logs": trace_logs
    }
