# Tests

Repository-level full-stack tests live here. Backend unit, route, and integration tests live under `backend/tests/`.

## Browser E2E

`tests/e2e/` contains browser tests that exercise:

```text
Browser → React frontend → FastAPI backend → PostgreSQL
```

The suite currently covers:

- registration and authentication
- workspace creation
- project creation
- issue creation and update
- comments
- labels, assignment, and filtering
- two-user organization invitation link flow
- invited-user registration/login redirect back to the invitation
- invitation acceptance
- pending invitation inbox after a normal sign-in
- shared workspace/project visibility for the invited member
- outsider project-access denial

Run locally after the backend and frontend are available:

```bash
cd tests/e2e
npm install
npx playwright install chromium
npm test
```

GitHub Actions provisions PostgreSQL, applies Alembic migrations, starts FastAPI and Vite, installs Chromium, and runs the same suite automatically.
