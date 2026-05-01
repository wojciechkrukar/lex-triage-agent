"""Ingestion node — normalises raw email input into TriageState."""

from __future__ import annotations

import time

from langsmith import traceable

from legal_triage.state import TriageState


@traceable(name="ingestion")
def ingestion_node(state: TriageState) -> dict:
    """
    Normalise the raw email.
    Validates required fields are present and prepares state for classification.
    """
    start = time.monotonic()
    errors = list(state.get("errors", []))

    raw_email = state.get("raw_email", "")
    if not raw_email:
        errors.append("ingestion: raw_email is empty")

    latency_ms = int((time.monotonic() - start) * 1000)

    return {
        "raw_email": raw_email.strip(),
        "errors": errors,
        "total_latency_ms": state.get("total_latency_ms", 0) + latency_ms,
    }
