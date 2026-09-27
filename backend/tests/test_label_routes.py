import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.labels import get_label_service
from app.main import app
from app.models.label import Label
from app.models.user import User
from app.services.label import (
    LabelAlreadyExistsError,
    LabelPermissionDeniedError,
    LabelProjectNotFoundError,
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


def make_label(
    project_id: uuid.UUID,
    name: str = "backend",
) -> Label:
    now = datetime.now(UTC)

    label = Label(
        project_id=project_id,
        name=name,
        color="#2563EB",
    )

    label.id = uuid.uuid4()
    label.created_at = now
    label.updated_at = now

    return label


def test_create_label() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    label = make_label(project_id)

    service.create_label.return_value = label

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "#2563EB",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "backend"
    assert body["color"] == "#2563EB"
    assert body["project_id"] == str(project_id)

    call = service.create_label.call_args

    assert call.kwargs["project_id"] == project_id
    assert call.kwargs["user_id"] == user.id
    assert call.kwargs["data"].name == "backend"
    assert call.kwargs["data"].color == "#2563EB"


def test_create_label_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_label_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.create_label.assert_not_called()


def test_create_label_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_label.side_effect = LabelPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You do not have permission to create labels in this project"
    )


def test_create_label_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_label.side_effect = LabelProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_create_label_when_name_exists() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.create_label.side_effect = LabelAlreadyExistsError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Label with this name already exists in this project"
    )


def test_create_label_rejects_invalid_color() -> None:
    user = make_user()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "blue",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_create_label_rejects_empty_name() -> None:
    user = make_user()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "",
            "color": "#2563EB",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_list_labels() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.list_labels.return_value = [
        make_label(
            project_id=project_id,
            name="backend",
        ),
        make_label(
            project_id=project_id,
            name="bug",
        ),
    ]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    assert body[0]["name"] == "backend"
    assert body[0]["color"] == "#2563EB"
    assert body[0]["project_id"] == str(project_id)

    assert body[1]["name"] == "bug"
    assert body[1]["color"] == "#2563EB"
    assert body[1]["project_id"] == str(project_id)

    service.list_labels.assert_called_once_with(
        project_id=project_id,
        user_id=user.id,
    )


def test_list_labels_returns_empty_list() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.list_labels.return_value = []

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []


def test_list_labels_requires_authentication() -> None:
    service = MagicMock()
    project_id = uuid.uuid4()

    app.dependency_overrides[get_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.list_labels.assert_not_called()


def test_list_labels_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.list_labels.side_effect = LabelPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == ("You do not have access to this project")


def test_list_labels_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()
    project_id = uuid.uuid4()

    service.list_labels.side_effect = LabelProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
