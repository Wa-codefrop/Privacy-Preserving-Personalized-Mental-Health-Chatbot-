# Data Card: mental_health_conversations.csv

- Provenance: UNVERIFIED
- Intended use: support-style conversational examples for retrieval and general assistance patterns
- Composition: 40,000 rows, mostly question/answer pairs, with repeated or partially empty fields
- Notes: `statement` is empty and `status` is not reliable; only a subset is usable for grounded retrieval.
- Known bias: duplicate rows and a large share of repeated examples require deduplication before training.
- Forbidden use: do not treat any answer as verified clinical advice or a medical fact.
