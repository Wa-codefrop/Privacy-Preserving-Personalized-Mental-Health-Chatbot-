# Dataset Review

## Scope

Read-only structural review of the local files in `datasets/Mental Health Conversational AI Training Dataset/`. Source files are not tracked by Git. Counts below describe the inspected local snapshot; they are not model metrics or evidence of clinical validity.

The directory contains eight files totaling approximately 307 MB: six CSVs and two JSON files. No accompanying README, source citation, or license file was present, so redistribution and research-use permissions remain unverified.

## Inventory and Findings

| File | Records | Structural findings |
| --- | ---: | --- |
| `conversations_training.csv` | 40,237 | `input`/`output` pairs; 20,663 exact duplicate rows. |
| `conversations_training.json` | 40,237 | Same ordered pairs as the CSV; redundant copy, not an independent split. |
| `mental_health_conversations.csv` | 40,000 | Two 20,000-row sources; `statement` is entirely empty, and `status` is missing in half the rows. Contains 1,326 exact duplicate rows. |
| `dialogues_training.csv` | 13,118 | `emotion` and `act` contain encoded sequences without a mapping file; 236 exact duplicate rows. `topic` has 10 values. |
| `mental_health_comprehensive.csv` | 276,143 | A concatenation of three incompatible sources: 232,074 suicide/non-suicide rows, 27,977 rows with binary `label`, and 16,092 survey/time-series rows without conversation text or classifier labels. Seven exact duplicate rows. |
| `sentiment_analysis.csv` | 416,809 | Six integer labels with no mapping or provenance documentation; class counts range from 14,972 to 141,067. Contains 1,515 exact duplicate rows. |
| `reddit_mental_health_combined.csv` | 588 | The `text`, `sentiment`, and `category` columns are completely empty. Author identifiers remain in the file; do not use or publish them. |
| `combined_intents.json` | 92 intents | 337 patterns and 156 correctly keyed responses; 12 intents store responses under the misspelled key `resonses`. |

The conversation-pair CSV and `mental_health_conversations.csv` share 19,337 unique normalized question/answer pairs. The JSON conversation file repeats the CSV records. These overlaps create substantial train/test contamination risk if files are combined and randomly split.

The merged comprehensive file has source-dependent schemas: survey fields are missing in 94.17% of all rows, `label` is missing in 89.87%, and `class` is missing in 15.96%. Within the survey source, demographic and time-period fields are present, but there is no conversation text. The binary label meanings are not documented.

A conservative pattern scan found nine rows with phone-number-like patterns across conversational fields. This is a heuristic and may include false positives; review and redact before sharing or training. The Reddit author field is also a direct privacy risk, especially alongside mental-health subreddit membership.

## Recommended Use

- Do not merge these files into one classifier dataset. They represent distinct tasks and incompatible label schemes.
- Do not treat sentiment, encoded emotion, or survey labels as safety-risk labels. Verify provenance, label definitions, and annotation quality first.
- For any future split, canonicalize and deduplicate text pairs across all sources before splitting; keep related duplicates in one partition and use a held-out source-aware test set.
- Exclude direct identifiers such as Reddit author names and post IDs. Review free text for personal information, and retain source metadata only when necessary and licensed.
- Audit source and demographic coverage before making subgroup or generalization claims. The Reddit subset is small and source-skewed; the survey portion is a different data modality.
- Treat conversational responses as unreviewed training material, not validated supportive guidance. Apply human safety review before using them in a user-facing system.
- Resolve the source/license for every component and document permitted uses before training or redistribution.

## Status

The dashboard/API only detect file presence. No preprocessing, labels, train/validation/test split, model, or evaluation result has been produced from these files yet.