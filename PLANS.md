# PLANS.md — DGN-PICKS

Read [STATUS.md](STATUS.md) for the latest session handoff, verified progress, and next steps. Current work: [2026-10-14 validation and release](docs/exec-plans/active/2026-10-14-validation-release.md), coordinating CI repair, isolated acceptance, documentation reconciliation, and publication. The [Gato publication checkpoint](docs/checkpoints/2026-09-26-gato-publication.md) is historical evidence; current production results and deployment IDs belong in STATUS and the current release checkpoint. Releases must use GitHub for committed source and direct Railway deployment, followed by verification; see `AGENTS.md`.

For work spanning multiple files, migrations, or UI/API integration, create an ExecPlan in `docs/exec-plans/active/`.

Each ExecPlan must include:
- Purpose
- Scope / Non-scope
- Progress
- Implementation plan
- Validation
- Surprises & Discoveries
- Decision Log
- Outcomes & Retrospective

When complete, move it to `docs/exec-plans/completed/`.
Do not silently diverge from `docs/product-specs/001-local-mvp.md`.
