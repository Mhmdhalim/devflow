# Database Design

DevFlow uses PostgreSQL as its persistent data store. The schema is managed through SQLAlchemy models and Alembic migrations.

## Main domains

### Users and authentication

- `users`

Passwords are stored as password hashes. Authentication uses JWT access tokens.

### Organizations, memberships, and invitations

- `organizations`
- `memberships`
- `organization_invitations`

A membership links a user to an organization with one of three roles: `owner`, `admin`, or `member`. A user can have only one membership per organization.

Invitations are scoped to one organization and one invited email. They store a SHA-256 token hash rather than the plaintext invite token, have an expiry timestamp, and record acceptance. Invitation roles are limited to `admin` or `member`.

### Projects

- `projects`

Each project belongs to one organization. Project keys are unique within that organization.

### Issues

- `issues`

Each issue belongs to one project and has a project-scoped sequential number, title, optional description, status, priority, reporter, optional assignee, and timestamps.

Statuses are `todo`, `in_progress`, or `done`. Priorities are `low`, `medium`, or `high`. The `(project_id, number)` pair is unique.

### Comments

- `comments`

Comments belong to issues and reference their author.

### Labels

- `labels`
- `issue_labels`

Labels are project-scoped and unique by `(project_id, name)`. `issue_labels` is the many-to-many join table between issues and labels.

## Current application tables

```text
users
organizations
memberships
organization_invitations
projects
issues
comments
labels
issue_labels
```

Alembic also maintains `alembic_version` for migration metadata.

## Relationships

```text
users
  ├── memberships ── organizations
  ├── sent organization_invitations ── organizations
  ├── reported issues
  ├── assigned issues
  └── comments

organizations
  ├── memberships
  ├── organization_invitations
  └── projects

projects
  ├── issues
  └── labels

issues
  ├── comments
  └── issue_labels ── labels
```

Foreign keys preserve relational integrity, while unique and check constraints enforce important domain rules at the database layer.

## Schema sources

The authoritative schema is defined by:

1. SQLAlchemy models in `backend/app/models/`
2. Alembic migrations in `backend/migrations/`
3. `docs/database/schema.dbml`

The visual ERD in this directory is a companion representation; the models and migrations remain authoritative.

## Future scope

- refresh-token persistence
- project-specific membership tables
- multiple issue assignees
- attachments
- audit logs
