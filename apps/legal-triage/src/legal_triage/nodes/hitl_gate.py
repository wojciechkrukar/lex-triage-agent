"""HITL Gate node — pauses the graph for human review if required."""

from __future__ import annotations

import time
from typing import Literal

from langsmith import traceable

from legal_triage.state import TriageState

# Score threshold below which HITL review is required
_HITL_SCORE_THRESHOLD = 0.7
# Confidence threshold below which HITL review is required
_HITL_CONFIDENCE_THRESHOLD = 0.6


@traceable(name="hitl_gate")
def hitl_gate_node(state: TriageState) -> dict:
    """
    Determine if HITL review is required.

    HITL is triggered if:
    - email_class is "pi_lead" (always review new leads)
    - appraisal_score < threshold
    - class_confidence < threshold
    """
    start = time.monotonic()

    email_class = state.get("email_class")
    appraisal_score = state.get("appraisal_score") or 1.0
    class_confidence = state.get("class_confidence") or 1.0

    hitl_required = (
        email_class == "pi_lead"
        or appraisal_score < _HITL_SCORE_THRESHOLD
        or class_confidence < _HITL_CONFIDENCE_THRESHOLD
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    return {
        "hitl_required": hitl_required,
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }


def hitl_gate_condition(state: TriageState) -> Literal["interrupt", "route"]:
    """LangGraph conditional edge function. Returns 'interrupt' or 'route'."""
    if state.get("hitl_required") and state.get("human_decision") is None:
        return "interrupt"
    return "route"
