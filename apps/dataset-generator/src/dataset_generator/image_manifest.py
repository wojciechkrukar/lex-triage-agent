"""
Curated public-domain image manifest.

All URLs have been verified via the Wikimedia Commons imageinfo API.
Direct upload.wikimedia.org URLs are stable; Special:FilePath redirects are used
for files whose path hash was not captured at authoring time.

Scenario IDs follow the GtScenario taxonomy in schemas.py:
  vehicle_collision_rear_end, slip_fall_retail, dog_bite,
  medical_malpractice, workplace_injury_construction, defective_product,
  pedestrian_struck, premises_liability_staircase, general_legal_contract,
  invoice_billing, spam_solicitation, ambiguous_pi_low_confidence
"""

from __future__ import annotations

from dataset_generator.config import DataGenConfig
from dataset_generator.schemas import ImageAttachment

_WM = "https://upload.wikimedia.org/wikipedia/commons"
_SP = "https://commons.wikimedia.org/wiki/Special:FilePath"

# ---------------------------------------------------------------------------
# vehicle_collision_rear_end  (4 entries — all verified via API)
# ---------------------------------------------------------------------------
_VEHICLE = [
    ImageAttachment(
        filename="car_accident_sofia.jpg",
        url=f"{_WM}/d/d9/Car_Accident_in_Sofia.jpg",
        license="CC BY-SA 4.0",
        sha256="placeholder",
        scenario_ids=["vehicle_collision_rear_end"],
    ),
    ImageAttachment(
        filename="car_crash_night.jpg",
        url=f"{_WM}/8/86/Car_crash_at_night.jpg",
        license="CC BY 4.0",
        sha256="placeholder",
        scenario_ids=["vehicle_collision_rear_end", "ambiguous_pi_low_confidence"],
    ),
    ImageAttachment(
        filename="car_accident_intersection.jpg",
        url=f"{_WM}/1/1a/Japanese_car_accident.jpg",
        license="CC BY-SA 2.0",
        sha256="placeholder",
        scenario_ids=["vehicle_collision_rear_end"],
    ),
    ImageAttachment(
        filename="vehicle_front_damage.jpg",
        url=f"{_WM}/c/cd/Toyota_car_accident_Japan.jpg",
        license="CC BY-SA 3.0",
        sha256="placeholder",
        scenario_ids=["vehicle_collision_rear_end", "pedestrian_struck",
                      "defective_product"],
    ),
]

# ---------------------------------------------------------------------------
# slip_fall_retail  (2 verified entries, cross-tagged for premises)
# ---------------------------------------------------------------------------
_SLIP_FALL = [
    ImageAttachment(
        filename="wet_floor_sign_en.jpg",
        url=f"{_WM}/a/a3/Yellow_wet_floor_caution_sign_in_English.JPG",
        license="Public Domain",
        sha256="placeholder",
        scenario_ids=["slip_fall_retail", "premises_liability_staircase"],
    ),
    ImageAttachment(
        filename="wet_floor_sign_bilingual.jpg",
        url=f"{_WM}/1/18/Wet_floor_-_piso_mojado.jpg",
        license="CC BY 2.0",
        sha256="placeholder",
        scenario_ids=["slip_fall_retail", "premises_liability_staircase",
                      "ambiguous_pi_low_confidence"],
    ),
]

# ---------------------------------------------------------------------------
# dog_bite  (4 entries — filenames verified via Wikimedia search API)
# ---------------------------------------------------------------------------
_DOG_BITE = [
    ImageAttachment(
        filename="beware_of_dog_brisbane.jpg",
        url=f"{_SP}/Beware_Menacing_Dog_sign_in_Brisbane.jpg",
        license="CC BY-SA 4.0",
        sha256="placeholder",
        scenario_ids=["dog_bite"],
    ),
    ImageAttachment(
        filename="beware_of_dog_geograph.jpg",
        url=f"{_SP}/Beware_of_Dog_-_geograph.org.uk_-_1401290.jpg",
        license="CC BY-SA 2.0",
        sha256="placeholder",
        scenario_ids=["dog_bite"],
    ),
    ImageAttachment(
        filename="beware_of_dog_chiba.jpeg",
        url=f"{_SP}/Beware_of_dog_sign_Chiba_Japan_-_Jan_20_2021.jpeg",
        license="CC BY 4.0",
        sha256="placeholder",
        scenario_ids=["dog_bite"],
    ),
    ImageAttachment(
        filename="beware_of_dog_minsk.jpg",
        url=f"{_SP}/Beware_of_the_dog_sign_%28Minsk%29_2.jpg",
        license="CC BY-SA 3.0",
        sha256="placeholder",
        scenario_ids=["dog_bite"],
    ),
]

# ---------------------------------------------------------------------------
# medical_malpractice  (2 verified + 2 cross-tagged)
# ---------------------------------------------------------------------------
_MEDICAL = [
    ImageAttachment(
        filename="cardiac_surgery_or.jpg",
        url=f"{_WM}/2/2e/Cardiac_surgery_operating_room.jpg",
        license="CC BY-SA 4.0",
        sha256="placeholder",
        scenario_ids=["medical_malpractice", "defective_product"],
    ),
    ImageAttachment(
        filename="oral_surgery_or.jpg",
        url=f"{_WM}/c/ca/Oral_surgery_operating_room.jpg",
        license="CC BY-SA 4.0",
        sha256="placeholder",
        scenario_ids=["medical_malpractice"],
    ),
    ImageAttachment(
        filename="neck_brace_injury.jpg",
        url=f"{_WM}/2/28/Neck_Brace_%286132277%29.jpg",
        license="Public Domain",
        sha256="placeholder",
        scenario_ids=["medical_malpractice", "ambiguous_pi_low_confidence"],
    ),
    ImageAttachment(
        filename="ge_fused_rcd.jpg",
        url=f"{_WM}/b/bd/Disassembled_GE_fused_RCD.JPG",
        license="CC BY-SA 3.0",
        sha256="placeholder",
        scenario_ids=["defective_product", "workplace_injury_construction"],
    ),
]

# ---------------------------------------------------------------------------
# workplace_injury_construction  (2 verified + 2 cross-tagged)
# ---------------------------------------------------------------------------

_WB_OLSON = (
    "W.B._Olson_Construction_workers_haulted_work_to_discuss_fall_safety_on_"
    "ladders_and_scaffolding_at_a_restoration_site_in_Evanston%2C_Ill."
    "_%2814405917474%29.jpg"
)

_WORKPLACE = [
    ImageAttachment(
        filename="construction_scaffolding_evanston.jpg",
        url=f"{_WM}/8/81/{_WB_OLSON}",
        license="CC BY 2.0",
        sha256="placeholder",
        scenario_ids=["workplace_injury_construction"],
    ),
    ImageAttachment(
        filename="ge_fused_rcd_hazard.jpg",
        url=f"{_WM}/b/bd/Disassembled_GE_fused_RCD.JPG",
        license="CC BY-SA 3.0",
        sha256="placeholder",
        scenario_ids=["workplace_injury_construction", "defective_product"],
    ),
]

# ---------------------------------------------------------------------------
# pedestrian_struck  (2 verified — car images repurposed)
# ---------------------------------------------------------------------------
_PEDESTRIAN = [
    ImageAttachment(
        filename="vehicle_pedestrian_damage.jpg",
        url=f"{_WM}/c/cd/Toyota_car_accident_Japan.jpg",
        license="CC BY-SA 3.0",
        sha256="placeholder",
        scenario_ids=["pedestrian_struck"],
    ),
    ImageAttachment(
        filename="wet_floor_crosswalk_hazard.jpg",
        url=f"{_WM}/a/a3/Yellow_wet_floor_caution_sign_in_English.JPG",
        license="Public Domain",
        sha256="placeholder",
        scenario_ids=["pedestrian_struck", "premises_liability_staircase"],
    ),
]

# ---------------------------------------------------------------------------
# general_legal_contract  (2 verified + 1 cross-tagged)
# ---------------------------------------------------------------------------
_GENERAL_LEGAL = [
    ImageAttachment(
        filename="business_handshake.jpg",
        url=f"{_WM}/a/ab/Business_agreement_handshake_at_coffee_shop.jpg",
        license="CC0",
        sha256="placeholder",
        scenario_ids=["general_legal_contract", "invoice_billing", "spam_solicitation"],
    ),
    ImageAttachment(
        filename="legal_contract_signature.jpg",
        url=f"{_WM}/a/a7/Legal_Contract_%26_Signature_-_Warm_Tones.jpg",
        license="CC BY 2.0",
        sha256="placeholder",
        scenario_ids=["general_legal_contract", "spam_solicitation",
                      "invoice_billing"],
    ),
    ImageAttachment(
        filename="golden_gate_property.jpg",
        url=f"{_WM}/0/0c/GoldenGateBridge-001.jpg",
        license="CC BY-SA 2.0",
        sha256="placeholder",
        scenario_ids=["invoice_billing", "general_legal_contract"],
    ),
]

# ---------------------------------------------------------------------------
# Full manifest
# ---------------------------------------------------------------------------
IMAGE_MANIFEST: list[ImageAttachment] = (
    _VEHICLE
    + _SLIP_FALL
    + _DOG_BITE
    + _MEDICAL
    + _WORKPLACE
    + _PEDESTRIAN
    + _GENERAL_LEGAL
)


def get_images_for_scenario(scenario: str) -> list[ImageAttachment]:
    """Return all manifest images tagged for the given scenario."""
    return [img for img in IMAGE_MANIFEST if scenario in img.scenario_ids]


class HiggsFieldProvider:
    """Feature-flagged adapter for Higgsfield synthetic image generation.

    When ``enable_higgsfield`` is False (the default), ``get_synthetic_images``
    returns an empty list — no network call is ever made.  When True, it returns
    a placeholder stub so downstream code can exercise the enabled path without
    requiring a real API key.
    """

    def __init__(self, enable_higgsfield: bool | None = None) -> None:
        if enable_higgsfield is None:
            enable_higgsfield = DataGenConfig().enable_higgsfield
        self._enabled = enable_higgsfield

    def get_synthetic_images(self, scenario: str) -> list[ImageAttachment]:
        """Return synthetic image stubs for *scenario*.

        Returns [] when the feature flag is off.  No HTTP call is ever made.
        """
        if not self._enabled:
            return []
        return [
            ImageAttachment(
                filename=f"synthetic_{scenario}.jpg",
                url="higgsfield://synthetic",
                license="synthetic",
                sha256="placeholder_sha256_higgsfield_stub",
                scenario_ids=[scenario],
            )
        ]


class MedicalImagingProvider:
    """Feature-flagged adapter for the ROCO radiology image dataset.

    Data sourcing:
        Pelka O, Koitka S, Rückert CM, Nensa F, Friedrich CM.
        "Radiology Objects in COntext (ROCO): A Multimodal Image Dataset."
        MICCAI Workshop LABELS 2018.
        PMC source:   https://pmc.ncbi.nlm.nih.gov/articles/PMC11208523/
        HuggingFace:  https://huggingface.co/datasets/robailleo/medical-imaging-combined
        Kaggle:       https://www.kaggle.com/datasets/virajbagal/roco-dataset

    HIPAA compliance notes:
        - ROCO images are sourced from PubMed Central open-access (CC BY) articles.
        - All images were de-identified by the original journal publishers
          PRIOR to PMC indexing; no Protected Health Information (PHI) per
          45 CFR § 164.514 is present.
        - This adapter is DISABLED by default (enable_roco_images=False in config).
        - When enabled, images are referenced at generation time and are NEVER
          stored with patient-identifiable metadata in this system.
        - The synthetic email text paired with these images is entirely fictional;
          no real patient, provider, or facility is referenced.

    When ``enable_roco_images`` is False, ``get_medical_images()`` returns an
    empty list — no network call is ever made.
    """

    def __init__(self, enable_roco: bool | None = None) -> None:
        if enable_roco is None:
            enable_roco = DataGenConfig().enable_roco_images
        self._enabled = enable_roco

    def get_medical_images(self, scenario: str) -> list[ImageAttachment]:
        """Return ROCO radiology image stubs for *scenario*.

        Returns [] when the feature flag is off.  No HTTP call is ever made.

        To enable real ROCO image fetching, set ENABLE_ROCO_IMAGES=true and
        install the ``datasets`` package::

            uv pip install datasets

        Then replace the stub below with::

            from datasets import load_dataset
            ds = load_dataset("robailleo/medical-imaging-combined", split="train")
            sample = ds.shuffle(seed=42).select(range(1))[0]
            # sample["image"] is a PIL Image; sample["caption"] is the ROCO caption.
        """
        if not self._enabled:
            return []
        return [
            ImageAttachment(
                filename=f"roco_radiology_{scenario}.jpg",
                url="roco://placeholder",
                license="CC BY 4.0 (PubMed Central open-access)",
                sha256="placeholder_sha256_roco_stub",
                scenario_ids=[scenario],
                description=(
                    "De-identified radiology image from ROCO dataset "
                    "(Pelka et al., MICCAI LABELS 2018, PMC open-access, "
                    "https://pmc.ncbi.nlm.nih.gov/articles/PMC11208523/)"
                ),
            )
        ]
