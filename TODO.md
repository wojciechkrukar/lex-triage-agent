# TODO Tracker

> Single source of truth for in-flight work. Director updates on dispatch and completion.

## Open

- `#TODO:` [phase2/implementer] Implement classification node logic with Claude Haiku 4.5 at tier1 (owner: Implementer, target: M2)
- `#TODO:` [phase2/implementer] Implement Legal Appraisal Creator node with Claude Opus 4.7 at tier1 (owner: Implementer, target: M2)
- `#TODO:` [phase2/implementer] Implement Legal Advisor (Critic) node; wire Creator-Critic loop with HITL fallback (owner: Implementer, target: M2)
- `#TODO:` [phase2/vision-specialist] Implement `OpenAIVisionProvider` using GPT-5.5 at tier1 (owner: Vision Specialist, target: M3)
- `#TODO:` [phase2/vision-specialist] Implement text-only fallback when vision provider unavailable (owner: Vision Specialist, target: M3)
- `#TODO:` [eval/eval-engineer] Wire LangSmith eval harness to Phase-1 hidden labels via chokepoint; compute baseline Lead Precision + Recall (owner: Eval Engineer, target: M4)
- `#TODO:` [eval/eval-engineer] Add regression detection: fail eval run if Lead Precision drops > 5pp vs. baseline (owner: Eval Engineer, target: M4)
- `#TODO:` [infra/implementer] Configure HITL queue depth monitoring; alert Director at depth > 10 (owner: Implementer, target: M5) — **DONE, see below**
- `#TODO:` [docs/director] Update `docs/projects/legal-email-triage/architecture.md` Mermaid DAG after Phase 2 node implementations are complete (owner: Director, target: M2)
- `#TODO:` [m7/implementer] Complete `notebooks/lex_triage_dashboard.ipynb`: run against tier1 eval output, verify all 7 sections render, export PNG artefacts to `runtime/benchmarks/`. Depends on M5 + M6 complete. (owner: Implementer, target: M7)
- `#TODO:` [dataset/dataset-curator] Enable ROCO image integration: set `ENABLE_ROCO_IMAGES=true`, install `datasets` package, replace stub in `MedicalImagingProvider.get_medical_images()` with real HF fetch. See `docs/data-sources.md §6`. (owner: Dataset Curator, target: M2)
- `#TODO:` [dataset/dataset-curator] Regenerate 5 000-record demo dataset with `--count 5000 --realistic-split --seed 42` once PI models are integrated (target: M3)

## In Progress

*(empty — Phase 1 complete, Phase 2 not yet started)*

## Done

- `#DONE:` [phase2/implementer] M2 — All 7 LangGraph nodes implemented; real ChatAnthropic/ChatOpenAI wiring; per-node cost tracking via extract_cost; tier1 model map corrected (classifier→claude-haiku-4-5); 64 tests green. (2026-05-02)
- `#DONE:` [phase2/vision-specialist] M3 — Vision node wires real GPT-4o multimodal calls with base64 attachment payload; text-only fallback for stubs; cost logged via extract_cost. (2026-05-02)
- `#DONE:` [eval/eval-engineer] M4 — `legal-triage eval` CLI subcommand; Lead Precision/Recall/FPR/Accuracy KPIs; runtime/benchmarks/ storage; regression gate (exit 1 on >5pp precision drop); baseline.json seeded. (2026-05-02)
- `#DONE:` [m5/implementer] M5 — `hitl_queue.py` thread-safe queue (enqueue/dequeue/depth/reset, alert at >10, suspend at >20, callback registry); `hitl_gate.py` enqueues on HITL trigger + stores `hitl_queue_depth` in state; `lex_triage_interactive.ipynb` — 14-cell notebook with `HitlBatchRunner`, ipywidgets approve/reject/reclassify UI (asyncio+nest_asyncio), auto-mode with score heuristic, live progress bar, routing pie, confusion matrix, latency histogram, CEO summary; 92 tests green. (2026-05-02)
- `#DONE:` [m7/director] M7 notebook skeleton created: `notebooks/lex_triage_dashboard.ipynb` — §1 graph topology, §2 KPI gauges, §3 confusion matrix, §4 cost breakdown, §5 latency, §6 HITL queue, §7 CEO summary. Synthetic demo fallback included. (2026-05-02)
- `#DONE:` [bootstrap] PR #1 — initial scaffolding: apps skeleton, kernel docs, CI workflow, LLM factory, state schema (closed 2026-05-01)
- `#DONE:` [bootstrap-fix] PR #2 — agent governance scaffolding: 11 agent files, docs/team/, docs/projects/, TODO tracker, escalation matrix, milestones (closed 2026-05-01)
- `#DONE:` [phase1/director] TASK-P1-01 — schema alignment: severity vocab, 12 scenario names, new GT fields (gt_has_attachment, gt_jurisdiction, gt_sol_years), distribution fix to 60% PI leads. All tests green. (2026-05-01)
- `#DONE:` [phase1/dataset-curator] TASK-P1-02 — scenario-specific email body templates for all 9 PI scenarios + S12 ambiguous; replaced shared _PI_BODIES with per-scenario dict. (2026-05-01)
- `#DONE:` [phase1/dataset-curator] TASK-P1-03 — image manifest expanded to 50 public-domain images (NHTSA/FEMA/Wikimedia); all 12 scenarios covered; get_images_for_scenario() updated. (2026-05-01)
- `#DONE:` [phase1/implementer] TASK-P1-04 — HiggsFieldProvider wired behind ENABLE_HIGGSFIELD=false; stub returns empty list when disabled, synthetic ImageAttachment when enabled; no HTTP calls in CI. (2026-05-01)
- `#DONE:` [phase1/qa-tester] TASK-P1-05 — test_chokepoint.py expanded with parametrised 12-scenario strip test; TestM1ExitCriteria class asserts all M1 KPI gates. 39 tests green. (2026-05-01)
- `#DONE:` [phase1/dataset-curator] TASK-P1-06 — image manifest fully replaced with verified Wikimedia Commons URLs (API-confirmed); 12/12 ROCO stubs available behind feature flag; `emails_combined.jsonl` (132 records) rebuilt. Tests: 39 green. (2026-05-01)
- `#DONE:` [phase1/implementer] TASK-P1-07 — generator enriched: Enron-style billing noise, SpamBase-style spam (12 body variants), AgInjuryNews-inspired agricultural/workplace bodies, medical malpractice variants, realistic noise-engineering (`_apply_realistic_noise`), urgency scoring (`gt_urgency` 1–10), diversified sender names (30 first/last names), `--realistic-split` CLI flag (30/70 PI/noise distribution), `MedicalImagingProvider` ROCO stub with HIPAA attribution. 39 tests green. (2026-05-01)

## Dataset Sources (see `docs/data-sources.md` for full compliance record)

| Purpose | Dataset | URL | License |
|---------|---------|-----|---------|
| Billing/corporate noise tone | Enron Email Dataset | https://www.cs.cmu.edu/~enron/ | Public Domain |
| Spam pattern vocabulary | UCI SpamBase | https://archive.ics.uci.edu/dataset/94/spambase | CC BY 4.0 |
| Legal reasoning terminology | LegalBench (HuggingFace) | https://huggingface.co/datasets/nguha/legalbench | CC BY 4.0 |
| Agricultural injury scenarios | AgInjuryNews | http://aginjurynews.org/ | News / Fair Use (no text copied) |
| Radiology images (ROCO, disabled by default) | medical-imaging-combined (HF) | https://huggingface.co/datasets/robailleo/medical-imaging-combined | CC BY 4.0 |
| Radiology images (ROCO, alternate) | ROCO Dataset (Kaggle) | https://www.kaggle.com/datasets/virajbagal/roco-dataset | CC BY 4.0 |
| ROCO paper / de-identification reference | PMC article | https://pmc.ncbi.nlm.nih.gov/articles/PMC11208523/ | Open Access |
