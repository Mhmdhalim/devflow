import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Issue(Base):
    __tablename__ = "issues"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "number",
            name="uq_issues_project_number",
        ),
        CheckConstraint(
            "number > 0",
            name="ck_issues_number_positive",
        ),
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')",
            name="ck_issues_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_issues_priority",
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

    number: Mapped[int] = mapped_column(
        Integer,
    )

    title: Mapped[str] = mapped_column(
        String(200),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="todo",
        server_default="todo",
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        server_default="medium",
    )

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
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
