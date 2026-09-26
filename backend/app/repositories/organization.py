import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_slug(self, slug: str) -> Organization | None:
        statement = select(Organization).where(Organization.slug == slug)
        return self.db.scalars(statement).first()

    def create_with_membership(
        self,
        data: OrganizationCreate,
        user_id: uuid.UUID,
        role: str,
    ) -> Organization:
        organization = Organization(
            name=data.name,
            slug=data.slug,
        )

        self.db.add(organization)

        try:
            self.db.flush()

            membership = Membership(
                user_id=user_id,
                organization_id=organization.id,
                role=role,
            )

            self.db.add(membership)

            self.db.commit()
            self.db.refresh(organization)

        except SQLAlchemyError:
            self.db.rollback()
            raise

        return organization
