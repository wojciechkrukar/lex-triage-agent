"""Legal Appraisal Creator node — drafts an appraisal for PI leads."""

from __future__ import annotations

import time

from langsmith import traceable

from legal_triage.llm_factory import get_llm
from legal_triage.state import ModelCall, TriageState

_APPRAISAL_PROMPT = """You are a senior legal intake specialist. Draft a concise appraisal
for the following email that has been classified as a personal injury lead.

EMAIL:
{email}

VISION NOTES (if any):
{vision_summary}

Your appraisal should cover:
1. Incident type and date (if mentioned)
2. Alleged injuries and severity
3. Liability assessment (clear/unclear/contested)
4. Recommended next step (intake call, request documents, decline)

Be factual and professional. Max 200 words.
"""


@traceable(name="appraisal_creator")
def appraisal_creator_node(state: TriageState) -> dict:
    """Draft a legal appraisal for PI leads."""
    start = time.monotonic()
    llm = get_llm("appraisal_creator")
    model_calls = list(state.get("model_calls", []))

    prompt = _APPRAISAL_PROMPT.format(
        email=state.get("raw_email", ""),
        vision_summary=state.get("vision_summary") or "No attachments.",
    )
    appraisal_draft = llm.invoke(prompt)

    latency_ms = int((time.monotonic() - start) * 1000)
    call: ModelCall = {
        "node": "appraisal_creator",
        "model": getattr(llm, "model_name", "unknown"),
        "cost_usd": 0.0,
        "latency_ms": latency_ms,
    }
    model_calls.append(call)

    return {
        "appraisal_draft": appraisal_draft,
        "model_calls": model_calls,
        "total_cost_usd": state.get("total_cost_usd", 0.0),
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
