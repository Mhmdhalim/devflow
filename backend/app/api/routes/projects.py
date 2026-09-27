import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.membership import MembershipRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead
from app.services.project import (
    ProjectAlreadyExistsError,
    ProjectOrganizationNotFoundError,
    ProjectPermissionDeniedError,
    ProjectService,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/projects",
    tags=["projects"],
)


def get_project_service(
    db: Session = Depends(get_db),
) -> ProjectService:
    return ProjectService(
        project_repository=ProjectRepository(db),
        organization_repository=OrganizationRepository(db),
        membership_repository=MembershipRepository(db),
    )


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    organization_id: uuid.UUID,
    data: ProjectCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    try:
        project = service.create_project(
            data=data,
            organization_id=organization_id,
            user_id=current_user.id,
        )

    except ProjectOrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        ) from exc

    except ProjectPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create projects in this organization",
        ) from exc

    except ProjectAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this key already exists in this organization",
        ) from exc

    return ProjectRead.model_validate(project)
