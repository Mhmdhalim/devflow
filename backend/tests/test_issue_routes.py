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
