# Image Sourcing

## Policy

All accident/incident images used in the dataset must be:
1. **Public domain** or **CC0** licensed.
2. **Documented** — source URL, licence, and retrieval date recorded in this file.
3. **Non-PII** — no identifiable individuals, no licence plates, no medical records of real people.

## Approved sources

| Source | Licence | Notes |
|--------|---------|-------|
| Wikimedia Commons | CC0 / Public Domain | Filter for accident/injury/damage categories |
| NHTSA crash test images | Public Domain (US federal) | Vehicle collision scenarios |
| FEMA photo library | Public Domain (US federal) | Property damage, flood, fire scenarios |
| US National Archives | Public Domain | Historical accident documentation |

## Prohibited sources

- Google Images / Bing Images (copyright ambiguous).
- Social media platforms (copyright belongs to poster).
- Getty Images, Shutterstock, or other commercial stock.
- Any source requiring attribution beyond documentation.

## Higgsfield (synthetic image generation)

Higgsfield may be used to **augment** the dataset with synthetic accident scene images.
- Feature flag: `ENABLE_HIGGSFIELD=false` in `.env` by default.
- Synthetic images must be clearly labelled `_gt_is_synthetic: true`.
- Human approval required before enabling Higgsfield in any pipeline step.
- Higgsfield is **never** used as a vision analyzer — only as a dataset generator.

## Image manifest

Images are catalogued in `apps/dataset-generator/src/dataset_generator/image_manifest.py`.
Each entry: `{url, source, licence, scenario_ids, retrieval_date, is_synthetic}`.
