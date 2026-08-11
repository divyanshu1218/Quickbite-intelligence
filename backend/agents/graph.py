from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from backend.agents.orchestrator import orchestrate_query
from backend.agents.analyst import analyze_data
from backend.agents.diagnostics_agent import run_diagnostic_analysis
from backend.agents.verifier import verify_analytical_state
from backend.agents.synthesizer import synthesize_response

# Define the State definition
class AgentState(TypedDict):
    question: str
    intent: str
    params: Dict[str, Any]
    period: Dict[str, Any]
    metrics_data: Dict[str, Any]
    diagnostic_data: Dict[str, Any]
    diagnostic_insights: Dict[str, Any]
    verification: Dict[str, Any]
    response: Dict[str, Any]
    trace: List[str]

# 1. Orchestrator Node
def orchestrator_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace", []))
    res = orchestrate_query(state["question"])
    trace.append(res["trace_log"])
    return {
        "intent": res["intent"],
        "params": res["params"],
        "period": res["period"],
        "trace": trace
    }

# 2. Analyst Node
def analyst_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace", []))
    res = analyze_data(state["intent"], state["params"], state["period"])
    for log in res["trace_logs"]:
        trace.append(log)
    return {
        "metrics_data": res["metrics_data"],
        "diagnostic_data": res["diagnostic_data"],
        "trace": trace
    }

# 3. Diagnostic Node (Likely Drivers)
def diagnostic_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace", []))
    res = run_diagnostic_analysis(state["intent"], state["metrics_data"], state["diagnostic_data"])
    trace.append(res["trace_log"])
    return {
        "diagnostic_insights": res,
        "trace": trace
    }

# 4. Verifier Node
def verifier_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace", []))
    res = verify_analytical_state(state["intent"], state["metrics_data"], state["diagnostic_data"])
    trace.append(res["trace_log"])
    return {
        "verification": res,
        "trace": trace
    }

# 5. Synthesizer Node
def synthesizer_node(state: AgentState) -> Dict[str, Any]:
    trace = list(state.get("trace", []))
    trace.append("✓ Synthesizing response.")
    res = synthesize_response(
        state["question"],
        state["intent"],
        state["period"],
        state["metrics_data"],
        state["diagnostic_data"],
        state["verification"],
        state.get("diagnostic_insights", {})
    )
    # Add final trace items into response
    res["trace"] = trace
    return {
        "response": res,
        "trace": trace
    }

# Conditional routing check
def route_diagnostics(state: AgentState):
    """
    Decides whether to route through the Diagnostic (Root Cause/Drivers) Agent
    or proceed directly to verification.
    """
    if state["intent"] == "store_diagnostic" or (state["diagnostic_data"] and "error" not in state["diagnostic_data"]):
        return "diagnostics"
    return "verifier"

# Construct the StateGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("diagnostics", diagnostic_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("synthesizer", synthesizer_node)

# Set entry point
workflow.add_edge(START, "orchestrator")
workflow.add_edge("orchestrator", "analyst")

# Add conditional edges
workflow.add_conditional_edges(
    "analyst",
    route_diagnostics,
    {
        "diagnostics": "diagnostics",
        "verifier": "verifier"
    }
)

# Connect intermediate nodes to verifier
workflow.add_edge("diagnostics", "verifier")
workflow.add_edge("verifier", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile graph
app_graph = workflow.compile()

def run_agent_pipeline(question: str) -> dict:
    """
    Invokes the compiled agent graph with a user question and returns the structured response.
    """
    initial_state = {
        "question": question,
        "intent": "unsupported",
        "params": {},
        "period": {},
        "metrics_data": {},
        "diagnostic_data": {},
        "diagnostic_insights": {},
        "verification": {},
        "response": {},
        "trace": ["✓ System initialized."]
    }
    
    output = app_graph.invoke(initial_state)
    return output.get("response", {})
