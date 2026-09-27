import uuid
from unittest.mock import MagicMock

from app.models.membership import Membership
from app.repositories.membership import MembershipRepository


def test_get_for_user_and_organization() -> None:
    db = MagicMock()
    repository = MembershipRepository(db)

    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    membership = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role="owner",
    )

    db.scalars.return_value.first.return_value = membership

    result = repository.get_for_user_and_organization(
        user_id=user_id,
        organization_id=organization_id,
    )

    assert result is membership
    db.scalars.assert_called_once()
