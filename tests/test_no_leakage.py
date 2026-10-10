import json
from pathlib import Path

import pandas as pd

from ml.data.build_corpora import build_corpora
from ml.scripts.profile_datasets import profile_datasets


def test_profile_datasets_creates_manifest(tmp_path):
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    (dataset_dir / "Mental Health Conversational AI Training Dataset").mkdir()

    pd.DataFrame([{"text": "I feel stressed", "label": 1}, {"text": "I feel anxious", "label": 0}]).to_csv(
        dataset_dir / "Mental Health Conversational AI Training Dataset" / "sentiment_analysis.csv",
        index=False,
    )
    pd.DataFrame([{"question": "A", "answer": "B", "source_dataset": "x"}]).to_csv(
        dataset_dir / "Mental Health Conversational AI Training Dataset" / "mental_health_conversations.csv",
        index=False,
    )

    manifest = profile_datasets(dataset_root=dataset_dir, out_path=tmp_path / "manifest.json")

    assert manifest["file_count"] >= 2
    assert manifest["files"][0]["role_in_pipeline"]
    assert (tmp_path / "manifest.json").exists()


def test_no_leakage_across_splits(tmp_path):
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    source_dir = dataset_dir / "Mental Health Conversational AI Training Dataset"
    source_dir.mkdir()

    pd.DataFrame(
        [
            {"question": "How do I relax?", "answer": "Try a slow breathing exercise.", "source_dataset": "c1"},
            {"question": "What helps with stress?", "answer": "Take a short walk and breathe deeply.", "source_dataset": "c1"},
            {"question": "How do I relax?", "answer": "Try a slow breathing exercise.", "source_dataset": "c2"},
        ]
    ).to_csv(source_dir / "mental_health_conversations.csv", index=False)

    pd.DataFrame(
        [
            {"text": "I am sad", "label": 1},
            {"text": "I feel joy", "label": 0},
            {"text": "I feel low", "label": 1},
            {"text": "I am excited", "label": 0},
        ]
    ).to_csv(source_dir / "sentiment_analysis.csv", index=False)

    pd.DataFrame(
        [
            {"text": "I feel like ending it all", "class": "suicide"},
            {"text": "I am okay and safe", "class": "non-suicide"},
            {"text": "I want to disappear", "class": "suicide"},
            {"text": "I had a good day", "class": "non-suicide"},
        ]
    ).to_csv(source_dir / "mental_health_comprehensive.csv", index=False)

    outputs = build_corpora(dataset_root=source_dir, output_dir=tmp_path / "processed", max_rows=10)

    for corpus_name, splits in outputs.items():
        seen = set()
        for split_name, rows in splits.items():
            ids = {row.get("id") or row.get("text") or row.get("question") for row in rows}
            assert not (seen & ids)
            seen |= ids

    assert any("train" in splits for _, splits in outputs.items())
