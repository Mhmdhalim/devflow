# Changelog

All notable changes to DevFlow are documented here.

## [Unreleased]

### Added

- React + TypeScript frontend
- full-stack Playwright E2E coverage
- organization invitations and member management
- pending invitation inbox
- Render deployment blueprint
- Docker Compose full-stack frontend/API/PostgreSQL environment
- container smoke CI

### Changed

- frontend API traffic uses a dedicated `/api` prefix for local and Docker reverse proxies
- user emails are normalized before persistence and lookup
- project assignees are restricted to organization members
- input validation rejects whitespace-only names, titles, labels, and comments

### Security

- removed unauthenticated global user listing/detail endpoints
- invitation tokens are stored as hashes
- invitation acceptance is restricted to the invited email
- authorization remains enforced on the backend for organization/project resources
