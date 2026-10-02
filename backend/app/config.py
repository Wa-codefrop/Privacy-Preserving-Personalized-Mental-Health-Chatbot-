from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Wellbeing Intelligence API"
    database_url: str = (
        "postgresql+psycopg://wellbeing:wellbeing-local@localhost:5432/wellbeing"
    )
    cors_origins: list[str] = ["http://localhost:5173"]
    dataset_dir: Path = PROJECT_ROOT / "datasets"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()