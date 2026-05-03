"""HITL Gate node — pauses the graph for human review if required."""

from __future__ import annotations

import os
import time
from typing import Literal

from langsmith import traceable

import legal_triage.hitl_queue as hitl_queue
from legal_triage.state import TriageState

# Score threshold below which HITL review is required
_HITL_SCORE_THRESHOLD = 0.7
# Confidence threshold below which HITL review is required
_HITL_CONFIDENCE_THRESHOLD = 0.6

# ─────────────────────────────────────────────────────────────────────────────
# DEMO SIMPLIFICATION — HITL_AUTO_APPROVE
# ─────────────────────────────────────────────────────────────────────────────
# When the environment variable HITL_AUTO_APPROVE=true is set, this gate
# becomes a no-op: every email is treated as if the reviewing attorney clicked
# "Approve" — the pipeline's own agent recommendation passes through unchanged.
#
# ⚠️  THIS IS A DEMO / EVAL CONVENIENCE ONLY.
# In production (HITL_AUTO_APPROVE unset or false) EVERY PI lead MUST be
# reviewed by a qualified attorney before an intake decision is recorded.
# Human-in-the-loop oversight is a legal and ethical requirement for this firm.
# Removing it in production removes the only safeguard against false-positive
# lead routing and potential unauthorized legal commitments.
# ─────────────────────────────────────────────────────────────────────────────


@traceable(name="hitl_gate")
def hitl_gate_node(state: TriageState) -> dict:
    """
    Determine if HITL review is required.

    HITL is triggered if:
    - email_class is "pi_lead" (always review new leads)
    - appraisal_score < threshold
    - class_confidence < threshold

    When HITL_AUTO_APPROVE=true (demo mode) this check is bypassed and
    human_decision is set to "approve" automatically — see module-level comment.
    """
    start = time.monotonic()
    latency_ms = int((time.monotonic() - start) * 1000)

    # ── Demo auto-approve bypass ──────────────────────────────────────────────
    # [DEMO SIMPLIFICATION] HITL_AUTO_APPROVE=true skips all human review.
    # Remove / unset this env var in any production deployment.
    if os.environ.get("HITL_AUTO_APPROVE", "false").lower() == "true":
        return {
            "hitl_required": False,
            # Set human_decision so router treats this as an explicit approve.
            # [DEMO SIMPLIFICATION] In production this must come from a real human.
            "human_decision": "approve",
            "hitl_queue_depth": hitl_queue.depth(),
            "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
        }

    # ── Normal production path ────────────────────────────────────────────────
    email_class = state.get("email_class")
    appraisal_score = state.get("appraisal_score") or 1.0
    class_confidence = state.get("class_confidence") or 1.0

    hitl_required = (
        email_class == "pi_lead"
        or appraisal_score < _HITL_SCORE_THRESHOLD
        or class_confidence < _HITL_CONFIDENCE_THRESHOLD
    )

    if hitl_required:
        hitl_queue.enqueue()

    latency_ms = int((time.monotonic() - start) * 1000)

    return {
        "hitl_required": hitl_required,
        "hitl_queue_depth": hitl_queue.depth(),
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }


def hitl_gate_condition(state: TriageState) -> Literal["interrupt", "route"]:
    """LangGraph conditional edge function. Returns 'interrupt' or 'route'."""
    if state.get("hitl_required") and state.get("human_decision") is None:
        return "interrupt"
    return "route"
