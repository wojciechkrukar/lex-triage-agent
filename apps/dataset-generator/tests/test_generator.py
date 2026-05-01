"""Tests for the synthetic email generator."""

from __future__ import annotations

from dataset_generator.chokepoint import assert_no_gt_fields
from dataset_generator.generator import generate_public_emails, generate_raw_emails
from dataset_generator.schemas import PublicEmailRecord, RawEmailRecord


class TestGenerateRawEmails:
    def test_returns_correct_count(self):
        emails = generate_raw_emails(count=10, seed=0)
        assert len(emails) == 10

    def test_all_raw_records(self):
        emails = generate_raw_emails(count=10, seed=0)
        for e in emails:
            assert isinstance(e, RawEmailRecord)

    def test_has_gt_fields(self):
        emails = generate_raw_emails(count=5, seed=0)
        for e in emails:
            assert e.gt_class in {"pi_lead", "general_legal", "spam", "invoice", "other"}
            assert e.gt_severity in {"low", "medium", "high", "critical"}
            assert e.gt_liability_clarity in {"clear", "unclear", "contested"}
            assert e.gt_scenario in {"car_accident", "slip_fall", "workplace", "medical", "other"}

    def test_deterministic_with_same_seed(self):
        emails_a = generate_raw_emails(count=10, seed=42)
        emails_b = generate_raw_emails(count=10, seed=42)
        assert [e.email_id for e in emails_a] == [e.email_id for e in emails_b]

    def test_different_seeds_produce_different_results(self):
        emails_a = generate_raw_emails(count=10, seed=1)
        emails_b = generate_raw_emails(count=10, seed=2)
        # At least one email_id should differ
        assert [e.email_id for e in emails_a] != [e.email_id for e in emails_b]


class TestGeneratePublicEmails:
    def test_returns_correct_count(self):
        emails = generate_public_emails(count=20, seed=0)
        assert len(emails) == 20

    def test_all_public_records(self):
        emails = generate_public_emails(count=10, seed=0)
        for e in emails:
            assert isinstance(e, PublicEmailRecord)

    def test_no_gt_fields_in_any_record(self):
        """THE KEY INVARIANT: no gt_* fields must survive in public emails."""
        emails = generate_public_emails(count=100, seed=42)
        for e in emails:
            assert_no_gt_fields(e)

    def test_email_ids_are_unique(self):
        emails = generate_public_emails(count=50, seed=0)
        ids = [e.email_id for e in emails]
        assert len(ids) == len(set(ids))

    def test_class_distribution_has_pi_leads(self):
        """At least some emails should be PI leads in the raw dataset."""
        raw = generate_raw_emails(count=100, seed=42)
        pi_leads = [e for e in raw if e.gt_class == "pi_lead"]
        assert len(pi_leads) >= 30, f"Expected >= 30 PI leads, got {len(pi_leads)}"
