# DevFlow Backend

Backend API for **DevFlow**, built with FastAPI.

## Requirements

* Python 3.12
* uv

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

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   ├── core/
│   │   └── config.py
│   └── main.py
├── tests/
│   └── test_health.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Development Checks

Before committing changes, run:

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

All checks should pass before opening a Pull Request.

## PostgreSQL

DevFlow uses PostgreSQL for persistent application data.

Start the local PostgreSQL container:

```bash
docker start devflow-postgres
```

Check that it is running:

```bash
docker ps
```

The backend reads the database connection from `backend/.env`.

Example:

```env
DATABASE_URL=postgresql+psycopg://devflow:change_me@localhost:5432/devflow
```

Do not commit the real `.env` file. Use `.env.example` as the shared configuration template.

To verify the database connection:

```bash
uv run python -c "from sqlalchemy import text; from app.db.session import engine; conn = engine.connect(); print(conn.execute(text('SELECT 1')).scalar()); conn.close()"
```

Expected output:

```text
1
```
