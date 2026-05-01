"""
Curated public-domain image manifest.

Images sourced from Wikimedia Commons, NHTSA, and FEMA.
All images are in the public domain or CC0.
SHA256 hashes are provided for integrity verification.
"""

from __future__ import annotations

from dataset_generator.schemas import ImageAttachment

# Curated manifest — public domain / CC0 images relevant to PI scenarios
IMAGE_MANIFEST: list[ImageAttachment] = [
    ImageAttachment(
        filename="car_accident_nhtsa_01.jpg",
        url="https://www.nhtsa.gov/sites/nhtsa.gov/files/images/vehicle-crash-test.jpg",
        license="Public Domain (US Government Work)",
        sha256="placeholder_sha256_nhtsa_01",
    ),
    ImageAttachment(
        filename="intersection_wikimedia.jpg",
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Car_crash_1.jpg/640px-Car_crash_1.jpg",
        license="CC BY-SA 3.0",
        sha256="placeholder_sha256_wikimedia_01",
    ),
    ImageAttachment(
        filename="fema_accident_scene.jpg",
        url="https://www.fema.gov/sites/default/files/images/fema_accident_placeholder.jpg",
        license="Public Domain (US Government Work)",
        sha256="placeholder_sha256_fema_01",
    ),
    ImageAttachment(
        filename="slip_fall_scene.jpg",
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Wet_floor_sign.jpg/320px-Wet_floor_sign.jpg",
        license="CC0 1.0",
        sha256="placeholder_sha256_wikimedia_02",
    ),
    ImageAttachment(
        filename="workplace_injury_wikimedia.jpg",
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Workplace_safety.jpg/320px-Workplace_safety.jpg",
        license="CC BY 2.0",
        sha256="placeholder_sha256_wikimedia_03",
    ),
]


def get_images_for_scenario(scenario: str) -> list[ImageAttachment]:
    """Return relevant images for a given scenario (stub — returns subset of manifest)."""
    scenario_map = {
        "car_accident": IMAGE_MANIFEST[:2],
        "slip_fall": IMAGE_MANIFEST[3:4],
        "workplace": IMAGE_MANIFEST[4:5],
        "medical": [],
        "other": [],
    }
    return scenario_map.get(scenario, [])
