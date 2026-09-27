import type { PropsWithChildren, ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { initials } from "../utils/format";

interface AppShellProps extends PropsWithChildren {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}

export function AppShell({ children, title, subtitle, actions }: AppShellProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/" className="brand">
          <span className="brand-mark">D</span>
          <span>DevFlow</span>
        </Link>

        <nav className="side-nav" aria-label="Primary navigation">
          <Link className={location.pathname === "/" ? "active" : ""} to="/">
            <span className="nav-icon">⌂</span>
            Workspaces
          </Link>
          <a href="https://github.com/Mhmdhalim/devflow" target="_blank" rel="noreferrer">
            <span className="nav-icon">↗</span>
            Repository
          </a>
        </nav>

        <div className="sidebar-spacer" />
        <div className="user-panel">
          <div className="avatar">{initials(user?.full_name ?? "User")}</div>
          <div className="user-copy">
            <strong>{user?.full_name}</strong>
            <span>{user?.email}</span>
          </div>
          <button className="icon-button subtle" type="button" onClick={handleLogout} title="Sign out">
            ↪
          </button>
        </div>
      </aside>

      <main className="main-area">
        {(title || actions) && (
          <header className="page-header">
            <div>
              {title ? <h1>{title}</h1> : null}
              {subtitle ? <p>{subtitle}</p> : null}
            </div>
            {actions ? <div className="page-actions">{actions}</div> : null}
          </header>
        )}
        {children}
      </main>
    </div>
  );
}
