import { type FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../api/client";
import { api } from "../api/devflow";
import { AppShell } from "../components/AppShell";
import { Modal } from "../components/Modal";
import { EmptyState, ErrorMessage, LoadingBlock } from "../components/StatusMessage";
import type { Organization, Project } from "../types";
import { slugify } from "../utils/format";

interface ProjectMap { [organizationId: string]: Project[] }

export function DashboardPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [projects, setProjects] = useState<ProjectMap>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<"checking" | "ready" | "degraded">("checking");
  const [orgModal, setOrgModal] = useState(false);
  const [projectOrg, setProjectOrg] = useState<Organization | null>(null);

  const [orgName, setOrgName] = useState("");
  const [orgSlug, setOrgSlug] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    setError(null);
    setLoading(true);
    try {
      const orgs = await api.organizations();
      setOrganizations(orgs);
      const entries = await Promise.all(
        orgs.map(async (org) => [org.id, await api.projects(org.id)] as const),
      );
      setProjects(Object.fromEntries(entries));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to load workspaces");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
    void Promise.all([api.health(), api.ready()])
      .then(() => setHealth("ready"))
      .catch(() => setHealth("degraded"));
  }, []);

  const projectCount = useMemo(
    () => Object.values(projects).reduce((total, list) => total + list.length, 0),
    [projects],
  );

  const submitOrganization = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await api.createOrganization({ name: orgName.trim(), slug: orgSlug.trim() });
      setOrgName("");
      setOrgSlug("");
      setOrgModal(false);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create workspace");
    } finally {
      setSubmitting(false);
    }
  };

  const submitProject = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectOrg) return;
    setError(null);
    setSubmitting(true);
    try {
      await api.createProject(projectOrg.id, {
        name: projectName.trim(),
        key: projectKey.trim().toUpperCase(),
        description: projectDescription.trim() || null,
      });
      setProjectName("");
      setProjectKey("");
      setProjectDescription("");
      setProjectOrg(null);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create project");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell
      title="Workspaces"
      subtitle="Your organizations, projects, and backend status in one place."
      actions={<button className="button primary" onClick={() => setOrgModal(true)}>+ New workspace</button>}
    >
      <ErrorMessage message={error} />

      <section className="stats-grid">
        <div className="stat-card"><span>Workspaces</span><strong>{organizations.length}</strong><small>Organizations you belong to</small></div>
        <div className="stat-card"><span>Projects</span><strong>{projectCount}</strong><small>Across accessible workspaces</small></div>
        <div className="stat-card"><span>Backend</span><strong className={health === "ready" ? "status-good" : health === "degraded" ? "status-bad" : ""}>{health === "ready" ? "Ready" : health === "degraded" ? "Degraded" : "Checking"}</strong><small>/health + /ready</small></div>
      </section>

      {loading ? <LoadingBlock label="Loading your workspaces…" /> : organizations.length === 0 ? (
        <EmptyState
          title="Create your first workspace"
          body="Organizations are the top-level home for your DevFlow projects."
          action={<button className="button primary" onClick={() => setOrgModal(true)}>Create workspace</button>}
        />
      ) : (
        <div className="workspace-list">
          {organizations.map((org) => {
            const orgProjects = projects[org.id] ?? [];
            const canCreate = org.role === "owner" || org.role === "admin";
            return (
              <section className="workspace-card" key={org.id}>
                <header className="workspace-header">
                  <div className="workspace-ident">
                    <div className="workspace-logo">{org.name.slice(0, 1).toUpperCase()}</div>
                    <div><h2>{org.name}</h2><p>{org.slug} · <span className="role-pill">{org.role}</span></p></div>
                  </div>
                  {canCreate ? <button className="button secondary small" onClick={() => setProjectOrg(org)}>+ Project</button> : null}
                </header>
                {orgProjects.length === 0 ? (
                  <div className="inline-empty">No projects yet{canCreate ? " — create the first one." : "."}</div>
                ) : (
                  <div className="project-grid">
                    {orgProjects.map((project) => (
                      <Link className="project-card" to={`/projects/${project.id}`} state={{ project, organization: org }} key={project.id}>
                        <div className="project-key">{project.key}</div>
                        <h3>{project.name}</h3>
                        <p>{project.description || "No project description yet."}</p>
                        <span className="project-open">Open board <b>→</b></span>
                      </Link>
                    ))}
                  </div>
                )}
              </section>
            );
          })}
        </div>
      )}

      <Modal
        open={orgModal}
        title="New workspace"
        description="Create an organization. You will become its owner."
        onClose={() => setOrgModal(false)}
      >
        <form className="stack-form" onSubmit={submitOrganization}>
          <label className="field"><span>Name</span><input value={orgName} onChange={(event) => { const value = event.target.value; setOrgName(value); if (!orgSlug) setOrgSlug(slugify(value)); }} placeholder="Acme Engineering" required maxLength={120} /></label>
          <label className="field"><span>Slug</span><input value={orgSlug} onChange={(event) => setOrgSlug(slugify(event.target.value))} placeholder="acme-engineering" pattern="[a-z0-9]+(?:-[a-z0-9]+)*" required maxLength={120} /></label>
          <div className="form-actions"><button className="button secondary" type="button" onClick={() => setOrgModal(false)}>Cancel</button><button className="button primary" disabled={submitting} type="submit">{submitting ? "Creating…" : "Create workspace"}</button></div>
        </form>
      </Modal>

      <Modal
        open={Boolean(projectOrg)}
        title="New project"
        description={projectOrg ? `Create a project inside ${projectOrg.name}.` : undefined}
        onClose={() => setProjectOrg(null)}
      >
        <form className="stack-form" onSubmit={submitProject}>
          <label className="field"><span>Project name</span><input value={projectName} onChange={(event) => setProjectName(event.target.value)} placeholder="Platform API" required maxLength={120} /></label>
          <label className="field"><span>Key</span><input value={projectKey} onChange={(event) => setProjectKey(event.target.value.toUpperCase().replace(/[^A-Z0-9]/g, ""))} placeholder="API" required maxLength={20} /></label>
          <label className="field"><span>Description <em>optional</em></span><textarea value={projectDescription} onChange={(event) => setProjectDescription(event.target.value)} placeholder="What is this project responsible for?" rows={4} /></label>
          <div className="form-actions"><button className="button secondary" type="button" onClick={() => setProjectOrg(null)}>Cancel</button><button className="button primary" disabled={submitting} type="submit">{submitting ? "Creating…" : "Create project"}</button></div>
        </form>
      </Modal>
    </AppShell>
  );
}
