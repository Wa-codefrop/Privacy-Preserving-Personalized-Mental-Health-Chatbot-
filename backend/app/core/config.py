from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Wellbeing Intelligence API"
    database_url: str = (
        "postgresql+psycopg://wellbeing:wellbeing-local@localhost:5432/wellbeing"
    )
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8501"]
    dataset_dir: Path = PROJECT_ROOT / "datasets"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    chroma_db_path: Path = PROJECT_ROOT / "knowledge_base" / "vector_db"
    safety_model_dir: Path = PROJECT_ROOT / "ml" / "results"
    session_db_path: Path = PROJECT_ROOT / "var" / "sessions.db"
    max_history_turns: int = 10
    relevance_threshold: float = 1.2
    crisis_resources: str = (
        "If you might act on this now, contact your local emergency service. "
        "In the United States or Canada, call or text 988. Elsewhere, "
        "findahelpline.com lists local crisis lines. If possible, tell someone "
        "you trust and stay with them."
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        extra="ignore",
    )


settings = Settings()