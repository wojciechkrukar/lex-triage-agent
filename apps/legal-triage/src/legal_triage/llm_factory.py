"""
LLM factory — the ONLY place that may resolve model names and create LLM clients.

Tier contract:
  tier1 — full-capability models (Claude Opus / GPT-4o)
  tier2 — cost-optimised models (Claude Haiku / GPT-4o-mini)
  tier3 — deterministic stubs, no network calls (default in tests)

Cost extraction helpers
-----------------------
After calling llm.invoke(...), pass the returned AIMessage to
``extract_cost(message, model_name)`` to get the USD cost for that call.
The cost is an estimate based on published token prices; it is NOT a
guarantee. Always treat it as approximate.
"""

from __future__ import annotations

import os
import warnings
from typing import Any

# ---------------------------------------------------------------------------
# Pricing table (USD per 1 000 tokens, input / output)
# Keep this table synchronised with docs/llm-roster.md
# ---------------------------------------------------------------------------
_PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-5":   (0.015,  0.075),
    "claude-haiku-4-5":  (0.00025, 0.00125),
    "claude-opus-4-7":   (0.015,  0.075),
    # OpenAI
    "gpt-4o":             (0.0025, 0.01),
    "gpt-4o-mini":        (0.00015, 0.0006),
}

# Vision role uses OpenAI; all other roles use Anthropic.
_VISION_ROLES = {"vision"}

_TIER1_MODELS: dict[str, str] = {
    "classifier":       "claude-haiku-4-5",   # fast + cheap; high precision gate
    "vision":           "gpt-4o",
    "appraisal_creator": "claude-opus-4-5",
    "appraisal_critic": "claude-opus-4-5",
    "router":           "claude-haiku-4-5",
}

_TIER2_MODELS: dict[str, str] = {
    "classifier":       "claude-haiku-4-5",
    "vision":           "gpt-4o-mini",
    "appraisal_creator": "claude-haiku-4-5",
    "appraisal_critic": "claude-haiku-4-5",
    "router":           "claude-haiku-4-5",
}


# ---------------------------------------------------------------------------
# Stub LLM (tier3 / CI)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Keyword heuristic for stub classifier
#
# NOTE — TIER-3 DEMO STUB ONLY.
# This keyword list drives the deterministic classifier used when LLM_TIER=tier3
# (CI / offline / dashboard demo).  It is NOT used with real LLM providers.
# The ordering matters: spam → invoice → general_legal → pi_lead.  A class is
# returned as soon as the first keyword match fires, so higher-priority classes
# shadow lower-priority ones.  "other" is the fall-through default.
#
# CAUTION — substring matching: keep all keywords ≥ 8 characters long (or use
# multi-word phrases) to avoid mid-word false matches.  Short acronyms like
# "nda" are intentionally replaced by the longer "non-disclosure" form.
# ---------------------------------------------------------------------------
_STUB_CLASSIFIER_KEYWORDS: dict[str, list[str]] = {
    "spam": [
        # Prize / lottery scams
        "congratulations", "cash prize", "you have been selected",
        "sweepstakes", "prize of", "monthly sweepstakes",
        # Nigerian advance-fee scams (419)
        "prince from nigeria", "princess from nigeria", "nigerian prince",
        "transfer funds", "transfer of funds", "dear friend, i am",
        "need your assistance to transfer", "wire transfer the sum",
        "western union", "moneygram",
        # Investment / crypto
        "crypto wealth", "trading algorithm", "wealth program",
        "limited time offer",
        # Generic spam
        "click here to claim", "unsubscribe", "free gift",
        "irs collections", "tax liability", "free reward", "act now",
    ],
    "invoice": [
        "invoice #", "invoice no.", "attached invoice", "revised invoice",
        "amount due", "payment due", "net 30", "remit payment",
        "services rendered", "billing department", "overdue invoice",
        "total due",
    ],
    "general_legal": [
        # Contract & business
        "non-disclosure", "due diligence", "acquiring", "merger",
        "lease agreement", "commercial lease", "review before signing",
        "review the contract", "contract to review", "contract review",
        # Employment
        "wrongful termination", "employment dispute", "employment contract",
        "dispute with my employer", "employer regarding",
        # Family / estate
        "estate planning", "probate", "divorce", "custody", "child support",
        # Litigation support
        "subpoena", "settlement offer", "contract dispute",
        "opposing party", "in-house counsel", "outside counsel",
        "landlord", "tenant dispute",
    ],
    "pi_lead": [
        # Direct injury statements
        "accident", "injur", "collision", "struck by", "hit by",
        "hit me", "struck me", "hurt me", "bit me", "attacked me",
        "slipped", "fell at", "fell on", "dog bit", "bitten by",
        # Medical / treatment
        "malpractice", "medical negligence", "misdiagnos", "misdiagnosed",
        "wrong diagnosis", "physician failed", "diagnostic test",
        "treatment cost", "medical expense", "medical bill",
        "surgery", "operated on", "reconstructive surgery",
        "head trauma", "broken leg", "broken arm", "broken wrist",
        "nerve damage", "second-degree burn",
        # Specific scenarios
        "defective", "malfunctioned", "crosswalk", "workers comp",
        "personal injury", "car crash", "car seat", "pesticide",
        "tractor", "rear-end", "rear end", "parking lot",
        # Ambiguous / low-confidence PI leads (still potential clients)
        "incident on 20",       # "incident on 2024-xx-xx" date pattern
        "gotten hurt", "got hurt", "may have been hurt",
        "worth pursuing", "qualif",    # "qualifies for a lawyer" etc.
        "need an attorney", "need a lawyer", "attorney to handle",
        "seeking legal representation", "legal representation",
    ],
}


def _stub_classify_heuristic(prompt_text: str) -> str:
    """
    Return a plausible email class for a stub classifier from keyword matching.

    Extracts only the email body portion of the prompt (the section after the
    "EMAIL:" header) so that keywords in the instruction preamble are ignored.
    Checks spam → invoice → general_legal → pi_lead in that order so that
    clearly non-PI emails are never mis-labelled as leads.  Default: "other".

    NOTE: This is a tier-3 demo stub only — NOT used with real LLM providers.
    """
    # The classification prompt ends with "EMAIL:\n<body>" — extract just that part
    marker = "EMAIL:"
    idx = prompt_text.find(marker)
    text = prompt_text[idx + len(marker):] if idx != -1 else prompt_text
    text = text.lower()

    for cls in ("spam", "invoice", "general_legal", "pi_lead"):
        for kw in _STUB_CLASSIFIER_KEYWORDS[cls]:
            if kw in text:
                return cls
    return "other"


class StubLLM:
    """Deterministic stub LLM for tier3 / CI usage. No network calls."""

    def __init__(self, tier: str, role: str) -> None:
        self.tier = tier
        self.role = role
        self.model_name = f"stub-{role}-{tier}"

    def invoke(self, prompt: Any, **kwargs: Any) -> "_StubMessage":
        """Return a deterministic stub response based on role."""
        if self.role == "classifier":
            # Use a keyword heuristic so eval metrics are meaningful in tier3.
            content = _stub_classify_heuristic(str(prompt))
        else:
            stubs = {
                "vision": "No significant damage visible in attached images.",
                "appraisal_creator": (
                    "APPRAISAL DRAFT\n\nIncident type: Car accident\n"
                    "Severity: High\nLiability: Clear\nRecommendation: Proceed to intake."
                ),
                "appraisal_critic": "SCORE: 0.85\nCRITIQUE: Appraisal is thorough and well-supported.",
                "router": "NewLead",
            }
            content = stubs.get(self.role, f"Stub response for {self.role}")
        return _StubMessage(content=content)

    def __repr__(self) -> str:
        return f"StubLLM(tier={self.tier!r}, role={self.role!r})"


class _StubMessage:
    """Minimal message wrapper returned by StubLLM so callers can use .content."""

    def __init__(self, content: str) -> None:
        self.content = content
        self.response_metadata: dict[str, Any] = {}

    def __str__(self) -> str:
        return self.content


# ---------------------------------------------------------------------------
# Cost extraction
# ---------------------------------------------------------------------------

def extract_cost(message: Any, model_name: str) -> float:
    """
    Estimate USD cost from an AIMessage returned by invoke().

    Reads ``response_metadata`` for token usage; falls back to 0.0 if the
    metadata is absent (e.g. stub responses, streaming, or providers that do
    not emit usage).

    Args:
        message: The AIMessage (or _StubMessage) returned by llm.invoke().
        model_name: The model name string, used to look up per-token pricing.

    Returns:
        Estimated cost in USD (float, >= 0.0).
    """
    meta = getattr(message, "response_metadata", {}) or {}

    # Anthropic response_metadata key: "usage" → {"input_tokens": N, "output_tokens": M}
    usage = meta.get("usage") or {}
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    # OpenAI response_metadata key: "token_usage" → {"prompt_tokens": N, "completion_tokens": M}
    if not input_tokens and not output_tokens:
        token_usage = meta.get("token_usage") or {}
        input_tokens = token_usage.get("prompt_tokens", 0)
        output_tokens = token_usage.get("completion_tokens", 0)

    price_in, price_out = _PRICING.get(model_name, (0.0, 0.0))
    return (input_tokens * price_in + output_tokens * price_out) / 1000.0


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_llm(role: str, tier: str | None = None) -> Any:
    """
    Resolve and return an LLM client for the given role and tier.

    Args:
        role: The node role (e.g. 'classifier', 'vision', 'appraisal_creator').
        tier: Override tier. Defaults to LLM_TIER env var, then 'tier3'.

    Returns:
        An LLM client with an .invoke(prompt) method.
        For tier3 → StubLLM (no network).
        For tier1/tier2 → ChatAnthropic or ChatOpenAI (real network calls).
    """
    resolved_tier = tier or os.environ.get("LLM_TIER", "tier3")

    if resolved_tier == "tier3":
        return StubLLM(tier=resolved_tier, role=role)

    model_map = _TIER1_MODELS if resolved_tier == "tier1" else _TIER2_MODELS
    model_name = model_map.get(role, "claude-haiku-4-5")

    if role in _VISION_ROLES:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            warnings.warn(
                f"OPENAI_API_KEY not set for tier={resolved_tier}, role={role}. "
                "Falling back to StubLLM.",
                stacklevel=2,
            )
            return StubLLM(tier=resolved_tier, role=role)
        from langchain_openai import ChatOpenAI  # noqa: PLC0415
        return ChatOpenAI(model=model_name, api_key=api_key)  # type: ignore[arg-type]
    else:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            warnings.warn(
                f"ANTHROPIC_API_KEY not set for tier={resolved_tier}, role={role}. "
                "Falling back to StubLLM.",
                stacklevel=2,
            )
            return StubLLM(tier=resolved_tier, role=role)
        from langchain_anthropic import ChatAnthropic  # noqa: PLC0415
        return ChatAnthropic(model=model_name, api_key=api_key)  # type: ignore[arg-type]


def get_model_name(role: str, tier: str | None = None) -> str:
    """Return the model name string for a given role and tier (used for telemetry)."""
    resolved_tier = tier or os.environ.get("LLM_TIER", "tier3")
    if resolved_tier == "tier3":
        return f"stub-{role}-tier3"
    model_map = _TIER1_MODELS if resolved_tier == "tier1" else _TIER2_MODELS
    return model_map.get(role, "claude-haiku-4-5")
