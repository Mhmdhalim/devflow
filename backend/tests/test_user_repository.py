import uuid
from unittest.mock import MagicMock

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


def test_create_user() -> None:
    db = MagicMock()
    repository = UserRepository(db)

    data = UserCreate(
        email="alice@example.com",
        full_name="Alice Johnson",
    )

    user = repository.create(data)

    assert user.email == "alice@example.com"
    assert user.full_name == "Alice Johnson"

    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_get_by_id() -> None:
    db = MagicMock()
    repository = UserRepository(db)

    user_id = uuid.uuid4()

    expected_user = User(
        email="bob@example.com",
        full_name="Bob Smith",
    )

    db.get.return_value = expected_user

    result = repository.get_by_id(user_id)

    assert result is expected_user
    db.get.assert_called_once_with(User, user_id)


def test_get_by_email() -> None:
    db = MagicMock()
    repository = UserRepository(db)

    expected_user = User(
        email="charlie@example.com",
        full_name="Charlie Brown",
    )

    db.scalars.return_value.first.return_value = expected_user

    result = repository.get_by_email("charlie@example.com")

    assert result is expected_user
    db.scalars.assert_called_once()


def test_list_all_users() -> None:
    db = MagicMock()
    repository = UserRepository(db)

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

    db.scalars.return_value.all.return_value = users

    result = repository.list_all()

    assert result == users
    db.scalars.assert_called_once()
