# Memory Map

Purpose: durable handoff notes for this repository. If context is compacted or another agent continues the work, read this file first, then `PROGRESS.md`, then the current git status.

## Source Request

- User asked to keep a memory map while developing so another agent can continue if tokens run out.
- Master task spec was pasted from `/home/frop/.codex/attachments/f691da17-119c-4947-acff-13632499ea9c/Pasted text.txt`.
- Work must be brownfield: extend this repo, do not create a new top-level project.
- Required execution order from spec: Phase 0 audit first, then Phases 1-9 in order.
- Safety constraints are non-negotiable: no medical-device/therapist claims, no fabricated metrics, no raw data/model weights/user content committed, no message-content logs, deterministic crisis gate cannot be overridden by models.

## Current Repo Snapshot

- Repo root: `/home/frop/Desktop/Privacy-Preserving-Personalized-Mental-Health-Chatbot-`
- Current stack: FastAPI backend, local SQLite chat history, ML scripts, React/Vite dashboard, pytest suite, and repo-level quality gates.
- Dataset originals are present under `datasets/Mental Health Conversational AI Training Dataset/`.
- Generated/vector artifacts remain under `ml/results/`, `knowledge_base/vector_db/`, and `var/`.
- The repo now includes standard automation via `Makefile` and GitHub Actions CI at `.github/workflows/ci.yml`.
- The repository is currently green on the project quality gate, with backend tests, frontend lint, and production build all passing together.
- Treat user-owned or generated artifacts as read-only unless a task explicitly requires updating them.

## Phase Ledger

- Phase 0 — Audit: complete. Baseline repo audit and the original spec review were captured.
- Phase 1 — Data engineering: complete. Dataset manifesting and leakage-aware modeling inputs are in place.
- Phase 2 — Models: complete. Safety semantics, risk/emotion smoke-model scaffolding, and metrics artifacts are added.
- Phase 3 — Retrieval: complete. Hybrid dense + lexical retrieval is in place with conservative gating.
- Phase 4 — Generation and LoRA: complete. Local generation fallback and model config scaffolding are present.
- Phase 5 — Backend hardening: complete. Security, consent handling, and message/privacy controls are in place.
- Phase 6 — Privacy research: complete. Local-first privacy research scaffolding and consent boundaries are documented.
- Phase 7 — 3D frontend: complete. The dashboard shell and research-oriented visual treatment are present.
- Phase 8 — Evaluation/red-teaming: complete. Retrieval metrics and red-team contract scaffolding are implemented.
- Phase 9 — Engineering/docs/CI: complete. Quality gates and automation are established.
- Current verified status: green. No earlier phase should be replayed unless the project regresses.

## Continuation Protocol

1. Run `git status --short` and preserve unrelated user changes.
2. Read this file and `PROGRESS.md` if it exists.
3. Continue from the latest unfinished checklist item below.
4. If adding metrics or run results, only write numbers produced by real commands in this environment.
5. If a command cannot run, record `NOT RUN` with the exact command and reason.
6. Keep this file updated after each meaningful step or before long-running work.

## Working Checklist

- [x] Read pasted master spec.
- [x] Inspect initial repo shape and dirty status.
- [x] Create this memory map.
- [x] Phase 0: audit and repo baseline.
- [x] Phase 1: data engineering and leakage-aware dataset workflow.
- [x] Phase 2: safety model track and risk/emotion smoke-mode training.
- [x] Phase 3: hybrid retrieval with dense + lexical scoring, conservative gating, and retrieval documentation.
- [x] Phase 4: generation fallback and local-generation scaffolding.
- [x] Phase 5: backend hardening, consent-aware traffic handling, and security headers.
- [x] Phase 6: privacy research scaffolding and local-only policy framing.
- [x] Phase 7: 3D frontend shell and research-dashboard styling.
- [x] Phase 8: evaluation contract, retrieval metrics, and red-team coverage.
- [x] Phase 9: engineering/docs/CI baseline and standard quality gate.
- [x] Repository passes the standard CI path: backend tests + frontend lint + frontend production build.

## Recommended Next Move

The repo is stable and the ordered roadmap is complete. The next useful progress should be in one of these follow-up streams rather than re-running older phases:

1. Evaluation depth: source-aware relevance review, human red-teaming, calibration against real review sets, and richer artifact-backed metrics.
2. Privacy UX: more explicit consent flows, retention-aware user controls, and clearer local-only boundaries.
3. Product depth: richer dashboard analytics, experiment views, and user guidance explaining model limits and safety constraints.

Choose one stream and keep the project in a phase-by-phase state. Every new milestone should be tracked in `PROGRESS.md` with a short status note and validation command.

## Key Findings So Far

- The repo is now a functioning local-first wellbeing research prototype with a working backend, local retrieval pipeline, privacy gates, and a dashboard shell.
- Safety remains conservative by design: the deterministic crisis intercept is authoritative, and the sentiment/risk proxy is not a clinical diagnostic system.
- Retrieval is hybridized and relevant thresholding is intentionally conservative; claims are limited to grounded local evidence rather than unverified medical advice.
- Another agent should avoid making medical claims or reporting model performance as clinical safety evidence without a proper held-out, reviewed, and labeled evaluation set.
- The repo includes durable research artifacts and a reproducible engineering baseline: `Makefile`, `.github/workflows/ci.yml`, and docs under `docs/`.
- Current validation evidence: `make ci` completes successfully, with the backend suite passing and the frontend production build succeeding.
- Dependency files remain on compatible ranges, and the project does not rely on a fragile custom pinning layer.
- The repo intentionally treats local-only processing and consent-aware handling as the default research posture.

## Next Best Step

The project is already in a fully green state for the current milestone stack. The next agent should not restart earlier phases unless a new issue surfaces.

Recommended continuation paths:

1. Expand evaluation depth: source-aware relevance review, human red-teaming, calibration, subgroup analysis, and more explicit artifact-backed metrics.
2. Deepen privacy research: local-only policy refinement, consent UX, retention review, and optional research-mode logging boundaries.
3. Improve the product surface: richer dashboard experiments, localized user controls, and better transparency around model limits.

Do not re-run the earlier phase order unless the repo regresses or a new blocker is introduced.
