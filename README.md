# Privacy-Preserving Personalized Wellbeing Intelligence Platform

A dashboard-first research platform for supportive wellbeing conversations and privacy-preserving ML experiments. It is not a medical diagnosis system, clinical decision tool, or therapist replacement.

## Current Phase: Local RAG and Safety Prototype

The React + TypeScript dashboard remains the primary landing page. The FastAPI service now includes local SQLite multi-turn chat history, a deterministic high-risk phrase intercept, a trained six-class sentiment proxy, optional Chroma retrieval, and optional OpenAI generation. Streamlit is provided as a separate chat client. This remains a local research prototype, not a clinical or production-ready service.

## Put Your Dataset Here

The conventional pipeline input location is **`datasets/raw/`** at the repository root. The supplied files are already in `datasets/Mental Health Conversational AI Training Dataset/`; they can stay there because the build scripts discover the named source files under `datasets/`. Do not move or rename the originals.

For reference, the pipeline input layout is:

```text
datasets/raw/your_dataset.csv
```

Raw and derived dataset contents in every `datasets/` subfolder are excluded from Git, so they will not be committed or pushed. The scripts read source files locally. Review [the dataset findings](docs/dataset.md) and [grounding boundaries](docs/dataset_grounding.md) before using or redistributing the material.

The API checks for non-hidden files under `datasets/`, excluding the generated `processed/`, `train/`, `validation/`, and `test/` folders. It does not read dataset contents.

## Run Locally

Create and activate a virtual environment, then install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Train the local sentiment proxy and build/evaluate the knowledge index:

```bash
python ml/scripts/train_safety_engine.py
python ml/scripts/build_knowledge_base.py
python ml/scripts/evaluate_retrieval.py
pytest
```

The first index build downloads the MiniLM model. Set `OPENAI_API_KEY` in a local `.env` only if you explicitly want user messages and retrieved excerpts sent to OpenAI; without a key, the service uses its local fallback.

Start the dashboard, API, PostgreSQL, and optional Streamlit client:

```bash
docker compose up --build
```

Open `http://localhost:5173` for the dashboard, `http://localhost:8000/docs` for the API, and `http://localhost:8501` for Streamlit.

For frontend-only development, run `cd frontend && npm install && npm run dev`. For local API/Streamlit development, use `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000` and `streamlit run backend/app/ui.py` from the repository root.

## Planned Phases

1. Project foundation and dataset review
2. Authentication and profiles
3. Dataset inspection, validation, and preprocessing
4. Baseline NLP model and evaluation
5. Dashboard expansion
6. Local RAG assistant and personalization
7. Wellbeing tracking and insights
8. Safety classification
9. Federated learning
10. Differential privacy
11. Research dashboards and experiments
12. Security, tests, and documentation

Each phase will be validated, committed, and pushed to the configured GitHub remote separately. Generated metrics will only be shown after they are produced by the actual pipeline.

## Safety and Privacy Limits

- The trained classifier predicts six undocumented sentiment labels; it is not a validated safety-risk model. Only the explicit keyword intercept has a deterministic high-risk behavior, and it is not exhaustive.
- Retrieved training conversations/intents are unverified. Similarity is not correctness, and the configured retrieval threshold has not been calibrated with human relevance judgments.
- SQLite chat history is local but not encrypted or authenticated. Do not expose this prototype to untrusted users or store identifiable records in it.
- OpenAI is optional. When configured, messages, recent history, and retrieved excerpts leave the machine for provider processing; get appropriate consent and review retention terms.
- The provided dataset has no verified license/provenance file. Do not redistribute it or make model release claims until its terms and privacy issues are resolved.
- Federated learning and differential privacy are planned, not active protections. Local Compose credentials are for development only.