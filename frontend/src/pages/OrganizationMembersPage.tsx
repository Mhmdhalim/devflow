import { type FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { api } from "../api/devflow";
import { AppShell } from "../components/AppShell";
import { ErrorMessage, LoadingBlock } from "../components/StatusMessage";
import type {
  InvitationRole,
  Organization,
  OrganizationInvitation,
  OrganizationMember,
} from "../types";
import { formatDate, initials } from "../utils/format";

function errorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback;
}

export function OrganizationMembersPage() {
  const { organizationId = "" } = useParams();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [invitations, setInvitations] = useState<OrganizationInvitation[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<InvitationRole>("member");
  const [inviteUrl, setInviteUrl] = useState("");
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canManage = useMemo(
    () => organization?.role === "owner" || organization?.role === "admin",
    [organization],
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const organizations = await api.organizations();
      const current = organizations.find((item) => item.id === organizationId);

      if (!current) {
        throw new Error("Workspace not found");
      }

      setOrganization(current);

      const memberList = await api.organizationMembers(organizationId);
      setMembers(memberList);

      if (current.role === "owner" || current.role === "admin") {
        setInvitations(await api.pendingInvitations(organizationId));
      } else {
        setInvitations([]);
      }
    } catch (err) {
      setError(errorMessage(err, "Unable to load workspace members"));
    } finally {
      setLoading(false);
    }
  }, [organizationId]);

  useEffect(() => {
    void load();
  }, [load]);

  const submitInvitation = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setInviteUrl("");
    setCopied(false);

    try {
      const invitation = await api.createInvitation(organizationId, {
        email: email.trim(),
        role,
      });

      setInviteUrl(
        `${window.location.origin}/invite/${invitation.token}`,
      );
      setEmail("");
      setRole("member");
      setInvitations(await api.pendingInvitations(organizationId));
    } catch (err) {
      setError(errorMessage(err, "Unable to create invitation"));
    } finally {
      setSubmitting(false);
    }
  };

  const copyInvite = async () => {
    if (!inviteUrl) return;

    try {
      await navigator.clipboard.writeText(inviteUrl);
      setCopied(true);
    } catch {
      setError("Unable to copy the invite link. Copy it manually instead.");
    }
  };

  if (loading) {
    return (
      <AppShell title="Members">
        <LoadingBlock label="Loading workspace members…" />
      </AppShell>
    );
  }

  if (!organization) {
    return (
      <AppShell title="Members">
        <ErrorMessage message={error ?? "Workspace not found"} />
        <Link className="button secondary" to="/">Back to workspaces</Link>
      </AppShell>
    );
  }

  return (
    <AppShell
      title={`${organization.name} members`}
      subtitle="Manage who can collaborate inside this workspace."
      actions={<Link className="button secondary" to="/">Back to workspaces</Link>}
    >
      <ErrorMessage message={error} />

      <section className="team-grid">
        <div className="team-card">
          <div className="section-heading">
            <div>
              <h2>Members</h2>
              <p>{members.length} people currently have access.</p>
            </div>
          </div>

          <div className="member-list">
            {members.map((member) => (
              <div className="member-row" key={member.user_id}>
                <div className="avatar">{initials(member.full_name)}</div>
                <div className="member-copy">
                  <strong>{member.full_name}</strong>
                  <span>{member.email}</span>
                </div>
                <span className="member-role">{member.role}</span>
              </div>
            ))}
          </div>
        </div>

        {canManage ? (
          <div className="team-card">
            <div className="section-heading">
              <div>
                <h2>Invite a teammate</h2>
                <p>Invite links expire after 7 days.</p>
              </div>
            </div>

            <form className="stack-form" onSubmit={submitInvitation}>
              <label className="field">
                <span>Email address</span>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="teammate@example.com"
                  required
                />
              </label>

              <label className="field">
                <span>Role</span>
                <select
                  value={role}
                  onChange={(event) => setRole(event.target.value as InvitationRole)}
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                </select>
              </label>

              <button className="button primary" type="submit" disabled={submitting}>
                {submitting ? "Creating invite…" : "Create invite"}
              </button>
            </form>

            {inviteUrl ? (
              <div className="invite-box">
                <strong>Invitation created</strong>
                <p>Send this link to the invited email address.</p>
                <div className="invite-link-row">
                  <input value={inviteUrl} readOnly />
                  <button className="button secondary small" type="button" onClick={copyInvite}>
                    {copied ? "Copied" : "Copy"}
                  </button>
                </div>
              </div>
            ) : null}

            <div className="pending-block">
              <h3>Pending invitations</h3>
              {invitations.length === 0 ? (
                <p className="muted">No pending invitations.</p>
              ) : (
                <div className="pending-list">
                  {invitations.map((invitation) => (
                    <div className="pending-row" key={invitation.id}>
                      <div>
                        <strong>{invitation.email}</strong>
                        <span>Expires {formatDate(invitation.expires_at)}</span>
                      </div>
                      <span className="member-role">{invitation.role}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : null}
      </section>
    </AppShell>
  );
}
