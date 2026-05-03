"""Tests for the synthetic email generator."""

from __future__ import annotations

import pytest

from dataset_generator.chokepoint import assert_no_gt_fields
from dataset_generator.generator import generate_public_emails, generate_raw_emails
from dataset_generator.schemas import PublicEmailRecord, RawEmailRecord


# ---------------------------------------------------------------------------
# Shared fixtures for M1 exit-criteria tests (module-scoped to avoid re-running)
# ---------------------------------------------------------------------------

_ALL_12_SCENARIOS = frozenset({
    "vehicle_collision_rear_end",
    "slip_fall_retail",
    "dog_bite",
    "medical_malpractice",
    "workplace_injury_construction",
    "defective_product",
    "pedestrian_struck",
    "premises_liability_staircase",
    "ambiguous_pi_low_confidence",
    "general_legal_contract",
    "invoice_billing",
    "spam_solicitation",
})


@pytest.fixture(scope="module")
def raw_batch_m1() -> list[RawEmailRecord]:
    return generate_raw_emails(200, seed=42)


@pytest.fixture(scope="module")
def public_batch_m1() -> list[PublicEmailRecord]:
    return generate_public_emails(100, seed=42)


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
            assert e.gt_severity in {"none", "minor", "moderate", "severe", "catastrophic"}
            assert e.gt_liability_clarity in {"clear", "unclear", "contested"}
            assert e.gt_scenario in {
                "vehicle_collision_rear_end", "slip_fall_retail", "dog_bite",
                "medical_malpractice", "workplace_injury_construction", "defective_product",
                "pedestrian_struck", "premises_liability_staircase",
                "general_legal_contract", "invoice_billing", "spam_solicitation",
                "ambiguous_pi_low_confidence",
            }
            assert isinstance(e.gt_has_attachment, bool)
            assert isinstance(e.gt_jurisdiction, str)
            # sol_years is None for non-PI, int for PI
            assert e.gt_sol_years is None or isinstance(e.gt_sol_years, int)

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
        """At least 60% of emails should be PI leads (M1 exit criterion)."""
        raw = generate_raw_emails(count=100, seed=42)
        pi_leads = [e for e in raw if e.gt_class == "pi_lead"]
        assert len(pi_leads) >= 60, f"Expected >= 60 PI leads, got {len(pi_leads)}"


# ---------------------------------------------------------------------------
# M1 exit-criteria gates — all must pass for Milestone 1 to be declared done
# ---------------------------------------------------------------------------


class TestM1ExitCriteria:
    """CI gates that enforce the M1 exit criteria from dataset-spec.md.

    All five tests must be green before Milestone 1 is closed.
    Failures are hard blockers, not warnings.
    """

    def test_minimum_100_emails(self, raw_batch_m1: list[RawEmailRecord]) -> None:
        """M1 requires at least 100 emails in a generated batch."""
        assert len(raw_batch_m1) >= 100, (
            f"M1 exit criterion FAILED: expected >= 100 emails, got {len(raw_batch_m1)}"
        )

    def test_pi_lead_ratio_at_least_60pct(self, raw_batch_m1: list[RawEmailRecord]) -> None:
        """PI leads must represent at least 60% of the batch."""
        pi_leads = [e for e in raw_batch_m1 if e.gt_class == "pi_lead"]
        ratio = len(pi_leads) / len(raw_batch_m1)
        assert ratio >= 0.60, (
            f"M1 exit criterion FAILED: PI lead ratio {ratio:.1%} is below 60% threshold "
            f"({len(pi_leads)}/{len(raw_batch_m1)} emails)"
        )

    def test_spam_ratio_at_most_15pct(self, raw_batch_m1: list[RawEmailRecord]) -> None:
        """Spam emails must not exceed 15% of the batch."""
        spam = [e for e in raw_batch_m1 if e.gt_class == "spam"]
        ratio = len(spam) / len(raw_batch_m1)
        assert ratio <= 0.15, (
            f"M1 exit criterion FAILED: spam ratio {ratio:.1%} exceeds 15% cap "
            f"({len(spam)}/{len(raw_batch_m1)} emails)"
        )

    def test_all_12_scenarios_represented(self, raw_batch_m1: list[RawEmailRecord]) -> None:
        """Every one of the 12 GtScenario values must appear at least once in a 200-email batch."""
        found = {e.gt_scenario for e in raw_batch_m1}
        missing = _ALL_12_SCENARIOS - found
        assert not missing, (
            f"M1 exit criterion FAILED: not all 12 scenarios represented. "
            f"Missing: {sorted(missing)}"
        )

    def test_no_gt_fields_leak_in_public_batch(
        self, public_batch_m1: list[PublicEmailRecord]
    ) -> None:
        """strip_labels() must have removed every GT field from all public emails."""
        for email in public_batch_m1:
            assert_no_gt_fields(email)
