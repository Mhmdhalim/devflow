import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.projects import get_project_service
from app.main import app
from app.models.project import Project
from app.models.user import User
from app.services.project import (
    ProjectAlreadyExistsError,
    ProjectOrganizationNotFoundError,
    ProjectPermissionDeniedError,
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


def make_project(
    organization_id: uuid.UUID,
) -> Project:
    now = datetime.now(UTC)

    project = Project(
        organization_id=organization_id,
        name="DevFlow Backend",
        key="DEV",
        description="Backend project",
    )

    project.id = uuid.uuid4()
    project.created_at = now
    project.updated_at = now

    return project


def test_create_project() -> None:
    service = MagicMock()
    user = make_user()
    organization_id = uuid.uuid4()

    project = make_project(organization_id)

    service.create_project.return_value = project

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/organizations/{organization_id}/projects",
        json={
            "name": "DevFlow Backend",
            "key": "DEV",
            "description": "Backend project",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["organization_id"] == str(organization_id)
    assert body["name"] == "DevFlow Backend"
    assert body["key"] == "DEV"

    service.create_project.assert_called_once()

    call = service.create_project.call_args

    assert call.kwargs["organization_id"] == (organization_id)

    assert call.kwargs["user_id"] == user.id
    assert call.kwargs["data"].key == "DEV"


def test_create_project_requires_authentication() -> None:
    service = MagicMock()
    organization_id = uuid.uuid4()

    app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/organizations/{organization_id}/projects",
        json={
            "name": "DevFlow Backend",
            "key": "DEV",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.create_project.assert_not_called()


def test_create_project_forbidden() -> None:
    service = MagicMock()
    user = make_user()
    organization_id = uuid.uuid4()

    service.create_project.side_effect = ProjectPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/organizations/{organization_id}/projects",
        json={
            "name": "DevFlow Backend",
            "key": "DEV",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_create_project_when_organization_missing() -> None:
    service = MagicMock()
    user = make_user()
    organization_id = uuid.uuid4()

    service.create_project.side_effect = ProjectOrganizationNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/organizations/{organization_id}/projects",
        json={
            "name": "DevFlow Backend",
            "key": "DEV",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_create_project_with_duplicate_key() -> None:
    service = MagicMock()
    user = make_user()
    organization_id = uuid.uuid4()

    service.create_project.side_effect = ProjectAlreadyExistsError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_project_service] = lambda: service

    response = client.post(
        f"/organizations/{organization_id}/projects",
        json={
            "name": "DevFlow Backend",
            "key": "DEV",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
