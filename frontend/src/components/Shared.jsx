// Shared UI primitives used across all pages

export function MetricCard({ label, value, sub }) {
  return (
    <div className="metric-card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {sub && <div className="sub">{sub}</div>}
    </div>
  );
}

export function Badge({ status }) {
  return <span className={`badge ${status?.toLowerCase()}`}>{status}</span>;
}

export function LoadingState({ text = "Loading…" }) {
  return <div className="loading">{text}</div>;
}

export function ErrorState({ message }) {
  return <div className="error-msg">{message}</div>;
}

export function EmptyState({ text = "No data available." }) {
  return <div className="empty">{text}</div>;
}

export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="tabs">
      {tabs.map((t) => (
        <div
          key={t}
          className={`tab${active === t ? " active" : ""}`}
          onClick={() => onChange(t)}
        >
          {t}
        </div>
      ))}
    </div>
  );
}

export function Pagination({ page, totalPages, onChange }) {
  return (
    <div className="pagination">
      <button className="btn" onClick={() => onChange(1)} disabled={page === 1}>«</button>
      <button className="btn" onClick={() => onChange(page - 1)} disabled={page === 1}>‹</button>
      <span>Page {page} of {totalPages}</span>
      <button className="btn" onClick={() => onChange(page + 1)} disabled={page === totalPages}>›</button>
      <button className="btn" onClick={() => onChange(totalPages)} disabled={page === totalPages}>»</button>
    </div>
  );
}

export function fmtINR(v) {
  if (v == null) return "—";
  return "₹" + Number(v).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function fmtNum(v) {
  if (v == null) return "—";
  return Number(v).toLocaleString("en-IN");
}

export function fmtDate(v) {
  if (!v) return "—";
  return v.slice(0, 16).replace("T", " ");
}
