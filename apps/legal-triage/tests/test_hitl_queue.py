"""Tests for the HITL queue depth manager."""

from __future__ import annotations

import threading
from unittest.mock import MagicMock

import pytest

import legal_triage.hitl_queue as hitl_queue


@pytest.fixture(autouse=True)
def reset_queue():
    """Ensure queue starts at 0 and callbacks are cleared for each test."""
    hitl_queue.reset()
    hitl_queue._alert_callbacks.clear()
    yield
    hitl_queue.reset()
    hitl_queue._alert_callbacks.clear()


# ---------------------------------------------------------------------------
# Basic operations
# ---------------------------------------------------------------------------


class TestBasicOperations:
    def test_initial_depth_is_zero(self):
        assert hitl_queue.depth() == 0

    def test_enqueue_increments_depth(self):
        hitl_queue.enqueue()
        assert hitl_queue.depth() == 1

    def test_enqueue_returns_new_depth(self):
        d = hitl_queue.enqueue()
        assert d == 1

    def test_multiple_enqueues(self):
        hitl_queue.enqueue()
        hitl_queue.enqueue()
        d = hitl_queue.enqueue()
        assert d == 3
        assert hitl_queue.depth() == 3

    def test_dequeue_decrements_depth(self):
        hitl_queue.enqueue()
        hitl_queue.enqueue()
        hitl_queue.dequeue()
        assert hitl_queue.depth() == 1

    def test_dequeue_returns_new_depth(self):
        hitl_queue.enqueue()
        hitl_queue.enqueue()
        d = hitl_queue.dequeue()
        assert d == 1

    def test_dequeue_floors_at_zero(self):
        d = hitl_queue.dequeue()
        assert d == 0
        assert hitl_queue.depth() == 0

    def test_reset_sets_depth_to_zero(self):
        hitl_queue.enqueue()
        hitl_queue.enqueue()
        hitl_queue.reset()
        assert hitl_queue.depth() == 0


# ---------------------------------------------------------------------------
# Alert thresholds
# ---------------------------------------------------------------------------


class TestAlertThresholds:
    def test_no_callback_below_alert_depth(self):
        cb = MagicMock()
        hitl_queue.register_alert_callback(cb)
        for _ in range(hitl_queue.ALERT_DEPTH):
            hitl_queue.enqueue()
        cb.assert_not_called()

    def test_callback_fires_at_alert_depth_plus_one(self):
        cb = MagicMock()
        hitl_queue.register_alert_callback(cb)
        for _ in range(hitl_queue.ALERT_DEPTH + 1):
            hitl_queue.enqueue()
        cb.assert_called_once()
        msg = cb.call_args[0][0]
        assert "Director" in msg or str(hitl_queue.ALERT_DEPTH) in msg

    def test_callback_fires_at_suspend_depth_plus_one(self):
        cb = MagicMock()
        hitl_queue.register_alert_callback(cb)
        for _ in range(hitl_queue.SUSPEND_DEPTH + 1):
            hitl_queue.enqueue()
        # Should have fired at ALERT_DEPTH+1 and again at SUSPEND_DEPTH+1
        assert cb.call_count == 2
        final_msg = cb.call_args[0][0]
        assert "SUSPEND" in final_msg.upper() or "INTAKE" in final_msg.upper()

    def test_register_multiple_callbacks(self):
        cb1, cb2 = MagicMock(), MagicMock()
        hitl_queue.register_alert_callback(cb1)
        hitl_queue.register_alert_callback(cb2)
        for _ in range(hitl_queue.ALERT_DEPTH + 1):
            hitl_queue.enqueue()
        cb1.assert_called_once()
        cb2.assert_called_once()


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_enqueues(self):
        threads = [threading.Thread(target=hitl_queue.enqueue) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert hitl_queue.depth() == 50

    def test_concurrent_enqueue_dequeue(self):
        # Enqueue 20, then dequeue 20 concurrently; net result should be 0
        for _ in range(20):
            hitl_queue.enqueue()
        threads = [threading.Thread(target=hitl_queue.dequeue) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert hitl_queue.depth() == 0


# ---------------------------------------------------------------------------
# Status message
# ---------------------------------------------------------------------------


class TestStatusMessage:
    def test_empty_queue_message(self):
        msg = hitl_queue.status_message()
        assert "empty" in msg.lower()

    def test_normal_queue_message(self):
        hitl_queue.enqueue()
        msg = hitl_queue.status_message()
        assert "1" in msg

    def test_alert_queue_message_contains_warning(self):
        for _ in range(hitl_queue.ALERT_DEPTH + 2):
            hitl_queue.enqueue()
        msg = hitl_queue.status_message()
        assert "⚠️" in msg or "Director" in msg

    def test_suspend_queue_message_contains_emergency(self):
        for _ in range(hitl_queue.SUSPEND_DEPTH + 2):
            hitl_queue.enqueue()
        msg = hitl_queue.status_message()
        assert "🚨" in msg or "SUSPEND" in msg.upper()
