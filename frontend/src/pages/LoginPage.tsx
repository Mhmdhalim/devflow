import { type FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { ErrorMessage } from "../components/StatusMessage";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to={from} replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-layout">
      <section className="auth-hero">
        <div className="auth-brand">
          <span className="brand-mark large">D</span>
          <span>DevFlow</span>
        </div>
        <div className="hero-copy">
          <span className="eyebrow light">Backend engineering, visible.</span>
          <h1>Ship work with less noise.</h1>
          <p>
            A focused workspace for projects, issues, comments, and labels — powered by the DevFlow backend v1.
          </p>
          <div className="hero-proof">
            <div><strong>FastAPI</strong><span>REST API</span></div>
            <div><strong>PostgreSQL</strong><span>Persistent data</span></div>
            <div><strong>JWT</strong><span>Secure access</span></div>
          </div>
        </div>
        <span className="auth-version">DevFlow · v1.0.0</span>
      </section>

      <section className="auth-panel">
        <form className="auth-card" onSubmit={submit}>
          <div>
            <span className="eyebrow">Welcome back</span>
            <h2>Sign in to DevFlow</h2>
            <p>Use the account registered with your DevFlow API.</p>
          </div>
          <ErrorMessage message={error} />
          <label className="field">
            <span>Email address</span>
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              required
            />
          </label>
          <button className="button primary full" disabled={submitting} type="submit">
            {submitting ? "Signing in…" : "Sign in"}
          </button>
          <p className="auth-switch">
            New to DevFlow?{" "}
            <Link to="/register" state={{ from }}>Create an account</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
