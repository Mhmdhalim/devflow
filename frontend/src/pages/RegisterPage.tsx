import { type FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { ErrorMessage } from "../components/StatusMessage";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(fullName.trim(), email.trim(), password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create account");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-layout">
      <section className="auth-hero auth-hero--alt">
        <div className="auth-brand">
          <span className="brand-mark large">D</span>
          <span>DevFlow</span>
        </div>
        <div className="hero-copy">
          <span className="eyebrow light">A clean start</span>
          <h1>Turn ideas into trackable work.</h1>
          <p>Create an account, open a workspace, and move issues from todo to done.</p>
          <div className="feature-list compact">
            <span>✓ Organization workspaces</span>
            <span>✓ Project-scoped issue numbers</span>
            <span>✓ Comments and labels</span>
          </div>
        </div>
        <span className="auth-version">DevFlow · v1.0.0</span>
      </section>

      <section className="auth-panel">
        <form className="auth-card" onSubmit={submit}>
          <div>
            <span className="eyebrow">Create account</span>
            <h2>Start using DevFlow</h2>
            <p>Your account is created directly against the backend v1 API.</p>
          </div>
          <ErrorMessage message={error} />
          <label className="field">
            <span>Full name</span>
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Your full name" required />
          </label>
          <label className="field">
            <span>Email address</span>
            <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required />
          </label>
          <label className="field">
            <span>Password</span>
            <input type="password" minLength={8} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 8 characters" required />
          </label>
          <button className="button primary full" disabled={submitting} type="submit">
            {submitting ? "Creating account…" : "Create account"}
          </button>
          <p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p>
        </form>
      </section>
    </div>
  );
}
