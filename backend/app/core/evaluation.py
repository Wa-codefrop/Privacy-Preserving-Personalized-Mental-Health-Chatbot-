from __future__ import annotations

import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVALUATION_CONFIG_PATH = PROJECT_ROOT / "configs" / "evaluation.yaml"


def load_evaluation_config() -> dict:
    if not EVALUATION_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Evaluation config not found: {EVALUATION_CONFIG_PATH}")
    with EVALUATION_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError("Evaluation config must be a mapping.")
    return payload


def build_evaluation_summary(config: dict | None = None) -> dict:
    payload = config or load_evaluation_config()
    retrieval_cfg = payload.get("retrieval", {})
    redteam_cfg = payload.get("redteam", {})
    prompts = redteam_cfg.get("prompts", [])

    cases = []
    categories: list[str] = []
    for item in prompts:
        if not isinstance(item, dict):
            continue
        prompt = item.get("prompt", "")
        category = item.get("category", "unlabeled")
        categories.append(category)
        cases.append(
            {
                "prompt": prompt,
                "category": category,
                "review_status": "planned",
            }
        )

    return {
        "retrieval": {
            "metrics": retrieval_cfg.get("metrics", []),
            "sample_size": retrieval_cfg.get("sample_size", 0),
            "seed": retrieval_cfg.get("seed", 0),
        },
        "redteam": {
            "count": len(cases),
            "categories": categories,
            "cases": cases,
        },
        "review_status": "planned",
        "notes": [
            "Retrieval metrics are an identity check, not a human-grounded relevance score.",
            "Red-team prompts should be reviewed for harm, drift, and safety-quality gaps.",
        ],
    }
