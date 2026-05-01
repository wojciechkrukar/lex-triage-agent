"""
LLM factory — the ONLY place that may resolve model names and create LLM clients.

Tier contract:
  tier1 — full-capability models (Claude Opus / GPT-4o)
  tier2 — cost-optimised models (Claude Haiku / GPT-4o-mini)
  tier3 — deterministic stubs, no network calls (default in tests)
"""

from __future__ import annotations

import os
from typing import Any


class StubLLM:
    """Deterministic stub LLM for tier3 / CI usage. No network calls."""

    def __init__(self, tier: str, role: str) -> None:
        self.tier = tier
        self.role = role
        self.model_name = f"stub-{role}-{tier}"

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """Return a deterministic stub response based on role."""
        stubs = {
            "classifier": "pi_lead",
            "vision": "No significant damage visible in attached images.",
            "appraisal_creator": (
                "APPRAISAL DRAFT\n\nIncident type: Car accident\n"
                "Severity: High\nLiability: Clear\nRecommendation: Proceed to intake."
            ),
            "appraisal_critic": "SCORE: 0.85\nCRITIQUE: Appraisal is thorough and well-supported.",
            "router": "NewLead",
        }
        return stubs.get(self.role, f"Stub response for {self.role}")

    def __repr__(self) -> str:
        return f"StubLLM(tier={self.tier!r}, role={self.role!r})"


_TIER1_MODELS = {
    "classifier": "claude-opus-4-5",
    "vision": "gpt-4o",
    "appraisal_creator": "claude-opus-4-5",
    "appraisal_critic": "claude-opus-4-5",
    "router": "claude-haiku-4-5",
}

_TIER2_MODELS = {
    "classifier": "claude-haiku-4-5",
    "vision": "gpt-4o-mini",
    "appraisal_creator": "claude-haiku-4-5",
    "appraisal_critic": "claude-haiku-4-5",
    "router": "claude-haiku-4-5",
}


def get_llm(role: str, tier: str | None = None) -> Any:
    """
    Resolve and return an LLM client for the given role and tier.

    Args:
        role: The node role (e.g. 'classifier', 'vision', 'appraisal_creator').
        tier: Override tier. Defaults to LLM_TIER env var, then 'tier3'.

    Returns:
        An LLM client with an .invoke(prompt) method.
    """
    resolved_tier = tier or os.environ.get("LLM_TIER", "tier3")

    if resolved_tier == "tier3":
        return StubLLM(tier=resolved_tier, role=role)

    model_map = _TIER1_MODELS if resolved_tier == "tier1" else _TIER2_MODELS
    model_name = model_map.get(role, "claude-haiku-4-5")

    # Real provider clients would be instantiated here.
    # For tier1/tier2 without API keys, fall back to stub with a warning.
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        import warnings

        warnings.warn(
            f"No API key found for tier={resolved_tier}. Falling back to stub for role={role}.",
            stacklevel=2,
        )
        return StubLLM(tier=resolved_tier, role=role)

    # Stub placeholder for real client instantiation
    # In production: return ChatAnthropic(model=model_name) or ChatOpenAI(model=model_name)
    return StubLLM(tier=resolved_tier, role=role)
