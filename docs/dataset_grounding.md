# Dataset Grounding Notes

The local source inventory and structural audit are in `docs/dataset.md`. This file is a quick boundary reference for the RAG pipeline:

- `mental_health_conversations.csv` is the Q&A grounding source, but includes two 20,000-row source groups with 19,337 normalized Q&A pairs shared with the separate training conversation file.
- `conversations_training.csv` and `.json` are duplicate representations of the same 40,237 records; they are not separate evaluation data.
- `combined_intents.json` supplies intent patterns and fallback text. Twelve entries have no correctly keyed `responses` list; the indexer accepts the legacy misspelling but the responses remain unverified.
- Reddit post text is entirely empty in its combined CSV and author identifiers remain; the file is excluded from indexing.
- Survey/time-series rows mixed into `mental_health_comprehensive.csv` are not conversational examples and are excluded from the knowledge builder.

All indexed items are marked `unverified_training_corpus`. Source/license status is unknown from the delivered directory. Do not publish or externally process this material until its permissions and privacy treatment are established.