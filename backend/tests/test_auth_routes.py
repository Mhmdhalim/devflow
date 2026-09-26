import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import jwt
from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.auth import get_auth_service
from app.core.config import get_settings
from app.core.security import ALGORITHM
from app.main import app
from app.models.user import User
from app.services.auth import InvalidCredentialsError

client = TestClient(app)


def test_login() -> None:
    service = MagicMock()

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password="not-used-in-router-test",
        is_active=True,
    )

    user.id = uuid.uuid4()

    service.authenticate.return_value = user

    app.dependency_overrides[get_auth_service] = lambda: service

    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "secure-password-123",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert "access_token" in body

    settings = get_settings()

    payload = jwt.decode(
        body["access_token"],
        settings.secret_key,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == str(user.id)
    assert "exp" in payload


def test_login_with_invalid_credentials() -> None:
    service = MagicMock()

    service.authenticate.side_effect = InvalidCredentialsError

    app.dependency_overrides[get_auth_service] = lambda: service

    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "wrong-password",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401

    assert response.json() == {"detail": "Invalid email or password"}

    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_get_me() -> None:
    now = datetime.now(UTC)

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password="not-exposed",
        is_active=True,
    )

    user.id = uuid.uuid4()
    user.created_at = now
    user.updated_at = now

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get("/auth/me")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(user.id)
    assert body["email"] == "alice@example.com"

    assert "password" not in body
    assert "hashed_password" not in body
