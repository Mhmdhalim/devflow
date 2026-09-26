import uuid
from unittest.mock import MagicMock

import pytest

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate
from app.services.organization import (
    OrganizationAlreadyExistsError,
    OrganizationService,
)


def test_create_organization() -> None:
    repository = MagicMock()
    service = OrganizationService(repository)

    owner_id = uuid.uuid4()

    data = OrganizationCreate(
        name="DevFlow",
        slug="devflow",
    )

    expected_organization = Organization(
        name="DevFlow",
        slug="devflow",
    )

    repository.get_by_slug.return_value = None
    repository.create_with_membership.return_value = expected_organization

    result = service.create_organization(
        data,
        owner_id,
    )

    assert result is expected_organization

    repository.get_by_slug.assert_called_once_with("devflow")

    repository.create_with_membership.assert_called_once_with(
        data=data,
        user_id=owner_id,
        role="owner",
    )


def test_create_organization_with_existing_slug() -> None:
    repository = MagicMock()
    service = OrganizationService(repository)

    owner_id = uuid.uuid4()

    data = OrganizationCreate(
        name="DevFlow",
        slug="devflow",
    )

    repository.get_by_slug.return_value = Organization(
        name="Existing DevFlow",
        slug="devflow",
    )

    with pytest.raises(OrganizationAlreadyExistsError):
        service.create_organization(
            data,
            owner_id,
        )

    repository.create_with_membership.assert_not_called()
