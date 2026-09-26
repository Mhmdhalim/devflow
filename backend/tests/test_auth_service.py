from unittest.mock import MagicMock

import pytest

from app.core.security import hash_password
from app.models.user import User
from app.services.auth import (
    AuthService,
    InvalidCredentialsError,
)


def test_authenticate_user() -> None:
    repository = MagicMock()
    service = AuthService(repository)

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password=hash_password("secure-password-123"),
        is_active=True,
    )

    repository.get_by_email.return_value = user

    result = service.authenticate(
        "alice@example.com",
        "secure-password-123",
    )

    assert result is user

    repository.get_by_email.assert_called_once_with("alice@example.com")


def test_authenticate_with_wrong_password() -> None:
    repository = MagicMock()
    service = AuthService(repository)

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password=hash_password("correct-password"),
        is_active=True,
    )

    repository.get_by_email.return_value = user

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(
            "alice@example.com",
            "wrong-password",
        )


def test_authenticate_unknown_user() -> None:
    repository = MagicMock()
    service = AuthService(repository)

    repository.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(
            "missing@example.com",
            "some-password",
        )


def test_authenticate_inactive_user() -> None:
    repository = MagicMock()
    service = AuthService(repository)

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password=hash_password("secure-password-123"),
        is_active=False,
    )

    repository.get_by_email.return_value = user

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(
            "alice@example.com",
            "secure-password-123",
        )
