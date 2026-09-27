import uuid
from unittest.mock import MagicMock

import pytest

from app.models.issue import Issue
from app.models.membership import Membership
from app.models.project import Project
from app.schemas.issue import (
    IssueCreate,
    IssueUpdate,
)
from app.services.issue import (
    IssueNotFoundError,
    IssuePermissionDeniedError,
    IssueProjectNotFoundError,
    IssueService,
)


def make_data() -> IssueCreate:
    return IssueCreate(
        title="Add authentication",
        description="Implement JWT",
        priority="high",
    )


def test_create_issue() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    reporter_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=reporter_id,
        organization_id=organization_id,
        role="member",
    )

    expected_issue = Issue(
        project_id=project_id,
        number=1,
        title="Add authentication",
        description="Implement JWT",
        status="todo",
        priority="high",
        reporter_id=reporter_id,
        assignee_id=None,
    )

    issue_repository.create_with_next_number.return_value = expected_issue

    data = make_data()

    result = service.create_issue(
        data=data,
        project_id=project_id,
        reporter_id=reporter_id,
    )

    assert result is expected_issue

    project_repository.get_by_id.assert_called_once_with(project_id)

    membership_repository.get_for_user_and_organization.assert_called_once_with(
        user_id=reporter_id,
        organization_id=organization_id,
    )

    issue_repository.create_with_next_number.assert_called_once_with(
        data=data,
        project_id=project_id,
        reporter_id=reporter_id,
    )


def test_create_issue_when_project_missing() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_id = uuid.uuid4()
    reporter_id = uuid.uuid4()

    project_repository.get_by_id.return_value = None

    with pytest.raises(IssueProjectNotFoundError):
        service.create_issue(
            data=make_data(),
            project_id=project_id,
            reporter_id=reporter_id,
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    issue_repository.create_with_next_number.assert_not_called()


def test_create_issue_when_user_is_not_member() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    reporter_id = uuid.uuid4()

    project_repository.get_by_id.return_value = Project(
        organization_id=organization_id,
        name="Backend",
        key="DEV",
        description=None,
    )

    membership_repository.get_for_user_and_organization.return_value = None

    with pytest.raises(IssuePermissionDeniedError):
        service.create_issue(
            data=make_data(),
            project_id=project_id,
            reporter_id=reporter_id,
        )

    issue_repository.create_with_next_number.assert_not_called()


def test_list_issues() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    expected_issues = [
        Issue(
            project_id=project_id,
            number=1,
            title="First",
            description=None,
            status="todo",
            priority="medium",
            reporter_id=user_id,
            assignee_id=None,
        ),
    ]

    issue_repository.list_for_project.return_value = expected_issues

    result = service.list_issues(
        project_id=project_id,
        user_id=user_id,
    )

    assert result == expected_issues

    issue_repository.list_for_project.assert_called_once_with(project_id)


def test_list_issues_when_user_is_not_member() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    with pytest.raises(IssuePermissionDeniedError):
        service.list_issues(
            project_id=project_id,
            user_id=user_id,
        )

    issue_repository.list_for_project.assert_not_called()


def test_list_issues_when_project_missing() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    project_repository.get_by_id.return_value = None

    with pytest.raises(IssueProjectNotFoundError):
        service.list_issues(
            project_id=project_id,
            user_id=user_id,
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    issue_repository.list_for_project.assert_not_called()


def test_get_issue() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    expected_issue = Issue(
        project_id=project_id,
        number=12,
        title="Fix login",
        description=None,
        status="todo",
        priority="high",
        reporter_id=user_id,
        assignee_id=None,
    )

    issue_repository.get_by_number.return_value = expected_issue

    result = service.get_issue(
        project_id=project_id,
        issue_number=12,
        user_id=user_id,
    )

    assert result is expected_issue

    issue_repository.get_by_number.assert_called_once_with(
        project_id=project_id,
        issue_number=12,
    )


def test_get_issue_when_issue_missing() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    with pytest.raises(IssueNotFoundError):
        service.get_issue(
            project_id=project_id,
            issue_number=99,
            user_id=user_id,
        )


def test_get_issue_when_user_is_not_member() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    with pytest.raises(IssuePermissionDeniedError):
        service.get_issue(
            project_id=project_id,
            issue_number=12,
            user_id=user_id,
        )

    issue_repository.get_by_number.assert_not_called()


def test_update_issue() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    issue = Issue(
        project_id=project_id,
        number=12,
        title="Old title",
        description=None,
        status="todo",
        priority="medium",
        reporter_id=user_id,
        assignee_id=None,
    )

    issue_repository.get_by_number.return_value = issue
    issue_repository.update.return_value = issue

    data = IssueUpdate(
        status="in_progress",
    )

    result = service.update_issue(
        data=data,
        project_id=project_id,
        issue_number=12,
        user_id=user_id,
    )

    assert result is issue

    issue_repository.update.assert_called_once_with(
        issue=issue,
        data=data,
    )


def test_update_issue_when_issue_missing() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    with pytest.raises(IssueNotFoundError):
        service.update_issue(
            data=IssueUpdate(priority="high"),
            project_id=project_id,
            issue_number=99,
            user_id=user_id,
        )

    issue_repository.update.assert_not_called()


def test_update_issue_when_user_is_not_member() -> None:
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = IssueService(
        issue_repository,
        project_repository,
        membership_repository,
    )

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

    with pytest.raises(IssuePermissionDeniedError):
        service.update_issue(
            data=IssueUpdate(priority="high"),
            project_id=project_id,
            issue_number=12,
            user_id=user_id,
        )

    issue_repository.get_by_number.assert_not_called()
    issue_repository.update.assert_not_called()
