import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.project import Project
from app.schemas.issue import IssueCreate


class IssueRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create_with_next_number(
        self,
        data: IssueCreate,
        project_id: uuid.UUID,
        reporter_id: uuid.UUID,
    ) -> Issue:
        project_statement = (
            select(Project).where(Project.id == project_id).with_for_update()
        )

        self.db.scalars(project_statement).one()

        max_number_statement = select(func.max(Issue.number)).where(
            Issue.project_id == project_id
        )

        max_number = self.db.scalar(max_number_statement)

        next_number = 1 if max_number is None else max_number + 1

        issue = Issue(
            project_id=project_id,
            number=next_number,
            title=data.title,
            description=data.description,
            status="todo",
            priority=data.priority,
            reporter_id=reporter_id,
            assignee_id=data.assignee_id,
        )

        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)

        return issue
