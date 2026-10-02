from fastapi.testclient import TestClient

from app.main import app
from app.routes import chat as chat_route
from app.schemas.chat import ChatResponse, GroundingMetadata, RiskAssessment
from app.services.system_status import get_database_status


def test_health_reports_database(monkeypatch):
    monkeypatch.setattr("app.services.system_status.get_database_status", lambda: "connected")

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


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

    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"user_id": "test-user", "message": "A test message"},
        )

    assert response.status_code == 200
    assert response.json() == expected.model_dump()


def test_high_risk_intercept_never_calls_chat_provider(monkeypatch):
    monkeypatch.setattr(chat_route, "save_message", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        chat_route.conversational_service,
        "process_user_query",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("provider must not be called")),
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"user_id": "safety-test", "message": "I want to end my life"},
        )

    assert response.status_code == 200
    assert response.json()["risk_assessment"]["risk_level"] == "HIGH"
    assert "988" in response.json()["response"]


def test_chat_rejects_empty_message():
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"user_id": "test-user", "message": " "})

    assert response.status_code == 422