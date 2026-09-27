import uuid

from app.models.project import Project
from app.repositories.organization import OrganizationRepository
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectAlreadyExistsError(Exception):
    pass


class ProjectOrganizationNotFoundError(Exception):
    pass


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        self.project_repository = project_repository
        self.organization_repository = organization_repository

    def create_project(
        self,
        data: ProjectCreate,
        organization_id: uuid.UUID,
    ) -> Project:
        organization = self.organization_repository.get_by_id(organization_id)

        if organization is None:
            raise ProjectOrganizationNotFoundError

        existing_project = self.project_repository.get_by_key(
            organization_id,
            data.key,
        )

        if existing_project is not None:
            raise ProjectAlreadyExistsError

        return self.project_repository.create(
            data=data,
            organization_id=organization_id,
        )
