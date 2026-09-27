import uuid
from unittest.mock import MagicMock

import pytest

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.services.project import (
    ProjectAlreadyExistsError,
    ProjectOrganizationNotFoundError,
    ProjectPermissionDeniedError,
    ProjectService,
)


def make_data() -> ProjectCreate:
    return ProjectCreate(
        name="DevFlow Backend",
        key="DEV",
        description="Backend project",
    )


def test_create_project() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    data = make_data()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="owner",
    )

    project_repository.get_by_key.return_value = None

    expected_project = Project(
        organization_id=organization_id,
        name=data.name,
        key=data.key,
        description=data.description,
    )

    project_repository.create.return_value = expected_project

    result = service.create_project(
        data,
        organization_id,
        user_id,
    )

    assert result is expected_project

    organization_repository.get_by_id.assert_called_once_with(organization_id)

    membership_repository.get_for_user_and_organization.assert_called_once_with(
        user_id=user_id,
        organization_id=organization_id,
    )

    project_repository.get_by_key.assert_called_once_with(
        organization_id,
        "DEV",
    )

    project_repository.create.assert_called_once_with(
        data=data,
        organization_id=organization_id,
    )


def test_create_project_when_organization_missing() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = None

    with pytest.raises(ProjectOrganizationNotFoundError):
        service.create_project(
            make_data(),
            organization_id,
            user_id,
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    project_repository.get_by_key.assert_not_called()
    project_repository.create.assert_not_called()


def test_create_project_with_existing_key() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    data = make_data()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="owner",
    )

    project_repository.get_by_key.return_value = Project(
        organization_id=organization_id,
        name="Existing",
        key="DEV",
        description=None,
    )

    with pytest.raises(ProjectAlreadyExistsError):
        service.create_project(
            data,
            organization_id,
            user_id,
        )

    project_repository.create.assert_not_called()


def test_create_project_when_user_is_not_member() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = None

    with pytest.raises(ProjectPermissionDeniedError):
        service.create_project(
            make_data(),
            organization_id,
            user_id,
        )

    project_repository.get_by_key.assert_not_called()
    project_repository.create.assert_not_called()


def test_create_project_when_user_is_regular_member() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="member",
    )

    with pytest.raises(ProjectPermissionDeniedError):
        service.create_project(
            make_data(),
            organization_id,
            user_id,
        )

    project_repository.get_by_key.assert_not_called()
    project_repository.create.assert_not_called()


def test_create_project_when_user_is_admin() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    data = make_data()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="admin",
    )

    project_repository.get_by_key.return_value = None

    expected_project = Project(
        organization_id=organization_id,
        name=data.name,
        key=data.key,
        description=data.description,
    )

    project_repository.create.return_value = expected_project

    result = service.create_project(
        data,
        organization_id,
        user_id,
    )

    assert result is expected_project

    project_repository.create.assert_called_once_with(
        data=data,
        organization_id=organization_id,
    )


def test_list_projects_when_user_is_member() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="member",
    )

    expected_projects = [
        Project(
            organization_id=organization_id,
            name="Backend",
            key="BACK",
            description=None,
        )
    ]

    project_repository.list_for_organization.return_value = expected_projects

    result = service.list_projects(
        organization_id,
        user_id,
    )

    assert result == expected_projects

    membership_repository.get_for_user_and_organization.assert_called_once_with(
        user_id=user_id,
        organization_id=organization_id,
    )

    project_repository.list_for_organization.assert_called_once_with(organization_id)


def test_list_projects_when_organization_missing() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = None

    with pytest.raises(ProjectOrganizationNotFoundError):
        service.list_projects(
            organization_id,
            user_id,
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    project_repository.list_for_organization.assert_not_called()


def test_list_projects_when_user_is_not_member() -> None:
    project_repository = MagicMock()
    organization_repository = MagicMock()
    membership_repository = MagicMock()

    service = ProjectService(
        project_repository,
        organization_repository,
        membership_repository,
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = Organization(
        name="DevFlow",
        slug="devflow",
    )

    membership_repository.get_for_user_and_organization.return_value = None

    with pytest.raises(ProjectPermissionDeniedError):
        service.list_projects(
            organization_id,
            user_id,
        )

    project_repository.list_for_organization.assert_not_called()
