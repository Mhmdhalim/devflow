import uuid

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, data: UserCreate) -> User:
        existing_user = self.repository.get_by_email(str(data.email))

        if existing_user is not None:
            raise UserAlreadyExistsError

        return self.repository.create(data)

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError

        return user

    def list_users(self) -> list[User]:
        return self.repository.list_all()
