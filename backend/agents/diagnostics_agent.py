import json
from backend.agents.orchestrator import get_groq_json_response

def run_diagnostic_analysis(intent: str, metrics_data: dict, diagnostic_data: dict) -> dict:
    """
    Diagnostic Agent Node:
    Takes structured diagnostic data and synthesizes likely drivers and reasoning basis
    using Groq without inventing or altering numbers.
    """
    if not diagnostic_data or "error" in diagnostic_data:
        # If no diagnostic data is present (e.g. Q1-Q7 queries), we skip or output minimal defaults.
        # This keeps execution fast and conditional!
        return {
            "reasoning_basis": [],
            "evidence": [],
            "trace_log": "✓ Diagnostic analysis skipped (normal path)."
        }
        
    system_prompt = """
    You are the Diagnostic Agent (Likely Drivers Interpreter) for QuickBite Intelligence.
    Your task is to review the structured diagnostic dataset for a declining store,
    and synthesize clear, professional, evidence-backed observations about likely drivers of decline.

    CRITICAL RULES:
    1. Do NOT make any causal claims. Use words like "likely driver", "strongest observed signal", "suggests", or "correlated with".
    2. Do NOT invent, fabricate, or modify any numbers. Use ONLY the figures provided in the diagnostic dataset.
    3. Output your response as a valid JSON object with the following structure:
       {
         "primary_driver": "A single sentence naming the primary driver and metric drop (e.g., 'A 15.3% drop in Swiggy channel revenue is the strongest observed signal of decline')",
         "reasoning_basis": [
           "A list of 3-4 bullet points detailing specific data-backed findings (e.g., 'Swiggy delivery segment contributed to 85% of the overall revenue drop', 'Order volume decreased by 12% while AOV remained stable')",
           ...
         ],
         "evidence": [
           {"label": "Detailed label of metric change", "value": "Formatted change percentage/value"}
         ]
       }
    """

    user_prompt = f"Diagnostic Data:\n{json.dumps(diagnostic_data, indent=2)}"
    
    parsed_report = get_groq_json_response(system_prompt, user_prompt)
    
    # If API call fails or is empty, provide a safe deterministic fallback from the calculated data itself
    if "error" in parsed_report or not parsed_report.get("reasoning_basis"):
        store_id = diagnostic_data.get("store_id", "Unknown")
        rev_change = diagnostic_data.get("revenue_change_pct", 0.0)
        drivers = diagnostic_data.get("drivers", {})
        
        fallback_basis = [
            f"Revenue declined by {rev_change}% from Month 1 to Month 3 for store {store_id}."
        ]
        for k, v in drivers.items():
            if v.get("score") in ("HIGH", "MEDIUM"):
                fallback_basis.append(f"Strong signal: {v.get('details')}")
                
        parsed_report = {
            "primary_driver": f"Decline of {rev_change}% observed for store {store_id}.",
            "reasoning_basis": fallback_basis,
            "evidence": [
                {"label": "Total Revenue Change", "value": f"{rev_change}%"}
            ]
        }
        
    return {
        "reasoning_basis": parsed_report.get("reasoning_basis", []),
        "evidence": parsed_report.get("evidence", []),
        "primary_driver": parsed_report.get("primary_driver", "Revenue contraction observed."),
        "trace_log": f"✓ Diagnostic analysis completed. Identified drivers: {parsed_report.get('primary_driver')}"
    }
