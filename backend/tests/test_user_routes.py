import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.routes.users import get_user_service
from app.main import app
from app.models.user import User
from app.services.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
)

client = TestClient(app)


def make_user(
    *,
    email: str = "alice@example.com",
    full_name: str = "Alice Johnson",
) -> User:
    now = datetime.now(UTC)

    user = User(
        email=email,
        full_name=full_name,
    )

    user.id = uuid.uuid4()
    user.is_active = True
    user.created_at = now
    user.updated_at = now

    return user


def test_create_user() -> None:
    service = MagicMock()
    user = make_user()

    service.create_user.return_value = user

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/users",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Johnson",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert response.json()["full_name"] == "Alice Johnson"


def test_create_user_with_existing_email() -> None:
    service = MagicMock()
    service.create_user.side_effect = UserAlreadyExistsError

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/users",
        json={
            "email": "alice@example.com",
            "full_name": "Alice Johnson",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {
        "detail": "User with this email already exists"
    }


def test_get_user() -> None:
    service = MagicMock()
    user = make_user()

    service.get_user.return_value = user

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.get(f"/users/{user.id}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)
    assert response.json()["email"] == user.email


def test_get_missing_user() -> None:
    service = MagicMock()
    user_id = uuid.uuid4()

    service.get_user.side_effect = UserNotFoundError

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.get(f"/users/{user_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_list_users() -> None:
    service = MagicMock()

    users = [
        make_user(
            email="alice@example.com",
            full_name="Alice Johnson",
        ),
        make_user(
            email="bob@example.com",
            full_name="Bob Smith",
        ),
    ]

    service.list_users.return_value = users

    app.dependency_overrides[get_user_service] = lambda: service

    response = client.get("/users")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["email"] == "alice@example.com"
    assert response.json()[1]["email"] == "bob@example.com"
