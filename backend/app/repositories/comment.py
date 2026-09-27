import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import CommentCreate


class CommentRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        data: CommentCreate,
        issue_id: uuid.UUID,
        author_id: uuid.UUID,
    ) -> Comment:
        comment = Comment(
            issue_id=issue_id,
            author_id=author_id,
            body=data.body,
        )

        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        return comment

    def list_for_issue(
        self,
        issue_id: uuid.UUID,
    ) -> list[Comment]:
        statement = (
            select(Comment)
            .where(Comment.issue_id == issue_id)
            .order_by(Comment.created_at)
        )

        return list(self.db.scalars(statement).all())
