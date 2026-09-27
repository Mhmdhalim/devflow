import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_app_debug_defaults_to_false() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://user:pass@localhost:5432/test",
        secret_key="a" * 32,
        _env_file=None,
    )

    assert settings.app_debug is False


def test_database_url_normalizes_plain_postgresql_scheme() -> None:
    settings = Settings(
        database_url="postgresql://user:pass@db.example.com:5432/devflow",
        secret_key="a" * 32,
        _env_file=None,
    )

    assert (
        settings.database_url
        == "postgresql+psycopg://user:pass@db.example.com:5432/devflow"
    )


def test_secret_key_rejects_short_value() -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql+psycopg://user:pass@localhost:5432/test",
            secret_key="too-short",
            _env_file=None,
        )
