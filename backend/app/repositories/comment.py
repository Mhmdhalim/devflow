import uuid

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
