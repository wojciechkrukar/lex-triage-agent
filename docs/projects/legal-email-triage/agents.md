# Agents

| Agent | Personality | Graph role | Default Tier-1 model |
|-------|-------------|-----------|---------------------|
| **Director** | Strategic, decisive | Orchestration (off-graph) | Claude Opus 4.7 |
| **Implementer** | Precise, minimal | Off-graph (builds nodes) | Claude Opus 4.7 |
| **Reviewer** | Adversarial, constructive | Off-graph (PR review) | Claude Opus 4.6 |
| **Triage** | Fast, organised | Off-graph (issue routing) | Claude Sonnet 4.6 |
| **Delivery** | Gate-keeping | Off-graph (governance) | Claude Opus 4.6 |
| **Legal Advisor** | Rigorous, liability-aware | `legal_advisor` node (Critic) | Claude Opus 4.7 |
| **Vision Specialist** | Detail-oriented | `vision` node | GPT-5.5 |
| **Dataset Curator** | Inventive, label-strict | Off-graph (Phase 1) | GPT-5.5 |
| **Eval Engineer** | Data-driven | Off-graph (eval harness) | Claude Opus 4.7 |
| **QA Tester** | Thorough, paranoid | Off-graph (testing) | Claude Sonnet 4.6 |
| **Critic** | Adversarial, principled | `appraisal_critic` node | Claude Opus 4.6 |

See `.github/agents/` for individual role cards and `docs/team/roles.md` for full definitions.
