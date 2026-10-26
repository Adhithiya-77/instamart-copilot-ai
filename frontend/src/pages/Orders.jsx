import { useState, useEffect, useCallback } from "react";
import { Search } from "lucide-react";
import { api } from "../api/client";
import {
  Badge, LoadingState, ErrorState, EmptyState,
  Pagination, fmtINR, fmtNum, fmtDate
} from "../components/Shared";

const STATUSES = ["", "completed", "cancelled", "pending"];

export default function Orders() {
  const [rows, setRows]         = useState([]);
  const [total, setTotal]       = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const [page, setPage]         = useState(1);
  const [search, setSearch]     = useState("");
  const [status, setStatus]     = useState("");
  const [sortBy, setSortBy]     = useState("order_ts");
  const [sortDir, setSortDir]   = useState("desc");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo]     = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const data = await api.orders.list({
        page, page_size: 50, search, status,
        sort_by: sortBy, sort_dir: sortDir,
        date_from: dateFrom, date_to: dateTo,
      });
      setRows(data.data);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, [page, search, status, sortBy, sortDir, dateFrom, dateTo]);

  useEffect(() => { load(); }, [load]);

  function handleSort(col) {
    if (sortBy === col) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortBy(col); setSortDir("desc"); }
    setPage(1);
  }

  function SortIndicator({ col }) {
    if (sortBy !== col) return null;
    return <span style={{ marginLeft: 4 }}>{sortDir === "asc" ? "▲" : "▼"}</span>;
  }

  return (
    <>
      <h1 style={{ marginBottom: 16 }}>Orders</h1>

      <div className="controls-row">
        <div style={{ position: "relative" }}>
          <Search size={13} style={{ position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", color: "var(--text-2)" }} />
          <input
            type="text"
            placeholder="Search order ID or customer ID…"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            style={{ paddingLeft: 28, width: 260 }}
          />
        </div>
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
          <option value="">All statuses</option>
          {STATUSES.filter(Boolean).map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <input type="date" value={dateFrom} onChange={e => { setDateFrom(e.target.value); setPage(1); }} title="From date" />
        <input type="date" value={dateTo}   onChange={e => { setDateTo(e.target.value);   setPage(1); }} title="To date" />
        <button className="btn" onClick={() => { setSearch(""); setStatus(""); setDateFrom(""); setDateTo(""); setPage(1); }}>
          Clear
        </button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", fontSize: "0.82rem", color: "var(--text-2)" }}>
          {loading ? "Loading…" : `${fmtNum(total)} orders`}
        </div>

        {error && <ErrorState message={error} />}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Product</th>
                <th onClick={() => handleSort("order_ts")} style={{ cursor: "pointer" }}>
                  Date <SortIndicator col="order_ts" />
                </th>
                <th>Qty</th>
                <th onClick={() => handleSort("status")} style={{ cursor: "pointer" }}>
                  Status <SortIndicator col="status" />
                </th>
                <th onClick={() => handleSort("order_amount")} style={{ cursor: "pointer" }}>
                  Amount <SortIndicator col="order_amount" />
                </th>
                <th onClick={() => handleSort("delivery_minutes")} style={{ cursor: "pointer" }}>
                  Delivery (min) <SortIndicator col="delivery_minutes" />
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8}><LoadingState /></td></tr>
              ) : !rows.length ? (
                <tr><td colSpan={8}><EmptyState text="No orders match the current filters." /></td></tr>
              ) : rows.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{r.order_id}</td>
                  <td>{r.customer_id}</td>
                  <td>{r.product_name ?? r.product_id}</td>
                  <td style={{ whiteSpace: "nowrap" }}>{fmtDate(r.order_ts)}</td>
                  <td>{r.quantity ?? "—"}</td>
                  <td><Badge status={r.status} /></td>
                  <td>{fmtINR(r.order_amount)}</td>
                  <td>{r.delivery_minutes != null ? r.delivery_minutes.toFixed(0) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div style={{ padding: "8px 16px" }}>
            <Pagination page={page} totalPages={totalPages} onChange={p => setPage(p)} />
          </div>
        )}
      </div>
    </>
  );
}
