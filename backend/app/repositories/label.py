import uuid

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.models.label import Label, issue_labels
from app.schemas.label import LabelCreate


class LabelRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_by_name(
        self,
        project_id: uuid.UUID,
        name: str,
    ) -> Label | None:
        statement = select(Label).where(
            Label.project_id == project_id,
            Label.name == name,
        )

        return self.db.scalars(statement).first()

    def get_by_id(
        self,
        label_id: uuid.UUID,
    ) -> Label | None:
        return self.db.get(
            Label,
            label_id,
        )

    def create(
        self,
        data: LabelCreate,
        project_id: uuid.UUID,
    ) -> Label:
        label = Label(
            project_id=project_id,
            name=data.name,
            color=data.color,
        )

        self.db.add(label)
        self.db.commit()
        self.db.refresh(label)

        return label

    def list_for_project(
        self,
        project_id: uuid.UUID,
    ) -> list[Label]:
        statement = (
            select(Label)
            .where(Label.project_id == project_id)
            .order_by(Label.created_at)
        )

        return list(self.db.scalars(statement).all())

    def is_assigned_to_issue(
        self,
        issue_id: uuid.UUID,
        label_id: uuid.UUID,
    ) -> bool:
        statement = select(issue_labels.c.label_id).where(
            issue_labels.c.issue_id == issue_id,
            issue_labels.c.label_id == label_id,
        )

        return self.db.scalar(statement) is not None

    def assign_to_issue(
        self,
        issue_id: uuid.UUID,
        label_id: uuid.UUID,
    ) -> None:
        statement = insert(issue_labels).values(
            issue_id=issue_id,
            label_id=label_id,
        )

        self.db.execute(statement)
        self.db.commit()

    def remove_from_issue(
        self,
        issue_id: uuid.UUID,
        label_id: uuid.UUID,
    ) -> None:
        statement = delete(issue_labels).where(
            issue_labels.c.issue_id == issue_id,
            issue_labels.c.label_id == label_id,
        )

        self.db.execute(statement)
        self.db.commit()

    def list_for_issue(
        self,
        issue_id: uuid.UUID,
    ) -> list[Label]:
        statement = (
            select(Label)
            .join(
                issue_labels,
                Label.id == issue_labels.c.label_id,
            )
            .where(issue_labels.c.issue_id == issue_id)
            .order_by(Label.created_at)
        )

        return list(self.db.scalars(statement).all())
