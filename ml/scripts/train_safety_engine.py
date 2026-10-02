import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "ml" / "results"


def find_dataset() -> Path:
    candidates = list(PROJECT_ROOT.glob("datasets/**/sentiment_analysis.csv"))
    candidates = [path for path in candidates if not any(
        part in {"processed", "train", "validation", "test"}
        for part in path.relative_to(PROJECT_ROOT / "datasets").parts
    )]
    if len(candidates) != 1:
        raise FileNotFoundError(
            "Expected exactly one source sentiment_analysis.csv under datasets/; "
            f"found {len(candidates)}. Pass --dataset explicitly."
        )
    return candidates[0]


def train(dataset_path: Path, results_dir: Path) -> dict:
    frame = pd.read_csv(dataset_path, usecols=["text", "label"])
    frame["text"] = frame["text"].fillna("").astype(str).str.strip()
    frame["label"] = pd.to_numeric(frame["label"], errors="coerce")
    frame = frame.loc[frame["text"].ne("") & frame["label"].notna()].copy()
    frame["label"] = frame["label"].astype(int)
    source_rows = len(frame)
    frame = frame.drop_duplicates(subset=["text", "label"])
    rows_after_pair_dedup = len(frame)
    label_counts = frame.groupby("text")["label"].nunique()
    conflicting_texts = set(label_counts[label_counts > 1].index)
    conflicting_rows = int(frame["text"].isin(conflicting_texts).sum())
    frame = frame.loc[~frame["text"].isin(conflicting_texts)]
    frame = frame.drop_duplicates(subset=["text"]).reset_index(drop=True)

    if set(frame["label"].unique()) != set(range(6)):
        raise ValueError("Expected integer emotion labels 0 through 5 in the source dataset.")

    train_texts, test_texts, train_labels, test_labels = train_test_split(
        frame["text"],
        frame["label"],
        test_size=0.2,
        random_state=42,
        stratify=frame["label"],
    )
    vectorizer = TfidfVectorizer(
        max_features=10_000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    train_features = vectorizer.fit_transform(train_texts)
    test_features = vectorizer.transform(test_texts)
    classifier = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    classifier.fit(train_features, train_labels)
    predictions = classifier.predict(test_features)
    labels = sorted(int(label) for label in classifier.classes_)
    no_text_overlap = set(train_texts).isdisjoint(set(test_texts))
    if not no_text_overlap:
        raise RuntimeError("The train and test partitions contain duplicate text.")

    metrics = {
        "dataset": dataset_path.name,
        "task": "six-class sentiment/emotion proxy; not a validated safety-risk model",
        "source_rows_after_empty_label_filter": int(source_rows),
        "rows_after_exact_text_label_dedup": int(rows_after_pair_dedup),
        "conflicting_label_text_groups_excluded": len(conflicting_texts),
        "rows_in_conflicting_label_groups_excluded": conflicting_rows,
        "unique_unambiguous_texts_for_split": int(len(frame)),
        "train_rows": int(len(train_labels)),
        "test_rows": int(len(test_labels)),
        "train_test_text_overlap": not no_text_overlap,
        "labels": labels,
        "accuracy": float(accuracy_score(test_labels, predictions)),
        "class_metrics": classification_report(
            test_labels,
            predictions,
            labels=labels,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(test_labels, predictions, labels=labels).tolist(),
        "split": {"method": "stratified holdout after text deduplication and conflicting-label exclusion", "test_size": 0.2, "random_state": 42},
    }

    results_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, results_dir / "safety_vectorizer.pkl", compress=3)
    joblib.dump(classifier, results_dir / "safety_classifier.pkl", compress=3)
    (results_dir / "safety_metrics.json").write_text(
        json.dumps(metrics, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the sentiment-derived support signal model.")
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args()
    dataset_path = args.dataset or find_dataset()
    metrics = train(dataset_path, args.results_dir)
    print(json.dumps({key: metrics[key] for key in ("dataset", "source_rows_after_empty_label_filter", "conflicting_label_text_groups_excluded", "unique_unambiguous_texts_for_split", "train_rows", "test_rows", "train_test_text_overlap", "accuracy")}, indent=2))


if __name__ == "__main__":
    main()