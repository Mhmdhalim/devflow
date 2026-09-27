import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.issue import IssueRepository
from app.repositories.label import LabelRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.label import LabelRead
from app.services.issue_label import (
    IssueLabelAlreadyAssignedError,
    IssueLabelIssueNotFoundError,
    IssueLabelLabelNotFoundError,
    IssueLabelLabelProjectMismatchError,
    IssueLabelNotAssignedError,
    IssueLabelPermissionDeniedError,
    IssueLabelProjectNotFoundError,
    IssueLabelService,
)

router = APIRouter(
    prefix="/projects/{project_id}/issues/{issue_number}/labels",
    tags=["issue-labels"],
)


def get_issue_label_service(
    db: Session = Depends(get_db),
) -> IssueLabelService:
    return IssueLabelService(
        label_repository=LabelRepository(db),
        issue_repository=IssueRepository(db),
        project_repository=ProjectRepository(db),
        membership_repository=MembershipRepository(db),
    )


@router.post(
    "/{label_id}",
    response_model=LabelRead,
    status_code=status.HTTP_201_CREATED,
)
def assign_label(
    project_id: uuid.UUID,
    issue_number: int,
    label_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: IssueLabelService = Depends(get_issue_label_service),
) -> LabelRead:
    try:
        label = service.assign_label(
            project_id=project_id,
            issue_number=issue_number,
            label_id=label_id,
            user_id=current_user.id,
        )

    except IssueLabelProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except IssueLabelPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    except IssueLabelIssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        ) from exc

    except (
        IssueLabelLabelNotFoundError,
        IssueLabelLabelProjectMismatchError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        ) from exc

    except IssueLabelAlreadyAssignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Label is already assigned to this issue",
        ) from exc

    return LabelRead.model_validate(label)


@router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_label(
    project_id: uuid.UUID,
    issue_number: int,
    label_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: IssueLabelService = Depends(get_issue_label_service),
) -> Response:
    try:
        service.remove_label(
            project_id=project_id,
            issue_number=issue_number,
            label_id=label_id,
            user_id=current_user.id,
        )

    except IssueLabelProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except IssueLabelPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    except IssueLabelIssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        ) from exc

    except (
        IssueLabelLabelNotFoundError,
        IssueLabelLabelProjectMismatchError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        ) from exc

    except IssueLabelNotAssignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Label is not assigned to this issue",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "",
    response_model=list[LabelRead],
)
def list_labels(
    project_id: uuid.UUID,
    issue_number: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: IssueLabelService = Depends(get_issue_label_service),
) -> list[LabelRead]:
    try:
        labels = service.list_labels(
            project_id=project_id,
            issue_number=issue_number,
            user_id=current_user.id,
        )

    except IssueLabelProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except IssueLabelPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    except IssueLabelIssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        ) from exc

    return [LabelRead.model_validate(label) for label in labels]
