# Architecture: Phase 1

## Running foundation

```text
React + TypeScript dashboard
          |
          v
      FastAPI API -------- PostgreSQL
          |
          +--------------- datasets/ (read-only mount)
```

The dashboard reads `GET /api/system/status`. The API checks its database connection and counts non-hidden source files under the configured dataset root, excluding generated split/output directories. It does not open or inspect dataset contents.

## Dataset boundary

Raw and derived dataset files are Git-ignored. Only directory placeholders are tracked. In Phase 3, the data pipeline will inspect the provided dataset's schema, labels, license, missingness, duplicates, class distribution, leakage risks, bias considerations, and privacy concerns before preprocessing.

## Planned services

Authentication, chat, personalization, wellbeing records, safety classification, model training, Flower clients/server, and differential privacy will be introduced in their respective phases. No model metrics or user activity are fabricated in the foundation phase.

The current Compose stack intentionally contains only the frontend, API, and PostgreSQL. ML and federated-learning containers will be added when those services exist.