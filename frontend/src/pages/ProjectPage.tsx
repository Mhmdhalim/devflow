import { type FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { api } from "../api/devflow";
import { AppShell } from "../components/AppShell";
import { Modal } from "../components/Modal";
import { EmptyState, ErrorMessage, LoadingBlock } from "../components/StatusMessage";
import { useAuth } from "../context/AuthContext";
import type { Comment, Issue, IssuePriority, IssueStatus, Label, Organization, OrganizationMember, Project } from "../types";
import { formatDate, initials } from "../utils/format";

const columns: Array<{ status: IssueStatus; title: string; hint: string }> = [
  { status: "todo", title: "Todo", hint: "Ready to start" },
  { status: "in_progress", title: "In progress", hint: "Currently moving" },
  { status: "done", title: "Done", hint: "Completed work" },
];

function priorityLabel(priority: IssuePriority) {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

function errorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback;
}

export function ProjectPage() {
  const { projectId = "" } = useParams();
  const { user } = useAuth();
  const [project, setProject] = useState<Project | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [labels, setLabels] = useState<Label[]>([]);
  const [users, setUsers] = useState<OrganizationMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterLabel, setFilterLabel] = useState("");

  const [createIssueOpen, setCreateIssueOpen] = useState(false);
  const [createLabelOpen, setCreateLabelOpen] = useState(false);
  const [issueTitle, setIssueTitle] = useState("");
  const [issueDescription, setIssueDescription] = useState("");
  const [issuePriority, setIssuePriority] = useState<IssuePriority>("medium");
  const [issueAssignee, setIssueAssignee] = useState("");
  const [labelName, setLabelName] = useState("");
  const [labelColor, setLabelColor] = useState("#7c3aed");
  const [submitting, setSubmitting] = useState(false);

  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [selectedLabels, setSelectedLabels] = useState<Label[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [commentBody, setCommentBody] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editStatus, setEditStatus] = useState<IssueStatus>("todo");
  const [editPriority, setEditPriority] = useState<IssuePriority>("medium");
  const [editAssignee, setEditAssignee] = useState("");

  const loadMetadata = useCallback(async () => {
    const orgs = await api.organizations();
    for (const org of orgs) {
      const orgProjects = await api.projects(org.id);
      const found = orgProjects.find((item) => item.id === projectId);
      if (found) {
        setProject(found);
        setOrganization(org);
        return org;
      }
    }
    throw new Error("Project not found in your accessible organizations");
  }, [projectId]);

  const loadBoard = useCallback(async (organizationId: string, labelId?: string) => {
    const [issueList, labelList, userList] = await Promise.all([
      api.issues(projectId, labelId || undefined),
      api.labels(projectId),
      api.organizationMembers(organizationId),
    ]);
    setIssues(issueList);
    setLabels(labelList);
    setUsers(userList);
  }, [projectId]);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const currentOrganization = await loadMetadata();
        await loadBoard(currentOrganization.id);
      } catch (err) {
        if (!cancelled) setError(errorMessage(err, "Unable to load this project"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void run();
    return () => { cancelled = true; };
  }, [loadMetadata, loadBoard]);

  useEffect(() => {
    if (loading) return;
    void api.issues(projectId, filterLabel || undefined)
      .then(setIssues)
      .catch((err) => setError(errorMessage(err, "Unable to filter issues")));
  }, [filterLabel, projectId, loading]);

  const usersById = useMemo(
    () => Object.fromEntries(users.map((item) => [item.user_id, item])),
    [users],
  );
  const canManage = organization?.role === "owner" || organization?.role === "admin";

  const openIssue = async (issue: Issue) => {
    setSelectedIssue(issue);
    setDetailLoading(true);
    setError(null);
    try {
      const [fresh, issueComments, issueLabels] = await Promise.all([
        api.issue(projectId, issue.number),
        api.comments(projectId, issue.number),
        api.issueLabels(projectId, issue.number),
      ]);
      setSelectedIssue(fresh);
      setComments(issueComments);
      setSelectedLabels(issueLabels);
      setEditTitle(fresh.title);
      setEditDescription(fresh.description ?? "");
      setEditStatus(fresh.status);
      setEditPriority(fresh.priority);
      setEditAssignee(fresh.assignee_id ?? "");
    } catch (err) {
      setError(errorMessage(err, "Unable to open issue"));
    } finally {
      setDetailLoading(false);
    }
  };

  const refreshSelected = async (issueNumber: number) => {
    const [fresh, issueComments, issueLabels] = await Promise.all([
      api.issue(projectId, issueNumber),
      api.comments(projectId, issueNumber),
      api.issueLabels(projectId, issueNumber),
    ]);
    setSelectedIssue(fresh);
    setComments(issueComments);
    setSelectedLabels(issueLabels);
    setEditTitle(fresh.title);
    setEditDescription(fresh.description ?? "");
    setEditStatus(fresh.status);
    setEditPriority(fresh.priority);
    setEditAssignee(fresh.assignee_id ?? "");
    if (organization) {
      await loadBoard(organization.id, filterLabel);
    }
  };

  const submitIssue = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createIssue(projectId, {
        title: issueTitle.trim(),
        description: issueDescription.trim() || null,
        priority: issuePriority,
        assignee_id: issueAssignee || null,
      });
      setIssueTitle("");
      setIssueDescription("");
      setIssuePriority("medium");
      setIssueAssignee("");
      setCreateIssueOpen(false);
      if (organization) {
        await loadBoard(organization.id, filterLabel);
      }
    } catch (err) {
      setError(errorMessage(err, "Unable to create issue"));
    } finally {
      setSubmitting(false);
    }
  };

  const submitLabel = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createLabel(projectId, { name: labelName.trim(), color: labelColor || null });
      setLabelName("");
      setLabelColor("#7c3aed");
      setCreateLabelOpen(false);
      setLabels(await api.labels(projectId));
    } catch (err) {
      setError(errorMessage(err, "Unable to create label"));
    } finally {
      setSubmitting(false);
    }
  };

  const saveIssue = async () => {
    if (!selectedIssue) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.updateIssue(projectId, selectedIssue.number, {
        title: editTitle.trim(),
        description: editDescription.trim() || null,
        status: editStatus,
        priority: editPriority,
        assignee_id: editAssignee || null,
      });
      await refreshSelected(selectedIssue.number);
    } catch (err) {
      setError(errorMessage(err, "Unable to update issue"));
    } finally {
      setSubmitting(false);
    }
  };

  const addComment = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedIssue || !commentBody.trim()) return;
    setSubmitting(true);
    try {
      await api.createComment(projectId, selectedIssue.number, commentBody.trim());
      setCommentBody("");
      setComments(await api.comments(projectId, selectedIssue.number));
    } catch (err) {
      setError(errorMessage(err, "Unable to add comment"));
    } finally {
      setSubmitting(false);
    }
  };

  const toggleLabel = async (label: Label) => {
    if (!selectedIssue) return;
    const assigned = selectedLabels.some((item) => item.id === label.id);
    try {
      if (assigned) await api.removeLabel(projectId, selectedIssue.number, label.id);
      else await api.assignLabel(projectId, selectedIssue.number, label.id);
      setSelectedLabels(await api.issueLabels(projectId, selectedIssue.number));
      if (organization) {
        await loadBoard(organization.id, filterLabel);
      }
    } catch (err) {
      setError(errorMessage(err, "Unable to change issue labels"));
    }
  };

  if (loading) {
    return <AppShell title="Project"><LoadingBlock label="Loading project board…" /></AppShell>;
  }

  if (!project || !organization) {
    return <AppShell title="Project"><ErrorMessage message={error ?? "Project not found"} /><Link className="button secondary" to="/">Back to workspaces</Link></AppShell>;
  }

  return (
    <AppShell
      title={project.name}
      subtitle={`${organization.name} / ${project.key} · ${project.description || "No description"}`}
      actions={<><button className="button secondary" onClick={() => setCreateLabelOpen(true)}>+ Label</button><button className="button primary" onClick={() => setCreateIssueOpen(true)}>+ New issue</button></>}
    >
      <ErrorMessage message={error} />

      <div className="project-toolbar">
        <div className="breadcrumb"><Link to="/">Workspaces</Link><span>/</span><b>{project.key}</b></div>
        <label className="filter-control"><span>Filter by label</span><select value={filterLabel} onChange={(event) => setFilterLabel(event.target.value)}><option value="">All issues</option>{labels.map((label) => <option key={label.id} value={label.id}>{label.name}</option>)}</select></label>
      </div>

      {issues.length === 0 && !filterLabel ? (
        <EmptyState title="No issues yet" body="Create the first issue to start moving work through the board." action={<button className="button primary" onClick={() => setCreateIssueOpen(true)}>Create issue</button>} />
      ) : (
        <section className="board">
          {columns.map((column) => {
            const columnIssues = issues.filter((issue) => issue.status === column.status);
            return (
              <div className="board-column" key={column.status}>
                <header><div><h2>{column.title}</h2><p>{column.hint}</p></div><span className="count-badge">{columnIssues.length}</span></header>
                <div className="issue-stack">
                  {columnIssues.map((issue) => {
                    const assignee = issue.assignee_id ? usersById[issue.assignee_id] : undefined;
                    return (
                      <button className="issue-card" key={issue.id} onClick={() => void openIssue(issue)}>
                        <div className="issue-card-top"><span className={`priority-dot priority-${issue.priority}`} /><span>{project.key}-{issue.number}</span><span className={`priority-text priority-${issue.priority}`}>{priorityLabel(issue.priority)}</span></div>
                        <h3>{issue.title}</h3>
                        <p>{issue.description || "No description"}</p>
                        <div className="issue-card-footer"><span>{formatDate(issue.updated_at)}</span>{assignee ? <span className="mini-avatar" title={assignee.full_name}>{initials(assignee.full_name)}</span> : <span className="unassigned">Unassigned</span>}</div>
                      </button>
                    );
                  })}
                  {columnIssues.length === 0 ? <div className="column-empty">No issues</div> : null}
                </div>
              </div>
            );
          })}
        </section>
      )}

      <Modal open={createIssueOpen} title="Create issue" description={`Add work to ${project.key}.`} onClose={() => setCreateIssueOpen(false)} wide>
        <form className="stack-form" onSubmit={submitIssue}>
          <label className="field"><span>Title</span><input value={issueTitle} onChange={(event) => setIssueTitle(event.target.value)} required maxLength={200} placeholder="Add API pagination" /></label>
          <label className="field"><span>Description <em>optional</em></span><textarea value={issueDescription} onChange={(event) => setIssueDescription(event.target.value)} rows={5} placeholder="Describe the expected outcome…" /></label>
          <div className="field-row"><label className="field"><span>Priority</span><select value={issuePriority} onChange={(event) => setIssuePriority(event.target.value as IssuePriority)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label><label className="field"><span>Assignee</span><select value={issueAssignee} onChange={(event) => setIssueAssignee(event.target.value)}><option value="">Unassigned</option>{users.map((item) => <option key={item.user_id} value={item.user_id}>{item.full_name}</option>)}</select></label></div>
          <div className="form-actions"><button className="button secondary" type="button" onClick={() => setCreateIssueOpen(false)}>Cancel</button><button className="button primary" disabled={submitting} type="submit">{submitting ? "Creating…" : "Create issue"}</button></div>
        </form>
      </Modal>

      <Modal open={createLabelOpen} title="Create label" description="Labels help group and filter project issues." onClose={() => setCreateLabelOpen(false)}>
        <form className="stack-form" onSubmit={submitLabel}>
          <label className="field"><span>Name</span><input value={labelName} onChange={(event) => setLabelName(event.target.value)} required maxLength={50} placeholder="backend" /></label>
          <label className="field"><span>Color</span><div className="color-field"><input type="color" value={labelColor} onChange={(event) => setLabelColor(event.target.value)} /><input value={labelColor} onChange={(event) => setLabelColor(event.target.value)} pattern="#[0-9A-Fa-f]{6}" /></div></label>
          {!canManage ? <p className="field-note">Your membership may not permit creating labels; the backend will enforce the organization role.</p> : null}
          <div className="form-actions"><button className="button secondary" type="button" onClick={() => setCreateLabelOpen(false)}>Cancel</button><button className="button primary" disabled={submitting} type="submit">Create label</button></div>
        </form>
      </Modal>

      <Modal open={Boolean(selectedIssue)} title={selectedIssue ? `${project.key}-${selectedIssue.number} · ${selectedIssue.title}` : "Issue"} onClose={() => setSelectedIssue(null)} wide>
        {detailLoading || !selectedIssue ? <LoadingBlock label="Loading issue…" /> : (
          <div className="issue-detail-grid">
            <div className="issue-detail-main">
              <label className="field"><span>Title</span><input value={editTitle} onChange={(event) => setEditTitle(event.target.value)} maxLength={200} /></label>
              <label className="field"><span>Description</span><textarea rows={7} value={editDescription} onChange={(event) => setEditDescription(event.target.value)} placeholder="No description yet" /></label>
              <div className="detail-section"><div className="section-heading"><div><h3>Comments</h3><p>{comments.length} conversation item{comments.length === 1 ? "" : "s"}</p></div></div><div className="comment-list">{comments.map((comment) => { const author = usersById[comment.author_id]; return <article className="comment" key={comment.id}><div className="mini-avatar">{initials(author?.full_name ?? "User")}</div><div><header><strong>{author?.full_name ?? "User"}</strong><span>{formatDate(comment.created_at)}</span></header><p>{comment.body}</p></div></article>; })}{comments.length === 0 ? <p className="muted">No comments yet.</p> : null}</div><form className="comment-form" onSubmit={addComment}><textarea rows={3} value={commentBody} onChange={(event) => setCommentBody(event.target.value)} placeholder="Add a comment…" required /><button className="button primary small" disabled={submitting || !commentBody.trim()} type="submit">Comment</button></form></div>
            </div>
            <aside className="issue-detail-side">
              <div className="side-block"><h3>Properties</h3><label className="field compact"><span>Status</span><select value={editStatus} onChange={(event) => setEditStatus(event.target.value as IssueStatus)}><option value="todo">Todo</option><option value="in_progress">In progress</option><option value="done">Done</option></select></label><label className="field compact"><span>Priority</span><select value={editPriority} onChange={(event) => setEditPriority(event.target.value as IssuePriority)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label><label className="field compact"><span>Assignee</span><select value={editAssignee} onChange={(event) => setEditAssignee(event.target.value)}><option value="">Unassigned</option>{users.map((item) => <option key={item.user_id} value={item.user_id}>{item.full_name}{item.user_id === user?.id ? " (you)" : ""}</option>)}</select></label><button className="button primary full" disabled={submitting || !editTitle.trim()} onClick={() => void saveIssue()} type="button">{submitting ? "Saving…" : "Save changes"}</button></div>
              <div className="side-block"><div className="section-heading"><div><h3>Labels</h3><p>Click to toggle</p></div></div><div className="label-picker">{labels.map((label) => { const assigned = selectedLabels.some((item) => item.id === label.id); return <button type="button" className={`label-chip${assigned ? " selected" : ""}`} key={label.id} onClick={() => void toggleLabel(label)}><span style={{ backgroundColor: label.color ?? "#98a2b3" }} />{label.name}{assigned ? " ✓" : ""}</button>; })}{labels.length === 0 ? <p className="muted">No project labels.</p> : null}</div></div>
              <div className="side-block metadata"><h3>Details</h3><dl><div><dt>Reporter</dt><dd>{usersById[selectedIssue.reporter_id]?.full_name ?? "Unknown"}</dd></div><div><dt>Created</dt><dd>{formatDate(selectedIssue.created_at)}</dd></div><div><dt>Updated</dt><dd>{formatDate(selectedIssue.updated_at)}</dd></div></dl></div>
            </aside>
          </div>
        )}
      </Modal>
    </AppShell>
  );
}
