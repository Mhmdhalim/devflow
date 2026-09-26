from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.services.organization import (
    OrganizationAlreadyExistsError,
    OrganizationService,
)

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
)


def get_organization_service(
    db: Session = Depends(get_db),
) -> OrganizationService:
    repository = OrganizationRepository(db)
    return OrganizationService(repository)


@router.post(
    "",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    data: OrganizationCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    try:
        organization = service.create_organization(
            data=data,
            owner_id=current_user.id,
        )

    except OrganizationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization with this slug already exists",
        ) from exc

    return OrganizationRead.model_validate(organization)
