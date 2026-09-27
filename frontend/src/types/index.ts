export type IssueStatus = "todo" | "in_progress" | "done";
export type IssuePriority = "low" | "medium" | "high";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Issue {
  id: string;
  project_id: string;
  number: number;
  title: string;
  description: string | null;
  status: IssueStatus;
  priority: IssuePriority;
  reporter_id: string;
  assignee_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  issue_id: string;
  author_id: string;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface Label {
  id: string;
  project_id: string;
  name: string;
  color: string | null;
  created_at: string;
  updated_at: string;
}

export interface HealthResponse {
  status: string;
}
