# Data Card: conversations_training.csv

- Provenance: UNVERIFIED
- Intended use: conversational corpus for style exemplars and retrieval grounding
- Composition: 40,237 rows with `input` and `output`; heavily duplicated
- Notes: these rows overlap with the mental health conversation corpus and must be deduplicated before model evaluation.
- Known bias: duplicated content inflates metrics unless source-aware splits are used.
- Forbidden use: do not present these responses as validated support or diagnosis.
