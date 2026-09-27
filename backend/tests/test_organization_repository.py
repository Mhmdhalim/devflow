import uuid
from unittest.mock import MagicMock

from app.models.membership import Membership
from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate


def test_get_by_slug() -> None:
    db = MagicMock()
    repository = OrganizationRepository(db)

    expected_organization = Organization(
        name="DevFlow",
        slug="devflow",
    )

    db.scalars.return_value.first.return_value = expected_organization

    result = repository.get_by_slug("devflow")

    assert result is expected_organization
    db.scalars.assert_called_once()


def test_create_with_membership() -> None:
    db = MagicMock()
    repository = OrganizationRepository(db)

    owner_id = uuid.uuid4()

    data = OrganizationCreate(
        name="DevFlow",
        slug="devflow",
    )

    def assign_organization_id() -> None:
        organization = db.add.call_args_list[0].args[0]
        organization.id = uuid.uuid4()

    db.flush.side_effect = assign_organization_id

    organization = repository.create_with_membership(
        data=data,
        user_id=owner_id,
        role="owner",
    )

    added_objects = [call.args[0] for call in db.add.call_args_list]

    assert len(added_objects) == 2

    added_organization = added_objects[0]
    added_membership = added_objects[1]

    assert isinstance(
        added_organization,
        Organization,
    )
    assert isinstance(
        added_membership,
        Membership,
    )

    assert added_organization.name == "DevFlow"
    assert added_organization.slug == "devflow"

    assert added_membership.user_id == owner_id
    assert added_membership.organization_id == added_organization.id
    assert added_membership.role == "owner"

    assert organization is added_organization

    db.flush.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_organization)


def test_list_for_user() -> None:
    db = MagicMock()
    repository = OrganizationRepository(db)

    user_id = uuid.uuid4()

    organization = Organization(
        name="DevFlow",
        slug="devflow",
    )

    db.execute.return_value.all.return_value = [
        (
            organization,
            "owner",
        )
    ]

    result = repository.list_for_user(user_id)

    assert result == [
        (
            organization,
            "owner",
        )
    ]

    db.execute.assert_called_once()
