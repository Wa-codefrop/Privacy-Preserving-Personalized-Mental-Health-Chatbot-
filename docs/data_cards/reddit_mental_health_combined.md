# Data Card: reddit_mental_health_combined.csv

- Provenance: UNVERIFIED
- Intended use: OOD evaluation and stress testing, not training
- Composition: 588 rows, mostly of short title text; contains direct author usernames
- Notes: `text`, `sentiment`, and `category` are empty; only title text is usable.
- Privacy risk: author names must be dropped immediately and never retained in a model or export.
- Forbidden use: never treat this as a clinical or representative sample of the target population.
