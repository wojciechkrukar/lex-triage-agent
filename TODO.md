# TODO Tracker

> Single source of truth for in-flight work. Director updates on dispatch and completion.

## Open

- `#TODO:` [phase1/dataset-curator] Expand scenario taxonomy to ≥ 12 scenarios + 100-email body templates (owner: Dataset Curator, target: M1)
- `#TODO:` [phase1/dataset-curator] Source and document ≥ 50 public-domain accident images from Wikimedia/NHTSA/FEMA; update `docs/projects/legal-email-triage/image-sourcing.md` (owner: Dataset Curator, target: M1)
- `#TODO:` [phase1/implementer] Wire Higgsfield adapter behind `ENABLE_HIGGSFIELD=false` for synthetic image augmentation only (owner: Implementer, target: M1)
- `#TODO:` [phase1/qa-tester] Expand `test_chokepoint.py` to cover all 12 scenario types and assert zero `_gt_*` leakage for each (owner: QA Tester, target: M1)
- `#TODO:` [phase2/implementer] Implement classification node logic with Claude Haiku 4.5 at tier1 (owner: Implementer, target: M2)
- `#TODO:` [phase2/implementer] Implement Legal Appraisal Creator node with Claude Opus 4.7 at tier1 (owner: Implementer, target: M2)
- `#TODO:` [phase2/implementer] Implement Legal Advisor (Critic) node; wire Creator-Critic loop with HITL fallback (owner: Implementer, target: M2)
- `#TODO:` [phase2/vision-specialist] Implement `OpenAIVisionProvider` using GPT-5.5 at tier1 (owner: Vision Specialist, target: M3)
- `#TODO:` [phase2/vision-specialist] Implement text-only fallback when vision provider unavailable (owner: Vision Specialist, target: M3)
- `#TODO:` [eval/eval-engineer] Wire LangSmith eval harness to Phase-1 hidden labels via chokepoint; compute baseline Lead Precision + Recall (owner: Eval Engineer, target: M4)
- `#TODO:` [eval/eval-engineer] Add regression detection: fail eval run if Lead Precision drops > 5pp vs. baseline (owner: Eval Engineer, target: M4)
- `#TODO:` [infra/implementer] Configure HITL queue depth monitoring; alert Director at depth > 10 (owner: Implementer, target: M5)
- `#TODO:` [docs/director] Update `docs/projects/legal-email-triage/architecture.md` Mermaid DAG after Phase 2 node implementations are complete (owner: Director, target: M2)

## In Progress

*(empty — awaiting first dispatch)*

## Done

- `#DONE:` [bootstrap] PR #1 — initial scaffolding: apps skeleton, kernel docs, CI workflow, LLM factory, state schema (closed 2026-05-01)
- `#DONE:` [bootstrap-fix] PR #2 — agent governance scaffolding: 11 agent files, docs/team/, docs/projects/, TODO tracker, escalation matrix, milestones (closed 2026-05-01)
