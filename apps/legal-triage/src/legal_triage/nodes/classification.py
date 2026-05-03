"""Classification node — classifies the email into one of five categories."""

from __future__ import annotations

import time

from langsmith import traceable

from legal_triage.llm_factory import extract_cost, get_llm, get_model_name
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

    model_name = get_model_name("classifier")
    prompt = _CLASSIFICATION_PROMPT.format(email=state.get("raw_email", ""))
    message = llm.invoke(prompt)

    # Both StubLLM._StubMessage and LangChain AIMessage expose .content
    raw_text = getattr(message, "content", str(message)).strip().lower()
    email_class = raw_text if raw_text in _VALID_CLASSES else "other"
    if raw_text not in _VALID_CLASSES:
        errors.append(f"classification: unexpected class {raw_text!r}, defaulting to 'other'")

    # Confidence: stubs return deterministic stub → 0.95; real LLM → 0.7 baseline
    class_confidence = 0.95 if isinstance(getattr(llm, "model_name", ""), str) and "stub" in getattr(llm, "model_name", "") else 0.7

    cost = extract_cost(message, model_name)
    latency_ms = int((time.monotonic() - start) * 1000)
    call: ModelCall = {
        "node": "classification",
        "model": model_name,
        "cost_usd": cost,
        "latency_ms": latency_ms,
    }
    model_calls.append(call)

    return {
        "email_class": email_class,
        "class_confidence": class_confidence,
        "model_calls": model_calls,
        "errors": errors,
        "total_cost_usd": state.get("total_cost_usd", 0.0) + cost,
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
