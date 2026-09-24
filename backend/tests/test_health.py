from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_check_when_database_is_unavailable() -> None:
    with patch(
        "app.api.routes.health.database_is_ready",
        return_value=False,
    ):
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


def test_request_id_is_added_to_response() -> None:
    response = client.get("/health")

    assert "X-Request-ID" in response.headers


def test_existing_request_id_is_preserved() -> None:
    response = client.get(
        "/health",
        headers={
            "X-Request-ID": "test-request-123",
        },
    )

    assert response.headers["X-Request-ID"] == "test-request-123"
