# DevFlow Frontend

React + TypeScript frontend for DevFlow Backend v1.0.0.

## Stack

- React 18
- TypeScript
- Vite
- React Router
- Native Fetch API
- Responsive CSS
- Nginx production container

## Local development

Run the DevFlow backend on `http://localhost:8000`, then:

```bash
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:5173`.

Vite proxies the backend routes to port `8000`, so the backend does not need a development CORS change.

## Production build

```bash
npm run build
npm run preview
```

## Docker

The included `Dockerfile` builds the frontend and serves it through Nginx. The included Nginx configuration expects the backend Docker Compose service to be named `api`, matching the current DevFlow compose configuration.

## Backend features represented

- registration and JWT login
- current-user session
- organizations and membership roles
- organization projects
- project issue board
- issue creation and partial updates
- priorities and statuses
- issue comments
- project labels
- issue-label assignment and removal
- label-based issue filtering
- API health/readiness status
