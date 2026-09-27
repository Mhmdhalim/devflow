import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership


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
