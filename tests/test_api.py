import pytest
from pydantic import ValidationError

from app.main import health
from app.routes import chat as chat_route
from app.schemas.chat import ChatRequest, ChatResponse, GroundingMetadata, RiskAssessment


def test_health_reports_database(monkeypatch):
    monkeypatch.setattr("app.services.system_status.get_database_status", lambda: "connected")

    assert health() == {"status": "ok", "database": "connected"}


def test_chat_response_matches_explicit_schema(monkeypatch):
    assessment = RiskAssessment(risk_level="LOW", action="proxy_test")
    expected = ChatResponse(
        user_id="test-user",
        response="A supportive response.",
        risk_assessment=assessment,
        grounding=GroundingMetadata(status="grounded", sources=[]),
    )
    monkeypatch.setattr(chat_route.safety_engine, "evaluate_risk", lambda _message: assessment)
    monkeypatch.setattr(
        chat_route.conversational_service,
        "process_user_query",
        lambda _user, _message, risk_assessment=None: expected,
    )

    response = chat_route.chat(ChatRequest(user_id="test-user", message="A test message"))

    assert response.model_dump() == expected.model_dump()


def test_high_risk_intercept_never_calls_chat_provider(monkeypatch):
    monkeypatch.setattr(chat_route, "save_message", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        chat_route.conversational_service,
        "process_user_query",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("provider must not be called")),
    )

    response = chat_route.chat(
        ChatRequest(user_id="safety-test", message="I want to end my life")
    )

    assert response.risk_assessment.risk_level == "HIGH"
    assert "988" in response.response


def test_chat_rejects_empty_message():
    with pytest.raises(ValidationError):
        ChatRequest(user_id="test-user", message=" ")
