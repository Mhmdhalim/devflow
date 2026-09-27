import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.comments import get_comment_service
from app.main import app
from app.models.comment import Comment
from app.models.user import User
from app.services.comment import (
    CommentIssueNotFoundError,
    CommentPermissionDeniedError,
    CommentProjectNotFoundError,
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


def make_comment(
    issue_id: uuid.UUID,
    author_id: uuid.UUID,
) -> Comment:
    now = datetime.now(UTC)

    comment = Comment(
        issue_id=issue_id,
        author_id=author_id,
        body="I am working on this.",
    )

    comment.id = uuid.uuid4()
    comment.created_at = now
    comment.updated_at = now

    return comment


def test_create_comment() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    issue_id = uuid.uuid4()

    comment = make_comment(
        issue_id=issue_id,
        author_id=user.id,
    )

    service.create_comment.return_value = comment

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_comment_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues/12/comments",
        json={
            "body": "I am working on this.",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["issue_id"] == str(issue_id)
    assert body["author_id"] == str(user.id)
    assert body["body"] == "I am working on this."

    call = service.create_comment.call_args

    assert call.kwargs["project_id"] == project_id
    assert call.kwargs["issue_number"] == 12
    assert call.kwargs["author_id"] == user.id
    assert call.kwargs["data"].body == "I am working on this."


def test_create_comment_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_comment_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues/12/comments",
        json={
            "body": "Hello",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.create_comment.assert_not_called()


def test_create_comment_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_comment.side_effect = CommentPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_comment_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues/12/comments",
        json={
            "body": "Hello",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_create_comment_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_comment.side_effect = CommentProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_comment_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues/12/comments",
        json={
            "body": "Hello",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_create_comment_when_issue_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_comment.side_effect = CommentIssueNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_comment_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/issues/99/comments",
        json={
            "body": "Hello",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Issue not found"


def test_create_comment_rejects_empty_body() -> None:
    user = make_user()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        f"/projects/{project_id}/issues/12/comments",
        json={
            "body": "",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
