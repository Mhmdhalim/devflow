import uuid

from app.models.comment import Comment
from app.models.issue import Issue
from app.repositories.comment import CommentRepository
from app.repositories.issue import IssueRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.comment import CommentCreate


class CommentProjectNotFoundError(Exception):
    pass


class CommentPermissionDeniedError(Exception):
    pass


class CommentIssueNotFoundError(Exception):
    pass


class CommentService:
    def __init__(
        self,
        comment_repository: CommentRepository,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        membership_repository: MembershipRepository,
    ) -> None:
        self.comment_repository = comment_repository
        self.issue_repository = issue_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _get_issue_for_member(
        self,
        project_id: uuid.UUID,
        issue_number: int,
        user_id: uuid.UUID,
    ) -> Issue:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise CommentProjectNotFoundError

        membership = self.membership_repository.get_for_user_and_organization(
            user_id=user_id,
            organization_id=project.organization_id,
        )

        if membership is None:
            raise CommentPermissionDeniedError

        issue = self.issue_repository.get_by_number(
            project_id=project_id,
            issue_number=issue_number,
        )

        if issue is None:
            raise CommentIssueNotFoundError

        return issue

    def create_comment(
        self,
        data: CommentCreate,
        project_id: uuid.UUID,
        issue_number: int,
        author_id: uuid.UUID,
    ) -> Comment:
        issue = self._get_issue_for_member(
            project_id=project_id,
            issue_number=issue_number,
            user_id=author_id,
        )

        return self.comment_repository.create(
            data=data,
            issue_id=issue.id,
            author_id=author_id,
        )

    def list_comments(
        self,
        project_id: uuid.UUID,
        issue_number: int,
        user_id: uuid.UUID,
    ) -> list[Comment]:
        issue = self._get_issue_for_member(
            project_id=project_id,
            issue_number=issue_number,
            user_id=user_id,
        )

        return self.comment_repository.list_for_issue(issue.id)
