# DevFlow API

FastAPI exposes interactive OpenAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

## Authentication

Register with `POST /users`, then authenticate with `POST /auth/login`.

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

`GET /auth/me` returns the current authenticated user.

## Endpoint groups

### Organizations and access

- `GET /organizations`
- `POST /organizations`
- `GET /organizations/{organization_id}/members`
- `GET /organizations/{organization_id}/invitations`
- `POST /organizations/{organization_id}/invitations`
- `GET /invitations` — current user's pending invitations
- `GET /invitations/{token}`
- `POST /invitations/{token}/accept`
- `POST /invitations/by-id/{invitation_id}/accept`

### Projects

- `GET /organizations/{organization_id}/projects`
- `POST /organizations/{organization_id}/projects`

### Issues

- `GET /projects/{project_id}/issues`
- `POST /projects/{project_id}/issues`
- `GET /projects/{project_id}/issues/{issue_number}`
- `PATCH /projects/{project_id}/issues/{issue_number}`

### Comments and labels

- issue comment create/list endpoints
- project label create/list endpoints
- issue label assign/remove/list endpoints
- optional issue filtering by `label_id`

## Authorization model

Registration does not grant organization access. Backend services verify organization membership for private resources. Owner/admin roles manage projects, labels, and invitations; members can participate in accessible project workflows. Issue assignees must belong to the project's organization.

The frontend is not treated as an authorization boundary; access control is enforced by FastAPI.
