import uuid
from unittest.mock import MagicMock

import pytest

from app.models.issue import Issue
from app.models.label import Label
from app.models.membership import Membership
from app.models.project import Project
from app.services.issue_label import (
    IssueLabelAlreadyAssignedError,
    IssueLabelIssueNotFoundError,
    IssueLabelLabelNotFoundError,
    IssueLabelLabelProjectMismatchError,
    IssueLabelNotAssignedError,
    IssueLabelPermissionDeniedError,
    IssueLabelProjectNotFoundError,
    IssueLabelService,
)


def make_service() -> tuple[
    IssueLabelService,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    label_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueLabelService(
        label_repository=label_repository,
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
    )

    return (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    )


def setup_valid_access(
    issue_repository: MagicMock,
    project_repository: MagicMock,
    membership_repository: MagicMock,
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    issue_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Issue:
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

    issue = Issue(
        project_id=project_id,
        number=12,
        title="Fix login",
        description=None,
        status="todo",
        priority="medium",
        reporter_id=user_id,
        assignee_id=None,
    )

    issue.id = issue_id

    issue_repository.get_by_number.return_value = issue

    return issue


def test_assign_label() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    label_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    label = Label(
        project_id=project_id,
        name="backend",
        color="#2563EB",
    )
    label.id = label_id

    label_repository.get_by_id.return_value = label
    label_repository.is_assigned_to_issue.return_value = False

    result = service.assign_label(
        project_id=project_id,
        issue_number=12,
        label_id=label_id,
        user_id=user_id,
    )

    assert result is label

    label_repository.assign_to_issue.assert_called_once_with(
        issue_id=issue_id,
        label_id=label_id,
    )


def test_assign_label_when_already_assigned() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    label_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    label = Label(
        project_id=project_id,
        name="backend",
        color=None,
    )
    label.id = label_id

    label_repository.get_by_id.return_value = label
    label_repository.is_assigned_to_issue.return_value = True

    with pytest.raises(IssueLabelAlreadyAssignedError):
        service.assign_label(
            project_id=project_id,
            issue_number=12,
            label_id=label_id,
            user_id=user_id,
        )

    label_repository.assign_to_issue.assert_not_called()


def test_assign_label_when_project_missing() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_repository.get_by_id.return_value = None

    with pytest.raises(IssueLabelProjectNotFoundError):
        service.assign_label(
            project_id=uuid.uuid4(),
            issue_number=12,
            label_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    issue_repository.get_by_number.assert_not_called()
    label_repository.get_by_id.assert_not_called()


def test_assign_label_when_user_is_not_member() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = None

    with pytest.raises(IssueLabelPermissionDeniedError):
        service.assign_label(
            project_id=project_id,
            issue_number=12,
            label_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )

    issue_repository.get_by_number.assert_not_called()
    label_repository.get_by_id.assert_not_called()


def test_assign_label_when_issue_missing() -> None:
    (
        service,
        label_repository,
        issue_repository,
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

    issue_repository.get_by_number.return_value = None

    with pytest.raises(IssueLabelIssueNotFoundError):
        service.assign_label(
            project_id=project_id,
            issue_number=99,
            label_id=uuid.uuid4(),
            user_id=user_id,
        )

    label_repository.get_by_id.assert_not_called()


def test_assign_label_when_label_missing() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    label_repository.get_by_id.return_value = None

    with pytest.raises(IssueLabelLabelNotFoundError):
        service.assign_label(
            project_id=project_id,
            issue_number=12,
            label_id=uuid.uuid4(),
            user_id=user_id,
        )

    label_repository.assign_to_issue.assert_not_called()


def test_assign_label_from_another_project() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    label_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    label = Label(
        project_id=uuid.uuid4(),
        name="backend",
        color=None,
    )
    label.id = label_id

    label_repository.get_by_id.return_value = label

    with pytest.raises(IssueLabelLabelProjectMismatchError):
        service.assign_label(
            project_id=project_id,
            issue_number=12,
            label_id=label_id,
            user_id=user_id,
        )

    label_repository.is_assigned_to_issue.assert_not_called()
    label_repository.assign_to_issue.assert_not_called()


def test_remove_label() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    label_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    label = Label(
        project_id=project_id,
        name="backend",
        color=None,
    )
    label.id = label_id

    label_repository.get_by_id.return_value = label
    label_repository.is_assigned_to_issue.return_value = True

    service.remove_label(
        project_id=project_id,
        issue_number=12,
        label_id=label_id,
        user_id=user_id,
    )

    label_repository.remove_from_issue.assert_called_once_with(
        issue_id=issue_id,
        label_id=label_id,
    )


def test_remove_label_when_not_assigned() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    label_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    label = Label(
        project_id=project_id,
        name="backend",
        color=None,
    )
    label.id = label_id

    label_repository.get_by_id.return_value = label
    label_repository.is_assigned_to_issue.return_value = False

    with pytest.raises(IssueLabelNotAssignedError):
        service.remove_label(
            project_id=project_id,
            issue_number=12,
            label_id=label_id,
            user_id=user_id,
        )

    label_repository.remove_from_issue.assert_not_called()


def test_list_labels() -> None:
    (
        service,
        label_repository,
        issue_repository,
        project_repository,
        membership_repository,
    ) = make_service()

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
    user_id = uuid.uuid4()

    setup_valid_access(
        issue_repository=issue_repository,
        project_repository=project_repository,
        membership_repository=membership_repository,
        project_id=project_id,
        organization_id=organization_id,
        issue_id=issue_id,
        user_id=user_id,
    )

    expected_labels = [
        Label(
            project_id=project_id,
            name="backend",
            color="#2563EB",
        ),
        Label(
            project_id=project_id,
            name="bug",
            color="#DC2626",
        ),
    ]

    label_repository.list_for_issue.return_value = expected_labels

    result = service.list_labels(
        project_id=project_id,
        issue_number=12,
        user_id=user_id,
    )

    assert result == expected_labels

    label_repository.list_for_issue.assert_called_once_with(issue_id)
