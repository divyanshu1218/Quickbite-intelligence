import json
from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.utils.dates import resolve_period_last_n_months
from backend.data.database import DatabaseManager

# Initialize Groq client
if not GROQ_API_KEY:
    # Use dummy client or raise, but let's handle empty keys gracefully for testing
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)

def get_groq_json_response(system_prompt: str, user_prompt: str) -> dict:
    """
    Helper to fetch JSON response from Groq.
    """
    if not client:
        # Fallback dictionary if Groq API key is not present (for test coverage)
        return {"intent": "unsupported", "params": {}}
        
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq API Error: {e}")
        # Return a fallback parsed dictionary
        return {"intent": "unsupported", "params": {}, "error": str(e)}

def rule_based_classify(question: str) -> dict:
    q = question.lower()
    
    # 1. Total revenue, orders, and AOV for the last 3 months
    if "revenue" in q and "orders" in q and "aov" in q:
        return {"intent": "revenue_overview", "params": {"n_months": 3}}
    if "total revenue" in q or "revenue, orders" in q or "revenue and orders" in q:
        return {"intent": "revenue_overview", "params": {"n_months": 3}}
    if "last 3 months" in q and "revenue" in q:
        return {"intent": "revenue_overview", "params": {"n_months": 3}}
    if "last 6 months" in q and "revenue" in q:
        return {"intent": "revenue_overview", "params": {"n_months": 6}}

    # Revenue growth / improvement questions → show overview + diagnostics
    if any(k in q for k in [
        "increase revenue", "grow revenue", "improve revenue", "boost revenue",
        "revenue growth", "improve sales", "increase sales", "grow sales",
        "boost sales", "improve performance", "increase profit", "grow profit",
        "how to improve", "suggestions", "recommendations", "what should we do",
        "action plan", "strategy", "what can we do", "how can we"
    ]):
        return {"intent": "revenue_growth_advisory", "params": {"n_months": 3}}

    # 8. Stores consistently declining
    if any(k in q for k in [
        "consistently declined", "consistently decline", "declining store",
        "store is declining", "stores are declining",
        "which store is declining", "which stores are declining",
        "key reasons", "consistently declined"
    ]):
        store_id = None
        for i in range(1, 51):
            sid = f"ST{i:03d}"
            if sid.lower() in q or f"store {i}" in q:
                store_id = sid
                break
        return {"intent": "store_diagnostic", "params": {"store_id": store_id}}

    if "declined" in q and "stores" in q:
        return {"intent": "store_diagnostic", "params": {"store_id": None}}

    # 2. Top 5 and bottom 5 stores by revenue
    if "top 5" in q and "bottom 5" in q:
        return {"intent": "store_rankings", "params": {"top_n": 5}}
    if "store rankings" in q or "stores by revenue" in q:
        return {"intent": "store_rankings", "params": {"top_n": 5}}
    if "top stores" in q or "best stores" in q or "top performing stores" in q:
        return {"intent": "store_rankings", "params": {"top_n": 5}}

    # 3. Revenue and AOV by channel
    if "channel" in q:
        return {"intent": "channel_performance", "params": {}}

    # 4. Top 5 SKUs by quantity sold and revenue
    if "sku" in q or "skus" in q or "highest selling" in q or "product" in q or "products" in q:
        return {"intent": "sku_rankings", "params": {"top_n": 5}}
    if "menu" in q or "item" in q or "food" in q:
        return {"intent": "sku_rankings", "params": {"top_n": 5}}

    # 5. Cities with declining revenue over the last 3 months
    if ("cities" in q or "city" in q) and ("decline" in q or "declining" in q or "drop" in q):
        return {"intent": "city_decline", "params": {}}
    if "geographic" in q or "location performance" in q or "city performance" in q:
        return {"intent": "city_decline", "params": {}}

    # 6. Weekend vs weekday performance
    if "weekend" in q or "weekday" in q:
        return {"intent": "period_weekend_weekday", "params": {}}
    if "saturday" in q or "sunday" in q:
        return {"intent": "period_weekend_weekday", "params": {}}

    # 7. Festive-period vs normal-period performance
    if "festive" in q or "festival" in q or "diwali" in q or "eid" in q or "holiday" in q:
        return {"intent": "period_festive_normal", "params": {}}

    # Decline / diagnostic for a specific store
    if "decline" in q or "why" in q or "reason" in q or "diagnosis" in q:
        for i in range(1, 51):
            sid = f"ST{i:03d}"
            if sid.lower() in q or f"st {i}" in q:
                return {"intent": "store_diagnostic", "params": {"store_id": sid}}
        # General 'why decline' without a specific store → show declining stores
        if "decline" in q or "declining" in q:
            return {"intent": "store_diagnostic", "params": {"store_id": None}}

    # Overview / summary / dashboard
    if any(k in q for k in ["overview", "summary", "dashboard", "performance", "how are we doing", "business health"]):
        return {"intent": "revenue_overview", "params": {"n_months": 3}}

    # Ambiguous
    if len(q.split()) < 3:
        return {"intent": "ambiguous", "params": {}}

    return {"intent": "unsupported", "params": {}}

def orchestrate_query(question: str) -> dict:
    """
    Orchestrator Agent Node:
    Uses rule-based classification first, then falls back to Groq for query intent and parameter extraction.
    Resolves dates deterministically.
    """
    # First pass: try rule-based classifier
    rule_res = rule_based_classify(question)
    
    if rule_res["intent"] != "unsupported" and rule_res["intent"] != "ambiguous":
        parsed_intent = rule_res
    else:
        # Fall back to Groq if client is available
        if client:
            system_prompt = """
            You are the Orchestrator Agent for QuickBite Intelligence (a QSR business analytics workspace).
            Your task is to classify a natural language business question into one of the supported analytical intents,
            and extract relevant parameters.

            SUPPORTED INTENTS:
            1. "revenue_overview": Total revenue, orders, and AOV (e.g. "What were total revenue, orders, and AOV for the last 3 months?", "metrics for last quarter").
            2. "store_rankings": Rankings of stores by revenue (e.g. "Top 5 and bottom 5 stores by revenue", "store rankings").
            3. "channel_performance": Revenue and AOV by channel (e.g. "Revenue and AOV by channel", "which channel did best?").
            4. "sku_rankings": Top SKUs by quantity and revenue (e.g. "Top 5 SKUs by quantity sold and revenue", "highest selling products").
            5. "city_decline": Cities showing declining revenue (e.g. "Which cities have shown a decline in revenue over the last 3 months?").
            6. "period_weekend_weekday": Weekend vs weekday comparison (e.g. "Weekend vs weekday performance").
            7. "period_festive_normal": Festive period vs normal period comparison (e.g. "Festive-period vs normal-period performance").
            8. "store_diagnostic": Stores consistently declining and their drivers (e.g. "Which stores consistently declined in the last 3 months and why?").
            9. "revenue_growth_advisory": Questions about how to improve, grow, or increase revenue, sales, or performance (e.g. "How to increase revenue?", "What should we do to grow sales?", "Recommendations to improve performance").
            10. "unsupported": For questions completely outside business scope (e.g. "Who is the Prime Minister of India?", "What is the weather?").
            11. "ambiguous": The question is vague (e.g. "metrics?").

            PARAMETERS TO EXTRACT:
            - "n_months": integer (default is 3, extract if user specifies e.g. "last 6 months")
            - "top_n": integer (default is 5, extract if user specifies e.g. "top 10 SKUs")
            - "store_id": string (extract if user asks about a specific store e.g. "why did ST001 decline?")
            - "city": string (extract if user asks about a specific city e.g. "Why did Hyderabad decline?")

            You must output a valid JSON object with the keys:
            "intent": string (one of the intent names above)
            "params": object containing any extracted parameters
            "explanation": string (brief explanation of classification rationale)
            """
            user_prompt = f"Question: '{question}'"
            parsed_intent = get_groq_json_response(system_prompt, user_prompt)
        else:
            parsed_intent = rule_res
    
    # Resolve dates deterministically based on extracted n_months or default (3 months)
    n_months = parsed_intent.get("params", {}).get("n_months", 3)
    start_date, end_date, label = resolve_period_last_n_months(n_months)
    
    # Enrich parameter extraction mapping if user queried a specific store by name
    store_id = parsed_intent.get("params", {}).get("store_id")
    if store_id and not store_id.startswith("ST"):
        # Attempt to map store name to ID from database
        query = "SELECT STORE_ID FROM Store_Master WHERE LOWER(STORE_NAME) LIKE ? OR LOWER(CITY) LIKE ? LIMIT 1;"
        param_term = f"%{store_id.lower()}%"
        res = DatabaseManager.execute_query(query, [param_term, param_term])
        if res:
            parsed_intent["params"]["store_id"] = res[0]["STORE_ID"]
            
    # Resolve cities if applicable
    city = parsed_intent.get("params", {}).get("city")
    
    final_intent = parsed_intent.get("intent", "unsupported")

    # Smart fallback for business queries if classification produced unsupported (e.g. Groq 403 / API error)
    if final_intent == "unsupported":
        q_lower = question.lower()
        if any(w in q_lower for w in ["revenue", "sales", "order", "aov", "store", "city", "channel", "sku", "product", "performance", "growth", "decline", "increase", "improve", "how", "what", "which", "recommendation", "strategy", "why"]):
            final_intent = "revenue_growth_advisory"

    return {
        "intent": final_intent,
        "params": parsed_intent.get("params", {}),
        "period": {
            "start": str(start_date),
            "end": str(end_date),
            "label": label
        },
        "trace_log": f"✓ Question interpreted as intent '{final_intent}' over period {label}."
    }
