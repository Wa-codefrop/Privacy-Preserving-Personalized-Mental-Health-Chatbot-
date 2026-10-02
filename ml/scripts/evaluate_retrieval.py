import argparse
import json
import random
import sys
from pathlib import Path

import chromadb
import pandas as pd
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from ml.scripts.build_knowledge_base import (  # noqa: E402
    COLLECTION_NAME,
    find_unique_dataset,
    record_id,
)


def evaluate(dataset_path: Path, persist_dir: Path, sample_size: int, seed: int) -> dict:
    frame = pd.read_csv(dataset_path, usecols=["question", "answer", "source_dataset"])
    frame = frame.dropna(subset=["question", "answer"])
    frame["question"] = frame["question"].astype(str).str.strip()
    frame["answer"] = frame["answer"].astype(str).str.strip()
    frame = frame.loc[frame["question"].ne("") & frame["answer"].ne("")]
    sample = frame.sample(n=min(sample_size, len(frame)), random_state=seed)

    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        ),
    )
    hits = 0
    reciprocal_ranks = []
    for row in sample.itertuples(index=False):
        source = getattr(row, "source_dataset", None)
        if pd.isna(source) or not source:
            source = "mental_health_conversations"
        document = f"User Question: {row.question}\nSource Response: {row.answer}"
        expected_id = record_id(str(source), "qa_pair", document)
        result = collection.query(query_texts=[row.question], n_results=3)
        returned_ids = result.get("ids", [[]])[0]
        if expected_id in returned_ids:
            hits += 1
            reciprocal_ranks.append(1 / (returned_ids.index(expected_id) + 1))
        else:
            reciprocal_ranks.append(0.0)

    count = len(sample)
    metrics = {
        "collection_documents": collection.count(),
        "queries": count,
        "recall_at_3_exact_source_pair": hits / count if count else 0.0,
        "mean_reciprocal_rank_at_3_exact_source_pair": sum(reciprocal_ranks) / count if count else 0.0,
        "sample_seed": seed,
        "note": "Exact-source-pair retrieval check only; not a human relevance or safety evaluation.",
    }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate exact-pair retrieval over a seeded query sample.")
    parser.add_argument("--qa-dataset", type=Path, default=None)
    parser.add_argument("--persist-dir", type=Path, default=PROJECT_ROOT / "knowledge_base" / "vector_db")
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "ml" / "results" / "retrieval_metrics.json")
    args = parser.parse_args()
    if args.sample_size <= 0:
        parser.error("--sample-size must be positive")
    metrics = evaluate(args.qa_dataset or find_unique_dataset("mental_health_conversations.csv"), args.persist_dir, args.sample_size, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()