import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from app.models.invitation import OrganizationInvitation
from app.models.membership import Membership
from app.repositories.invitation import OrganizationInvitationRepository


def test_get_by_token_hash() -> None:
    db = MagicMock()
    repository = OrganizationInvitationRepository(db)

    invitation = OrganizationInvitation(
        organization_id=uuid.uuid4(),
        email="member@example.com",
        role="member",
        token_hash="hashed",
        invited_by_id=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    db.scalars.return_value.first.return_value = invitation

    result = repository.get_by_token_hash("hashed")

    assert result is invitation
    db.scalars.assert_called_once()


def test_accept_invitation_creates_membership() -> None:
    db = MagicMock()
    repository = OrganizationInvitationRepository(db)

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    accepted_at = datetime.now(UTC)

    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email="member@example.com",
        role="admin",
        token_hash="hashed",
        invited_by_id=uuid.uuid4(),
        expires_at=accepted_at + timedelta(days=1),
    )

    membership = repository.accept(
        invitation=invitation,
        user_id=user_id,
        accepted_at=accepted_at,
    )

    assert isinstance(membership, Membership)
    assert membership.user_id == user_id
    assert membership.organization_id == organization_id
    assert membership.role == "admin"
    assert invitation.accepted_at == accepted_at

    db.add.assert_called_once_with(membership)
    db.commit.assert_called_once()
