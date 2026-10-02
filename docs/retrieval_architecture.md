# Retrieval Architecture

## Local Build

`ml/scripts/build_knowledge_base.py` reads `mental_health_conversations.csv` and `combined_intents.json` from the local `datasets/` tree. It removes exact duplicate documents, assigns deterministic SHA-256 IDs, embeds in 5,000-record batches with `sentence-transformers/all-MiniLM-L6-v2`, and upserts into the persistent `wellbeing_knowledge` Chroma collection using cosine distance.

Each document is tagged `grounding_status=unverified_training_corpus`. This label is deliberate: no provenance or license statement accompanied the local files, and corpus presence does not establish answer accuracy or safety. The script does not make OpenAI calls. Model weights are downloaded separately from Hugging Face on first build and cached under `var/huggingface/`.

## Query Path

1. A validated user message is checked by the deterministic safety intercept.
2. The local Chroma collection is queried for at most three records.
3. Retrieval is insufficient when the collection is missing or empty, the query fails, or the top cosine distance exceeds `RELEVANCE_THRESHOLD`.
4. Only grounded excerpts are packaged with recent SQLite history for an optional OpenAI request. If `OPENAI_API_KEY` is unset, the service responds without a provider call.
5. Every retrieved source is returned as metadata; retrieved text is not exposed through the API response.

The threshold is a prototype setting, not an empirically calibrated relevance boundary. Distance and exact-match retrieval results do not prove semantic relevance. See `docs/evaluation.md` before interpreting retrieval metrics.

## Privacy and Limits

Conversation history is stored locally in SQLite under `var/sessions.db`. If OpenAI is configured, the current message, bounded prior turns, and selected retrieved excerpts are sent to that provider; review provider terms and user consent requirements before deployment. If it is not configured, no user conversation is transmitted to an LLM. The vector store and model cache are local and ignored by Git.

The corpus contains unreviewed mental-health conversations and intent responses. It can contain harmful or misleading text. It is not approved clinical guidance; retrieval does not make its contents verified. Keep the service local until the dataset license, privacy review, and human quality/safety evaluation are complete.