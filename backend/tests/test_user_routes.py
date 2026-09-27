import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.routes.users import get_user_service
from app.main import app
from app.models.user import User
from app.services.user import UserAlreadyExistsError

client = TestClient(app)


def test_create_user() -> None:
    service = MagicMock()
    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password="not-used",
        is_active=True,
    )
    now = datetime.now(UTC)
    user.id = uuid.uuid4()
    user.created_at = now
    user.updated_at = now
    service.create_user.return_value = user

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/users",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Johnson",
            "password": "secure-password-123",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "Alice Johnson"
    assert "password" not in body
    assert "hashed_password" not in body


def test_create_user_with_existing_email() -> None:
    service = MagicMock()
    service.create_user.side_effect = UserAlreadyExistsError

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/users",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Johnson",
            "password": "secure-password-123",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_create_user_rejects_short_password() -> None:
    service = MagicMock()

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/users",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Johnson",
            "password": "short",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    service.create_user.assert_not_called()


def test_users_collection_does_not_allow_public_listing() -> None:
    response = client.get("/users")
    assert response.status_code == 405


def test_user_detail_endpoint_is_not_exposed() -> None:
    response = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_user_rejects_blank_full_name() -> None:
    service = MagicMock()
    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/users",
        json={
            "email": "blank-name@example.com",
            "full_name": "   ",
            "password": "secure-password-123",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    service.create_user.assert_not_called()
