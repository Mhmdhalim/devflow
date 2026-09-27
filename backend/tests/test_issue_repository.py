import uuid
from unittest.mock import MagicMock

from app.models.issue import Issue
from app.repositories.issue import IssueRepository
from app.schemas.issue import IssueCreate


def make_data() -> IssueCreate:
    return IssueCreate(
        title="Add authentication",
        description="Implement JWT login",
        priority="high",
    )


def test_create_first_issue() -> None:
    db = MagicMock()
    repository = IssueRepository(db)

    project_id = uuid.uuid4()
    reporter_id = uuid.uuid4()

    db.scalar.return_value = None

    result = repository.create_with_next_number(
        data=make_data(),
        project_id=project_id,
        reporter_id=reporter_id,
    )

    added_issue = db.add.call_args.args[0]

    assert isinstance(
        added_issue,
        Issue,
    )

    assert added_issue.project_id == project_id
    assert added_issue.number == 1
    assert added_issue.title == "Add authentication"
    assert added_issue.status == "todo"
    assert added_issue.priority == "high"
    assert added_issue.reporter_id == reporter_id
    assert added_issue.assignee_id is None

    assert result is added_issue

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_issue)


def test_create_issue_increments_number() -> None:
    db = MagicMock()
    repository = IssueRepository(db)

    project_id = uuid.uuid4()
    reporter_id = uuid.uuid4()

    db.scalar.return_value = 7

    result = repository.create_with_next_number(
        data=make_data(),
        project_id=project_id,
        reporter_id=reporter_id,
    )

    assert result.number == 8


def test_create_issue_with_assignee() -> None:
    db = MagicMock()
    repository = IssueRepository(db)

    project_id = uuid.uuid4()
    reporter_id = uuid.uuid4()
    assignee_id = uuid.uuid4()

    db.scalar.return_value = None

    data = IssueCreate(
        title="Fix login",
        priority="medium",
        assignee_id=assignee_id,
    )

    result = repository.create_with_next_number(
        data=data,
        project_id=project_id,
        reporter_id=reporter_id,
    )

    assert result.assignee_id == assignee_id


def test_list_for_project() -> None:
    db = MagicMock()
    repository = IssueRepository(db)

    project_id = uuid.uuid4()
    reporter_id = uuid.uuid4()

    issues = [
        Issue(
            project_id=project_id,
            number=1,
            title="First issue",
            description=None,
            status="todo",
            priority="medium",
            reporter_id=reporter_id,
            assignee_id=None,
        ),
        Issue(
            project_id=project_id,
            number=2,
            title="Second issue",
            description=None,
            status="todo",
            priority="high",
            reporter_id=reporter_id,
            assignee_id=None,
        ),
    ]

    db.scalars.return_value.all.return_value = issues

    result = repository.list_for_project(project_id)

    assert result == issues
    db.scalars.assert_called_once()


def test_get_by_number() -> None:
    db = MagicMock()
    repository = IssueRepository(db)

    project_id = uuid.uuid4()

    expected_issue = Issue(
        project_id=project_id,
        number=12,
        title="Fix authentication",
        description=None,
        status="todo",
        priority="high",
        reporter_id=uuid.uuid4(),
        assignee_id=None,
    )

    db.scalars.return_value.first.return_value = expected_issue

    result = repository.get_by_number(
        project_id=project_id,
        issue_number=12,
    )

    assert result is expected_issue
    db.scalars.assert_called_once()


def test_get_by_number_returns_none() -> None:
    db = MagicMock()
    repository = IssueRepository(db)

    db.scalars.return_value.first.return_value = None

    result = repository.get_by_number(
        project_id=uuid.uuid4(),
        issue_number=99,
    )

    assert result is None
