import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { MetricCard, LoadingState, ErrorState, fmtNum } from "../components/Shared";

function PassFail({ ok }) {
  return (
    <span style={{
      padding: "2px 8px", borderRadius: 3, fontSize: "0.72rem", fontWeight: 600,
      background: ok ? "#E6F0E6" : "#F5E6E4",
      color: ok ? "var(--success)" : "var(--error)",
    }}>
      {ok ? "Pass" : "Fail"}
    </span>
  );
}

export default function DataQuality() {
  const summary  = useFetch(() => api.dataQuality.summary(), []);
  const dups     = useFetch(() => api.dataQuality.duplicates(), []);
  const nulls    = useFetch(() => api.dataQuality.columnNulls(), []);
  const missing  = useFetch(() => api.dataQuality.missingAmounts(), []);

  const s = summary.data;

  return (
    <>
      <h1 style={{ marginBottom: 4 }}>Data Quality Report</h1>
      <p style={{ color: "var(--text-2)", fontSize: "0.82rem", marginBottom: 20 }}>
        Validation findings from the Instamart SQLite database. No records are modified from this page.
      </p>

      {summary.error && <ErrorState message={summary.error} />}

      <div className="metrics-grid">
        <MetricCard label="Total Orders"           value={s ? fmtNum(s.total_orders) : "…"} />
        <MetricCard label="Missing Amounts"        value={s ? fmtNum(s.missing_amounts) : "…"}
          sub={s ? `${s.missing_amounts_pct}% of orders` : ""} />
        <MetricCard label="Missing Delivery Times" value={s ? fmtNum(s.missing_delivery) : "…"}
          sub={s ? `${s.missing_delivery_pct}% of orders` : ""} />
        <MetricCard label="Duplicate Order IDs"    value={s ? fmtNum(s.duplicate_order_ids) : "…"} />
        <MetricCard label="Orphan FK Refs"         value={s ? fmtNum(s.orphan_customer_refs + s.orphan_product_refs) : "…"} />
        <MetricCard label="Completed w/ No Amount" value={s ? fmtNum(s.completed_missing_amount) : "…"} />
      </div>

      <div className="card">
        <div className="card-header"><h2>Referential Integrity</h2></div>
        {summary.loading ? <LoadingState /> : s && (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Check</th><th>Violations</th><th>Result</th></tr></thead>
              <tbody>
                <tr>
                  <td>Orders → valid customer_id</td>
                  <td>{fmtNum(s.orphan_customer_refs)}</td>
                  <td><PassFail ok={s.orphan_customer_refs === 0} /></td>
                </tr>
                <tr>
                  <td>Orders → valid product_id</td>
                  <td>{fmtNum(s.orphan_product_refs)}</td>
                  <td><PassFail ok={s.orphan_product_refs === 0} /></td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header"><h2>Missing Values per Column (orders table)</h2></div>
        {nulls.loading ? <LoadingState /> : nulls.error ? <ErrorState message={nulls.error} /> :
          <div className="table-wrap">
            <table>
              <thead><tr><th>Column</th><th>Missing</th><th>Percentage</th><th>Result</th></tr></thead>
              <tbody>
                {(nulls.data ?? []).map((r, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: "monospace" }}>{r.column}</td>
                    <td>{fmtNum(r.missing)}</td>
                    <td>{r.pct}%</td>
                    <td><PassFail ok={r.missing === 0} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        }
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Duplicate Order IDs</h2>
        </div>
        <p style={{ fontSize: "0.82rem", color: "var(--text-2)", marginBottom: 12 }}>
          These order_id values appear more than once. All correspond to <strong>pending</strong> orders —
          each pending order shares an ID with its originating record. This is a known characteristic of the dataset.
        </p>
        {dups.loading ? <LoadingState /> : dups.error ? <ErrorState message={dups.error} /> :
          !dups.data?.length ? <div className="empty">No duplicates found.</div> :
          <div className="table-wrap">
            <table>
              <thead><tr><th>Order ID</th><th>Occurrences</th><th>Statuses</th></tr></thead>
              <tbody>
                {dups.data.map((r, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{r.order_id}</td>
                    <td>{r.occurrences}</td>
                    <td style={{ fontSize: "0.78rem", color: "var(--text-2)" }}>{r.statuses}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        }
      </div>

      <div className="card">
        <div className="card-header"><h2>Sample Orders with Missing Amounts</h2></div>
        {missing.loading ? <LoadingState /> : missing.error ? <ErrorState message={missing.error} /> :
          !missing.data?.length ? <div className="empty">No orders with missing amounts.</div> :
          <div className="table-wrap">
            <table>
              <thead><tr><th>Order ID</th><th>Customer</th><th>Product</th><th>Date</th><th>Status</th></tr></thead>
              <tbody>
                {missing.data.map((r, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{r.order_id}</td>
                    <td>{r.customer_id}</td>
                    <td>{r.product_id}</td>
                    <td>{r.order_ts ? r.order_ts.slice(0, 10) : "—"}</td>
                    <td>{r.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        }
      </div>
    </>
  );
}
