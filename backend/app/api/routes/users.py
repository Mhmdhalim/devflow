import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserRead
from app.services.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        user = service.create_user(data)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from exc

    return UserRead.model_validate(user)


@router.get(
    "",
    response_model=list[UserRead],
)
def list_users(
    service: UserService = Depends(get_user_service),
) -> list[UserRead]:
    users = service.list_users()
    return [UserRead.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        user = service.get_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc

    return UserRead.model_validate(user)