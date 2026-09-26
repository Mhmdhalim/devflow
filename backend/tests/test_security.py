from app.core.security import hash_password, verify_password


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
