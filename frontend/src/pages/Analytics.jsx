import { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from "recharts";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import { Tabs, LoadingState, ErrorState, fmtINR, fmtNum } from "../components/Shared";

const TABS = ["Products", "Customers", "Cities", "Delivery"];
const COLORS = ["#68734A", "#A0AB7E", "#C8D0B0", "#414A30", "#DED9CA"];

export default function Analytics() {
  const [tab, setTab] = useState("Products");

  const prodData  = useFetch(() => api.analytics.products(), []);
  const custData  = useFetch(() => api.analytics.customers(), []);
  const cityData  = useFetch(() => api.analytics.cities(), []);
  const delData   = useFetch(() => api.analytics.delivery(), []);

  return (
    <>
      <h1 style={{ marginBottom: 16 }}>Analytics</h1>
      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === "Products" && (
        <>
          <div className="charts-row">
            <div className="card">
              <div className="card-header"><h2>Top 15 by Order Count</h2></div>
              {prodData.loading ? <LoadingState /> : prodData.error ? <ErrorState message={prodData.error} /> :
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prodData.data?.by_order_count?.slice(0, 15)} layout="vertical"
                    margin={{ top: 4, right: 16, left: 110, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis type="number" tick={{ fontSize: 10 }} />
                    <YAxis type="category" dataKey="product_name" tick={{ fontSize: 9 }} width={110} />
                    <Tooltip formatter={v => fmtNum(v)} />
                    <Bar dataKey="orders" fill="#68734A" radius={[0, 3, 3, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              }
            </div>
            <div className="card">
              <div className="card-header"><h2>Top 15 by Recorded Revenue</h2></div>
              {prodData.loading ? <LoadingState /> : prodData.error ? <ErrorState message={prodData.error} /> :
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prodData.data?.by_revenue?.slice(0, 15)} layout="vertical"
                    margin={{ top: 4, right: 16, left: 110, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                    <YAxis type="category" dataKey="product_name" tick={{ fontSize: 9 }} width={110} />
                    <Tooltip formatter={v => fmtINR(v)} />
                    <Bar dataKey="recorded_revenue" fill="#A0AB7E" radius={[0, 3, 3, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              }
            </div>
          </div>
        </>
      )}

      {tab === "Customers" && (
        <>
          <div className="charts-row">
            <div className="card">
              <div className="card-header"><h2>Gender Distribution</h2></div>
              {custData.loading ? <LoadingState /> : custData.error ? <ErrorState message={custData.error} /> :
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={custData.data?.by_gender} dataKey="customers" nameKey="gender"
                      cx="50%" cy="50%" outerRadius={80} label={({ gender, percent }) => `${gender} ${(percent * 100).toFixed(0)}%`}>
                      {(custData.data?.by_gender ?? []).map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              }
            </div>
            <div className="card">
              <div className="card-header"><h2>Age Group Distribution</h2></div>
              {custData.loading ? <LoadingState /> : custData.error ? <ErrorState message={custData.error} /> :
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={custData.data?.age_buckets} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="age_group" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="customers" fill="#68734A" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              }
            </div>
          </div>
          <div className="card">
            <div className="card-header"><h2>Top 15 Customers by Order Count</h2></div>
            {custData.loading ? <LoadingState /> : custData.error ? <ErrorState message={custData.error} /> :
              <div className="table-wrap">
                <table>
                  <thead><tr>
                    <th>Customer ID</th><th>City</th><th>Gender</th>
                    <th>Orders</th><th>Recorded Spend</th>
                  </tr></thead>
                  <tbody>
                    {(custData.data?.top_by_orders ?? []).map((r, i) => (
                      <tr key={i}>
                        <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{r.customer_id}</td>
                        <td>{r.city}</td><td>{r.gender ?? "—"}</td>
                        <td>{fmtNum(r.orders)}</td>
                        <td>{r.recorded_spend != null ? fmtINR(r.recorded_spend) : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            }
          </div>
        </>
      )}

      {tab === "Cities" && (
        <div className="card">
          <div className="card-header"><h2>City Performance</h2></div>
          {cityData.loading ? <LoadingState /> : cityData.error ? <ErrorState message={cityData.error} /> :
            <>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={cityData.data?.slice(0, 12)} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="city" tick={{ fontSize: 10 }} />
                  <YAxis yAxisId="left" tick={{ fontSize: 10 }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                  <Tooltip formatter={(v, name) => name === "recorded_revenue" ? fmtINR(v) : fmtNum(v)} />
                  <Legend />
                  <Bar yAxisId="left" dataKey="customers" fill="#68734A" radius={[3, 3, 0, 0]} />
                  <Bar yAxisId="left" dataKey="orders" fill="#A0AB7E" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <div className="table-wrap" style={{ marginTop: 16 }}>
                <table>
                  <thead><tr><th>City</th><th>Customers</th><th>Orders</th><th>Recorded Revenue</th></tr></thead>
                  <tbody>
                    {cityData.data?.map((r, i) => (
                      <tr key={i}>
                        <td>{r.city}</td>
                        <td>{fmtNum(r.customers)}</td>
                        <td>{fmtNum(r.orders)}</td>
                        <td>{r.recorded_revenue != null ? fmtINR(r.recorded_revenue) : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          }
        </div>
      )}

      {tab === "Delivery" && (
        <>
          {delData.loading ? <LoadingState /> : delData.error ? <ErrorState message={delData.error} /> : (
            <>
              <div className="metrics-grid" style={{ marginBottom: 20 }}>
                <div className="metric-card">
                  <div className="label">Avg Delivery</div>
                  <div className="value">{delData.data?.summary?.avg_minutes} min</div>
                </div>
                <div className="metric-card">
                  <div className="label">Min Delivery</div>
                  <div className="value">{delData.data?.summary?.min_minutes} min</div>
                </div>
                <div className="metric-card">
                  <div className="label">Max Delivery</div>
                  <div className="value">{delData.data?.summary?.max_minutes} min</div>
                </div>
                <div className="metric-card">
                  <div className="label">Orders with Data</div>
                  <div className="value">{fmtNum(delData.data?.summary?.orders_with_data)}</div>
                </div>
              </div>
              <div className="card">
                <div className="card-header"><h2>Avg Delivery Time by Status</h2></div>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Status</th><th>Avg Minutes</th><th>Orders</th></tr></thead>
                    <tbody>
                      {(delData.data?.by_status ?? []).map((r, i) => (
                        <tr key={i}>
                          <td>{r.status}</td>
                          <td>{r.avg_minutes}</td>
                          <td>{fmtNum(r.orders)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </>
  );
}
