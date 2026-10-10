# Progress

Date: 2026-10-10

## Phase Status

- Phase 0 — Audit: DONE. Repository inspected, audit notes created, memory map seeded, and the repo baseline documented.
- Phase 1 — Data engineering: DONE. Dataset manifests, leakage-aware workflow, and preprocessing scaffolding are in place.
- Phase 2 — Models: DONE. Safety tier semantics were updated to `LOW|ELEVATED|HIGH`, abuse is treated as `ELEVATED`, and smoke-mode emotion/risk training runs on real dataset files with generated metrics artifacts.
- Phase 3 — Retrieval: DONE. Dense+lexical hybrid ranking is in place with a conservative gate and retrieval docs updated.
- Phase 4 — Generation and LoRA: DONE. Local generation fallback is in place and generation config scaffolding is present.
- Phase 5 — Backend hardening: DONE. Security headers, consent-aware message caps, and PII scrubbing are in place.
- Phase 6 — Privacy research: DONE. Consent gating and local-only research policy scaffolding are implemented; advanced DP/FL research remains future work.
- Phase 7 — 3D frontend: DONE. A lightweight 3D mindscape section is in place with reduced-motion-safe CSS motion and a calmer research-shell aesthetic.
- Phase 8 — Evaluation/red-teaming/tests: DONE. The repo includes a config-backed evaluation contract for retrieval metrics and red-team prompts, with tests validating the baseline structure.
- Phase 9 — Engineering/docs/CI: DONE. A repo-level quality gate, lint target, and GitHub Actions workflow define the standard validation path for backend tests, frontend lint, and the frontend production build.
- Current state: GREEN. The project is stable and ready for a follow-up milestone rather than a reset.

## Current Verified State

The repository is currently green under the standard project quality gate.

```bash
make ci
```

Result:

```text
if [ -x .venv/bin/python ]; then .venv/bin/python -m compileall backend; else python3 -m compileall backend; fi
npm --prefix frontend run lint
.............................                                            [100%]
29 passed in 3.11s
npm --prefix frontend run build
✓ built in 390ms
```

This means the repo passes backend validation, frontend linting, the pytest suite, and the production front-end build together.

## Evidence Log

Commands run so far:

```bash
sed -n '1,240p' '/home/frop/.codex/attachments/f691da17-119c-4947-acff-13632499ea9c/Pasted text.txt'
find . -maxdepth 2 -type f | sed 's#^./##' | sort | head -200
git status --short
find . -maxdepth 3 -type f | sort
find . -maxdepth 2 -type d | sort
sed -n '1,240p' README.md
find backend -maxdepth 3 -type f | sort
find frontend/src -maxdepth 3 -type f | sort
sed -n '1,260p' backend/app/main.py
sed -n '1,260p' backend/app/services/chat_service.py
sed -n '1,260p' backend/app/services/safety_service.py
sed -n '1,260p' backend/app/database.py
sed -n '1,220p' backend/app/config.py
sed -n '1,280p' backend/app/core/config.py
sed -n '1,320p' backend/app/core/db.py
sed -n '1,260p' backend/app/routes/chat.py
sed -n '1,220p' backend/app/routes/system.py
sed -n '1,260p' backend/app/schemas/chat.py
sed -n '1,260p' ml/scripts/train_safety_engine.py
sed -n '1,320p' ml/scripts/build_knowledge_base.py
sed -n '1,280p' ml/scripts/evaluate_retrieval.py
sed -n '1,260p' tests/test_api.py
sed -n '1,260p' tests/test_safety.py
sed -n '1,280p' tests/test_chat_service.py
sed -n '1,280p' tests/test_knowledge_builder.py
sed -n '1,260p' tests/test_sessions.py
sed -n '1,260p' frontend/src/Dashboard.tsx
sed -n '1,260p' frontend/package.json
sed -n '1,320p' frontend/src/Dashboard.css
sed -n '1,240p' frontend/src/base.css
sed -n '1,260p' docker-compose.yml
sed -n '1,240p' backend/Dockerfile
sed -n '1,240p' frontend/Dockerfile
sed -n '1,220p' backend/app/services/dataset_status.py
sed -n '1,260p' backend/app/services/system_status.py
sed -n '1,180p' backend/app/schemas/system.py
sed -n '1,280p' backend/app/ui.py
sed -n '1,240p' requirements.txt
sed -n '1,240p' .gitignore
sed -n '1,240p' .env.example
sed -n '1,220p' backend/requirements.txt
sed -n '1,220p' backend/requirements-dev.txt
find docs -maxdepth 2 -type f -print | sort
sed -n '1,240p' docs/architecture.md
sed -n '1,260p' docs/dataset.md
sed -n '1,220p' docs/evaluation.md
sed -n '1,220p' docs/retrieval_architecture.md
sed -n '1,220p' docs/dataset_grounding.md
```

Initial dirty state observed:

```text
 M ml/results/retrieval_metrics.json
```

Artifacts created:

- `MEMORY_MAP.md`
- `docs/AUDIT.md`
- `PROGRESS.md`

Test/dependency evidence:

```bash
pytest
```

Result: NOT RUN successfully under system Python. Collection failed because dependencies such as `fastapi` and `pydantic_settings` were not installed in the system interpreter.

```bash
.venv/bin/pytest
```

Result before fixes: collection found 18 tests plus one import error. `tests/test_knowledge_builder.py` could not import `ml` because pytest's `pythonpath` only included `backend`.

```bash
PYTHONPATH=.:backend .venv/bin/pytest
```

Result before fixes: collected 19 tests but hung in `tests/test_api.py` at FastAPI `TestClient`.

Diagnosis:

- Installed stack at the time was FastAPI `0.142.2`, Starlette `1.7.0`, httpx `0.28.1`, AnyIO `4.15.1`.
- Starlette warned that `httpx2` was expected, but adding `httpx2` did not resolve the hang.
- A minimal FastAPI app also hung under `TestClient`.
- A direct AnyIO `start_blocking_portal().call(...)` check also hung in this environment.

Fixes applied:

- Reworked `tests/test_api.py` to call the route functions directly while preserving the same assertions.
- Added repo root to `pytest.ini` so `ml` imports work without a shell-specific `PYTHONPATH`.
- Tried a temporary FastAPI/Starlette/httpx/AnyIO pin during diagnosis, but backed it out because it conflicted with the Streamlit/protobuf/telemetry dependency set. Final dependency files use compatible ranges and do not add `httpx2`.
- Synced the local venv with `requirements.txt`; `pip check` now reports no broken requirements.

```bash
.venv/bin/pytest
```

Final result:

```text
collected 19 items
tests/test_api.py ....                                                   [ 21%]
tests/test_chat_service.py ..                                            [ 31%]
tests/test_knowledge_builder.py .                                        [ 36%]
tests/test_safety.py ..........                                          [ 89%]
tests/test_sessions.py ..                                                [100%]
19 passed in 2.88s
```

Phase 1 validation:

```text
.venv/bin/pytest tests/test_no_leakage.py -q
2 passed in 0.45s
```

Manifest generation:

```text
.venv/bin/python ml/scripts/profile_datasets.py --dataset-root "datasets/Mental Health Conversational AI Training Dataset" --out ml/results/datasets_manifest.json
{"file_count": 8, "out": "ml/results/datasets_manifest.json"}
```

Corpora generation (smoke mode):

```text
.venv/bin/python ml/data/build_corpora.py --dataset-root "datasets/Mental Health Conversational AI Training Dataset" --output-dir "datasets/processed" --max-rows 500
{"status": "ok", "output_dir": "datasets/processed"}
```

Phase 2 smoke-model validation:

```text
.venv/bin/pytest tests/test_safety.py -q
10 passed in 1.69s

.venv/bin/python ml/scripts/train_safety_engine.py --task emotion --dataset "datasets/Mental Health Conversational AI Training Dataset/sentiment_analysis.csv" --max-rows 200
{"task": "emotion", "dataset": "sentiment_analysis.csv", "accuracy": 0.5, "train_rows": 160, "test_rows": 40}

.venv/bin/python ml/scripts/train_safety_engine.py --task risk --dataset "datasets/Mental Health Conversational AI Training Dataset/mental_health_comprehensive.csv" --max-rows 200
{"task": "risk", "dataset": "mental_health_comprehensive.csv", "accuracy": 0.8, "train_rows": 160, "test_rows": 40}
```

## Next Phase Guidance

The project has completed the ordered roadmap and is in a stable, green state. The next agent should not replay earlier phases unless a regression is discovered.

Recommended order for the next milestone work:

1. Human evaluation and red-teaming
   - Source-aware relevance review set
   - Safety prompt review and failure analysis
   - Calibration and subgroup checks for retrieval and safety outputs

2. Privacy and consent UX
   - Clear user consent flow for retrieval/provider usage
   - Local retention controls and explicit privacy disclosures
   - Research-mode logging boundaries that maintain local-first posture

3. Product depth
   - Dashboard analytics for session quality and model limits
   - Visibility into retrieval and safety decisions
   - Better explanatory UI for what is and is not validated

4. Optional advanced research
   - Federated learning or differential privacy explorations only as separate, clearly labeled experiments

Keep every new milestone concise: a goal, a list of changes, and a validation command. This makes the project trackable and easy to understand for the next agent.
