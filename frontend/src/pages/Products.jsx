import { useState } from "react";
import { Search } from "lucide-react";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { LoadingState, ErrorState, EmptyState, fmtINR, fmtNum } from "../components/Shared";

export default function Products() {
  const [search, setSearch]   = useState("");
  const [category, setCategory] = useState("");
  const [sortBy, setSortBy]   = useState("order_count");
  const [sortDir, setSortDir] = useState("desc");

  const cats = useFetch(() => api.products.categories(), []);
  const products = useFetch(
    () => api.products.list({ search, category, sort_by: sortBy, sort_dir: sortDir }),
    [search, category, sortBy, sortDir]
  );

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
      <h1 style={{ marginBottom: 16 }}>Products</h1>

      <div className="controls-row">
        <div style={{ position: "relative" }}>
          <Search size={13} style={{ position: "absolute", left: 8, top: "50%", transform: "translateY(-50%)", color: "var(--text-2)" }} />
          <input
            type="text"
            placeholder="Search product name…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: 28, width: 220 }}
          />
        </div>
        <select value={category} onChange={e => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {(cats.data ?? []).map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <button className="btn" onClick={() => { setSearch(""); setCategory(""); }}>Clear</button>
      </div>

      {products.error && <ErrorState message={products.error} />}

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", fontSize: "0.82rem", color: "var(--text-2)" }}>
          {products.loading ? "Loading…" : `${products.data?.length ?? 0} products`}
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Name</th>
                <th>Category</th>
                <th onClick={() => handleSort("price_inr")} style={{ cursor: "pointer" }}>
                  Price (INR) <SortInd col="price_inr" />
                </th>
                <th onClick={() => handleSort("order_count")} style={{ cursor: "pointer" }}>
                  Orders <SortInd col="order_count" />
                </th>
                <th onClick={() => handleSort("quantity_sold")} style={{ cursor: "pointer" }}>
                  Qty Sold <SortInd col="quantity_sold" />
                </th>
                <th onClick={() => handleSort("recorded_revenue")} style={{ cursor: "pointer" }}>
                  Recorded Revenue <SortInd col="recorded_revenue" />
                </th>
              </tr>
            </thead>
            <tbody>
              {products.loading ? (
                <tr><td colSpan={7}><LoadingState /></td></tr>
              ) : !products.data?.length ? (
                <tr><td colSpan={7}><EmptyState text="No products match the current filters." /></td></tr>
              ) : products.data.map((p) => (
                <tr key={p.product_id}>
                  <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{p.product_id}</td>
                  <td style={{ fontWeight: 500 }}>{p.product_name}</td>
                  <td>
                    <span style={{
                      background: "var(--olive-lt)", color: "var(--olive-dk)",
                      padding: "2px 7px", borderRadius: 3, fontSize: "0.72rem", fontWeight: 600
                    }}>{p.category}</span>
                  </td>
                  <td>{fmtINR(p.price_inr)}</td>
                  <td>{fmtNum(p.order_count)}</td>
                  <td>{fmtNum(p.quantity_sold)}</td>
                  <td>{p.recorded_revenue != null ? fmtINR(p.recorded_revenue) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
