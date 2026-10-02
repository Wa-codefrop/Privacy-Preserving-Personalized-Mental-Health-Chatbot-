# Evaluation Plan and Current Results

## Sentiment Proxy

`ml/scripts/train_safety_engine.py` deduplicates exact text/label pairs, creates a seeded stratified 80/20 random holdout, fits a 10,000-feature unigram/bigram TF-IDF vectorizer and logistic regression, and writes model and class-wise metrics locally under `ml/results/`.

The current holdout contains 74,157 unique text rows from `sentiment_analysis.csv`. Before splitting, the pipeline removes exact text/label duplicates and excludes 22,253 text groups with conflicting labels (44,512 deduplicated rows). The seeded stratified holdout produced accuracy `0.9728` and macro F1 `0.9697` for the six numeric sentiment/emotion labels, with no exact text overlap between train and test. These values are actual held-out sentiment results only. The data provides no validated safety-risk target or class-name mapping; they must not be reported as safety performance or used for diagnosis.

The split prevents exact-text leakage but may still overestimate generalization because near-duplicate text and source groups are undocumented. Before research claims, evaluate with source-aware and near-duplicate-aware held-out partitions, verify class semantics, and report class-wise recall, false negatives, calibration, and subgroup limits.

## Retrieval

Run `ml/scripts/evaluate_retrieval.py --sample-size 200 --seed 42` after building the index. It reports recall@3 and MRR@3 for finding the exact source Q&A pair from a seeded sample. This is a retrieval plumbing/identity check, not human relevance, response correctness, or safety evaluation.

The completed local run indexed 39,009 documents. On the 200-query sample (seed 42), exact-pair recall@3 was `0.91` and MRR@3 was `0.6692`. These scores say whether the exact indexed pair appeared among the top three results; they do not establish that the result is suitable or safe to show a person.

For a meaningful next evaluation, have reviewers create a consented query-to-source relevance set, compare retrieval settings, measure precision/recall at K, and assess whether responses faithfully cite relevant source items. Do not use unverified corpus outputs as gold labels.

## Safety Interception

High-risk phrase interception is deterministic and has unit/API tests proving it bypasses the conversational provider. It is not an exhaustive safety detector and may miss paraphrases or produce false positives. The sentiment proxy only raises a `CONCERNING` signal for configured labels; it never determines emergency status. Human review and a separately labeled, appropriately governed evaluation set are required before any safety-performance claim.