import json
import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database import engine

logger = logging.getLogger(__name__)


def get_database_status() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return "disconnected"
    return "connected"


def get_safety_model_status(results_dir: Path | None = None) -> dict:
    metrics_path = (results_dir or settings.safety_model_dir) / "safety_metrics.json"
    if not metrics_path.is_file():
        return {"trained": False}
    try:
        with metrics_path.open("r", encoding="utf-8") as handle:
            metrics = json.load(handle)
        return {
            "trained": True,
            "accuracy": metrics.get("accuracy"),
            "macro_f1": metrics.get("class_metrics", {}).get("macro avg", {}).get("f1-score"),
            "test_rows": metrics.get("test_rows"),
        }
    except (OSError, ValueError, TypeError) as error:
        logger.warning("Safety metrics unavailable: %s", type(error).__name__)
        return {"trained": False}