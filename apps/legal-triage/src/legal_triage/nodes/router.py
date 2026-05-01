"""Router node — routes the email to its terminal sink."""

from __future__ import annotations

import time

from langsmith import traceable

from legal_triage.state import TriageState

_CLASS_TO_SINK = {
    "pi_lead": "NewLead",
    "general_legal": "GeneralLegal",
    "spam": "Refused-Spam",
    "invoice": "Refused-Invoice",
    "other": "Refused-Other",
}


@traceable(name="router")
def router_node(state: TriageState) -> dict:
    """Route the email to its terminal sink based on classification."""
    start = time.monotonic()

    email_class = state.get("email_class") or "other"
    human_decision = state.get("human_decision")

    # Human override takes precedence
    if human_decision == "reject":
        terminal_sink = "Refused-Other"
    elif human_decision == "reclassify":
        # Re-route based on human notes or default to GeneralLegal
        terminal_sink = "GeneralLegal"
    else:
        terminal_sink = _CLASS_TO_SINK.get(email_class, "Refused-Other")

    latency_ms = int((time.monotonic() - start) * 1000)

    return {
        "terminal_sink": terminal_sink,
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
