import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.issues import get_issue_service
from app.main import app
from app.models.issue import Issue
from app.models.user import User
from app.services.issue import (
    IssueAssigneeNotMemberError,
    IssueNotFoundError,
    IssuePermissionDeniedError,
    IssueProjectNotFoundError,
)

client = TestClient(app)


def make_user() -> User:
    user = User(
        email="alice@example.com",
        full_name="Alice",
        hashed_password="not-used",
        is_active=True,
    )

    user.id = uuid.uuid4()

    return user


def make_issue(
    project_id: uuid.UUID,
    reporter_id: uuid.UUID,
) -> Issue:
    now = datetime.now(UTC)

    issue = Issue(
        project_id=project_id,
        number=1,
        title="Fix login",
        description="JWT issue",
        status="todo",
        priority="high",
        reporter_id=reporter_id,
        assignee_id=None,
    )

    issue.id = uuid.uuid4()
    issue.created_at = now
    issue.updated_at = now

    return issue


def test_create_issue() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    issue = make_issue(
        project_id,
        user.id,
    )

    service.create_issue.return_value = issue

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Fix login",
            "description": "JWT issue",
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["project_id"] == str(project_id)
    assert body["number"] == 1
    assert body["title"] == "Fix login"
    assert body["status"] == "todo"
    assert body["priority"] == "high"
    assert body["reporter_id"] == str(user.id)

    service.create_issue.assert_called_once()

    call = service.create_issue.call_args

    assert call.kwargs["project_id"] == (project_id)

    assert call.kwargs["reporter_id"] == (user.id)

    assert call.kwargs["data"].title == ("Fix login")


def test_create_issue_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Fix login",
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401

    service.create_issue.assert_not_called()


def test_create_issue_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_issue.side_effect = IssuePermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Fix login",
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_create_issue_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_issue.side_effect = IssueProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Fix login",
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_list_issues() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    first_issue = make_issue(
        project_id,
        user.id,
    )

    second_issue = make_issue(
        project_id,
        user.id,
    )
    second_issue.number = 2
    second_issue.title = "Second issue"

    service.list_issues.return_value = [
        first_issue,
        second_issue,
    ]

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["number"] == 1
    assert body[1]["number"] == 2

    service.list_issues.assert_called_once_with(
        project_id=project_id,
        user_id=user.id,
    )


def test_list_issues_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.list_issues.assert_not_called()


def test_list_issues_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.list_issues.side_effect = IssuePermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues")

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_list_issues_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.list_issues.side_effect = IssueProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues")

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_get_issue() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    issue = make_issue(
        project_id,
        user.id,
    )
    issue.number = 12

    service.get_issue.return_value = issue

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["number"] == 12
    assert body["project_id"] == str(project_id)

    service.get_issue.assert_called_once_with(
        project_id=project_id,
        issue_number=12,
        user_id=user.id,
    )


def test_get_issue_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.get_issue.assert_not_called()


def test_get_issue_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.get_issue.side_effect = IssuePermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12")

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_get_issue_when_issue_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.get_issue.side_effect = IssueNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/99")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == ("Issue not found")


def test_get_issue_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.get_issue.side_effect = IssueProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == ("Project not found")


def test_update_issue() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    issue = make_issue(
        project_id,
        user.id,
    )
    issue.number = 12
    issue.status = "in_progress"
    issue.priority = "high"

    service.update_issue.return_value = issue

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.patch(
        f"/projects/{project_id}/issues/12",
        json={
            "status": "in_progress",
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["number"] == 12
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"

    call = service.update_issue.call_args

    assert call.kwargs["project_id"] == project_id
    assert call.kwargs["issue_number"] == 12
    assert call.kwargs["user_id"] == user.id
    assert call.kwargs["data"].status == ("in_progress")


def test_update_issue_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.patch(
        f"/projects/{project_id}/issues/12",
        json={
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.update_issue.assert_not_called()


def test_update_issue_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.update_issue.side_effect = IssuePermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.patch(
        f"/projects/{project_id}/issues/12",
        json={
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_update_issue_when_issue_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.update_issue.side_effect = IssueNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.patch(
        f"/projects/{project_id}/issues/99",
        json={
            "priority": "high",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == ("Issue not found")


def test_update_issue_rejects_null_title() -> None:
    user = make_user()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.patch(
        f"/projects/{project_id}/issues/12",
        json={
            "title": None,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_list_issues_with_label() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    issue = make_issue(
        project_id,
        user.id,
    )

    service.list_issues.return_value = [issue]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues?label_id={label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["project_id"] == str(project_id)

    service.list_issues.assert_called_once_with(
        project_id=project_id,
        user_id=user.id,
        label_id=label_id,
    )


def test_list_issues_rejects_invalid_label_id() -> None:
    user = make_user()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get(f"/projects/{project_id}/issues?label_id=not-a-uuid")

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_create_issue_rejects_non_member_assignee() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_issue.side_effect = IssueAssigneeNotMemberError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Assign work",
            "assignee_id": str(uuid.uuid4()),
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Assignee must be a member of the project organization"
    )


def test_update_issue_rejects_non_member_assignee() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.update_issue.side_effect = IssueAssigneeNotMemberError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_service] = lambda: service

    response = client.patch(
        f"/projects/{project_id}/issues/12",
        json={
            "assignee_id": str(uuid.uuid4()),
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Assignee must be a member of the project organization"
    )


def test_create_issue_rejects_whitespace_title() -> None:
    user = make_user()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        f"/projects/{project_id}/issues",
        json={"title": "   "},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
