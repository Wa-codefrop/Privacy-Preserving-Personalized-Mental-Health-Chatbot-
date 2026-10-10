# Data Card: sentiment_analysis.csv

- Provenance: UNVERIFIED
- Intended use: emotion-tone proxy only, not a risk model
- Composition: 416,809 rows, 3 columns (`text`, `source`, `label`)
- Notes: label values are informal sentiment/emotion labels; the project config stores the default mapping `0=sadness, 1=joy, 2=love, 3=anger, 4=fear, 5=surprise` but this must be verified by a human audit.
- Known bias: duplicates and conflicting labels exist; do not treat this as a clinical safety label.
- PII findings: basic heuristic scan should be run before any publication.
