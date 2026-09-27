import uuid

from app.models.issue import Issue
from app.repositories.issue import IssueRepository
from app.repositories.project import ProjectRepository
from app.schemas.issue import IssueCreate


class IssueProjectNotFoundError(Exception):
    pass


class IssueService:
    def __init__(
        self,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self.issue_repository = issue_repository
        self.project_repository = project_repository

    def create_issue(
        self,
        data: IssueCreate,
        project_id: uuid.UUID,
        reporter_id: uuid.UUID,
    ) -> Issue:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise IssueProjectNotFoundError

        return self.issue_repository.create_with_next_number(
            data=data,
            project_id=project_id,
            reporter_id=reporter_id,
        )
