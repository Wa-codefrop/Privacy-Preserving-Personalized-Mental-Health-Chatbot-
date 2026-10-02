from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine


def get_database_status() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return "disconnected"
    return "connected"