from app.core.db import clear_history, get_recent_history, save_message


def test_recent_history_is_ordered_and_scoped(tmp_path):
    database = tmp_path / "sessions.sqlite3"
    save_message("user-a", "user", "first", database)
    save_message("user-a", "assistant", "reply", database)
    save_message("user-a", "user", "second", database)
    save_message("user-b", "user", "other user", database)

    history = get_recent_history("user-a", limit=2, db_path=database)

    assert [message["content"] for message in history] == ["reply", "second"]
    assert [message["role"] for message in history] == ["assistant", "user"]


def test_clear_history_only_deletes_selected_user(tmp_path):
    database = tmp_path / "sessions.sqlite3"
    save_message("user-a", "user", "private", database)
    save_message("user-b", "user", "retained", database)

    clear_history("user-a", database)

    assert get_recent_history("user-a", db_path=database) == []
    assert [row["content"] for row in get_recent_history("user-b", db_path=database)] == ["retained"]