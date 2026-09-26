import jwt

from app.core.config import get_settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password() -> None:
    password = "secure-password-123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password() -> None:
    password = "secure-password-123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_wrong_password() -> None:
    hashed = hash_password("correct-password")

    assert (
        verify_password(
            "wrong-password",
            hashed,
        )
        is False
    )


def test_create_access_token() -> None:
    settings = get_settings()

    token = create_access_token("user-123")

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "user-123"
    assert "exp" in payload


def test_decode_access_token() -> None:
    token = create_access_token("user-123")

    subject = decode_access_token(token)

    assert subject == "user-123"
