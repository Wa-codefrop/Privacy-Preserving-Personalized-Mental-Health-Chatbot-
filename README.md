# Privacy-Preserving Personalized Wellbeing Intelligence Platform

A dashboard-first research platform for supportive wellbeing conversations and privacy-preserving ML experiments. It is not a medical diagnosis system, clinical decision tool, or therapist replacement.

## Phase 1: Project Foundation

The initial foundation includes a React + TypeScript dashboard, a FastAPI status API, PostgreSQL, and a Docker Compose development setup. The dashboard reports live API, database, and local dataset availability. Wellbeing and model metrics remain empty until real records and experiments exist.

## Put Your Dataset Here

The expected pipeline input location is **`datasets/raw/`** at the repository root. For a new dataset, place the original file(s) there. Your existing `datasets/Mental Health Conversational AI Training Dataset/` folder can stay where it is while I review it; do not move or rename the originals yet.

For reference, the pipeline input layout is:

```text
datasets/raw/your_dataset.csv
```

Raw and derived dataset contents in every `datasets/` subfolder are excluded from Git, so they will not be committed or pushed. Keep the original files unchanged; we will inspect their schema, labels, license, and sensitivity before preprocessing. Do not share credentials or private records in chat.

The API only checks whether non-hidden files exist in `datasets/raw/`; it does not read their contents.

## Run Locally

1. Copy `.env.example` to `.env` and change the local development values if needed.
2. Start the services:

	```bash
	docker compose up --build
	```

3. Open the dashboard at `http://localhost:5173` and the API docs at `http://localhost:8000/docs`.

For frontend-only development, run `cd frontend && npm install && npm run dev`. It expects the API at `http://localhost:8000/api` by default.

## Planned Phases

1. Project foundation and dataset location
2. Authentication and profiles
3. Dataset inspection, validation, and preprocessing
4. Baseline NLP model and evaluation
5. Dashboard expansion
6. Assistant and personalization
7. Wellbeing tracking and insights
8. Safety classification
9. Federated learning
10. Differential privacy
11. Research dashboards and experiments
12. Security, tests, and documentation

Each phase will be validated, committed, and pushed to the configured GitHub remote separately. Generated metrics will only be shown after they are produced by the actual pipeline.

## Current Limitations

- Authentication, conversations, mood tracking, and research models are not implemented yet.
- Federated learning and differential privacy are planned research components, not active protections in this foundation phase.
- Local Compose credentials are for development only; production deployment requires managed secrets and additional security review.