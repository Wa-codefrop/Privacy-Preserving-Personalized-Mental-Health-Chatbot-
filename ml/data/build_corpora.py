from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "datasets" / "Mental Health Conversational AI Training Dataset"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed"
SEED = 42


def normalize_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def stable_split(value: str) -> str:
    bucket = int(hashlib.sha256(value.encode("utf-8")).hexdigest(), 16) % 100
    if bucket < 80:
        return "train"
    if bucket < 90:
        return "val"
    return "test"


def _record_identity(row: dict[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        cleaned[column] = cleaned[column].map(lambda value: normalize_text(value))
    cleaned = cleaned.replace({"": pd.NA})
    return cleaned.dropna(how="all")


def _write_split_jsonl(output_dir: Path, corpus_name: str, rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    files_by_split: dict[str, list[dict[str, Any]]] = {"train": [], "val": [], "test": []}
    for row in rows:
        split_name = stable_split(row.get("group_key") or json.dumps(row, sort_keys=True))
        files_by_split.setdefault(split_name, []).append(row)

    for split_name, records in files_by_split.items():
        path = output_dir / corpus_name / f"{split_name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return files_by_split


def _load_counselor_pairs(dataset_dir: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    csv_paths = [
        dataset_dir / "conversations_training.csv",
        dataset_dir / "mental_health_conversations.csv",
    ]
    for csv_path in csv_paths:
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path)
        if {"question", "answer"}.issubset(df.columns):
            subset = df[["question", "answer"]].copy()
            for row in subset.itertuples(index=False, name=None):
                question, answer = row
                question = normalize_text(question)
                answer = normalize_text(answer)
                if not question or not answer:
                    continue
                record = {
                    "id": hashlib.sha256(f"q-a::{question}::{answer}".encode("utf-8")).hexdigest(),
                    "question": question,
                    "answer": answer,
                    "group_key": question,
                    "source": csv_path.name,
                    "dataset": "counselor_pairs",
                }
                rows[record["id"]] = record

    json_path = dataset_dir / "conversations_training.json"
    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        records = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else payload
        if isinstance(records, list):
            for item in records:
                if not isinstance(item, dict):
                    continue
                question = normalize_text(item.get("input") or item.get("question"))
                answer = normalize_text(item.get("output") or item.get("answer"))
                if not question or not answer:
                    continue
                record = {
                    "id": hashlib.sha256(f"json::{question}::{answer}".encode("utf-8")).hexdigest(),
                    "question": question,
                    "answer": answer,
                    "group_key": question,
                    "source": json_path.name,
                    "dataset": "counselor_pairs",
                }
                rows.setdefault(record["id"], record)

    ordered = list(rows.values())
    if max_rows is not None:
        ordered = ordered[:max_rows]
    return ordered


def _load_emotion(dataset_dir: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    csv_path = dataset_dir / "sentiment_analysis.csv"
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path)
    if "text" not in df.columns or "label" not in df.columns:
        return []
    rows: dict[str, dict[str, Any]] = {}
    for item in df[["text", "label"]].itertuples(index=False, name=None):
        text, label = item
        text = normalize_text(text)
        if not text:
            continue
        normalized_label = int(float(label)) if str(label).strip() not in {"", "nan", "NaN"} else None
        record = {
            "id": hashlib.sha256(f"emotion::{text}::{label}".encode("utf-8")).hexdigest(),
            "text": text,
            "label": normalized_label,
            "group_key": text,
            "dataset": "emotion",
        }
        rows.setdefault(record["id"], record)
    ordered = list(rows.values())
    if max_rows is not None:
        ordered = ordered[:max_rows]
    return ordered


def _load_risk(dataset_dir: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    csv_path = dataset_dir / "mental_health_comprehensive.csv"
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path, low_memory=False)
    if "source" not in df.columns or "class" not in df.columns:
        return []
    subset = df[df["source"].astype(str).str.contains("Suicide_Detection_processed", na=False)]
    rows: list[dict[str, Any]] = []
    for item in subset[["text", "class"]].itertuples(index=False, name=None):
        text, label = item
        text = normalize_text(text)
        if not text or pd.isna(label):
            continue
        value = str(label).strip().lower()
        if value not in {"suicide", "non-suicide"}:
            continue
        rows.append({
            "id": hashlib.sha256(f"risk::{text}".encode("utf-8")).hexdigest(),
            "text": text,
            "label": value,
            "group_key": text,
            "dataset": "risk",
        })
    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        deduped.setdefault(row["id"], row)
    ordered = list(deduped.values())
    if max_rows is not None:
        ordered = ordered[:max_rows]
    return ordered


def _load_dialogues(dataset_dir: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    csv_path = dataset_dir / "dialogues_training.csv"
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path)
    if "text" not in df.columns:
        return []
    rows: list[dict[str, Any]] = []
    for text in df["text"].dropna():
        text = normalize_text(text)
        if not text:
            continue
        utterances = [part.strip() for part in text.split("__eou__") if part.strip()]
        if len(utterances) < 2:
            continue
        rows.append({
            "id": hashlib.sha256(f"dialogue::{text}".encode("utf-8")).hexdigest(),
            "context": " | ".join(utterances[:-1]),
            "next_utterance": utterances[-1],
            "group_key": text,
            "dataset": "dialogues",
        })
    if max_rows is not None:
        rows = rows[:max_rows]
    return rows


def _load_intents(dataset_dir: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    json_path = dataset_dir / "combined_intents.json"
    if not json_path.exists():
        return []
    with json_path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    intents = payload.get("intents", []) if isinstance(payload, dict) else []
    rows: list[dict[str, Any]] = []
    if isinstance(intents, list):
        for intent in intents:
            if not isinstance(intent, dict):
                continue
            tag = str(intent.get("tag", "unknown")).strip()
            patterns = intent.get("patterns") or []
            responses = intent.get("responses") or intent.get("resonses") or []
            if isinstance(responses, str):
                responses = [responses]
            for pattern in patterns:
                pattern_text = normalize_text(pattern)
                if not pattern_text:
                    continue
                response_text = " | ".join(str(item).strip() for item in responses if str(item).strip())
                rows.append({
                    "id": hashlib.sha256(f"intent::{tag}::{pattern_text}".encode("utf-8")).hexdigest(),
                    "pattern": pattern_text,
                    "tag": tag,
                    "response": response_text,
                    "group_key": pattern_text,
                    "dataset": "intents",
                })
    if max_rows is not None:
        rows = rows[:max_rows]
    return rows


def _load_population_stats(dataset_dir: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    csv_path = dataset_dir / "mental_health_comprehensive.csv"
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path, low_memory=False)
    if "source" not in df.columns:
        return []
    subset = df[df["source"].astype(str).str.contains("Indicators_of_Anxiety_or_Depression_processed", na=False)]
    rows: list[dict[str, Any]] = []
    for record in subset.to_dict(orient="records"):
        row = {key: normalize_text(value) for key, value in record.items() if not pd.isna(value)}
        if not row:
            continue
        row["dataset"] = "population_stats"
        row["group_key"] = json.dumps({k: v for k, v in row.items() if k != "dataset"}, sort_keys=True)
        row["id"] = hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()
        rows.append(row)
    if max_rows is not None:
        rows = rows[:max_rows]
    return rows


def _split_records(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    splits: dict[str, list[dict[str, Any]]] = {"train": [], "val": [], "test": []}
    for row in rows:
        group_value = row.get("group_key") or json.dumps(row, sort_keys=True)
        split_name = stable_split(str(group_value))
        splits[split_name].append(row)
    return splits


def build_corpora(dataset_root: str | Path = DEFAULT_DATASET_ROOT, output_dir: str | Path = DEFAULT_OUTPUT_DIR, max_rows: int | None = None) -> dict[str, dict[str, list[dict[str, Any]]]]:
    dataset_dir = Path(dataset_root)
    output_path = Path(output_dir)
    corpus_map = {
        "counselor_pairs": _split_records(_load_counselor_pairs(dataset_dir, max_rows=max_rows)),
        "emotion": _split_records(_load_emotion(dataset_dir, max_rows=max_rows)),
        "risk": _split_records(_load_risk(dataset_dir, max_rows=max_rows)),
        "dialogues": _split_records(_load_dialogues(dataset_dir, max_rows=max_rows)),
        "intents": _split_records(_load_intents(dataset_dir, max_rows=max_rows)),
        "population_stats": _split_records(_load_population_stats(dataset_dir, max_rows=max_rows)),
    }

    manifest_summary: dict[str, dict[str, int]] = {}
    for corpus_name, splits in corpus_map.items():
        for split_name, rows in splits.items():
            if not rows:
                continue
            target_dir = output_path / corpus_name
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / f"{split_name}.jsonl"
            with file_path.open("w", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        manifest_summary[corpus_name] = {split_name: len(rows) for split_name, rows in splits.items()}

    manifest_path = output_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_summary, indent=2, sort_keys=True), encoding="utf-8")
    return corpus_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Phase 1 corpora for the wellbeing dataset pipeline.")
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-rows", type=int, default=None)
    args = parser.parse_args()
    build_corpora(dataset_root=args.dataset_root, output_dir=args.output_dir, max_rows=args.max_rows)
    print(json.dumps({"status": "ok", "output_dir": str(args.output_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
