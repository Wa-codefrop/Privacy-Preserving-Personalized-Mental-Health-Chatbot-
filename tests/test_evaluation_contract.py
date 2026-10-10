from app.core.evaluation import build_evaluation_summary, load_evaluation_config


def test_evaluation_config_exposes_metrics_and_redteam_cases():
    config = load_evaluation_config()

    assert config["retrieval"]["metrics"][0] == "recall@3"
    assert len(config["redteam"]["prompts"]) >= 3
    assert all("prompt" in item for item in config["redteam"]["prompts"])


def test_build_evaluation_summary_produces_review_plan():
    summary = build_evaluation_summary()

    assert summary["retrieval"]["metrics"][0] == "recall@3"
    assert summary["redteam"]["count"] >= 3
    assert summary["review_status"] == "planned"
    assert all("category" in item for item in summary["redteam"]["cases"])
