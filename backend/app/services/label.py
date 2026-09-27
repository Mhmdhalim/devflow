import uuid

from app.models.label import Label
from app.models.membership import Membership
from app.repositories.label import LabelRepository
from app.repositories.membership import MembershipRepository
from app.repositories.project import ProjectRepository
from app.schemas.label import LabelCreate


class LabelProjectNotFoundError(Exception):
    pass


class LabelPermissionDeniedError(Exception):
    pass


class LabelAlreadyExistsError(Exception):
    pass


class LabelService:
    def __init__(
        self,
        label_repository: LabelRepository,
        project_repository: ProjectRepository,
        membership_repository: MembershipRepository,
    ) -> None:
        self.label_repository = label_repository
        self.project_repository = project_repository
        self.membership_repository = membership_repository

    def _get_membership_for_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Membership:
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise LabelProjectNotFoundError

        membership = self.membership_repository.get_for_user_and_organization(
            user_id=user_id,
            organization_id=project.organization_id,
        )

        if membership is None:
            raise LabelPermissionDeniedError

        return membership

    def create_label(
        self,
        data: LabelCreate,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Label:
        membership = self._get_membership_for_project(
            project_id=project_id,
            user_id=user_id,
        )

        if membership.role not in {
            "owner",
            "admin",
        }:
            raise LabelPermissionDeniedError

        existing_label = self.label_repository.get_by_name(
            project_id=project_id,
            name=data.name,
        )

        if existing_label is not None:
            raise LabelAlreadyExistsError

        return self.label_repository.create(
            data=data,
            project_id=project_id,
        )

    def list_labels(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Label]:
        self._get_membership_for_project(
            project_id=project_id,
            user_id=user_id,
        )

        return self.label_repository.list_for_project(project_id)
