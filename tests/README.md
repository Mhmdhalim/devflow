# Tests

Repository-level tests live here.

## E2E

`tests/e2e/` contains Playwright browser tests that exercise the full DevFlow stack:

browser → React frontend → FastAPI backend → PostgreSQL

The smoke test covers registration, workspace creation, project creation, issue creation and update, comments, labels, and label filtering.

Run locally after the backend and frontend are available:

```bash
cd tests/e2e
npm install
npx playwright install chromium
npm test
```

GitHub Actions runs the same flow automatically with PostgreSQL, database migrations, the backend API, the frontend, and Chromium.
