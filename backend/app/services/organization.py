import uuid

from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate


class OrganizationAlreadyExistsError(Exception):
    pass


class OrganizationService:
    def __init__(
        self,
        repository: OrganizationRepository,
    ) -> None:
        self.repository = repository

    def create_organization(
        self,
        data: OrganizationCreate,
        owner_id: uuid.UUID,
    ) -> Organization:
        existing_organization = self.repository.get_by_slug(data.slug)

        if existing_organization is not None:
            raise OrganizationAlreadyExistsError

        return self.repository.create_with_membership(
            data=data,
            user_id=owner_id,
            role="owner",
        )

    def list_user_organizations(
        self,
        user_id: uuid.UUID,
    ) -> list[tuple[Organization, str]]:
        return self.repository.list_for_user(user_id)
