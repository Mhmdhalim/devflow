# DevFlow Backend

Backend API for **DevFlow**, built with FastAPI.

## Requirements

* Python 3.12
* uv
* Docker

## Setup

From the `backend` directory:

```bash
uv sync
```

This installs the project dependencies using `pyproject.toml` and `uv.lock`.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Health Check

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Run Tests

```bash
uv run pytest
```

For verbose output:

```bash
uv run pytest -v
```

## Lint

```bash
uv run ruff check .
```

Automatically fix supported issues:

```bash
uv run ruff check . --fix
```

Format the code:

```bash
uv run ruff format .
```

## Type Checking

```bash
uv run mypy app
```

## Development Checks

Before committing changes, run:

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

All checks should pass before opening a Pull Request.

## PostgreSQL with Docker Compose

DevFlow uses PostgreSQL for persistent application data.

From the repository root, start the local PostgreSQL service:

```bash
docker compose up -d
```

Check the service status:

```bash
docker compose ps
```

View PostgreSQL logs:

```bash
docker compose logs postgres
```

Stop the local infrastructure:

```bash
docker compose down
```

PostgreSQL data is persisted in the named Docker volume `devflow_pgdata`. Running `docker compose down` keeps this volume. Running `docker compose down -v` also removes the volume and should only be used when intentionally resetting local database data.

The backend reads database configuration from `backend/.env`. Do not commit the real `.env` file; use `backend/.env.example` as the shared template.

Example:

```env
DATABASE_URL=postgresql+psycopg://devflow:change_me@localhost:5432/devflow
```

To verify the database connection:

```bash
uv run python -c "from sqlalchemy import text; from app.db.session import engine; conn = engine.connect(); print(conn.execute(text('SELECT 1')).scalar()); conn.close()"
```

Expected output:

```text
1
```

## Database Migrations

DevFlow uses Alembic to manage PostgreSQL schema changes.

Create a new migration:

```bash
uv run alembic revision -m "migration description"
```

Create a migration automatically from SQLAlchemy model changes:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

Apply all pending migrations:

```bash
uv run alembic upgrade head
```

Show the current database revision:

```bash
uv run alembic current
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

Alembic reads the database URL from the same application settings used by the FastAPI backend.

## Pre-commit

Install the Git hooks:

```bash
uv run pre-commit install