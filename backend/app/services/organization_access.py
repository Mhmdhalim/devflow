import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from app.models.invitation import OrganizationInvitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.repositories.invitation import OrganizationInvitationRepository
from app.repositories.membership import MembershipRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.invitation import OrganizationInvitationCreate


class OrganizationAccessNotFoundError(Exception):
    pass


class OrganizationAccessPermissionDeniedError(Exception):
    pass


class OrganizationMemberAlreadyExistsError(Exception):
    pass


class OrganizationInvitationAlreadyExistsError(Exception):
    pass


class OrganizationInvitationNotFoundError(Exception):
    pass


class OrganizationInvitationExpiredError(Exception):
    pass


class OrganizationInvitationAlreadyAcceptedError(Exception):
    pass


class OrganizationInvitationEmailMismatchError(Exception):
    pass


class OrganizationAccessService:
    invitation_lifetime = timedelta(days=7)

    def __init__(
        self,
        invitation_repository: OrganizationInvitationRepository,
        membership_repository: MembershipRepository,
        organization_repository: OrganizationRepository,
        user_repository: UserRepository,
    ) -> None:
        self.invitation_repository = invitation_repository
        self.membership_repository = membership_repository
        self.organization_repository = organization_repository
        self.user_repository = user_repository

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _get_organization(
        self,
        organization_id: uuid.UUID,
    ) -> Organization:
        organization = self.organization_repository.get_by_id(organization_id)

        if organization is None:
            raise OrganizationAccessNotFoundError

        return organization

    def _require_membership(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Membership:
        self._get_organization(organization_id)

        membership = self.membership_repository.get_for_user_and_organization(
            user_id=user_id,
            organization_id=organization_id,
        )

        if membership is None:
            raise OrganizationAccessPermissionDeniedError

        return membership

    def _require_manager(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Membership:
        membership = self._require_membership(
            organization_id=organization_id,
            user_id=user_id,
        )

        if membership.role not in {"owner", "admin"}:
            raise OrganizationAccessPermissionDeniedError

        return membership

    def create_invitation(
        self,
        *,
        organization_id: uuid.UUID,
        inviter_id: uuid.UUID,
        data: OrganizationInvitationCreate,
    ) -> tuple[OrganizationInvitation, str]:
        self._require_manager(
            organization_id=organization_id,
            user_id=inviter_id,
        )

        email = str(data.email).strip().lower()
        invited_user = self.user_repository.get_by_email(email)

        if invited_user is not None:
            membership = self.membership_repository.get_for_user_and_organization(
                user_id=invited_user.id,
                organization_id=organization_id,
            )

            if membership is not None:
                raise OrganizationMemberAlreadyExistsError

        now = datetime.now(UTC)

        pending = self.invitation_repository.get_pending_for_email(
            organization_id=organization_id,
            email=email,
            now=now,
        )

        if pending is not None:
            raise OrganizationInvitationAlreadyExistsError

        token = secrets.token_urlsafe(32)

        invitation = self.invitation_repository.create(
            organization_id=organization_id,
            email=email,
            role=data.role,
            token_hash=self._hash_token(token),
            invited_by_id=inviter_id,
            expires_at=now + self.invitation_lifetime,
        )

        return invitation, token

    def list_members(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[tuple[Membership, User]]:
        self._require_membership(
            organization_id=organization_id,
            user_id=user_id,
        )

        return self.membership_repository.list_for_organization(
            organization_id=organization_id,
        )

    def list_pending_invitations(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[OrganizationInvitation]:
        self._require_manager(
            organization_id=organization_id,
            user_id=user_id,
        )

        return self.invitation_repository.list_pending_for_organization(
            organization_id=organization_id,
            now=datetime.now(UTC),
        )

    def get_invitation(
        self,
        *,
        token: str,
        user_email: str,
    ) -> tuple[OrganizationInvitation, Organization]:
        invitation = self.invitation_repository.get_by_token_hash(
            self._hash_token(token),
        )

        if invitation is None:
            raise OrganizationInvitationNotFoundError

        if invitation.accepted_at is not None:
            raise OrganizationInvitationAlreadyAcceptedError

        if invitation.expires_at <= datetime.now(UTC):
            raise OrganizationInvitationExpiredError

        if invitation.email.lower() != user_email.strip().lower():
            raise OrganizationInvitationEmailMismatchError

        organization = self._get_organization(invitation.organization_id)

        return invitation, organization

    def accept_invitation(
        self,
        *,
        token: str,
        user: User,
    ) -> tuple[Organization, Membership]:
        invitation, organization = self.get_invitation(
            token=token,
            user_email=user.email,
        )

        existing = self.membership_repository.get_for_user_and_organization(
            user_id=user.id,
            organization_id=invitation.organization_id,
        )

        if existing is not None:
            raise OrganizationMemberAlreadyExistsError

        membership = self.invitation_repository.accept(
            invitation=invitation,
            user_id=user.id,
            accepted_at=datetime.now(UTC),
        )

        return organization, membership
