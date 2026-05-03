"""Unit tests for individual LangGraph nodes."""

from __future__ import annotations

import os

import pytest

from legal_triage.nodes.appraisal_creator import appraisal_creator_node
from legal_triage.nodes.appraisal_critic import appraisal_critic_node, _parse_score
from legal_triage.nodes.classification import classification_node
from legal_triage.nodes.hitl_gate import hitl_gate_condition, hitl_gate_node
from legal_triage.nodes.ingestion import ingestion_node
from legal_triage.nodes.router import router_node
from legal_triage.nodes.vision import vision_node
from legal_triage.state import TriageState, initial_state


def _base_state(**overrides) -> TriageState:
    s = initial_state("test-001", "Test email body about a car accident.")
    s.update(overrides)
    return s


class TestIngestionNode:
    def test_strips_whitespace(self):
        state = _base_state(raw_email="  hello world  ")
        result = ingestion_node(state)
        assert result["raw_email"] == "hello world"

    def test_empty_email_adds_error(self):
        state = _base_state(raw_email="")
        result = ingestion_node(state)
        assert any("empty" in e for e in result["errors"])

    def test_increments_latency(self):
        state = _base_state(raw_email="test")
        result = ingestion_node(state)
        assert result["total_latency_ms"] >= 0


class TestClassificationNode:
    def test_returns_valid_class(self):
        state = _base_state(raw_email="I was injured in a car accident.")
        result = classification_node(state)
        assert result["email_class"] in {"pi_lead", "general_legal", "spam", "invoice", "other"}

    def test_stub_returns_pi_lead_for_pi_email(self):
        """Stub classifier returns 'pi_lead' when the email body contains PI keywords."""
        import os
        os.environ["LLM_TIER"] = "tier3"
        # _base_state default email contains "car accident" — a clear PI keyword
        state = _base_state()
        result = classification_node(state)
        assert result["email_class"] == "pi_lead"

    def test_stub_returns_spam_for_spam_email(self):
        """Stub classifier returns 'spam' for a spam email body."""
        import os
        os.environ["LLM_TIER"] = "tier3"
        state = _base_state(
            raw_email="Congratulations! You have been selected to receive a cash prize. Click here."
        )
        result = classification_node(state)
        assert result["email_class"] == "spam"

    def test_stub_returns_invoice_for_invoice_email(self):
        """Stub classifier returns 'invoice' for an invoice email body."""
        import os
        os.environ["LLM_TIER"] = "tier3"
        state = _base_state(
            raw_email="Please find attached invoice #1234. Total due: $500. Net 30."
        )
        result = classification_node(state)
        assert result["email_class"] == "invoice"

    def test_stub_returns_other_for_unrecognised_email(self):
        """Stub classifier returns 'other' when no keywords match."""
        import os
        os.environ["LLM_TIER"] = "tier3"
        state = _base_state(raw_email="Please join us for the annual holiday party.")
        result = classification_node(state)
        assert result["email_class"] == "other"

    def test_records_model_call(self):
        state = _base_state()
        result = classification_node(state)
        assert len(result["model_calls"]) >= 1
        assert result["model_calls"][-1]["node"] == "classification"

    def test_model_name_not_unknown(self):
        """Model name should be a real model/stub name, never 'unknown'."""
        state = _base_state()
        result = classification_node(state)
        assert result["model_calls"][-1]["model"] != "unknown"

    def test_cost_usd_field_present(self):
        state = _base_state()
        result = classification_node(state)
        assert "cost_usd" in result["model_calls"][-1]
        assert isinstance(result["model_calls"][-1]["cost_usd"], float)

    def test_total_cost_usd_accumulates(self):
        state = _base_state(total_cost_usd=0.001)
        result = classification_node(state)
        # In tier3 stubs emit 0 cost, so total should stay >= initial
        assert result["total_cost_usd"] >= 0.001


class TestVisionNode:
    def test_returns_vision_summary(self):
        state = _base_state(attachments=[{"filename": "img.jpg"}])
        result = vision_node(state)
        assert isinstance(result["vision_summary"], str)
        assert len(result["vision_summary"]) > 0

    def test_records_model_call(self):
        state = _base_state(attachments=[{"filename": "img.jpg"}])
        result = vision_node(state)
        assert result["model_calls"][-1]["node"] == "vision"

    def test_model_name_not_unknown(self):
        state = _base_state(attachments=[{"filename": "img.jpg"}])
        result = vision_node(state)
        assert result["model_calls"][-1]["model"] != "unknown"

    def test_cost_field_present(self):
        state = _base_state(attachments=[{"filename": "img.jpg"}])
        result = vision_node(state)
        assert isinstance(result["model_calls"][-1]["cost_usd"], float)


class TestAppraisalCreatorNode:
    def test_returns_draft(self):
        state = _base_state(raw_email="Car accident email.", email_class="pi_lead")
        result = appraisal_creator_node(state)
        assert isinstance(result["appraisal_draft"], str)
        assert len(result["appraisal_draft"]) > 0

    def test_records_model_call(self):
        state = _base_state(email_class="pi_lead")
        result = appraisal_creator_node(state)
        assert result["model_calls"][-1]["node"] == "appraisal_creator"

    def test_model_name_not_unknown(self):
        state = _base_state(email_class="pi_lead")
        result = appraisal_creator_node(state)
        assert result["model_calls"][-1]["model"] != "unknown"


class TestAppraisalCriticNode:
    def test_returns_score_between_0_and_1(self):
        state = _base_state(appraisal_draft="Draft appraisal text.")
        result = appraisal_critic_node(state)
        assert 0.0 <= result["appraisal_score"] <= 1.0

    def test_returns_critique(self):
        state = _base_state(appraisal_draft="Draft appraisal text.")
        result = appraisal_critic_node(state)
        assert isinstance(result["appraisal_critique"], str)

    def test_parse_score_valid(self):
        assert _parse_score("SCORE: 0.85\nCRITIQUE: Good.") == 0.85

    def test_parse_score_fallback(self):
        assert _parse_score("No score here") == 0.5

    def test_model_name_not_unknown(self):
        state = _base_state(appraisal_draft="Draft.")
        result = appraisal_critic_node(state)
        assert result["model_calls"][-1]["model"] != "unknown"

    def test_cost_accumulates(self):
        state = _base_state(appraisal_draft="Draft.", total_cost_usd=0.005)
        result = appraisal_critic_node(state)
        # stub emits 0 cost so total stays >= original
        assert result["total_cost_usd"] >= 0.005


class TestHITLGateNode:
    def setup_method(self):
        # Ensure HITL_AUTO_APPROVE is off for all production-path tests.
        os.environ.pop("HITL_AUTO_APPROVE", None)

    def teardown_method(self):
        os.environ.pop("HITL_AUTO_APPROVE", None)

    def test_pi_lead_requires_hitl(self):
        state = _base_state(email_class="pi_lead", appraisal_score=0.9, class_confidence=0.95)
        result = hitl_gate_node(state)
        assert result["hitl_required"] is True

    def test_spam_does_not_require_hitl(self):
        state = _base_state(email_class="spam", appraisal_score=0.9, class_confidence=0.95)
        result = hitl_gate_node(state)
        assert result["hitl_required"] is False

    def test_low_score_triggers_hitl(self):
        state = _base_state(email_class="spam", appraisal_score=0.3, class_confidence=0.95)
        result = hitl_gate_node(state)
        assert result["hitl_required"] is True

    def test_low_confidence_triggers_hitl(self):
        state = _base_state(email_class="spam", appraisal_score=0.9, class_confidence=0.3)
        result = hitl_gate_node(state)
        assert result["hitl_required"] is True

    def test_auto_approve_bypasses_hitl(self):
        """When HITL_AUTO_APPROVE=true, gate always returns hitl_required=False."""
        os.environ["HITL_AUTO_APPROVE"] = "true"
        state = _base_state(email_class="pi_lead", appraisal_score=0.9, class_confidence=0.95)
        result = hitl_gate_node(state)
        assert result["hitl_required"] is False
        assert result.get("human_decision") == "approve"


class TestHITLGateCondition:
    def test_returns_interrupt_when_hitl_required_no_decision(self):
        state = _base_state(hitl_required=True, human_decision=None)
        assert hitl_gate_condition(state) == "interrupt"

    def test_returns_route_when_no_hitl(self):
        state = _base_state(hitl_required=False)
        assert hitl_gate_condition(state) == "route"

    def test_returns_route_when_human_decided(self):
        state = _base_state(hitl_required=True, human_decision="approve")
        assert hitl_gate_condition(state) == "route"


class TestRouterNode:
    def test_pi_lead_routes_to_new_lead(self):
        state = _base_state(email_class="pi_lead")
        result = router_node(state)
        assert result["terminal_sink"] == "NewLead"

    def test_spam_routes_to_refused_spam(self):
        state = _base_state(email_class="spam")
        result = router_node(state)
        assert result["terminal_sink"] == "Refused-Spam"

    def test_invoice_routes_to_refused_invoice(self):
        state = _base_state(email_class="invoice")
        result = router_node(state)
        assert result["terminal_sink"] == "Refused-Invoice"

    def test_general_legal_routes_correctly(self):
        state = _base_state(email_class="general_legal")
        result = router_node(state)
        assert result["terminal_sink"] == "GeneralLegal"

    def test_human_reject_overrides(self):
        state = _base_state(email_class="pi_lead", human_decision="reject")
        result = router_node(state)
        assert result["terminal_sink"] == "Refused-Other"

    def test_human_reclassify_overrides(self):
        state = _base_state(email_class="pi_lead", human_decision="reclassify")
        result = router_node(state)
        assert result["terminal_sink"] == "GeneralLegal"
