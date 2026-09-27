import uuid
from unittest.mock import MagicMock

import pytest

from app.models.label import Label
from app.models.membership import Membership
from app.models.project import Project
from app.schemas.label import LabelCreate
from app.services.label import (
    LabelAlreadyExistsError,
    LabelPermissionDeniedError,
    LabelProjectNotFoundError,
    LabelService,
)


def make_service() -> tuple[
    LabelService,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    label_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = LabelService(
        label_repository,
        project_repository,
        membership_repository,
    )

    return (
        service,
        label_repository,
        project_repository,
        membership_repository,
    )


def test_create_label() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="owner",
    )

    label_repository.get_by_name.return_value = None

    data = LabelCreate(
        name="backend",
        color="#2563EB",
    )

    expected_label = Label(
        project_id=project_id,
        name=data.name,
        color=data.color,
    )

    label_repository.create.return_value = expected_label

    result = service.create_label(
        data=data,
        project_id=project_id,
        user_id=user_id,
    )

    assert result is expected_label

    label_repository.create.assert_called_once_with(
        data=data,
        project_id=project_id,
    )


def test_create_label_when_user_is_admin() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="admin",
    )

    label_repository.get_by_name.return_value = None

    data = LabelCreate(
        name="backend",
        color="#2563EB",
    )

    expected_label = Label(
        project_id=project_id,
        name=data.name,
        color=data.color,
    )

    label_repository.create.return_value = expected_label

    result = service.create_label(
        data=data,
        project_id=project_id,
        user_id=user_id,
    )

    assert result is expected_label
    label_repository.create.assert_called_once_with(
        data=data,
        project_id=project_id,
    )


def test_create_label_when_name_exists() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="owner",
    )

    label_repository.get_by_name.return_value = Label(
        project_id=project_id,
        name="backend",
        color=None,
    )

    with pytest.raises(LabelAlreadyExistsError):
        service.create_label(
            data=LabelCreate(
                name="backend",
            ),
            project_id=project_id,
            user_id=user_id,
        )

    label_repository.create.assert_not_called()


def test_create_label_when_user_is_regular_member() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="member",
    )

    with pytest.raises(LabelPermissionDeniedError):
        service.create_label(
            data=LabelCreate(
                name="backend",
            ),
            project_id=project_id,
            user_id=user_id,
        )

    label_repository.get_by_name.assert_not_called()
    label_repository.create.assert_not_called()


def test_create_label_when_project_missing() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_repository.get_by_id.return_value = None

    with pytest.raises(LabelProjectNotFoundError):
        service.create_label(
            data=LabelCreate(
                name="backend",
            ),
            project_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    label_repository.create.assert_not_called()


def test_list_labels_when_user_is_member() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="member",
    )

    expected_labels = [
        Label(
            project_id=project_id,
            name="backend",
            color="#2563EB",
        )
    ]

    label_repository.list_for_project.return_value = expected_labels

    result = service.list_labels(
        project_id=project_id,
        user_id=user_id,
    )

    assert result == expected_labels

    label_repository.list_for_project.assert_called_once_with(project_id)


def test_list_labels_when_user_is_not_member() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = None

    with pytest.raises(LabelPermissionDeniedError):
        service.list_labels(
            project_id=project_id,
            user_id=user_id,
        )

    label_repository.list_for_project.assert_not_called()


def test_list_labels_when_project_missing() -> None:
    (
        service,
        label_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_repository.get_by_id.return_value = None

    with pytest.raises(LabelProjectNotFoundError):
        service.list_labels(
            project_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    label_repository.list_for_project.assert_not_called()
