import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.invitation import OrganizationInvitation
from app.models.membership import Membership


class OrganizationInvitationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        organization_id: uuid.UUID,
        email: str,
        role: str,
        token_hash: str,
        invited_by_id: uuid.UUID,
        expires_at: datetime,
    ) -> OrganizationInvitation:
        invitation = OrganizationInvitation(
            organization_id=organization_id,
            email=email,
            role=role,
            token_hash=token_hash,
            invited_by_id=invited_by_id,
            expires_at=expires_at,
        )

        self.db.add(invitation)
        self.db.commit()
        self.db.refresh(invitation)

        return invitation

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> OrganizationInvitation | None:
        statement = select(OrganizationInvitation).where(
            OrganizationInvitation.token_hash == token_hash,
        )
        return self.db.scalars(statement).first()

    def get_pending_for_email(
        self,
        *,
        organization_id: uuid.UUID,
        email: str,
        now: datetime,
    ) -> OrganizationInvitation | None:
        statement = select(OrganizationInvitation).where(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.email == email,
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.expires_at > now,
        )

        return self.db.scalars(statement).first()

    def get_by_id(
        self,
        invitation_id: uuid.UUID,
    ) -> OrganizationInvitation | None:
        return self.db.get(OrganizationInvitation, invitation_id)

    def list_pending_for_email(
        self,
        *,
        email: str,
        now: datetime,
    ) -> list[OrganizationInvitation]:
        statement = (
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.email == email,
                OrganizationInvitation.accepted_at.is_(None),
                OrganizationInvitation.expires_at > now,
            )
            .order_by(OrganizationInvitation.created_at)
        )

        return list(self.db.scalars(statement).all())

    def list_pending_for_organization(
        self,
        *,
        organization_id: uuid.UUID,
        now: datetime,
    ) -> list[OrganizationInvitation]:
        statement = (
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.organization_id == organization_id,
                OrganizationInvitation.accepted_at.is_(None),
                OrganizationInvitation.expires_at > now,
            )
            .order_by(OrganizationInvitation.created_at)
        )

        return list(self.db.scalars(statement).all())

    def accept(
        self,
        *,
        invitation: OrganizationInvitation,
        user_id: uuid.UUID,
        accepted_at: datetime,
    ) -> Membership:
        membership = Membership(
            user_id=user_id,
            organization_id=invitation.organization_id,
            role=invitation.role,
        )

        self.db.add(membership)
        invitation.accepted_at = accepted_at

        try:
            self.db.commit()
            self.db.refresh(membership)
            self.db.refresh(invitation)
        except SQLAlchemyError:
            self.db.rollback()
            raise

        return membership
