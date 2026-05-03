"""Vision node — analyses image attachments if present."""

from __future__ import annotations

import time
from typing import Any

from langsmith import traceable

from legal_triage.llm_factory import StubLLM, extract_cost, get_llm, get_model_name
from legal_triage.state import ModelCall, TriageState

_VISION_TEXT_PROMPT = """You are a legal scene analyst reviewing images attached to an email.
Describe any visible damage, injuries, or hazards that are relevant to a personal injury claim.
Be concise (max 3 sentences).

Context: {email_class} claim
Attachments: {attachment_count} image(s)
"""


def _build_vision_payload(email_class: str, attachments: list[dict[str, Any]]) -> Any:
    """
    Build the LangChain message payload for vision inference.

    For real LLMs (tier1/tier2): returns a HumanMessage with interleaved text +
    base64 image_url parts so GPT-4o can see the actual images.

    For stub/fallback: returns the plain text prompt string.
    """
    from langchain_core.messages import HumanMessage  # noqa: PLC0415

    text_part: dict[str, Any] = {
        "type": "text",
        "text": _VISION_TEXT_PROMPT.format(
            email_class=email_class,
            attachment_count=len(attachments),
        ),
    }
    content: list[dict[str, Any]] = [text_part]

    for att in attachments:
        data_b64 = att.get("data_b64", "")
        content_type = att.get("content_type", "image/jpeg")
        if data_b64:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{content_type};base64,{data_b64}"},
                }
            )

    return HumanMessage(content=content)


@traceable(name="vision_analysis")
def vision_node(state: TriageState) -> dict:
    """Analyse image attachments using the vision LLM."""
    start = time.monotonic()
    llm = get_llm("vision")
    model_calls = list(state.get("model_calls", []))

    model_name = get_model_name("vision")
    attachments = state.get("attachments", [])
    email_class = state.get("email_class", "unknown")

    # Stub: pass plain text prompt. Real LLM: pass multimodal HumanMessage.
    if isinstance(llm, StubLLM):
        payload: Any = _VISION_TEXT_PROMPT.format(
            email_class=email_class,
            attachment_count=len(attachments),
        )
    else:
        payload = _build_vision_payload(email_class, attachments)

    message = llm.invoke(payload)
    vision_summary = getattr(message, "content", str(message))

    cost = extract_cost(message, model_name)
    latency_ms = int((time.monotonic() - start) * 1000)
    call: ModelCall = {
        "node": "vision",
        "model": model_name,
        "cost_usd": cost,
        "latency_ms": latency_ms,
    }
    model_calls.append(call)

    return {
        "vision_summary": vision_summary,
        "model_calls": model_calls,
        "total_cost_usd": state.get("total_cost_usd", 0.0) + cost,
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
