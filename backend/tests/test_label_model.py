import uuid

from app.models.label import Label, issue_labels


def test_label_model() -> None:
    project_id = uuid.uuid4()

    label = Label(
        project_id=project_id,
        name="backend",
        color="#2563EB",
    )

    assert label.project_id == project_id
    assert label.name == "backend"
    assert label.color == "#2563EB"


def test_issue_labels_table() -> None:
    assert issue_labels.name == "issue_labels"

    assert {column.name for column in issue_labels.primary_key.columns} == {
        "issue_id",
        "label_id",
    }

    foreign_keys = {
        foreign_key.target_fullname for foreign_key in issue_labels.foreign_keys
    }

    assert foreign_keys == {
        "issues.id",
        "labels.id",
    }
