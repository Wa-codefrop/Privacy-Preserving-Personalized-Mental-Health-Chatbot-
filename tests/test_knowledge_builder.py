import json

import pandas as pd

from ml.scripts.build_knowledge_base import collect_records


def test_qa_records_deduplicate_and_normalize_missing_source(tmp_path):
    qa_path = tmp_path / "qa.csv"
    intents_path = tmp_path / "intents.json"
    pd.DataFrame(
        [
            {"question": "How can I rest?", "answer": "Take a short break.", "source_dataset": None},
            {"question": "How can I rest?", "answer": "Take a short break.", "source_dataset": None},
        ]
    ).to_csv(qa_path, index=False)
    intents_path.write_text(
        json.dumps({"intents": [{"tag": "rest", "patterns": ["need rest"], "resonses": ["Consider a pause."]}]}),
        encoding="utf-8",
    )

    records = collect_records(qa_path, intents_path)

    assert len(records) == 2
    qa_record = next(record for record in records if record[2]["record_type"] == "qa_pair")
    intent_record = next(record for record in records if record[2]["record_type"] == "intent_pattern")
    assert qa_record[2]["source_dataset"] == "mental_health_conversations"
    assert qa_record[2]["grounding_status"] == "unverified_training_corpus"
    assert "Consider a pause." in intent_record[1]