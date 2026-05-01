"""
Tests for chokepoint.py — the ONLY place that may access ground-truth label fields.

Key invariant: strip_labels() MUST remove ALL gt_* fields so they never reach the triage app.
"""

from __future__ import annotations

import pytest

from dataset_generator.chokepoint import assert_no_gt_fields, strip_labels, strip_labels_dict
from dataset_generator.schemas import PublicEmailRecord, RawEmailRecord


def _make_raw() -> RawEmailRecord:
    return RawEmailRecord(
        email_id="test-001",
        subject="Test PI lead",
        body="I was injured in a car accident.",
        sender="victim@example.com",
        attachments=[],
        gt_class="pi_lead",
        gt_severity="high",
        gt_liability_clarity="clear",
        gt_scenario="car_accident",
    )


class TestStripLabels:
    def test_returns_public_record(self):
        raw = _make_raw()
        public = strip_labels(raw)
        assert isinstance(public, PublicEmailRecord)

    def test_gt_fields_are_removed(self):
        raw = _make_raw()
        public = strip_labels(raw)
        data = public.model_dump()
        gt_fields = {"gt_class", "gt_severity", "gt_liability_clarity", "gt_scenario"}
        assert not gt_fields.intersection(data.keys()), (
            f"GT fields leaked into public record: {gt_fields.intersection(data.keys())}"
        )

    def test_public_fields_preserved(self):
        raw = _make_raw()
        public = strip_labels(raw)
        assert public.email_id == raw.email_id
        assert public.subject == raw.subject
        assert public.body == raw.body
        assert public.sender == raw.sender

    def test_assert_no_gt_fields_passes_on_public(self):
        raw = _make_raw()
        public = strip_labels(raw)
        # Should not raise
        assert_no_gt_fields(public)

    def test_assert_no_gt_fields_raises_on_raw_dict(self):
        raw_dict = {
            "email_id": "x",
            "subject": "s",
            "body": "b",
            "sender": "a@b.com",
            "gt_class": "pi_lead",
        }
        with pytest.raises(AssertionError, match="gt_class"):
            assert_no_gt_fields(raw_dict)


class TestStripLabelsDict:
    def test_removes_all_gt_fields(self):
        raw_dict = {
            "email_id": "x",
            "gt_class": "pi_lead",
            "gt_severity": "high",
            "gt_liability_clarity": "clear",
            "gt_scenario": "car_accident",
        }
        result = strip_labels_dict(raw_dict)
        assert "gt_class" not in result
        assert "gt_severity" not in result
        assert "gt_liability_clarity" not in result
        assert "gt_scenario" not in result
        assert result["email_id"] == "x"

    def test_does_not_mutate_input(self):
        raw_dict = {"email_id": "x", "gt_class": "spam"}
        strip_labels_dict(raw_dict)
        assert "gt_class" in raw_dict  # original unchanged
