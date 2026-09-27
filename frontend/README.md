# DevFlow Frontend

React + TypeScript frontend for DevFlow.

## Stack

- React 18
- TypeScript
- Vite
- React Router
- Native Fetch API
- Responsive CSS
- Nginx production container

## Local development

Run the FastAPI backend on `http://127.0.0.1:8000`, then from this directory:

```bash
npm install
npm run typecheck
npm run dev
```

Open `http://localhost:5173`.

The Vite dev server sends API requests through the local `/api` reverse proxy to `127.0.0.1:8000`. This avoids frontend/backend route collisions and the Windows IPv6 `localhost` mismatch.

To expose the frontend to another device on the same local network:

```bash
npm run dev -- --host 0.0.0.0
```

Use the Network URL printed by Vite. A `localhost` URL always points to the device opening it.

## Production build

```bash
npm run build
npm run preview
```

## Docker

The frontend Dockerfile builds the React application and serves it through Nginx. In Docker Compose, Nginx proxies `/api/*` to the `api` service and falls back to `index.html` for client-side routes such as invitation deep links.

## Product flows represented

- registration and JWT login
- authenticated session hydration
- organizations/workspaces and membership roles
- team member listing
- secure invitation links
- pending invitation inbox and acceptance
- organization projects
- project issue board
- issue creation and partial updates
- organization-scoped assignees
- priorities and statuses
- comments
- project labels and assignment
- label-based issue filtering
- backend health/readiness status
