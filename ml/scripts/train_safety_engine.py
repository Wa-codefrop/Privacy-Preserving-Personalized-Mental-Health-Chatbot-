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


def find_dataset(task: str) -> Path:
    dataset_name = "sentiment_analysis.csv" if task == "emotion" else "mental_health_comprehensive.csv"
    candidates = list(PROJECT_ROOT.glob(f"datasets/**/{dataset_name}"))
    candidates = [
        path for path in candidates if not any(
            part in {"processed", "train", "validation", "test"}
            for part in path.relative_to(PROJECT_ROOT / "datasets").parts
        )
    ]
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"Expected exactly one source {dataset_name} under datasets/; "
            f"found {len(candidates)}. Pass --dataset explicitly."
        )
    return candidates[0]


def _coerce_text_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame[column].fillna("").astype(str).str.strip()


def train_emotion(dataset_path: Path, results_dir: Path, max_rows: int | None = None) -> dict:
    frame = pd.read_csv(dataset_path, usecols=["text", "label"])
    frame["text"] = _coerce_text_series(frame, "text")
    frame["label"] = pd.to_numeric(frame["label"], errors="coerce")
    frame = frame.loc[frame["text"].ne("") & frame["label"].notna()].copy()
    frame["label"] = frame["label"].astype(int)
    if max_rows is not None:
        frame = frame.head(max_rows)
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
    vectorizer = TfidfVectorizer(max_features=10_000, stop_words="english", ngram_range=(1, 2))
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
        "task": "emotion_model",
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
        "class_metrics": classification_report(test_labels, predictions, labels=labels, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(test_labels, predictions, labels=labels).tolist(),
        "split": {"method": "stratified holdout after text deduplication and conflicting-label exclusion", "test_size": 0.2, "random_state": 42},
    }

    results_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, results_dir / "emotion_vectorizer.pkl", compress=3)
    joblib.dump(classifier, results_dir / "emotion_classifier.pkl", compress=3)
    (results_dir / "emotion_metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return metrics


def train_risk(dataset_path: Path, results_dir: Path, max_rows: int | None = None) -> dict:
    frame = pd.read_csv(dataset_path, low_memory=False)
    frame = frame.loc[frame["source"].astype(str).str.contains("Suicide_Detection_processed", na=False), ["text", "class"]].copy()
    frame["text"] = _coerce_text_series(frame, "text")
    frame["class"] = frame["class"].astype(str).str.strip().str.lower()
    frame = frame.loc[frame["text"].ne("") & frame["class"].isin({"suicide", "non-suicide"})].copy()
    if max_rows is not None:
        frame = frame.head(max_rows)
    frame["label"] = frame["class"].map({"suicide": 1, "non-suicide": 0})
    source_rows = len(frame)
    frame = frame.drop_duplicates(subset=["text", "label"])
    rows_after_pair_dedup = len(frame)
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        frame["text"],
        frame["label"],
        test_size=0.2,
        random_state=42,
        stratify=frame["label"],
    )
    vectorizer = TfidfVectorizer(max_features=20_000, ngram_range=(1, 2))
    train_features = vectorizer.fit_transform(train_texts)
    test_features = vectorizer.transform(test_texts)
    classifier = LogisticRegression(max_iter=2000, C=1.0, random_state=42)
    classifier.fit(train_features, train_labels)
    predictions = classifier.predict(test_features)
    labels = [0, 1]
    metrics = {
        "dataset": dataset_path.name,
        "task": "risk_model",
        "source_rows_after_empty_label_filter": int(source_rows),
        "rows_after_exact_text_label_dedup": int(rows_after_pair_dedup),
        "train_rows": int(len(train_labels)),
        "test_rows": int(len(test_labels)),
        "labels": labels,
        "accuracy": float(accuracy_score(test_labels, predictions)),
        "class_metrics": classification_report(test_labels, predictions, labels=labels, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(test_labels, predictions, labels=labels).tolist(),
        "split": {"method": "stratified holdout on suicidal vs non-suicidal text", "test_size": 0.2, "random_state": 42},
        "label_map": {0: "non-suicide", 1: "suicide"},
    }

    results_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, results_dir / "risk_vectorizer.pkl", compress=3)
    joblib.dump(classifier, results_dir / "risk_classifier.pkl", compress=3)
    (results_dir / "risk_metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return metrics


def train(task: str, dataset_path: Path | None, results_dir: Path, max_rows: int | None = None) -> dict:
    dataset = dataset_path or find_dataset(task)
    if task == "emotion":
        return train_emotion(dataset, results_dir, max_rows=max_rows)
    if task == "risk":
        return train_risk(dataset, results_dir, max_rows=max_rows)
    raise ValueError(f"Unsupported task: {task}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the local emotion and risk model baselines for the wellbeing assistant.")
    parser.add_argument("--task", choices=["emotion", "risk"], default="emotion")
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--max-rows", type=int, default=None)
    args = parser.parse_args()
    metrics = train(args.task, args.dataset, args.results_dir, max_rows=args.max_rows)
    print(json.dumps({"task": args.task, "dataset": metrics["dataset"], "accuracy": metrics["accuracy"], "train_rows": metrics["train_rows"], "test_rows": metrics["test_rows"]}, indent=2))


if __name__ == "__main__":
    main()