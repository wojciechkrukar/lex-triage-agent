"""Classification node — classifies the email into one of five categories."""

from __future__ import annotations

import time

from langsmith import traceable

from legal_triage.llm_factory import get_llm
from legal_triage.state import ModelCall, TriageState

_VALID_CLASSES = {"pi_lead", "general_legal", "spam", "invoice", "other"}

_CLASSIFICATION_PROMPT = """You are a legal email classifier. Classify the following email into exactly one of these categories:
- pi_lead: New personal injury or accident lead (the primary case type for this firm)
- general_legal: General legal inquiry (not PI, e.g. contract, employment, family)
- spam: Spam, junk, or unsolicited commercial email
- invoice: Invoice, billing statement, or payment request
- other: Anything else (internal, newsletter, announcements)

Return ONLY the category name, nothing else.

EMAIL:
{email}
"""


@traceable(name="classification")
def classification_node(state: TriageState) -> dict:
    """Classify the email using the LLM factory."""
    start = time.monotonic()
    llm = get_llm("classifier")
    model_calls = list(state.get("model_calls", []))
    errors = list(state.get("errors", []))

    prompt = _CLASSIFICATION_PROMPT.format(email=state.get("raw_email", ""))
    raw_response = llm.invoke(prompt)

    # Parse response
    email_class = raw_response.strip().lower()
    if email_class not in _VALID_CLASSES:
        errors.append(f"classification: unexpected class {email_class!r}, defaulting to 'other'")
        email_class = "other"

    # Stub confidence
    class_confidence = 0.95 if hasattr(llm, "role") and llm.role == "classifier" else 0.7

    latency_ms = int((time.monotonic() - start) * 1000)
    call: ModelCall = {
        "node": "classification",
        "model": getattr(llm, "model_name", "unknown"),
        "cost_usd": 0.0,
        "latency_ms": latency_ms,
    }
    model_calls.append(call)

    return {
        "email_class": email_class,
        "class_confidence": class_confidence,
        "model_calls": model_calls,
        "errors": errors,
        "total_cost_usd": state.get("total_cost_usd", 0.0),
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
