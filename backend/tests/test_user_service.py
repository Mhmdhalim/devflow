import uuid
from unittest.mock import MagicMock

import pytest

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


def test_create_user() -> None:
    repository = MagicMock()
    service = UserService(repository)

    data = UserCreate(
        email="alice@example.com",
        full_name="Alice Johnson",
    )

    expected_user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
    )

    repository.get_by_email.return_value = None
    repository.create.return_value = expected_user

    result = service.create_user(data)

    assert result is expected_user
    repository.get_by_email.assert_called_once_with("alice@example.com")
    repository.create.assert_called_once_with(data)


def test_create_user_with_existing_email() -> None:
    repository = MagicMock()
    service = UserService(repository)

    data = UserCreate(
        email="alice@example.com",
        full_name="Alice Johnson",
    )

    repository.get_by_email.return_value = User(
        email="alice@example.com",
        full_name="Existing User",
    )

    with pytest.raises(UserAlreadyExistsError):
        service.create_user(data)

    repository.create.assert_not_called()


def test_get_user() -> None:
    repository = MagicMock()
    service = UserService(repository)

    user_id = uuid.uuid4()
    expected_user = User(
        email="bob@example.com",
        full_name="Bob Smith",
    )

    repository.get_by_id.return_value = expected_user

    result = service.get_user(user_id)

    assert result is expected_user
    repository.get_by_id.assert_called_once_with(user_id)


def test_get_missing_user() -> None:
    repository = MagicMock()
    service = UserService(repository)

    user_id = uuid.uuid4()
    repository.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        service.get_user(user_id)


def test_list_users() -> None:
    repository = MagicMock()
    service = UserService(repository)

    users = [
        User(
            email="alice@example.com",
            full_name="Alice Johnson",
        ),
        User(
            email="bob@example.com",
            full_name="Bob Smith",
        ),
    ]

    repository.list_all.return_value = users

    result = service.list_users()

    assert result == users
    repository.list_all.assert_called_once()
