import { apiRequest } from "./client";
import type {
  Comment,
  HealthResponse,
  InvitationRole,
  Issue,
  IssuePriority,
  IssueStatus,
  Label,
  Organization,
  OrganizationInvitation,
  OrganizationInvitationCreated,
  OrganizationInvitationDetail,
  OrganizationMember,
  Project,
  TokenResponse,
  User,
} from "../types";

export const api = {
  register: (payload: { email: string; full_name: string; password: string }) =>
    apiRequest<User>("/users", {
      method: "POST",
      body: JSON.stringify(payload),
    }, false),

  login: (payload: { email: string; password: string }) =>
    apiRequest<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }, false),

  me: () => apiRequest<User>("/auth/me"),
  health: () => apiRequest<HealthResponse>("/health", {}, false),
  ready: () => apiRequest<HealthResponse>("/ready", {}, false),

  organizations: () => apiRequest<Organization[]>("/organizations"),
  createOrganization: (payload: { name: string; slug: string }) =>
    apiRequest<Organization>("/organizations", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  organizationMembers: (organizationId: string) =>
    apiRequest<OrganizationMember[]>(
      `/organizations/${organizationId}/members`,
    ),

  pendingInvitations: (organizationId: string) =>
    apiRequest<OrganizationInvitation[]>(
      `/organizations/${organizationId}/invitations`,
    ),

  createInvitation: (
    organizationId: string,
    payload: { email: string; role: InvitationRole },
  ) =>
    apiRequest<OrganizationInvitationCreated>(
      `/organizations/${organizationId}/invitations`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    ),

  invitation: (token: string) =>
    apiRequest<OrganizationInvitationDetail>(
      `/invitations/${encodeURIComponent(token)}`,
    ),

  acceptInvitation: (token: string) =>
    apiRequest<Organization>(
      `/invitations/${encodeURIComponent(token)}/accept`,
      { method: "POST" },
    ),

  projects: (organizationId: string) =>
    apiRequest<Project[]>(`/organizations/${organizationId}/projects`),
  createProject: (
    organizationId: string,
    payload: { name: string; key: string; description: string | null },
  ) =>
    apiRequest<Project>(`/organizations/${organizationId}/projects`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  issues: (projectId: string, labelId?: string) => {
    const query = labelId ? `?label_id=${encodeURIComponent(labelId)}` : "";
    return apiRequest<Issue[]>(`/projects/${projectId}/issues${query}`);
  },
  issue: (projectId: string, issueNumber: number) =>
    apiRequest<Issue>(`/projects/${projectId}/issues/${issueNumber}`),
  createIssue: (
    projectId: string,
    payload: {
      title: string;
      description: string | null;
      priority: IssuePriority;
      assignee_id: string | null;
    },
  ) =>
    apiRequest<Issue>(`/projects/${projectId}/issues`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateIssue: (
    projectId: string,
    issueNumber: number,
    payload: Partial<{
      title: string;
      description: string | null;
      status: IssueStatus;
      priority: IssuePriority;
      assignee_id: string | null;
    }>,
  ) =>
    apiRequest<Issue>(`/projects/${projectId}/issues/${issueNumber}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  comments: (projectId: string, issueNumber: number) =>
    apiRequest<Comment[]>(
      `/projects/${projectId}/issues/${issueNumber}/comments`,
    ),
  createComment: (projectId: string, issueNumber: number, body: string) =>
    apiRequest<Comment>(
      `/projects/${projectId}/issues/${issueNumber}/comments`,
      { method: "POST", body: JSON.stringify({ body }) },
    ),

  labels: (projectId: string) =>
    apiRequest<Label[]>(`/projects/${projectId}/labels`),
  createLabel: (projectId: string, payload: { name: string; color: string | null }) =>
    apiRequest<Label>(`/projects/${projectId}/labels`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  issueLabels: (projectId: string, issueNumber: number) =>
    apiRequest<Label[]>(`/projects/${projectId}/issues/${issueNumber}/labels`),
  assignLabel: (projectId: string, issueNumber: number, labelId: string) =>
    apiRequest<Label>(
      `/projects/${projectId}/issues/${issueNumber}/labels/${labelId}`,
      { method: "POST" },
    ),
  removeLabel: (projectId: string, issueNumber: number, labelId: string) =>
    apiRequest<void>(
      `/projects/${projectId}/issues/${issueNumber}/labels/${labelId}`,
      { method: "DELETE" },
    ),
};
