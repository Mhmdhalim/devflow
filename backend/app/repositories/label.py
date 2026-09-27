import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.label import Label
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
