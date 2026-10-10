import pytest
from fastapi import HTTPException

from app.core.privacy import check_consent, scrub_text
from app.routes import chat as chat_route
from app.schemas.chat import ChatRequest


def test_consent_gate_requires_explicit_grant():
    assert check_consent("granted") is True
    assert check_consent("yes") is True
    assert check_consent("denied") is False
    assert check_consent(None) is False


def test_diagnostics_scrub_contact_details():
    source = "Call me at 555-123-4567 or alice@example.com"
    assert "555-123-4567" not in scrub_text(source)
    assert "alice@example.com" not in scrub_text(source)
    assert "[PHONE]" in scrub_text(source)
    assert "[EMAIL]" in scrub_text(source)


def test_chat_route_enforces_consent_when_configured(monkeypatch):
    monkeypatch.setattr(chat_route.settings, "require_consent", True)

    with pytest.raises(HTTPException):
        chat_route.chat(ChatRequest(user_id="u", message="hello"), consent=None)
