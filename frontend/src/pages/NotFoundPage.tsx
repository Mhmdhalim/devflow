import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="fullscreen-center not-found">
      <span className="eyebrow">404</span>
      <h1>Page not found</h1>
      <p>The page you requested is not part of this DevFlow workspace.</p>
      <Link className="button primary" to="/">Back to workspaces</Link>
    </div>
  );
}
