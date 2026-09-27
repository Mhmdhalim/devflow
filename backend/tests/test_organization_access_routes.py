import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.organization_access import get_organization_access_service
from app.main import app
from app.models.invitation import OrganizationInvitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.organization_access import (
    OrganizationAccessPermissionDeniedError,
    OrganizationInvitationEmailMismatchError,
)

client = TestClient(app)


def make_user(email: str = "owner@example.com") -> User:
    user = User(
        email=email,
        full_name="Owner",
        hashed_password="not-used",
        is_active=True,
    )
    user.id = uuid.uuid4()
    return user


def make_organization() -> Organization:
    now = datetime.now(UTC)
    organization = Organization(name="Acme", slug="acme")
    organization.id = uuid.uuid4()
    organization.created_at = now
    organization.updated_at = now
    return organization


def make_invitation(
    organization_id: uuid.UUID,
    invited_by_id: uuid.UUID,
) -> OrganizationInvitation:
    now = datetime.now(UTC)
    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email="member@example.com",
        role="member",
        token_hash="hashed",
        invited_by_id=invited_by_id,
        expires_at=now + timedelta(days=7),
    )
    invitation.id = uuid.uuid4()
    invitation.created_at = now
    invitation.accepted_at = None
    return invitation


def test_create_invitation() -> None:
    service = MagicMock()
    user = make_user()
    organization = make_organization()
    invitation = make_invitation(organization.id, user.id)

    service.create_invitation.return_value = (
        invitation,
        "plain-invite-token",
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_organization_access_service] = lambda: service

    response = client.post(
        f"/organizations/{organization.id}/invitations",
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "member@example.com"
    assert body["role"] == "member"
    assert body["token"] == "plain-invite-token"


def test_create_invitation_forbidden_for_regular_member() -> None:
    service = MagicMock()
    user = make_user()
    organization_id = uuid.uuid4()

    service.create_invitation.side_effect = OrganizationAccessPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_organization_access_service] = lambda: service

    response = client.post(
        f"/organizations/{organization_id}/invitations",
        json={
            "email": "member@example.com",
            "role": "member",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_list_members() -> None:
    service = MagicMock()
    current_user = make_user()
    member = make_user("member@example.com")
    organization = make_organization()
    now = datetime.now(UTC)

    membership = Membership(
        user_id=member.id,
        organization_id=organization.id,
        role="member",
    )
    membership.created_at = now

    service.list_members.return_value = [(membership, member)]

    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_organization_access_service] = lambda: service

    response = client.get(
        f"/organizations/{organization.id}/members",
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body[0]["email"] == "member@example.com"
    assert body[0]["role"] == "member"


def test_get_invitation_rejects_different_email() -> None:
    service = MagicMock()
    user = make_user("different@example.com")

    service.get_invitation.side_effect = OrganizationInvitationEmailMismatchError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_organization_access_service] = lambda: service

    response = client.get("/invitations/token-value")

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_accept_invitation() -> None:
    service = MagicMock()
    user = make_user("member@example.com")
    organization = make_organization()

    membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role="member",
    )

    service.accept_invitation.return_value = (
        organization,
        membership,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_organization_access_service] = lambda: service

    response = client.post("/invitations/token-value/accept")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(organization.id)
    assert body["role"] == "member"
