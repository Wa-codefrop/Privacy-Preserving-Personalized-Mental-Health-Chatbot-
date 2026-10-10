from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_are_present():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Request-ID")


def test_message_length_cap_is_2000_chars():
    long_message = "x" * 2001
    response = TestClient(app).post(
        "/api/chat",
        json={"user_id": "u", "message": long_message},
    )

    assert response.status_code == 422
