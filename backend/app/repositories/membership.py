import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.user import User


class MembershipRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_for_user_and_organization(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Membership | None:
        statement = select(Membership).where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
        )

        return self.db.scalars(statement).first()

    def list_for_organization(
        self,
        organization_id: uuid.UUID,
    ) -> list[tuple[Membership, User]]:
        statement = (
            select(Membership, User)
            .join(User, User.id == Membership.user_id)
            .where(Membership.organization_id == organization_id)
            .order_by(Membership.created_at)
        )

        rows = self.db.execute(statement).all()
        return [(membership, user) for membership, user in rows]
