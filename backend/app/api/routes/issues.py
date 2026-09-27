import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.issue import IssueRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.issue import IssueCreate, IssueRead
from app.services.issue import (
    IssueNotFoundError,
    IssuePermissionDeniedError,
    IssueProjectNotFoundError,
    IssueService,
)

router = APIRouter(
    prefix="/projects/{project_id}/issues",
    tags=["issues"],
)


def get_issue_service(
    db: Session = Depends(get_db),
) -> IssueService:
    return IssueService(
        issue_repository=IssueRepository(db),
        project_repository=ProjectRepository(db),
        membership_repository=MembershipRepository(db),
    )


@router.post(
    "",
    response_model=IssueRead,
    status_code=status.HTTP_201_CREATED,
)
def create_issue(
    project_id: uuid.UUID,
    data: IssueCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: IssueService = Depends(get_issue_service),
) -> IssueRead:
    try:
        issue = service.create_issue(
            data=data,
            project_id=project_id,
            reporter_id=current_user.id,
        )

    except IssueProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except IssuePermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    return IssueRead.model_validate(issue)


@router.get(
    "",
    response_model=list[IssueRead],
)
def list_issues(
    project_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: IssueService = Depends(get_issue_service),
) -> list[IssueRead]:
    try:
        issues = service.list_issues(
            project_id=project_id,
            user_id=current_user.id,
        )

    except IssueProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except IssuePermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    return [IssueRead.model_validate(issue) for issue in issues]


@router.get(
    "/{issue_number}",
    response_model=IssueRead,
)
def get_issue(
    project_id: uuid.UUID,
    issue_number: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: IssueService = Depends(get_issue_service),
) -> IssueRead:
    try:
        issue = service.get_issue(
            project_id=project_id,
            issue_number=issue_number,
            user_id=current_user.id,
        )

    except IssueProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except IssuePermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        ) from exc

    return IssueRead.model_validate(issue)
