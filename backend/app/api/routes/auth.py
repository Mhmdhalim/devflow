from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService, InvalidCredentialsError

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    repository = UserRepository(db)
    return AuthService(repository)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        user = service.authenticate(
            str(data.email),
            data.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
    )
