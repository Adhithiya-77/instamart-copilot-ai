import { useState } from "react";
import { Search } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { LoadingState, ErrorState, EmptyState, fmtINR, fmtNum } from "../components/Shared";

export default function Customers() {
  const [search, setSearch] = useState("");
  const [city, setCity]     = useState("");
  const [sortBy, setSortBy] = useState("order_count");
  const [sortDir, setSortDir] = useState("desc");

  const cities    = useFetch(() => api.customers.cities(), []);
  const customers = useFetch(
    () => api.customers.list({ search, city, sort_by: sortBy, sort_dir: sortDir, limit: 200 }),
    [search, city, sortBy, sortDir]
  );
  const cityDist  = useFetch(() => api.analytics.cities(), []);

  function handleSort(col) {
    if (sortBy === col) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortBy(col); setSortDir("desc"); }
  }

  function SortInd({ col }) {
    if (sortBy !== col) return null;
    return <span style={{ marginLeft: 4 }}>{sortDir === "asc" ? "▲" : "▼"}</span>;
  }

  return (
    <>
      <h1 style={{ marginBottom: 16 }}>Customers</h1>

      <div className="charts-row">
        <div className="card">
          <div className="card-header"><h2>Customers by City</h2></div>
          {cityDist.loading ? <LoadingState /> : cityDist.error ? <ErrorState message={cityDist.error} /> :
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={cityDist.data?.slice(0, 10)} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="city" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="customers" fill="#68734A" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          }
        </div>
        <div className="card">
          <div className="card-header"><h2>Orders by City</h2></div>
          {cityDist.loading ? <LoadingState /> : cityDist.error ? <ErrorState message={cityDist.error} /> :
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={cityDist.data?.slice(0, 10)} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="city" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="orders" fill="#A0AB7E" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          }
        </div>
      </div>

      <div className="controls-row">
        <div style={{ position: "relative" }}>
          <Search size={13} style={{ position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", color: "var(--text-2)" }} />
          <input
            type="text"
            placeholder="Search customer ID…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: 28, width: 220 }}
          />
        </div>
        <select value={city} onChange={e => setCity(e.target.value)}>
          <option value="">All cities</option>
          {(cities.data ?? []).map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <button className="btn" onClick={() => { setSearch(""); setCity(""); }}>Clear</button>
      </div>

      {customers.error && <ErrorState message={customers.error} />}

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", fontSize: "0.82rem", color: "var(--text-2)" }}>
          {customers.loading ? "Loading…" : `${customers.data?.length ?? 0} customers`}
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>City</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Signup Date</th>
                <th onClick={() => handleSort("order_count")} style={{ cursor: "pointer" }}>
                  Orders <SortInd col="order_count" />
                </th>
                <th onClick={() => handleSort("recorded_spend")} style={{ cursor: "pointer" }}>
                  Recorded Spend <SortInd col="recorded_spend" />
                </th>
              </tr>
            </thead>
            <tbody>
              {customers.loading ? (
                <tr><td colSpan={7}><LoadingState /></td></tr>
              ) : !customers.data?.length ? (
                <tr><td colSpan={7}><EmptyState text="No customers match the current filters." /></td></tr>
              ) : customers.data.map((c) => (
                <tr key={c.customer_id}>
                  <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{c.customer_id}</td>
                  <td>{c.city}</td>
                  <td>{c.age ?? "—"}</td>
                  <td>{c.gender ?? "—"}</td>
                  <td>{c.signup_date ? c.signup_date.slice(0, 10) : "—"}</td>
                  <td>{fmtNum(c.order_count)}</td>
                  <td>{c.recorded_spend != null ? fmtINR(c.recorded_spend) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
