import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_by_key(
        self,
        organization_id: uuid.UUID,
        key: str,
    ) -> Project | None:
        statement = select(Project).where(
            Project.organization_id == organization_id,
            Project.key == key,
        )

        return self.db.scalars(statement).first()

    def create(
        self,
        data: ProjectCreate,
        organization_id: uuid.UUID,
    ) -> Project:
        project = Project(
            organization_id=organization_id,
            name=data.name,
            key=data.key,
            description=data.description,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
    ) -> list[Project]:
        statement = (
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.created_at)
        )
        return list(self.db.scalars(statement).all())
