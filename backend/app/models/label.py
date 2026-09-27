import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

issue_labels = Table(
    "issue_labels",
    Base.metadata,
    Column(
        "issue_id",
        Uuid(),
        ForeignKey(
            "issues.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "label_id",
        Uuid(),
        ForeignKey(
            "labels.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


class Label(Base):
    __tablename__ = "labels"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            name="uq_labels_project_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"),
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
    )

    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
