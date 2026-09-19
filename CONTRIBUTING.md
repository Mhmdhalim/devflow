# Contributing to DevFlow

DevFlow uses an issue-driven development workflow.

## Workflow

1. Create or select a GitHub Issue.
2. Confirm the acceptance criteria.
3. Create a branch from `main`.
4. Implement the smallest complete change.
5. Add or update tests.
6. Run local quality checks.
7. Open a Pull Request.
8. Ensure CI passes.
9. Resolve review comments.
10. Merge only when the Definition of Done is satisfied.

## Branch naming

```text
feat/<issue-number>-short-description
fix/<issue-number>-short-description
test/<issue-number>-short-description
docs/<issue-number>-short-description
refactor/<issue-number>-short-description
```

## Commit messages

Use clear Conventional Commit-style messages, for example:

```text
feat(auth): add refresh token rotation
fix(issues): reject invalid status transition
test(auth): cover expired access tokens
docs(database): document issue relationships
```

## Definition of Done

- Acceptance criteria are satisfied.
- Tests are added or updated where appropriate.
- Local quality checks pass.
- CI is green.
- Documentation is updated when behavior or architecture changes.
- Database migrations are included when required.
- No secrets or credentials are committed.
