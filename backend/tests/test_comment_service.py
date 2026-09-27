import uuid
from unittest.mock import MagicMock

import pytest

from app.models.comment import Comment
from app.models.issue import Issue
from app.models.membership import Membership
from app.models.project import Project
from app.schemas.comment import CommentCreate
from app.services.comment import (
    CommentIssueNotFoundError,
    CommentPermissionDeniedError,
    CommentProjectNotFoundError,
    CommentService,
)


def test_create_comment() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
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
        title="Fix login",
        description=None,
        status="todo",
        priority="medium",
        reporter_id=user_id,
        assignee_id=None,
    )
    issue.id = issue_id

    issue_repository.get_by_number.return_value = issue

    expected_comment = Comment(
        issue_id=issue_id,
        author_id=user_id,
        body="I am working on this.",
    )

    comment_repository.create.return_value = expected_comment

    data = CommentCreate(body="I am working on this.")

    result = service.create_comment(
        data=data,
        project_id=project_id,
        issue_number=12,
        author_id=user_id,
    )

    assert result is expected_comment

    comment_repository.create.assert_called_once_with(
        data=data,
        issue_id=issue_id,
        author_id=user_id,
    )


def test_create_comment_when_project_missing() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_repository.get_by_id.return_value = None

    with pytest.raises(CommentProjectNotFoundError):
        service.create_comment(
            data=CommentCreate(body="Hello"),
            project_id=uuid.uuid4(),
            issue_number=12,
            author_id=uuid.uuid4(),
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    issue_repository.get_by_number.assert_not_called()
    comment_repository.create.assert_not_called()


def test_create_comment_when_user_is_not_member() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
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

    with pytest.raises(CommentPermissionDeniedError):
        service.create_comment(
            data=CommentCreate(body="Hello"),
            project_id=project_id,
            issue_number=12,
            author_id=user_id,
        )

    issue_repository.get_by_number.assert_not_called()
    comment_repository.create.assert_not_called()


def test_create_comment_when_issue_missing() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
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

    with pytest.raises(CommentIssueNotFoundError):
        service.create_comment(
            data=CommentCreate(body="Hello"),
            project_id=project_id,
            issue_number=99,
            author_id=user_id,
        )

    comment_repository.create.assert_not_called()


def test_list_comments() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    issue_id = uuid.uuid4()
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
        title="Fix login",
        description=None,
        status="todo",
        priority="medium",
        reporter_id=user_id,
        assignee_id=None,
    )
    issue.id = issue_id

    issue_repository.get_by_number.return_value = issue

    expected_comments = [
        Comment(
            issue_id=issue_id,
            author_id=user_id,
            body="First",
        ),
        Comment(
            issue_id=issue_id,
            author_id=user_id,
            body="Second",
        ),
    ]

    comment_repository.list_for_issue.return_value = expected_comments

    result = service.list_comments(
        project_id=project_id,
        issue_number=12,
        user_id=user_id,
    )

    assert result == expected_comments

    comment_repository.list_for_issue.assert_called_once_with(issue_id)


def test_list_comments_when_user_is_not_member() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
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

    with pytest.raises(CommentPermissionDeniedError):
        service.list_comments(
            project_id=project_id,
            issue_number=12,
            user_id=user_id,
        )

    issue_repository.get_by_number.assert_not_called()
    comment_repository.list_for_issue.assert_not_called()


def test_list_comments_when_issue_missing() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
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

    with pytest.raises(CommentIssueNotFoundError):
        service.list_comments(
            project_id=project_id,
            issue_number=99,
            user_id=user_id,
        )

    comment_repository.list_for_issue.assert_not_called()


def test_list_comments_when_project_missing() -> None:
    comment_repository = MagicMock()
    issue_repository = MagicMock()
    project_repository = MagicMock()
    membership_repository = MagicMock()

    service = CommentService(
        comment_repository,
        issue_repository,
        project_repository,
        membership_repository,
    )

    project_repository.get_by_id.return_value = None

    with pytest.raises(CommentProjectNotFoundError):
        service.list_comments(
            project_id=uuid.uuid4(),
            issue_number=12,
            user_id=uuid.uuid4(),
        )

    membership_repository.get_for_user_and_organization.assert_not_called()
    issue_repository.get_by_number.assert_not_called()
    comment_repository.list_for_issue.assert_not_called()
