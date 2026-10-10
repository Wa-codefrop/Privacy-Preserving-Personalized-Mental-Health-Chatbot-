# Data Card: mental_health_comprehensive.csv

- Provenance: UNVERIFIED
- Intended use: risk-model training data and dashboard statistics only
- Composition: 276,143 rows; stacked sources include text and survey statistics
- Notes: `Suicide_Detection_processed.csv` rows are the risk-training portion; `Indicators_of_Anxiety_or_Depression_processed.csv` is population-statistics-only and never for training.
- Known bias: source-dependent schemas, duplicate texts, and an English-only proxy label structure are all present.
- Forbidden use: do not use the survey rows or any numeric indicators as direct mental-health diagnosis data.
