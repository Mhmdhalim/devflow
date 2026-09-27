import uuid

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.user import User

EXPECTED_TABLES = {
    "alembic_version",
    "users",
    "organizations",
    "memberships",
    "projects",
    "issues",
    "comments",
    "labels",
    "issue_labels",
    "organization_invitations",
}


def test_postgresql_schema_and_user_round_trip() -> None:
    assert engine.dialect.name == "postgresql"

    inspector = inspect(engine)
    actual_tables = set(inspector.get_table_names())

    assert EXPECTED_TABLES <= actual_tables

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        email = f"integration-{uuid.uuid4()}@example.com"

        user = User(
            email=email,
            full_name="Integration Test User",
            hashed_password="not-a-real-password-hash",
            is_active=True,
        )

        session.add(user)
        session.flush()

        saved_user = session.scalar(select(User).where(User.email == email))

        assert saved_user is not None
        assert saved_user.id == user.id
        assert saved_user.email == email
        assert saved_user.full_name == "Integration Test User"

    finally:
        session.close()
        transaction.rollback()
        connection.close()
