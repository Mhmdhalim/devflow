import uuid
from unittest.mock import MagicMock

from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.schemas.comment import CommentCreate


def test_create_comment() -> None:
    db = MagicMock()
    repository = CommentRepository(db)

    issue_id = uuid.uuid4()
    author_id = uuid.uuid4()

    data = CommentCreate(body="I am working on this.")

    result = repository.create(
        data=data,
        issue_id=issue_id,
        author_id=author_id,
    )

    added_comment = db.add.call_args.args[0]

    assert isinstance(
        added_comment,
        Comment,
    )

    assert added_comment.issue_id == issue_id
    assert added_comment.author_id == author_id
    assert added_comment.body == ("I am working on this.")

    assert result is added_comment

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_comment)


def test_list_for_issue() -> None:
    db = MagicMock()
    repository = CommentRepository(db)

    issue_id = uuid.uuid4()
    author_id = uuid.uuid4()

    comments = [
        Comment(
            issue_id=issue_id,
            author_id=author_id,
            body="First comment",
        ),
        Comment(
            issue_id=issue_id,
            author_id=author_id,
            body="Second comment",
        ),
    ]

    db.scalars.return_value.all.return_value = comments

    result = repository.list_for_issue(issue_id)

    assert result == comments
    db.scalars.assert_called_once()
