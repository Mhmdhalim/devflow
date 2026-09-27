import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.organizations import (
    get_organization_service,
)
from app.main import app
from app.models.organization import Organization
from app.models.user import User
from app.services.organization import (
    OrganizationAlreadyExistsError,
)

client = TestClient(app)


def make_user() -> User:
    user = User(
        email="alice@example.com",
        full_name="Alice Johnson",
        hashed_password="not-used",
        is_active=True,
    )

    user.id = uuid.uuid4()

    return user


def make_organization() -> Organization:
    now = datetime.now(UTC)

    organization = Organization(
        name="DevFlow",
        slug="devflow",
    )

    organization.id = uuid.uuid4()
    organization.created_at = now
    organization.updated_at = now

    return organization


def test_create_organization() -> None:
    service = MagicMock()
    user = make_user()
    organization = make_organization()

    service.create_organization.return_value = organization

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_organization_service] = lambda: service

    response = client.post(
        "/organizations",
        json={
            "name": "DevFlow",
            "slug": "devflow",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["id"] == str(organization.id)
    assert body["name"] == "DevFlow"
    assert body["slug"] == "devflow"

    service.create_organization.assert_called_once()

    call = service.create_organization.call_args

    assert call.kwargs["owner_id"] == user.id
    assert call.kwargs["data"].slug == "devflow"


def test_create_organization_with_existing_slug() -> None:
    service = MagicMock()
    user = make_user()

    service.create_organization.side_effect = OrganizationAlreadyExistsError

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_organization_service] = lambda: service

    response = client.post(
        "/organizations",
        json={
            "name": "DevFlow",
            "slug": "devflow",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "Organization with this slug already exists"}


def test_create_organization_requires_authentication() -> None:
    service = MagicMock()

    app.dependency_overrides[get_organization_service] = lambda: service

    response = client.post(
        "/organizations",
        json={
            "name": "DevFlow",
            "slug": "devflow",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 401

    service.create_organization.assert_not_called()


def test_list_organizations() -> None:
    service = MagicMock()
    user = make_user()

    first = make_organization()

    second = Organization(
        name="Backend Team",
        slug="backend-team",
    )

    now = datetime.now(UTC)

    second.id = uuid.uuid4()
    second.created_at = now
    second.updated_at = now

    service.list_user_organizations.return_value = [
        (
            first,
            "owner",
        ),
        (
            second,
            "member",
        ),
    ]

    app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_organization_service] = lambda: service

    response = client.get("/organizations")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    assert body[0]["slug"] == "devflow"
    assert body[0]["role"] == "owner"

    assert body[1]["slug"] == "backend-team"
    assert body[1]["role"] == "member"

    service.list_user_organizations.assert_called_once_with(user.id)


def test_list_organizations_requires_authentication() -> None:
    service = MagicMock()

    app.dependency_overrides[get_organization_service] = lambda: service

    response = client.get("/organizations")

    app.dependency_overrides.clear()

    assert response.status_code == 401

    service.list_user_organizations.assert_not_called()
