import type { ReactNode } from "react";

export function ErrorMessage({ message }: { message: string | null }) {
  return message ? <div className="alert alert-error">{message}</div> : null;
}

export function LoadingBlock({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="loading-block" role="status">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  );
}

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">◇</div>
      <h3>{title}</h3>
      <p>{body}</p>
      {action}
    </div>
  );
}
