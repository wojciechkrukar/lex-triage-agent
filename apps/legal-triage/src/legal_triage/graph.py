"""
LangGraph StateGraph assembly for the legal triage pipeline.

Graph topology:
  ingestion → classification → [vision?] → appraisal_creator → appraisal_critic
  → hitl_gate → [interrupt?] → router → terminal sinks
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from legal_triage.nodes.appraisal_creator import appraisal_creator_node
from legal_triage.nodes.appraisal_critic import appraisal_critic_node
from legal_triage.nodes.classification import classification_node
from legal_triage.nodes.hitl_gate import hitl_gate_condition, hitl_gate_node
from legal_triage.nodes.ingestion import ingestion_node
from legal_triage.nodes.router import router_node
from legal_triage.nodes.vision import vision_node
from legal_triage.state import TriageState


def _should_run_vision(state: TriageState) -> str:
    """Route to vision node if there are attachments."""
    if state.get("attachments"):
        return "vision"
    return "appraisal_creator"


def build_graph() -> StateGraph:
    """Build and compile the triage StateGraph."""
    graph = StateGraph(TriageState)

    # Add nodes
    graph.add_node("ingestion", ingestion_node)
    graph.add_node("classification", classification_node)
    graph.add_node("vision", vision_node)
    graph.add_node("appraisal_creator", appraisal_creator_node)
    graph.add_node("appraisal_critic", appraisal_critic_node)
    graph.add_node("hitl_gate", hitl_gate_node)
    graph.add_node("router", router_node)

    # Edges
    graph.add_edge(START, "ingestion")
    graph.add_edge("ingestion", "classification")

    # Conditional: vision if attachments, else skip to appraisal_creator
    graph.add_conditional_edges(
        "classification",
        _should_run_vision,
        {"vision": "vision", "appraisal_creator": "appraisal_creator"},
    )
    graph.add_edge("vision", "appraisal_creator")
    graph.add_edge("appraisal_creator", "appraisal_critic")
    graph.add_edge("appraisal_critic", "hitl_gate")

    # Conditional: HITL interrupt or proceed to router
    graph.add_conditional_edges(
        "hitl_gate",
        hitl_gate_condition,
        {"interrupt": END, "route": "router"},
    )
    graph.add_edge("router", END)

    return graph


def get_compiled_graph():
    """Return a compiled LangGraph graph ready for invocation."""
    return build_graph().compile()


def export_mermaid() -> str:
    """Export the graph topology as a Mermaid diagram string."""
    return """graph LR
    A[Ingestion] --> B[Classification]
    B --> C{Has attachments?}
    C -- yes --> D[Vision Analysis]
    C -- no --> E[Legal Appraisal Creator]
    D --> E
    E --> F[Legal Appraisal Critic]
    F --> G[HITL Gate]
    G -- hitl_required --> H([INTERRUPT])
    G -- no hitl --> I[Router]
    I --> J([NewLead])
    I --> K([GeneralLegal])
    I --> L([Refused-Spam])
    I --> M([Refused-Invoice])
    I --> N([Refused-Other])"""
