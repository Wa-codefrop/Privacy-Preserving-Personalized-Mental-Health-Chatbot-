from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "datasets" / "Mental Health Conversational AI Training Dataset"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "ml" / "results" / "datasets_manifest.json"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
HANDLE_RE = re.compile(r"(?:^|\W)@([A-Za-z0-9_]{1,32})")


def _read_dataset_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, low_memory=False)
        return df.to_dict(orient="records")
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("intents"), list):
            return payload["intents"]
    return []


def _pii_hits(values: list[str]) -> dict[str, int]:
    hits = {"emails": 0, "phones": 0, "urls": 0, "handles": 0}
    for value in values:
        if not value:
            continue
        hits["emails"] += len(EMAIL_RE.findall(value))
        hits["phones"] += len(PHONE_RE.findall(value))
        hits["urls"] += len(URL_RE.findall(value))
        hits["handles"] += len(HANDLE_RE.findall(value))
    return hits


def _word_lengths(values: list[str]) -> dict[str, float | int]:
    lengths = [len(str(value).split()) for value in values if str(value).strip()]
    if not lengths:
        return {"p50": 0, "p95": 0, "max": 0}
    lengths_sorted = sorted(lengths)
    p50 = lengths_sorted[int(len(lengths_sorted) * 0.50)]
    p95 = lengths_sorted[min(len(lengths_sorted) - 1, int(len(lengths_sorted) * 0.95))]
    return {"p50": p50, "p95": p95, "max": max(lengths_sorted)}


def _infer_role(path: Path) -> str:
    name = path.name.lower()
    if "sentiment" in name:
        return "emotion_train"
    if "comprehensive" in name:
        return "risk_train_and_stats"
    if "conversations" in name or "conversations_training" in name or "dialogues" in name:
        return "counselor_or_dialogue"
    if "combined_intents" in name:
        return "intent_router"
    if "reddit" in name:
        return "ood_test"
    return "supporting_data"


def _label_distribution(rows: list[dict[str, Any]]) -> dict[str, int]:
    if not rows:
        return {}
    counts: dict[str, int] = {}
    for row in rows:
        for key in ("label", "class", "emotion", "sentiment"):
            if key in row and row[key] not in (None, ""):
                label = str(row[key])
                counts[label] = counts.get(label, 0) + 1
                break
    return counts


def profile_datasets(dataset_root: str | Path = DEFAULT_DATASET_ROOT, out_path: str | Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    root = Path(dataset_root)
    if root.name == "Mental Health Conversational AI Training Dataset":
        files = sorted(root.iterdir())
    elif root.is_dir():
        files = sorted(root.rglob("*"))
    else:
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    manifest_files: list[dict[str, Any]] = []
    for path in files:
        if not path.is_file():
            continue
        rows = _read_dataset_rows(path)
        if not rows:
            continue
        flattened_values = [str(value).strip() for row in rows for value in row.values() if value is not None and str(value).strip()]
        pii = _pii_hits(flattened_values)
        text_values = [str(value).strip() for row in rows for value in row.values() if isinstance(value, str) and value.strip()]
        file_entry = {
            "name": path.name,
            "rows": len(rows),
            "columns": len(rows[0].keys()) if rows and isinstance(rows[0], dict) else 0,
            "null_pct": round((sum(1 for row in rows for value in row.values() if value is None or (isinstance(value, str) and not value.strip())) / max(1, len(rows) * max(1, len(rows[0].keys()) if rows and isinstance(rows[0], dict) else 1))) * 100, 2),
            "duplicate_rows": len(rows) - len({hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest() for row in rows}),
            "label_distribution": _label_distribution(rows),
            "length_stats": _word_lengths(text_values),
            "pii_hits": pii,
            "role_in_pipeline": _infer_role(path),
            "quality_caveats": [
                "dataset provenance is unverified",
                "do not redistribute without confirming license",
                "train/test leakage must be controlled by source-aware splits",
            ],
            "license_status": "UNVERIFIED",
        }
        manifest_files.append(file_entry)

    result = {
        "dataset_root": str(root),
        "file_count": len(manifest_files),
        "files": manifest_files,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile the local dataset files and write a manifest for the frontend.")
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args()
    manifest = profile_datasets(dataset_root=args.dataset_root, out_path=args.out)
    print(json.dumps({"file_count": manifest["file_count"], "out": str(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
