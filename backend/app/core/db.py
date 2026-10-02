import sqlite3
from pathlib import Path
from typing import Any

from app.core.config import settings


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path or settings.session_db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize_database(db_path: Path | str | None = None) -> None:
    with _connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_user_id_id "
            "ON conversations (user_id, id)"
        )


def save_message(
    user_id: str,
    role: str,
    content: str,
    db_path: Path | str | None = None,
) -> None:
    if role not in {"user", "assistant"}:
        raise ValueError("role must be 'user' or 'assistant'")
    initialize_database(db_path)
    with _connect(db_path) as connection:
        connection.execute(
            "INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )


def get_recent_history(
    user_id: str,
    limit: int = 10,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    initialize_database(db_path)
    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT role, content, timestamp
            FROM conversations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def clear_history(user_id: str, db_path: Path | str | None = None) -> None:
    initialize_database(db_path)
    with _connect(db_path) as connection:
        connection.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))