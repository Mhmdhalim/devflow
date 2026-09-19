# DevFlow

**DevFlow** is a production-oriented issue and project management platform built as a portfolio-grade backend engineering project.

The project is designed to demonstrate practical skills relevant to Python/backend development, software engineering internships, working-student roles, and QA/test automation.

## Project goals

DevFlow is intentionally built like a real engineering product rather than a tutorial application. The repository will demonstrate API design with FastAPI, PostgreSQL data modelling, service/repository layers, authentication and authorization, Redis, background processing, automated testing, Docker, CI/CD, and engineering documentation.

## Architecture

DevFlow starts as a **modular monolith**.

```text
Client
  ↓
FastAPI
  ↓
Router
  ↓
Service
  ↓
Repository
  ↓
PostgreSQL
```

Detailed diagrams live in `docs/architecture/`.

![DevFlow system architecture](docs/architecture/diagrams/01-system-architecture.png)

## Documentation

- [Architecture](docs/architecture/overview.md)
- [Database design](docs/database/database-design.md)
- [Engineering workflow](docs/planning/engineering-workflow.md)
- [Architecture decisions](docs/decisions/)

## Current status

**Phase: Engineering Foundation**

## Development principle

```text
Requirement
→ GitHub Issue
→ Design
→ Branch
→ Implementation
→ Tests
→ Pull Request
→ CI
→ Merge
→ Documentation
```
