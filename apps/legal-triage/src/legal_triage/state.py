"""LangGraph state definition for the legal triage pipeline."""

from __future__ import annotations

from typing import TypedDict


class ModelCall(TypedDict):
    node: str
    model: str
    cost_usd: float
    latency_ms: int


class TriageState(TypedDict):
    # Input
    email_id: str
    raw_email: str
    attachments: list[dict]  # [{filename, content_type, data_b64}]

    # Classification
    email_class: str | None  # "pi_lead" | "general_legal" | "spam" | "invoice" | "other"
    class_confidence: float | None

    # Vision
    vision_summary: str | None

    # Appraisal
    appraisal_draft: str | None
    appraisal_score: float | None  # 0-1, set by Critic
    appraisal_critique: str | None

    # HITL
    hitl_required: bool
    human_decision: str | None  # "approve" | "reject" | "reclassify"
    human_notes: str | None

    # Routing
    terminal_sink: str | None  # "NewLead" | "GeneralLegal" | "Refused-Spam" | ...

    # Telemetry
    total_cost_usd: float
    total_latency_ms: int
    model_calls: list[ModelCall]

    # Errors
    errors: list[str]


def initial_state(email_id: str, raw_email: str, attachments: list[dict] | None = None) -> TriageState:
    """Create an initial TriageState for a new email."""
    return TriageState(
        email_id=email_id,
        raw_email=raw_email,
        attachments=attachments or [],
        email_class=None,
        class_confidence=None,
        vision_summary=None,
        appraisal_draft=None,
        appraisal_score=None,
        appraisal_critique=None,
        hitl_required=False,
        human_decision=None,
        human_notes=None,
        terminal_sink=None,
        total_cost_usd=0.0,
        total_latency_ms=0,
        model_calls=[],
        errors=[],
    )
