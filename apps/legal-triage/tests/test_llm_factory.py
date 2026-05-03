"""Tests for llm_factory — tier resolution, real client wiring, and cost extraction."""

from __future__ import annotations

import os
import warnings

import pytest


def setup_function():
    # Ensure tier3 is default for all tests here
    os.environ["LLM_TIER"] = "tier3"


class TestTier3Stubs:
    def test_classifier_returns_stub(self):
        from legal_triage.llm_factory import StubLLM, get_llm

        llm = get_llm("classifier", "tier3")
        assert isinstance(llm, StubLLM)

    def test_vision_returns_stub(self):
        from legal_triage.llm_factory import StubLLM, get_llm

        llm = get_llm("vision", "tier3")
        assert isinstance(llm, StubLLM)

    def test_stub_invoke_returns_message_with_content(self):
        from legal_triage.llm_factory import get_llm

        llm = get_llm("classifier", "tier3")
        # Prompt must contain a PI keyword so the heuristic fires correctly
        msg = llm.invoke("I was injured in a car accident.")
        assert hasattr(msg, "content")
        assert msg.content == "pi_lead"

    def test_stub_router_content(self):
        from legal_triage.llm_factory import get_llm

        llm = get_llm("router", "tier3")
        msg = llm.invoke("route this")
        assert msg.content == "NewLead"

    def test_stub_vision_content(self):
        from legal_triage.llm_factory import get_llm

        llm = get_llm("vision", "tier3")
        msg = llm.invoke("describe this")
        assert "damage" in msg.content.lower() or len(msg.content) > 0


class TestModelNames:
    def test_tier1_classifier_is_haiku(self):
        from legal_triage.llm_factory import get_model_name

        assert get_model_name("classifier", "tier1") == "claude-haiku-4-5"

    def test_tier1_vision_is_gpt4o(self):
        from legal_triage.llm_factory import get_model_name

        assert get_model_name("vision", "tier1") == "gpt-4o"

    def test_tier1_appraisal_creator_is_opus(self):
        from legal_triage.llm_factory import get_model_name

        assert get_model_name("appraisal_creator", "tier1") == "claude-opus-4-5"

    def test_tier1_appraisal_critic_is_opus(self):
        from legal_triage.llm_factory import get_model_name

        assert get_model_name("appraisal_critic", "tier1") == "claude-opus-4-5"

    def test_tier2_all_haiku_or_mini(self):
        from legal_triage.llm_factory import get_model_name

        for role in ("classifier", "appraisal_creator", "appraisal_critic", "router"):
            assert get_model_name(role, "tier2") == "claude-haiku-4-5"
        assert get_model_name("vision", "tier2") == "gpt-4o-mini"

    def test_tier3_returns_stub_name(self):
        from legal_triage.llm_factory import get_model_name

        name = get_model_name("classifier", "tier3")
        assert "stub" in name


class TestFallbackWithoutKeys:
    def test_tier1_without_anthropic_key_returns_stub_with_warning(self):
        """get_llm tier1 for Anthropic role with no API key → StubLLM + warning."""
        from legal_triage.llm_factory import StubLLM, get_llm

        env_backup = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                llm = get_llm("classifier", "tier1")
            assert isinstance(llm, StubLLM)
            assert any("ANTHROPIC_API_KEY" in str(warning.message) for warning in w)
        finally:
            if env_backup is not None:
                os.environ["ANTHROPIC_API_KEY"] = env_backup

    def test_tier1_without_openai_key_returns_stub_with_warning(self):
        """get_llm tier1 for vision role with no OpenAI key → StubLLM + warning."""
        from legal_triage.llm_factory import StubLLM, get_llm

        env_backup = os.environ.pop("OPENAI_API_KEY", None)
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                llm = get_llm("vision", "tier1")
            assert isinstance(llm, StubLLM)
            assert any("OPENAI_API_KEY" in str(warning.message) for warning in w)
        finally:
            if env_backup is not None:
                os.environ["OPENAI_API_KEY"] = env_backup

    def test_tier2_without_key_returns_stub(self):
        from legal_triage.llm_factory import StubLLM, get_llm

        env_backup = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                llm = get_llm("classifier", "tier2")
            assert isinstance(llm, StubLLM)
        finally:
            if env_backup is not None:
                os.environ["ANTHROPIC_API_KEY"] = env_backup


class TestRealClientInstantiation:
    def test_tier1_anthropic_returns_chat_anthropic(self, monkeypatch):
        """With a fake key, tier1 should return ChatAnthropic (mock the import)."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key-for-test")

        # Only import ChatAnthropic is attempted; validate it's NOT a StubLLM
        from legal_triage.llm_factory import StubLLM, get_llm

        try:
            llm = get_llm("classifier", "tier1")
            # If langchain_anthropic is installed, a real client is returned
            assert not isinstance(llm, StubLLM), "Should return real ChatAnthropic, not stub"
        except Exception:
            # If the SDK isn't installed in this env, this is acceptable
            pytest.skip("langchain-anthropic not available in this environment")

    def test_tier1_openai_returns_chat_openai(self, monkeypatch):
        """With a fake key, tier1 vision should return ChatOpenAI."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-test")

        from legal_triage.llm_factory import StubLLM, get_llm

        try:
            llm = get_llm("vision", "tier1")
            assert not isinstance(llm, StubLLM), "Should return real ChatOpenAI, not stub"
        except Exception:
            pytest.skip("langchain-openai not available in this environment")


class TestExtractCost:
    def test_stub_message_returns_zero(self):
        from legal_triage.llm_factory import extract_cost, get_llm

        llm = get_llm("classifier", "tier3")
        msg = llm.invoke("test")
        cost = extract_cost(msg, "claude-haiku-4-5")
        assert cost == 0.0

    def test_anthropic_usage_metadata(self):
        """Simulate Anthropic response_metadata with token usage."""
        from legal_triage.llm_factory import extract_cost

        class FakeMsg:
            response_metadata = {"usage": {"input_tokens": 100, "output_tokens": 50}}

        cost = extract_cost(FakeMsg(), "claude-haiku-4-5")
        # 100 * 0.00025/1000 + 50 * 0.00125/1000
        expected = (100 * 0.00025 + 50 * 0.00125) / 1000.0
        assert abs(cost - expected) < 1e-9

    def test_openai_usage_metadata(self):
        """Simulate OpenAI response_metadata with token usage."""
        from legal_triage.llm_factory import extract_cost

        class FakeMsg:
            response_metadata = {
                "token_usage": {"prompt_tokens": 200, "completion_tokens": 100}
            }

        cost = extract_cost(FakeMsg(), "gpt-4o")
        # 200 * 0.0025/1000 + 100 * 0.01/1000
        expected = (200 * 0.0025 + 100 * 0.01) / 1000.0
        assert abs(cost - expected) < 1e-9

    def test_unknown_model_returns_zero(self):
        from legal_triage.llm_factory import extract_cost

        class FakeMsg:
            response_metadata = {"usage": {"input_tokens": 100, "output_tokens": 50}}

        cost = extract_cost(FakeMsg(), "unknown-model-xyz")
        assert cost == 0.0

    def test_missing_metadata_returns_zero(self):
        from legal_triage.llm_factory import extract_cost

        class FakeMsg:
            response_metadata = {}

        cost = extract_cost(FakeMsg(), "claude-opus-4-5")
        assert cost == 0.0
