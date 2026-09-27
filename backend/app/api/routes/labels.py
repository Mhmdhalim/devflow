import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.label import LabelRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.label import LabelCreate, LabelRead
from app.services.label import (
    LabelAlreadyExistsError,
    LabelPermissionDeniedError,
    LabelProjectNotFoundError,
    LabelService,
)

router = APIRouter(
    prefix="/projects/{project_id}/labels",
    tags=["labels"],
)


def get_label_service(
    db: Session = Depends(get_db),
) -> LabelService:
    return LabelService(
        label_repository=LabelRepository(db),
        project_repository=ProjectRepository(db),
        membership_repository=MembershipRepository(db),
    )


@router.post(
    "",
    response_model=LabelRead,
    status_code=status.HTTP_201_CREATED,
)
def create_label(
    project_id: uuid.UUID,
    data: LabelCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: LabelService = Depends(get_label_service),
) -> LabelRead:
    try:
        label = service.create_label(
            data=data,
            project_id=project_id,
            user_id=current_user.id,
        )

    except LabelProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except LabelPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create labels in this project",
        ) from exc

    except LabelAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Label with this name already exists in this project",
        ) from exc

    return LabelRead.model_validate(label)


@router.get(
    "",
    response_model=list[LabelRead],
)
def list_labels(
    project_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: LabelService = Depends(get_label_service),
) -> list[LabelRead]:
    try:
        labels = service.list_labels(
            project_id=project_id,
            user_id=current_user.id,
        )

    except LabelProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except LabelPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    return [LabelRead.model_validate(label) for label in labels]
