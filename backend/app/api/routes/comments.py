import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.issue import IssueRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment import (
    CommentIssueNotFoundError,
    CommentPermissionDeniedError,
    CommentProjectNotFoundError,
    CommentService,
)

router = APIRouter(
    prefix="/projects/{project_id}/issues/{issue_number}/comments",
    tags=["comments"],
)


def get_comment_service(
    db: Session = Depends(get_db),
) -> CommentService:
    return CommentService(
        comment_repository=CommentRepository(db),
        issue_repository=IssueRepository(db),
        project_repository=ProjectRepository(db),
        membership_repository=MembershipRepository(db),
    )


@router.post(
    "",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    project_id: uuid.UUID,
    issue_number: int,
    data: CommentCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    try:
        comment = service.create_comment(
            data=data,
            project_id=project_id,
            issue_number=issue_number,
            author_id=current_user.id,
        )

    except CommentProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    except CommentPermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        ) from exc

    except CommentIssueNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        ) from exc

    return CommentRead.model_validate(comment)
