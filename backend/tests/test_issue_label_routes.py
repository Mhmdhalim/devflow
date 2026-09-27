import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.api.routes.issue_labels import get_issue_label_service
from app.main import app
from app.models.label import Label
from app.models.user import User
from app.services.issue_label import (
    IssueLabelAlreadyAssignedError,
    IssueLabelIssueNotFoundError,
    IssueLabelLabelNotFoundError,
    IssueLabelLabelProjectMismatchError,
    IssueLabelNotAssignedError,
    IssueLabelPermissionDeniedError,
    IssueLabelProjectNotFoundError,
)

client = TestClient(app)


def make_user() -> User:
    user = User(
        email="alice@example.com",
        full_name="Alice",
        hashed_password="not-used",
        is_active=True,
    )

    user.id = uuid.uuid4()

    return user


def make_label(
    project_id: uuid.UUID,
    name: str = "backend",
) -> Label:
    now = datetime.now(UTC)

    label = Label(
        project_id=project_id,
        name=name,
        color="#2563EB",
    )

    label.id = uuid.uuid4()
    label.created_at = now
    label.updated_at = now

    return label


def test_assign_label() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label = make_label(project_id)

    service.assign_label.return_value = label

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label.id}")

    app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["id"] == str(label.id)
    assert body["project_id"] == str(project_id)
    assert body["name"] == "backend"

    service.assign_label.assert_called_once_with(
        project_id=project_id,
        issue_number=12,
        label_id=label.id,
        user_id=user.id,
    )


def test_assign_label_requires_authentication() -> None:
    service = MagicMock()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.assign_label.assert_not_called()


def test_assign_label_forbidden() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.assign_label.side_effect = IssueLabelPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this project"


def test_assign_label_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.assign_label.side_effect = IssueLabelProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_assign_label_when_issue_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.assign_label.side_effect = IssueLabelIssueNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/99/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Issue not found"


def test_assign_label_when_label_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.assign_label.side_effect = IssueLabelLabelNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


def test_assign_label_from_another_project() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.assign_label.side_effect = IssueLabelLabelProjectMismatchError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


def test_assign_label_when_already_assigned() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.assign_label.side_effect = IssueLabelAlreadyAssignedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.post(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == ("Label is already assigned to this issue")


def test_remove_label() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 204
    assert response.content == b""

    service.remove_label.assert_called_once_with(
        project_id=project_id,
        issue_number=12,
        label_id=label_id,
        user_id=user.id,
    )


def test_remove_label_requires_authentication() -> None:
    service = MagicMock()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.remove_label.assert_not_called()


def test_remove_label_forbidden() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.remove_label.side_effect = IssueLabelPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_remove_label_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.remove_label.side_effect = IssueLabelProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_remove_label_when_issue_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.remove_label.side_effect = IssueLabelIssueNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/99/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Issue not found"


def test_remove_label_when_label_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.remove_label.side_effect = IssueLabelLabelNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


def test_remove_label_from_another_project() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.remove_label.side_effect = IssueLabelLabelProjectMismatchError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


def test_remove_label_when_not_assigned() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()
    label_id = uuid.uuid4()

    service.remove_label.side_effect = IssueLabelNotAssignedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.delete(f"/projects/{project_id}/issues/12/labels/{label_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == ("Label is not assigned to this issue")


def test_list_issue_labels() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()

    service.list_labels.return_value = [
        make_label(
            project_id=project_id,
            name="backend",
        ),
        make_label(
            project_id=project_id,
            name="bug",
        ),
    ]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["name"] == "backend"
    assert body[1]["name"] == "bug"

    service.list_labels.assert_called_once_with(
        project_id=project_id,
        issue_number=12,
        user_id=user.id,
    )


def test_list_issue_labels_requires_authentication() -> None:
    service = MagicMock()

    project_id = uuid.uuid4()

    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    service.list_labels.assert_not_called()


def test_list_issue_labels_forbidden() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()

    service.list_labels.side_effect = IssueLabelPermissionDeniedError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_list_issue_labels_when_project_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()

    service.list_labels.side_effect = IssueLabelProjectNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/12/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_list_issue_labels_when_issue_missing() -> None:
    service = MagicMock()
    user = make_user()

    project_id = uuid.uuid4()

    service.list_labels.side_effect = IssueLabelIssueNotFoundError

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_issue_label_service] = lambda: service

    response = client.get(f"/projects/{project_id}/issues/99/labels")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Issue not found"
