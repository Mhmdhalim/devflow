import uuid
from unittest.mock import MagicMock

from app.models.label import Label
from app.repositories.label import LabelRepository
from app.schemas.label import LabelCreate


def test_get_by_name() -> None:
    db = MagicMock()
    repository = LabelRepository(db)

    project_id = uuid.uuid4()

    expected_label = Label(
        project_id=project_id,
        name="backend",
        color="#2563EB",
    )

    db.scalars.return_value.first.return_value = expected_label

    result = repository.get_by_name(
        project_id=project_id,
        name="backend",
    )

    assert result is expected_label
    db.scalars.assert_called_once()


def test_create_label() -> None:
    db = MagicMock()
    repository = LabelRepository(db)

    project_id = uuid.uuid4()

    data = LabelCreate(
        name="backend",
        color="#2563EB",
    )

    result = repository.create(
        data=data,
        project_id=project_id,
    )

    added_label = db.add.call_args.args[0]

    assert isinstance(added_label, Label)
    assert added_label.project_id == project_id
    assert added_label.name == "backend"
    assert added_label.color == "#2563EB"
    assert result is added_label

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_label)


def test_list_for_project() -> None:
    db = MagicMock()
    repository = LabelRepository(db)

    project_id = uuid.uuid4()

    labels = [
        Label(
            project_id=project_id,
            name="backend",
            color="#2563EB",
        ),
        Label(
            project_id=project_id,
            name="bug",
            color="#DC2626",
        ),
    ]

    db.scalars.return_value.all.return_value = labels

    result = repository.list_for_project(project_id)

    assert result == labels
    db.scalars.assert_called_once()
