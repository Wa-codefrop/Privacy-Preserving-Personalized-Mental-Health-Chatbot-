# Phase 0 Audit

Date: 2026-10-10

Scope: read-only audit of the current brownfield repository against the v2 master specification. No raw dataset rows were copied into this document.

## Current Structure

- `backend/app/`: FastAPI service with chat and system routes, Pydantic schemas, a SQLite conversation store, PostgreSQL connectivity checks, retrieval/generation orchestration, and a Streamlit fallback UI.
- `frontend/`: React + TypeScript + Vite dashboard. It currently renders a status-oriented workspace shell, not the requested 3D Mindscape product.
- `ml/scripts/`: three local scripts: sentiment-proxy training, Chroma knowledge-base build, and exact-pair retrieval evaluation.
- `ml/results/`: generated metrics and local model artifacts. Pickle artifacts are ignored by Git; JSON metrics may be present locally.
- `knowledge_base/vector_db/`: local Chroma vector store, ignored by Git.
- `datasets/`: source files are present locally under `datasets/Mental Health Conversational AI Training Dataset/`; dataset contents are ignored by Git.
- `docs/`: existing architecture, dataset review, retrieval, and evaluation notes.
- `tests/`: pytest coverage for health/chat API, deterministic high-risk bypass, SQLite history scoping, chat-service grounding behavior, and knowledge-builder deduplication.

## What Works

- The API starts from `backend/app/main.py`, initializes the local SQLite conversation table on lifespan startup, exposes `/health`, `/api/system/status`, and `/api/chat`.
- `POST /api/chat` runs a deterministic high-risk check before calling the conversational provider. The tested HIGH path bypasses `conversational_service.process_user_query`.
- The current code is honest that the trained model is a six-class sentiment/emotion proxy, not a validated safety-risk model.
- The Chroma retrieval path is local-first and returns source metadata, not raw retrieved training text, in the API response.
- OpenAI is optional. If no API key is configured, the service falls back to a non-provider response.
- The index builder marks retrieved corpus material as unverified training content.
- `.gitignore` excludes raw datasets, derived dataset directories, vector stores, SQLite databases, logs, virtualenvs, frontend build output, and model pickle files.
- Existing docs already warn that dataset provenance/licensing is unverified and that retrieval/sentiment metrics are not clinical or safety claims.
- Tests cover several important prototype invariants, especially provider bypass for explicit high-risk messages.

## Broken, Missing, or Divergent From v2

- Phase ordering has not been followed yet for v2: there was no `docs/AUDIT.md` before this file, no generated `PROGRESS.md`, and no Phase 1 manifest/data-card pipeline.
- There is no `configs/` directory for `labels.yaml`, `safety.yaml`, `retrieval.yaml`, `blocklist.yaml`, `crisis_resources.yaml`, or LoRA settings.
- The existing "safety classifier" is trained on `sentiment_analysis.csv`. The v2 spec requires separate emotion and risk models, with risk trained from the `Suicide_Detection` rows inside `mental_health_comprehensive.csv`.
- Risk levels currently use `LOW|CONCERNING|HIGH`; v2 requires `LOW|ELEVATED|HIGH`.
- The deterministic safety rules are a small keyword tuple. They do not yet implement tiered rules, leetspeak/spacing normalization, negation/figurative handling, or the required regression suite.
- `abuse` currently maps to HIGH in the keyword tuple, while v2 says abuse/violence disclosures should be ELEVATED unless imminent danger is present.
- The HIGH response uses a generic text setting with 988 and findahelpline-style wording, but there is no country-keyed crisis resource config with verification metadata.
- Chat persistence is plaintext SQLite keyed only by a caller-provided `user_id`. There is no authentication, guest/session distinction, consent, retention TTL, export endpoint, hard-delete endpoint across stores, or field-level encryption.
- `GET /api/chat/history/{user_id}` exposes plaintext history for any user id without auth.
- User message content is saved before encryption/scrubbing exists. Provider calls can include recent plaintext history and retrieved excerpts if OpenAI is configured.
- There is no PII scrubber, prompt-injection delimiting layer, output guard, provider abstraction, circuit breaker beyond OpenAI retry, rolling summary, or trace schema.
- Retrieval is dense-only Chroma top-3 with a fixed `RELEVANCE_THRESHOLD=1.2`. v2 requires dense + BM25 hybrid search, RRF, optional rerank, and a calibrated relevance gate.
- Retrieval documents currently combine question and answer text. v2 requires embedding the question/pattern side and returning paired answers only as unverified style exemplars.
- The insufficient-grounding note still says "dataset knowledge base"; v2 requires the exact user-facing wording without that jargon.
- ML scripts do not provide `--max-rows`, `--device auto`, pinned deterministic experiment configs, data cards, leakage tests, model cards, calibration artifacts, DP/FL experiments, or LoRA training.
- There is no `Makefile`, CI workflow, pre-commit config, ruff/mypy setup, pip-audit/npm-audit workflow, secret scan, Docker Compose profiles, or non-root container hardening.
- Frontend is a static status dashboard. It lacks the 3D hero, chat UX, workflow scrollytelling, dataset/model/privacy/about pages, i18n, reduced-motion handling for a 3D scene, Playwright tests, and artifact-driven metrics pages required by v2.
- Streamlit remains a fallback prototype and still reflects the old `CONCERNING` risk vocabulary.

## Security and Privacy Issues

- No authentication or authorization protects chat, history, deletion, or system endpoints.
- Plaintext user content is stored in `var/sessions.db`; there is no field-level encryption or per-user key model.
- CORS allows localhost origins in config, but there is no production allow-list enforcement profile.
- Docker Compose has development PostgreSQL credentials with defaults; credentials are parameterized but still usable without a real secret in local/prod distinction.
- Containers run as root by default.
- There is no rate limiting, request-id structured logging policy, security headers, body-size cap beyond Pydantic message length, or stack-trace hardening audit.
- `ChatRequest.message` allows up to 8,000 chars; v2 requires a 2,000-char cap.
- No consent gate exists before persistence, mood tracking, retrieval, or external provider usage.
- No PII scrubbing runs before storage, logs, retrieval, or optional external calls.
- OpenAI opt-in is environment-level only, not explicit per user.

## Dead Code and Design Smells

- `backend/app/database.py` defines a SQLAlchemy engine used for status checks only; application chat persistence uses the separate SQLite helper in `backend/app/core/db.py`.
- `backend/app/config.py` is a compatibility re-export around `backend/app/core/config.py`.
- PostgreSQL is required by Compose and status reporting, but no application tables or migrations use it yet.
- Frontend navigation advertises planned pages as disabled items rather than implemented routes.
- Local generated outputs exist in ignored directories; future work should avoid overwriting user-modified generated metrics unless intentionally rerunning that pipeline.

## Test Coverage

Existing tests cover:

- `/health` response shape.
- `/api/chat` schema passthrough with mocked services.
- HIGH-risk bypass of the conversational provider.
- Empty-message validation.
- Safety keyword matching and sentiment-proxy fallback behavior.
- SQLite history ordering/scoping and selected-user deletion.
- Retrieval insufficiency note and metadata persistence.
- Knowledge-builder exact deduplication and misspelled `resonses` handling.

Missing tests required by v2:

- Full safety regression suite from `tests/safety_cases.yaml`.
- PII scrubber unit/property tests.
- Encryption round trip and key/retention behavior.
- Tier max-logic tests for deterministic rules plus model output.
- Output guard tests.
- Retrieval leakage/gate tests and no-overlap data split tests.
- API integration tests for auth, consent gating, export, hard delete, SSE streaming, HIGH path with zero provider calls, and trace schema.
- Prompt-injection tests.
- Frontend Playwright, accessibility, reduced-motion, and mocked chat tests.

## Recommended Next Phase

Proceed to Phase 1 only after preserving this audit in `PROGRESS.md` and verifying current tests. Phase 1 should add config scaffolding, data profiling, corpus builders, leakage tests, and data cards without changing the user-facing safety/generation flow yet.
