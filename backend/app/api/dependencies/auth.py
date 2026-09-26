import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    auto_error=False,
)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        subject = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(subject)

    except (InvalidTokenError, ValueError) as exc:
        raise credentials_exception from exc

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise credentials_exception

    return user
