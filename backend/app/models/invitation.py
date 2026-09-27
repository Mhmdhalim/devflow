import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'member')",
            name="ck_organization_invitations_role",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="member",
        server_default="member",
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    invited_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
