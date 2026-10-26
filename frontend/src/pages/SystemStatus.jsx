import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { LoadingState, ErrorState } from "../components/Shared";

export default function SystemStatus() {
  const health = useFetch(() => api.health(), []);

  return (
    <>
      <h1 style={{ marginBottom: 16 }}>System Status</h1>

      <div className="card">
        <div className="card-header"><h2>API Health</h2></div>
        {health.loading ? <LoadingState /> : health.error ? <ErrorState message={health.error} /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Property</th><th>Value</th></tr></thead>
              <tbody>
                <tr><td>API Status</td><td style={{ fontWeight: 600, color: health.data?.status === "ok" ? "var(--success)" : "var(--error)" }}>{health.data?.status}</td></tr>
                <tr><td>Database</td><td>{health.data?.database}</td></tr>
                <tr><td>DB Path</td><td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{health.data?.db_path}</td></tr>
              </tbody>
            </table>
          </div>
        )}
        <button className="btn" style={{ marginTop: 12 }} onClick={health.refresh}>Refresh</button>
      </div>

      <div className="card">
        <div className="card-header"><h2>Stack</h2></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Layer</th><th>Technology</th></tr></thead>
            <tbody>
              <tr><td>Frontend</td><td>React 19 + Vite + Recharts + Lucide</td></tr>
              <tr><td>Backend</td><td>Python + FastAPI + Uvicorn</td></tr>
              <tr><td>Database</td><td>SQLite (read-only analytics queries)</td></tr>
              <tr><td>Data</td><td>Synthetic dataset — 12,965 orders, 1,200 customers, 40 products</td></tr>
              <tr><td>Assistant</td><td>Rule-based keyword routing to parameterised SQL — no paid API</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h2>Dataset Notes</h2></div>
        <ul style={{ fontSize: "0.82rem", color: "var(--text-2)", lineHeight: 2, paddingLeft: 18 }}>
          <li>Dataset is synthetic — generated to simulate a quick-commerce grocery platform.</li>
          <li>118 orders have no recorded order_amount (~0.9%).</li>
          <li>2,629 orders have no recorded delivery_minutes (~20%).</li>
          <li>656 order_id values appear more than once — all correspond to pending orders.</li>
          <li>All customer and product foreign keys are valid (no orphan references).</li>
          <li>Date range: April 2025 – September 2025.</li>
          <li>Revenue figures are recorded amounts only, not verified accounting revenue.</li>
        </ul>
      </div>
    </>
  );
}
