from app.core.security import DUMMY_HASH, verify_password
from app.models.user import User
from app.repositories.user import UserRepository


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User:
        user = self.repository.get_by_email(email)

        if user is None:
            verify_password(password, DUMMY_HASH)
            raise InvalidCredentialsError

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError

        if not user.is_active:
            raise InvalidCredentialsError

        return user
