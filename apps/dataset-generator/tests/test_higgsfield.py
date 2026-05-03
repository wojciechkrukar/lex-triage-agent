"""Tests for HiggsFieldProvider feature-flag adapter."""

from __future__ import annotations

from dataset_generator.image_manifest import HiggsFieldProvider
from dataset_generator.schemas import ImageAttachment


class TestHiggsFieldProvider:
    def test_disabled_returns_empty_list(self):
        provider = HiggsFieldProvider(enable_higgsfield=False)
        assert provider.get_synthetic_images("vehicle_collision_rear_end") == []

    def test_enabled_returns_non_empty_list(self):
        provider = HiggsFieldProvider(enable_higgsfield=True)
        result = provider.get_synthetic_images("vehicle_collision_rear_end")
        assert len(result) > 0
        assert all(isinstance(img, ImageAttachment) for img in result)

    def test_enabled_stub_has_expected_fields(self):
        provider = HiggsFieldProvider(enable_higgsfield=True)
        result = provider.get_synthetic_images("vehicle_collision_rear_end")
        img = result[0]
        assert img.filename == "synthetic_vehicle_collision_rear_end.jpg"
        assert img.url == "higgsfield://synthetic"
        assert img.license == "synthetic"
        assert img.sha256 == "placeholder_sha256_higgsfield_stub"
        assert "vehicle_collision_rear_end" in img.scenario_ids

    def test_disabled_by_default_from_config(self, monkeypatch):
        """Default DataGenConfig has enable_higgsfield=False — no network call."""
        monkeypatch.delenv("ENABLE_HIGGSFIELD", raising=False)
        provider = HiggsFieldProvider()  # reads from DataGenConfig
        assert provider.get_synthetic_images("slip_fall_retail") == []

    def test_enabled_works_for_arbitrary_scenario(self):
        provider = HiggsFieldProvider(enable_higgsfield=True)
        result = provider.get_synthetic_images("dog_bite")
        assert len(result) == 1
        assert result[0].scenario_ids == ["dog_bite"]
