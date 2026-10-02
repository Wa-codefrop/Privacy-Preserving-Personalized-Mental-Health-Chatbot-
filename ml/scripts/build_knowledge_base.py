import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / "var" / "huggingface"))

import chromadb
import pandas as pd
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

COLLECTION_NAME = "wellbeing_knowledge"
BATCH_SIZE = 5_000


def find_unique_dataset(filename: str) -> Path:
    candidates = list(PROJECT_ROOT.glob(f"datasets/**/{filename}"))
    candidates = [
        path
        for path in candidates
        if not any(
            part in {"processed", "train", "validation", "test"}
            for part in path.relative_to(PROJECT_ROOT / "datasets").parts
        )
    ]
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"Expected exactly one source {filename} under datasets/; "
            f"found {len(candidates)}."
        )
    return candidates[0]


def record_id(source: str, record_type: str, text: str) -> str:
    digest = hashlib.sha256(
        f"{source}\0{record_type}\0{text}".encode("utf-8")
    ).hexdigest()
    return digest


def intent_responses(intent: dict[str, Any]) -> list[str]:
    responses = intent.get("responses") or intent.get("resonses") or []
    if isinstance(responses, str):
        return [responses.strip()] if responses.strip() else []
    return [str(response).strip() for response in responses if str(response).strip()]


def collect_records(qa_path: Path, intents_path: Path) -> list[tuple[str, str, dict[str, str]]]:
    records: dict[str, tuple[str, str, dict[str, str]]] = {}
    qa = pd.read_csv(qa_path, usecols=lambda column: column in {"question", "answer", "source_dataset"})
    if not {"question", "answer"}.issubset(qa.columns):
        raise ValueError("The grounding CSV must have question and answer columns.")

    for row in qa.itertuples(index=False, name=None):
        values = dict(zip(qa.columns, row, strict=True))
        question = "" if pd.isna(values.get("question")) else str(values["question"]).strip()
        answer = "" if pd.isna(values.get("answer")) else str(values["answer"]).strip()
        if not question or not answer:
            continue
        document = f"User Question: {question}\nSource Response: {answer}"
        raw_source = values.get("source_dataset")
        source = (
            "mental_health_conversations"
            if pd.isna(raw_source) or not str(raw_source).strip()
            else str(raw_source).strip()
        )
        metadata = {
            "source_dataset": source,
            "record_type": "qa_pair",
            "grounding_status": "unverified_training_corpus",
        }
        identifier = record_id(source, "qa_pair", document)
        records.setdefault(identifier, (identifier, document, metadata))

    with intents_path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    intents = payload.get("intents", []) if isinstance(payload, dict) else []
    if not isinstance(intents, list):
        raise ValueError("combined_intents.json must contain an intents list.")

    for intent in intents:
        if not isinstance(intent, dict):
            continue
        tag = str(intent.get("tag", "unknown"))[:120]
        responses = intent_responses(intent)
        if not responses:
            continue
        for pattern in intent.get("patterns", []):
            pattern_text = str(pattern).strip()
            if not pattern_text:
                continue
            response_text = " | ".join(responses)
            document = (
                f"Intent Pattern [{tag}]: {pattern_text}\n"
                f"Suggested Response: {response_text}"
            )
            metadata = {
                "source_dataset": "combined_intents.json",
                "record_type": "intent_pattern",
                "grounding_status": "unverified_training_corpus",
                "intent_tag": tag,
            }
            identifier = record_id("combined_intents.json", "intent_pattern", document)
            records.setdefault(identifier, (identifier, document, metadata))

    return list(records.values())


def build(qa_path: Path, intents_path: Path, persist_dir: Path) -> int:
    records = collect_records(qa_path, intents_path)
    persist_dir.mkdir(parents=True, exist_ok=True)
    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_function,
    )

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start : start + BATCH_SIZE]
        collection.upsert(
            ids=[record[0] for record in batch],
            documents=[record[1] for record in batch],
            metadatas=[record[2] for record in batch],
        )
    return collection.count()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local wellbeing retrieval index.")
    parser.add_argument("--qa-dataset", type=Path, default=None)
    parser.add_argument("--intents", type=Path, default=None)
    parser.add_argument("--persist-dir", type=Path, default=PROJECT_ROOT / "knowledge_base" / "vector_db")
    args = parser.parse_args()
    qa_path = args.qa_dataset or find_unique_dataset("mental_health_conversations.csv")
    intents_path = args.intents or find_unique_dataset("combined_intents.json")
    count = build(qa_path, intents_path, args.persist_dir)
    print(json.dumps({"collection": COLLECTION_NAME, "documents": count, "persist_dir": str(args.persist_dir)}))


if __name__ == "__main__":
    main()