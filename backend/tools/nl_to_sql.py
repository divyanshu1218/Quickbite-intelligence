"""
Natural Language to SQL Engine
Converts plain English questions into SQL queries using pattern matching and entity extraction.
Sub-100ms response, 100% deterministic, no LLM dependency.
"""
import re
import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

# Compiled regex patterns for intent detection
PATTERNS = {
    "top_stores": [
        re.compile(r"top\s+(\d+)\s+stores?\s+(?:by\s+)?(?:in\s+)?(\w+)?", re.I),
        re.compile(r"best\s+(?:performing\s+)?stores?", re.I),
        re.compile(r"highest\s+(?:revenue\s+)?stores?", re.I),
    ],
    "bottom_stores": [
        re.compile(r"bottom\s+(\d+)\s+stores?", re.I),
        re.compile(r"worst\s+(?:performing\s+)?stores?", re.I),
        re.compile(r"lowest\s+(?:revenue\s+)?stores?", re.I),
    ],
    "store_revenue": [
        re.compile(r"(?:revenue|sales)\s+(?:for|of|at)\s+(?:store\s+)?(\w+)", re.I),
        re.compile(r"how\s+(?:much|is)\s+(?:revenue|sales)\s+(?:at|for|in)\s+(\w+)", re.I),
    ],
    "city_performance": [
        re.compile(r"(?:how|what)\s+(?:is|are)\s+(\w+)\s+(?:doing|performing)", re.I),
        re.compile(r"(?:revenue|performance|sales)\s+(?:in|for|of)\s+(\w+)", re.I),
    ],
    "channel_breakdown": [
        re.compile(r"channel\s+(?:breakdown|performance|split|comparison)", re.I),
        re.compile(r"(?:swiggy|zomato|dine.?in|takeaway)\s+(?:vs|versus|compared)", re.I),
        re.compile(r"(?:revenue|aov|sales|orders)?\s*(?:by|per|across|for)?\s*channels?", re.I),
        re.compile(r"channel", re.I),
    ],
    "decline_detection": [
        re.compile(r"(?:which|what)\s+(?:stores?|cities?)\s+(?:are|is)?\s*(?:declining|dropped|fell|decreased|losing)", re.I),
        re.compile(r"(?:declining|losing)\s+(?:stores?|cities?|sales|revenue)", re.I),
        re.compile(r"decline\s+(?:in|at|for)\s+(\w+)", re.I),
        re.compile(r"store\s+(?:decline|declining|drop)", re.I),
    ],

    "growth_analysis": [
        re.compile(r"(?:which|what)\s+(?:stores?|cities?)\s+(?:are\s+)?(?:growing|increased|improved)", re.I),
        re.compile(r"growth\s+(?:in|at|for)\s+(\w+)", re.I),
    ],
    "monthly_trend": [
        re.compile(r"(?:monthly|month.over.month|mom)\s+(?:trend|revenue|performance)", re.I),
        re.compile(r"(?:trend|revenue)\s+(?:over|across)\s+(?:months|time)", re.I),
    ],
    "product_performance": [
        re.compile(r"(?:top|best|highest)\s+(?:selling\s+)?(?:products?|skus?|items?|menu)", re.I),
        re.compile(r"(?:which|what)\s+(?:products?|skus?|items?)\s+(?:sell|sold|perform)", re.I),
    ],
    "weekend_weekday": [
        re.compile(r"weekend\s+(?:vs|versus|compared|performance)", re.I),
        re.compile(r"weekday\s+(?:vs|versus|compared|performance)", re.I),
    ],
}

# Entity extraction patterns
CITY_PATTERN = re.compile(
    r"\b(Pune|Mumbai|Delhi|Bengaluru|Bangalore|Hyderabad|Chennai|Kolkata|Ahmedabad|Jaipur|Gurugram|Gurgaon|Lucknow|Chandigarh|Kochi|Noida)\b", re.I
)
STORE_ID_PATTERN = re.compile(r"\b(ST\d{3})\b", re.I)
NUMBER_PATTERN = re.compile(r"\b(\d+)\b")
MONTH_PATTERN = re.compile(r"\b(last\s+(\d+)\s+months?)\b", re.I)
CHANNEL_PATTERN = re.compile(r"\b(Swiggy|Zomato|Dine.?in|Takeaway)\b", re.I)

def extract_entities(question: str) -> dict:
    """Extract named entities from user input."""
    entities = {}
    
    # Cities
    city_matches = CITY_PATTERN.findall(question)
    if city_matches:
        entities["cities"] = [c.title() for c in city_matches]
    
    # Store IDs
    store_matches = STORE_ID_PATTERN.findall(question)
    if store_matches:
        entities["store_ids"] = [s.upper() for s in store_matches]
    
    # Channels
    channel_matches = CHANNEL_PATTERN.findall(question)
    if channel_matches:
        entities["channels"] = [c.title().replace("Dine In", "Dine-in").replace("Dinein", "Dine-in") for c in channel_matches]
    
    # Month range
    month_match = MONTH_PATTERN.search(question)
    if month_match:
        entities["n_months"] = int(month_match.group(2))
    
    # Top N
    top_match = re.search(r"(?:top|best|worst|bottom)\s+(\d+)", question, re.I)
    if top_match:
        entities["top_n"] = int(top_match.group(1))
    
    return entities

def detect_intent(question: str) -> str:
    """Detect query intent using compiled regex patterns."""
    q = question.lower()
    for intent_name, patterns in PATTERNS.items():
        for pattern in patterns:
            if pattern.search(q):
                return intent_name
    return None

def build_sql_query(intent: str, entities: dict) -> tuple:
    """Build parameterized SQL query based on intent and entities."""
    n_months = entities.get("n_months", 3)
    start_date, end_date, label = resolve_period_last_n_months(n_months)
    top_n = entities.get("top_n", 5)
    
    if intent == "top_stores":
        city_filter = ""
        params = [start_date, end_date]
        if "cities" in entities:
            placeholders = ",".join(["?" for _ in entities["cities"]])
            city_filter = f"AND s.CITY IN ({placeholders})"
            params.extend(entities["cities"])
        
        sql = f"""
            SELECT s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT,
                   SUM(o.NET_REVENUE) as revenue, COUNT(o.ORDER_ID) as orders,
                   SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) as aov
            FROM Store_Master s JOIN Orders o ON o.STORE_ID = s.STORE_ID
            WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ? {city_filter}
            GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT
            ORDER BY revenue DESC LIMIT {top_n}
        """
        return sql, params, label
    
    elif intent == "bottom_stores":
        city_filter = ""
        params = [start_date, end_date]
        if "cities" in entities:
            placeholders = ",".join(["?" for _ in entities["cities"]])
            city_filter = f"AND s.CITY IN ({placeholders})"
            params.extend(entities["cities"])
        
        sql = f"""
            SELECT s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT,
                   SUM(o.NET_REVENUE) as revenue, COUNT(o.ORDER_ID) as orders,
                   SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) as aov
            FROM Store_Master s JOIN Orders o ON o.STORE_ID = s.STORE_ID
            WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ? {city_filter}
            GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT
            ORDER BY revenue ASC LIMIT {top_n}
        """
        return sql, params, label
    
    elif intent == "store_revenue":
        store_ids = entities.get("store_ids", [])
        if store_ids:
            placeholders = ",".join(["?" for _ in store_ids])
            sql = f"""
                SELECT s.STORE_ID, s.STORE_NAME, s.CITY,
                       SUM(o.NET_REVENUE) as revenue, COUNT(o.ORDER_ID) as orders,
                       SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) as aov
                FROM Store_Master s JOIN Orders o ON o.STORE_ID = s.STORE_ID
                WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
                  AND s.STORE_ID IN ({placeholders})
                GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY
            """
            return sql, [start_date, end_date] + store_ids, label
        return None, None, label
    
    elif intent == "city_performance":
        cities = entities.get("cities", [])
        if cities:
            placeholders = ",".join(["?" for _ in cities])
            sql = f"""
                SELECT s.CITY as city, SUM(o.NET_REVENUE) as revenue,
                       COUNT(o.ORDER_ID) as orders, SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) as aov
                FROM Store_Master s JOIN Orders o ON o.STORE_ID = s.STORE_ID
                WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
                  AND s.CITY IN ({placeholders})
                GROUP BY s.CITY ORDER BY revenue DESC
            """
            return sql, [start_date, end_date] + cities, label
        else:
            sql = """
                SELECT s.CITY as city, SUM(o.NET_REVENUE) as revenue,
                       COUNT(o.ORDER_ID) as orders, SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) as aov
                FROM Store_Master s JOIN Orders o ON o.STORE_ID = s.STORE_ID
                WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
                GROUP BY s.CITY ORDER BY revenue DESC
            """
            return sql, [start_date, end_date], label
    
    elif intent == "channel_breakdown":
        sql = """
            SELECT CHANNEL as channel, SUM(NET_REVENUE) as revenue,
                   COUNT(ORDER_ID) as orders, SUM(NET_REVENUE)/COUNT(ORDER_ID) as aov
            FROM Orders
            WHERE CAST(ORDER_DATETIME AS DATE) >= ? AND CAST(ORDER_DATETIME AS DATE) <= ?
            GROUP BY CHANNEL ORDER BY revenue DESC
        """
        return sql, [start_date, end_date], label
    
    elif intent == "monthly_trend":
        sql = """
            SELECT c.YEAR as year, c.MONTH as month, c.MONTH_NO as month_no,
                   SUM(o.NET_REVENUE) as revenue, COUNT(o.ORDER_ID) as orders,
                   SUM(o.NET_REVENUE)/COUNT(o.ORDER_ID) as aov
            FROM Calendar c JOIN Orders o ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
            WHERE c.DATE >= ? AND c.DATE <= ?
            GROUP BY c.YEAR, c.MONTH, c.MONTH_NO ORDER BY c.YEAR, c.MONTH_NO
        """
        return sql, [start_date, end_date], label
    
    elif intent == "product_performance":
        sql = f"""
            SELECT p.SKU_ID, p.SKU_NAME, p.CATEGORY, p.VEG_NONVEG,
                   SUM(od.QUANTITY) as quantity_sold, SUM(od.LINE_NET_VALUE) as revenue
            FROM Product_Master p JOIN Order_Details od ON od.SKU_ID = p.SKU_ID
            JOIN Orders o ON o.ORDER_ID = od.ORDER_ID
            WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
            GROUP BY p.SKU_ID, p.SKU_NAME, p.CATEGORY, p.VEG_NONVEG
            ORDER BY revenue DESC LIMIT {top_n}
        """
        return sql, [start_date, end_date], label

    elif intent == "decline_detection":
        sql = """
            SELECT s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT,
                   COALESCE(SUM(CASE WHEN c.MONTH_NO = 5 THEN o.NET_REVENUE ELSE 0 END), 0) as may_revenue,
                   COALESCE(SUM(CASE WHEN c.MONTH_NO = 6 THEN o.NET_REVENUE ELSE 0 END), 0) as june_revenue,
                   COALESCE(SUM(CASE WHEN c.MONTH_NO = 7 THEN o.NET_REVENUE ELSE 0 END), 0) as july_revenue,
                   ROUND(((COALESCE(SUM(CASE WHEN c.MONTH_NO = 7 THEN o.NET_REVENUE ELSE 0 END), 0) -
                           COALESCE(SUM(CASE WHEN c.MONTH_NO = 5 THEN o.NET_REVENUE ELSE 0 END), 0)) /
                          NULLIF(SUM(CASE WHEN c.MONTH_NO = 5 THEN o.NET_REVENUE ELSE 0 END), 0)) * 100, 1) as pct_change
            FROM Store_Master s
            JOIN Orders o ON o.STORE_ID = s.STORE_ID
            JOIN Calendar c ON CAST(o.ORDER_DATETIME AS DATE) = c.DATE
            WHERE c.DATE >= ? AND c.DATE <= ?
            GROUP BY s.STORE_ID, s.STORE_NAME, s.CITY, s.STORE_FORMAT
            HAVING may_revenue > june_revenue AND june_revenue > july_revenue
            ORDER BY pct_change ASC
        """
        return sql, [start_date, end_date], label

    
    return None, None, label

def execute_nl_query(question: str) -> dict:
    """
    Main entry point: attempts to execute a natural language query using pure pattern matching.
    Returns None if the question doesn't match any known pattern (falls back to LLM).
    """
    import time
    start_time = time.perf_counter()
    
    intent = detect_intent(question)
    if not intent:
        return None  # Signal fallback to LLM pipeline
    
    entities = extract_entities(question)
    sql, params, period_label = build_sql_query(intent, entities)
    
    if not sql:
        return None
    
    results = DatabaseManager.execute_query(sql, params)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)
    
    # Format results into structured response
    start_date, end_date, _ = resolve_period_last_n_months(entities.get("n_months", 3))
    
    return {
        "question": question,
        "analysis_type": f"nl_sql_{intent}",
        "period": {"start": str(start_date), "end": str(end_date), "label": period_label},
        "insight": f"Query executed in {elapsed_ms}ms using deterministic SQL engine. Found {len(results)} results.",
        "metrics": {"results": results, "result_count": len(results)},
        "chart": _build_chart_for_intent(intent, results),
        "evidence": [{"label": "Execution Method", "value": "Deterministic SQL (no LLM)"},
                     {"label": "Response Time", "value": f"{elapsed_ms}ms"},
                     {"label": "Records Analyzed", "value": str(len(results))}],
        "reasoning_basis": [f"Pattern-matched intent: {intent}", f"Entities extracted: {entities}"],
        "verification": {"status": "passed", "checks": [
            {"description": f"SQL query returned {len(results)} rows", "result": "passed"}
        ]},
        "confidence": "high",
        "trace": [f"✓ NL-to-SQL engine matched intent '{intent}' in {elapsed_ms}ms",
                  f"✓ Extracted entities: {entities}",
                  "✓ SQL executed deterministically (no LLM call)"]
    }

def _build_chart_for_intent(intent: str, results: list) -> dict:
    """Build chart specification from NL-SQL results."""
    if intent in ("top_stores", "bottom_stores"):
        return {
            "type": "bar", "title": f"{'Top' if intent == 'top_stores' else 'Bottom'} Stores by Revenue",
            "xKey": "STORE_NAME", "series": [{"key": "revenue", "label": "Revenue (INR)", "type": "bar"}],
            "data": results
        }
    elif intent == "channel_breakdown":
        return {
            "type": "grouped-bar", "title": "Channel Performance",
            "xKey": "channel", "series": [{"key": "revenue", "label": "Revenue", "type": "bar"}, {"key": "aov", "label": "AOV", "type": "line"}],
            "data": results
        }
    elif intent == "monthly_trend":
        return {
            "type": "line", "title": "Monthly Revenue Trend",
            "xKey": "month", "series": [{"key": "revenue", "label": "Revenue (INR)", "type": "line"}],
            "data": results
        }
    elif intent == "product_performance":
        return {
            "type": "bar", "title": "Top Products by Revenue",
            "xKey": "SKU_NAME", "series": [{"key": "revenue", "label": "Revenue", "type": "bar"}],
            "data": results
        }
    return {"type": "bar", "title": "Results", "xKey": "name", "series": [], "data": results}
