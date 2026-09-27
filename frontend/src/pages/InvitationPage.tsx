import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { api } from "../api/devflow";
import { AppShell } from "../components/AppShell";
import { ErrorMessage, LoadingBlock } from "../components/StatusMessage";
import { useAuth } from "../context/AuthContext";
import type { OrganizationInvitationDetail } from "../types";
import { formatDate } from "../utils/format";

export function InvitationPage() {
  const { token = "" } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [invitation, setInvitation] = useState<OrganizationInvitationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await api.invitation(token);
        if (!cancelled) setInvitation(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Unable to load invitation");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const accept = async () => {
    setAccepting(true);
    setError(null);

    try {
      await api.acceptInvitation(token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to accept invitation");
    } finally {
      setAccepting(false);
    }
  };

  if (loading) {
    return (
      <AppShell title="Invitation">
        <LoadingBlock label="Checking invitation…" />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Workspace invitation"
      subtitle="Join an existing DevFlow organization."
      actions={<Link className="button secondary" to="/">Back to workspaces</Link>}
    >
      <ErrorMessage message={error} />

      {invitation ? (
        <section className="invite-accept-card">
          <span className="eyebrow">You are invited</span>
          <h2>{invitation.organization_name}</h2>
          <p>
            <strong>{user?.email}</strong> has been invited as{" "}
            <span className="member-role">{invitation.role}</span>.
          </p>
          <p className="muted">
            This invitation expires {formatDate(invitation.expires_at)}.
          </p>
          <button
            className="button primary"
            type="button"
            disabled={accepting}
            onClick={accept}
          >
            {accepting ? "Joining workspace…" : "Accept invitation"}
          </button>
        </section>
      ) : null}
    </AppShell>
  );
}
