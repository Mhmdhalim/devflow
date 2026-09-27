# DevFlow

**DevFlow** is a full-stack issue and project management platform built as a portfolio-grade software engineering project.

It demonstrates practical backend and full-stack engineering skills with Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, React, TypeScript, Docker, automated tests, and CI.

## Core capabilities

- JWT registration, login, and authenticated sessions
- Organizations/workspaces with owner, admin, and member roles
- Secure organization invitations and pending-invitation inbox
- Projects scoped to organizations
- Project-scoped sequential issue numbers
- Issue creation, updates, assignees, priorities, and statuses
- Comments and project labels
- Label assignment and issue filtering
- Backend authorization on organization and project boundaries
- React frontend with protected routes
- PostgreSQL persistence and Alembic migrations
- Docker Compose full-stack environment
- GitHub Actions backend, browser E2E, and container smoke CI

## Architecture

DevFlow is a modular monolith with a separate browser client:

```text
Browser
  ↓
React + TypeScript
  ↓
FastAPI
  ↓
Router → Service → Repository
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

Detailed architecture documentation lives in [docs/architecture](docs/architecture/).

![DevFlow system architecture](docs/architecture/diagrams/01-system-architecture.svg)

## Documentation

- [API](docs/api/README.md)
- [Architecture](docs/architecture/overview.md)
- [Database design](docs/database/database-design.md)
- [Deployment](docs/deployment/README.md)
- [QA and testing](docs/qa/README.md)
- [Engineering workflow](docs/planning/engineering-workflow.md)
- [Architecture decisions](docs/decisions/)

## Local full-stack run

Create the local environment file once:

```bash
cp backend/.env.example backend/.env
```

Then start PostgreSQL, FastAPI, and the production-style Nginx frontend:

```bash
docker compose up --build
```

Open:

```text
Frontend:  http://localhost:5173
API:       http://localhost:8000
API docs:  http://localhost:8000/docs
Health:    http://localhost:8000/health
Readiness: http://localhost:8000/ready
```

For frontend hot reload, run the backend/PostgreSQL locally and use `npm run dev` from `frontend/`.

## Quality gates

Backend CI validates:

- PostgreSQL 18 migrations
- pytest unit/route/integration tests
- Ruff lint and formatting
- mypy

E2E CI validates browser workflows against a real FastAPI + PostgreSQL stack, including the two-user invitation journey.

Container CI builds the Docker Compose stack and checks Nginx → FastAPI routing, readiness, SPA deep links, and migrations.

## Development workflow

```text
Requirement
→ GitHub Issue
→ Branch
→ Implementation
→ Tests
→ Pull Request
→ CI
→ Merge
→ Documentation
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch and pull-request workflow.
