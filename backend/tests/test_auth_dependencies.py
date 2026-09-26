import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.core.security import ALGORITHM, create_access_token
from app.models.user import User


def test_get_current_user() -> None:
    db = MagicMock()

    user_id = uuid.uuid4()

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password="hashed-password",
        is_active=True,
    )

    db.get.return_value = user

    token = create_access_token(str(user_id))

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    result = get_current_user(
        credentials,
        db,
    )

    assert result is user

    db.get.assert_called_once_with(
        User,
        user_id,
    )


def test_get_current_user_without_token() -> None:
    db = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            None,
            db,
        )

    assert exc_info.value.status_code == 401


def test_get_current_user_with_invalid_token() -> None:
    db = MagicMock()

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="this-is-not-a-jwt",
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials,
            db,
        )

    assert exc_info.value.status_code == 401


def test_get_current_user_with_expired_token() -> None:
    db = MagicMock()
    settings = get_settings()

    user_id = uuid.uuid4()

    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials,
            db,
        )

    assert exc_info.value.status_code == 401


def test_get_current_user_when_user_missing() -> None:
    db = MagicMock()

    user_id = uuid.uuid4()

    db.get.return_value = None

    token = create_access_token(str(user_id))

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials,
            db,
        )

    assert exc_info.value.status_code == 401


def test_get_current_user_when_user_inactive() -> None:
    db = MagicMock()

    user_id = uuid.uuid4()

    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password="hashed-password",
        is_active=False,
    )

    db.get.return_value = user

    token = create_access_token(str(user_id))

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials,
            db,
        )

    assert exc_info.value.status_code == 401


def test_get_current_user_with_invalid_subject() -> None:
    db = MagicMock()

    token = create_access_token("not-a-uuid")

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            credentials,
            db,
        )

    assert exc_info.value.status_code == 401
