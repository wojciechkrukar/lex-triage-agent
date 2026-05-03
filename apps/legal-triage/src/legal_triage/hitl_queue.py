"""
HITL queue depth manager.

Tracks how many emails are currently awaiting human review.

Alert thresholds (from docs/projects/legal-email-triage/hitl.md):
  depth > 10  → Director alert
  depth > 20  → Intake suspension

Thread-safe: may be called from multiple threads (e.g. async graph runners).

Usage::

    from legal_triage import hitl_queue

    # When HITL is triggered for an email
    depth = hitl_queue.enqueue()

    # When human decision is recorded
    hitl_queue.dequeue()

    # Current queue depth
    print(hitl_queue.depth())

    # Register a custom alert callback (e.g. send to Slack)
    hitl_queue.register_alert_callback(lambda msg: slack.send(msg))
"""

from __future__ import annotations

import sys
import threading
from typing import Callable

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
ALERT_DEPTH   = 10   # Director alert threshold
SUSPEND_DEPTH = 20   # Intake suspension threshold

# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------
_lock: threading.Lock = threading.Lock()
_depth: int = 0
_alert_callbacks: list[Callable[[str], None]] = []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def register_alert_callback(fn: Callable[[str], None]) -> None:
    """Register a callable that receives the alert message string."""
    _alert_callbacks.append(fn)


def enqueue() -> int:
    """
    Record that one email has entered the HITL queue.

    Returns:
        New queue depth after adding this email.

    Side effects:
        Fires alert callbacks if depth crosses ALERT_DEPTH or SUSPEND_DEPTH.
    """
    global _depth
    with _lock:
        _depth += 1
        current = _depth
    _fire_alerts(current)
    return current


def dequeue() -> int:
    """
    Record that one email has been resolved (human decision received).

    Returns:
        New queue depth after removing this email (floor 0).
    """
    global _depth
    with _lock:
        _depth = max(0, _depth - 1)
        return _depth


def depth() -> int:
    """Return the current number of emails awaiting human review."""
    with _lock:
        return _depth


def reset() -> None:
    """Reset queue depth to 0.  Use in tests and at the start of a new batch."""
    global _depth
    with _lock:
        _depth = 0


def status_message() -> str:
    """Return a human-readable status string."""
    d = depth()
    if d == 0:
        return "HITL queue: empty"
    if d > SUSPEND_DEPTH:
        return f"🚨 HITL queue: {d} pending  [INTAKE SUSPENDED — depth > {SUSPEND_DEPTH}]"
    if d > ALERT_DEPTH:
        return f"⚠️  HITL queue: {d} pending  [Director alerted — depth > {ALERT_DEPTH}]"
    return f"HITL queue: {d} pending"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fire_alerts(current_depth: int) -> None:
    if current_depth == ALERT_DEPTH + 1:
        msg = (
            f"⚠️  HITL queue depth reached {current_depth} "
            f"(threshold {ALERT_DEPTH}): Director alerted."
        )
        _emit(msg)
    elif current_depth == SUSPEND_DEPTH + 1:
        msg = (
            f"🚨 HITL queue depth reached {current_depth} "
            f"(threshold {SUSPEND_DEPTH}): NEW EMAIL INTAKE SUSPENDED."
        )
        _emit(msg)


def _emit(msg: str) -> None:
    if _alert_callbacks:
        for cb in _alert_callbacks:
            try:
                cb(msg)
            except Exception:
                pass
    else:
        print(msg, file=sys.stderr)
