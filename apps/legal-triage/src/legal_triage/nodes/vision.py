"""Vision node — analyses image attachments if present."""

from __future__ import annotations

import time

from langsmith import traceable

from legal_triage.llm_factory import get_llm
from legal_triage.state import ModelCall, TriageState

_VISION_PROMPT = """You are a legal scene analyst reviewing images attached to an email.
Describe any visible damage, injuries, or hazards that are relevant to a personal injury claim.
Be concise (max 3 sentences).

Context: {email_class} claim
Attachments: {attachment_count} image(s)
"""


@traceable(name="vision_analysis")
def vision_node(state: TriageState) -> dict:
    """Analyse image attachments using the vision LLM."""
    start = time.monotonic()
    llm = get_llm("vision")
    model_calls = list(state.get("model_calls", []))

    attachments = state.get("attachments", [])
    prompt = _VISION_PROMPT.format(
        email_class=state.get("email_class", "unknown"),
        attachment_count=len(attachments),
    )
    vision_summary = llm.invoke(prompt)

    latency_ms = int((time.monotonic() - start) * 1000)
    call: ModelCall = {
        "node": "vision",
        "model": getattr(llm, "model_name", "unknown"),
        "cost_usd": 0.0,
        "latency_ms": latency_ms,
    }
    model_calls.append(call)

    return {
        "vision_summary": vision_summary,
        "model_calls": model_calls,
        "total_cost_usd": state.get("total_cost_usd", 0.0),
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
