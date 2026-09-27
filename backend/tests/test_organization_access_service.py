import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.models.invitation import OrganizationInvitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.schemas.invitation import OrganizationInvitationCreate
from app.services.organization_access import (
    OrganizationAccessPermissionDeniedError,
    OrganizationAccessService,
    OrganizationInvitationEmailMismatchError,
    OrganizationMemberAlreadyExistsError,
)


def make_service() -> tuple[
    OrganizationAccessService,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    invitation_repository = MagicMock()
    membership_repository = MagicMock()
    organization_repository = MagicMock()
    user_repository = MagicMock()

    service = OrganizationAccessService(
        invitation_repository,
        membership_repository,
        organization_repository,
        user_repository,
    )

    return (
        service,
        invitation_repository,
        membership_repository,
        organization_repository,
        user_repository,
    )


def make_organization() -> Organization:
    organization = Organization(name="Acme", slug="acme")
    organization.id = uuid.uuid4()
    return organization


def make_user(email: str = "member@example.com") -> User:
    user = User(
        email=email,
        full_name="Team Member",
        hashed_password="not-used",
        is_active=True,
    )
    user.id = uuid.uuid4()
    return user


def make_invitation(
    organization_id: uuid.UUID,
    *,
    email: str = "member@example.com",
) -> OrganizationInvitation:
    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=email,
        role="member",
        token_hash="hashed-token",
        invited_by_id=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    invitation.id = uuid.uuid4()
    return invitation


def test_create_invitation_as_owner() -> None:
    (
        service,
        invitation_repository,
        membership_repository,
        organization_repository,
        user_repository,
    ) = make_service()

    organization = make_organization()
    inviter_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = organization
    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=inviter_id,
        organization_id=organization.id,
        role="owner",
    )
    user_repository.get_by_email.return_value = None
    invitation_repository.get_pending_for_email.return_value = None

    expected = make_invitation(organization.id)
    invitation_repository.create.return_value = expected

    invitation, token = service.create_invitation(
        organization_id=organization.id,
        inviter_id=inviter_id,
        data=OrganizationInvitationCreate(
            email="Member@Example.com",
            role="member",
        ),
    )

    assert invitation is expected
    assert token
    assert len(token) >= 32

    call = invitation_repository.create.call_args
    assert call.kwargs["organization_id"] == organization.id
    assert call.kwargs["email"] == "member@example.com"
    assert call.kwargs["role"] == "member"
    assert call.kwargs["invited_by_id"] == inviter_id
    assert len(call.kwargs["token_hash"]) == 64


def test_create_invitation_as_regular_member_is_forbidden() -> None:
    (
        service,
        invitation_repository,
        membership_repository,
        organization_repository,
        user_repository,
    ) = make_service()

    organization = make_organization()
    inviter_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = organization
    membership_repository.get_for_user_and_organization.return_value = Membership(
        user_id=inviter_id,
        organization_id=organization.id,
        role="member",
    )

    with pytest.raises(OrganizationAccessPermissionDeniedError):
        service.create_invitation(
            organization_id=organization.id,
            inviter_id=inviter_id,
            data=OrganizationInvitationCreate(
                email="member@example.com",
            ),
        )

    user_repository.get_by_email.assert_not_called()
    invitation_repository.create.assert_not_called()


def test_create_invitation_rejects_existing_member() -> None:
    (
        service,
        invitation_repository,
        membership_repository,
        organization_repository,
        user_repository,
    ) = make_service()

    organization = make_organization()
    inviter_id = uuid.uuid4()
    invited_user = make_user()

    organization_repository.get_by_id.return_value = organization
    membership_repository.get_for_user_and_organization.side_effect = [
        Membership(
            user_id=inviter_id,
            organization_id=organization.id,
            role="owner",
        ),
        Membership(
            user_id=invited_user.id,
            organization_id=organization.id,
            role="member",
        ),
    ]
    user_repository.get_by_email.return_value = invited_user

    with pytest.raises(OrganizationMemberAlreadyExistsError):
        service.create_invitation(
            organization_id=organization.id,
            inviter_id=inviter_id,
            data=OrganizationInvitationCreate(
                email=invited_user.email,
            ),
        )

    invitation_repository.create.assert_not_called()


def test_accept_invitation() -> None:
    (
        service,
        invitation_repository,
        membership_repository,
        organization_repository,
        _,
    ) = make_service()

    organization = make_organization()
    user = make_user()
    invitation = make_invitation(organization.id, email=user.email)

    invitation_repository.get_by_token_hash.return_value = invitation
    organization_repository.get_by_id.return_value = organization
    membership_repository.get_for_user_and_organization.return_value = None

    expected_membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role="member",
    )
    invitation_repository.accept.return_value = expected_membership

    result_organization, result_membership = service.accept_invitation(
        token="invite-token",
        user=user,
    )

    assert result_organization is organization
    assert result_membership is expected_membership

    invitation_repository.accept.assert_called_once()
    call = invitation_repository.accept.call_args
    assert call.kwargs["invitation"] is invitation
    assert call.kwargs["user_id"] == user.id


def test_invitation_cannot_be_accepted_by_different_email() -> None:
    (
        service,
        invitation_repository,
        _,
        organization_repository,
        _,
    ) = make_service()

    organization = make_organization()
    invitation = make_invitation(
        organization.id,
        email="invited@example.com",
    )

    invitation_repository.get_by_token_hash.return_value = invitation

    with pytest.raises(OrganizationInvitationEmailMismatchError):
        service.get_invitation(
            token="invite-token",
            user_email="different@example.com",
        )

    organization_repository.get_by_id.assert_not_called()


def test_list_members_requires_membership() -> None:
    (
        service,
        _,
        membership_repository,
        organization_repository,
        _,
    ) = make_service()

    organization = make_organization()
    user_id = uuid.uuid4()

    organization_repository.get_by_id.return_value = organization
    membership_repository.get_for_user_and_organization.return_value = None

    with pytest.raises(OrganizationAccessPermissionDeniedError):
        service.list_members(
            organization_id=organization.id,
            user_id=user_id,
        )

    membership_repository.list_for_organization.assert_not_called()


def test_list_user_invitations_returns_organizations() -> None:
    (
        service,
        invitation_repository,
        _,
        organization_repository,
        _,
    ) = make_service()

    organization = make_organization()
    invitation = make_invitation(organization.id)
    invitation_repository.list_pending_for_email.return_value = [invitation]
    organization_repository.get_by_id.return_value = organization

    result = service.list_user_invitations(user_email=" Member@Example.com ")

    assert result == [(invitation, organization)]
    invitation_repository.list_pending_for_email.assert_called_once()
    call = invitation_repository.list_pending_for_email.call_args
    assert call.kwargs["email"] == "member@example.com"


def test_accept_invitation_by_id() -> None:
    (
        service,
        invitation_repository,
        membership_repository,
        organization_repository,
        _,
    ) = make_service()

    organization = make_organization()
    user = make_user()
    invitation = make_invitation(organization.id, email=user.email)
    expected_membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role="member",
    )

    invitation_repository.get_by_id.return_value = invitation
    organization_repository.get_by_id.return_value = organization
    membership_repository.get_for_user_and_organization.return_value = None
    invitation_repository.accept.return_value = expected_membership

    result_organization, result_membership = service.accept_invitation_by_id(
        invitation_id=invitation.id,
        user=user,
    )

    assert result_organization is organization
    assert result_membership is expected_membership
    invitation_repository.accept.assert_called_once()
