# Deployment

DevFlow supports local Docker Compose and includes a Render Blueprint for a public portfolio deployment.

## Local Docker Compose

Create `backend/.env` from the example and run:

```bash
docker compose up --build
```

The stack contains:

```text
Browser
  ↓
Nginx / React :5173
  ↓ /api
FastAPI :8000
  ↓
PostgreSQL :5432
```

The API container runs `alembic upgrade head` before starting Uvicorn and fails startup if migrations fail.

## Render

`render.yaml` defines:

- a FastAPI web service
- a React static site
- a PostgreSQL database
- generated production secret key
- database connection wiring
- frontend API base URL
- production CORS origin

The Render Blueprint must be created/deployed from the Render dashboard before the public URLs exist. Committing `render.yaml` alone does not create Render services.

Expected service names are:

```text
devflow-api-mhmdhalim
devflow-mhmdhalim
devflow-db-mhmdhalim
```

After deployment, verify `/ready`, `/docs`, registration/login, workspace creation, invitation acceptance with a second account, shared project access, and outsider denial before publishing a Live Demo link.
