import uuid

from app.models.issue import Issue
from app.models.project import Project
from app.repositories.issue import IssueRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.issue import IssueCreate


class IssueProjectNotFoundError(Exception):
    pass


class IssuePermissionDeniedError(Exception):
    pass


class IssueService:
    def __init__(
        self,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        membership_repository: MembershipRepository,
    ) -> None:
        self.issue_repository = issue_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _get_project_for_member(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Project:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise IssueProjectNotFoundError

        membership = self.membership_repository.get_for_user_and_organization(
            user_id=user_id,
            organization_id=project.organization_id,
        )

        if membership is None:
            raise IssuePermissionDeniedError

        return project

    def create_issue(
        self,
        data: IssueCreate,
        project_id: uuid.UUID,
        reporter_id: uuid.UUID,
    ) -> Issue:
        self._get_project_for_member(
            project_id=project_id,
            user_id=reporter_id,
        )

        return self.issue_repository.create_with_next_number(
            data=data,
            project_id=project_id,
            reporter_id=reporter_id,
        )

    def list_issues(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Issue]:
        self._get_project_for_member(
            project_id=project_id,
            user_id=user_id,
        )

        return self.issue_repository.list_for_project(project_id)
