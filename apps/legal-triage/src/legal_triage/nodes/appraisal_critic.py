"""Appraisal Critic node — scores and critiques the appraisal draft."""

from __future__ import annotations

import re
import time

from langsmith import traceable

from legal_triage.llm_factory import get_llm
from legal_triage.state import ModelCall, TriageState

_CRITIC_PROMPT = """You are an adversarial legal reviewer. Your job is to critique the following
appraisal draft and assign a quality score.

APPRAISAL DRAFT:
{appraisal_draft}

Respond in exactly this format:
SCORE: <float between 0.0 and 1.0>
CRITIQUE: <one paragraph critique>
"""


def _parse_score(response: str) -> float:
    """Extract score from critic response. Returns 0.5 on parse failure."""
    match = re.search(r"SCORE:\s*([0-9.]+)", response)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return 0.5


@traceable(name="appraisal_critic")
def appraisal_critic_node(state: TriageState) -> dict:
    """Critique the appraisal draft and assign a quality score."""
    start = time.monotonic()
    llm = get_llm("appraisal_critic")
    model_calls = list(state.get("model_calls", []))

    prompt = _CRITIC_PROMPT.format(appraisal_draft=state.get("appraisal_draft", ""))
    response = llm.invoke(prompt)

    appraisal_score = _parse_score(response)
    appraisal_critique = response

    latency_ms = int((time.monotonic() - start) * 1000)
    call: ModelCall = {
        "node": "appraisal_critic",
        "model": getattr(llm, "model_name", "unknown"),
        "cost_usd": 0.0,
        "latency_ms": latency_ms,
    }
    model_calls.append(call)

    return {
        "appraisal_score": appraisal_score,
        "appraisal_critique": appraisal_critique,
        "model_calls": model_calls,
        "total_cost_usd": state.get("total_cost_usd", 0.0),
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
