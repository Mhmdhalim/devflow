# QA and Testing

DevFlow uses multiple test layers instead of relying on one smoke test.

## Backend tests

Run from `backend/`:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy app
```

Coverage includes services, repositories, API routes, authentication, authorization boundaries, validation, invitations, issue assignee membership, comments, labels, and PostgreSQL integration.

## PostgreSQL integration

CI starts PostgreSQL 18, applies Alembic migrations to a clean database, and verifies real SQLAlchemy persistence plus expected schema tables.

## Browser E2E

Playwright runs against a real FastAPI + PostgreSQL stack.

The E2E suite covers:

- registration and login
- workspace creation
- project creation
- issue creation/update
- comments
- labels and filtering
- owner → invited member invitation link flow
- second browser context registration/login
- invitation acceptance
- shared workspace/project visibility
- outsider isolation
- pending invitation inbox after normal sign-in

## Container smoke test

Container CI builds the full Docker Compose stack and verifies:

- frontend container availability
- Nginx → FastAPI `/api` routing
- readiness
- SPA deep-link fallback
- migrations

A change is ready to merge only when all relevant CI workflows are green.
