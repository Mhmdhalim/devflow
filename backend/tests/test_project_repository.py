import uuid
from unittest.mock import MagicMock

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate


def test_get_by_key() -> None:
    db = MagicMock()
    repository = ProjectRepository(db)

    organization_id = uuid.uuid4()

    expected_project = Project(
        organization_id=organization_id,
        name="DevFlow Backend",
        key="DEV",
        description=None,
    )

    db.scalars.return_value.first.return_value = expected_project

    result = repository.get_by_key(
        organization_id,
        "DEV",
    )

    assert result is expected_project
    db.scalars.assert_called_once()


def test_create_project() -> None:
    db = MagicMock()
    repository = ProjectRepository(db)

    organization_id = uuid.uuid4()

    data = ProjectCreate(
        name="DevFlow Backend",
        key="DEV",
        description="Backend project",
    )

    result = repository.create(
        data=data,
        organization_id=organization_id,
    )

    added_project = db.add.call_args.args[0]

    assert isinstance(added_project, Project)
    assert added_project.organization_id == organization_id
    assert added_project.name == "DevFlow Backend"
    assert added_project.key == "DEV"
    assert added_project.description == "Backend project"

    assert result is added_project

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_project)


def test_list_for_organization() -> None:
    db = MagicMock()
    repository = ProjectRepository(db)

    organization_id = uuid.uuid4()

    projects = [
        Project(
            organization_id=organization_id,
            name="Backend",
            key="BACK",
            description=None,
        ),
        Project(
            organization_id=organization_id,
            name="Frontend",
            key="FRONT",
            description=None,
        ),
    ]

    db.scalars.return_value.all.return_value = projects

    result = repository.list_for_organization(organization_id)

    assert result == projects
    db.scalars.assert_called_once()
