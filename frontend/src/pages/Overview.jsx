import { useState } from "react";
import { RefreshCw } from "lucide-react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from "recharts";
import { useFetch } from "../hooks/useFetch";
import { api } from "../api/client";
import {
  MetricCard, LoadingState, ErrorState, EmptyState,
  Badge, fmtINR, fmtNum, fmtDate
} from "../components/Shared";

const OLIVE = "#68734A";
const OLIVE2 = "#A0AB7E";
const OLIVE3 = "#C8D0B0";

export default function Overview() {
  const summary   = useFetch(() => api.dashboard.summary());
  const status    = useFetch(() => api.dashboard.orderStatus());
  const trends    = useFetch(() => api.dashboard.orderTrends());
  const topProds  = useFetch(() => api.dashboard.topProducts(10));
  const cities    = useFetch(() => api.dashboard.cityDistribution());
  const catRev    = useFetch(() => api.dashboard.categoryRevenue());
  const recent    = useFetch(() => api.dashboard.recentOrders(8));

  function refreshAll() {
    summary.refresh(); status.refresh(); trends.refresh();
    topProds.refresh(); cities.refresh(); catRev.refresh(); recent.refresh();
  }

  const s = summary.data;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h1>Overview</h1>
          <p style={{ color: "var(--text-2)", fontSize: "0.82rem", marginTop: 2 }}>
            Key metrics from the Instamart SQLite database. Amounts are recorded values only.
          </p>
        </div>
        <button className="btn" onClick={refreshAll}><RefreshCw size={13} /> Refresh</button>
      </div>

      {summary.error && <ErrorState message={summary.error} />}

      <div className="metrics-grid">
        <MetricCard label="Total Orders"     value={s ? fmtNum(s.total_orders)     : "…"} />
        <MetricCard label="Completed"        value={s ? fmtNum(s.completed)        : "…"} />
        <MetricCard label="Cancelled"        value={s ? fmtNum(s.cancelled)        : "…"} />
        <MetricCard label="Pending"          value={s ? fmtNum(s.pending)          : "…"} />
        <MetricCard
          label="Recorded Revenue"
          value={s ? fmtINR(s.recorded_revenue) : "…"}
          sub="Recorded amounts only"
        />
        <MetricCard
          label="Missing Amounts"
          value={s ? fmtNum(s.missing_amounts) : "…"}
          sub={s ? `${((s.missing_amounts / s.total_orders) * 100).toFixed(1)}% of orders` : ""}
        />
        <MetricCard label="Customers"  value={s ? fmtNum(s.total_customers) : "…"} />
        <MetricCard label="Products"   value={s ? fmtNum(s.total_products)  : "…"} />
      </div>

      <div className="charts-row">
        <div className="card">
          <div className="card-header"><h2>Order Status</h2></div>
          {status.loading ? <LoadingState /> : status.error ? <ErrorState message={status.error} /> :
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={status.data} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="status" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => fmtNum(v)} />
                <Bar dataKey="count" fill={OLIVE} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          }
        </div>

        <div className="card">
          <div className="card-header"><h2>Monthly Order Volume</h2></div>
          {trends.loading ? <LoadingState /> : trends.error ? <ErrorState message={trends.error} /> :
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trends.data} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => fmtNum(v)} />
                <Line type="monotone" dataKey="orders" stroke={OLIVE} strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          }
        </div>
      </div>

      <div className="charts-row">
        <div className="card">
          <div className="card-header"><h2>Top 10 Products by Order Count</h2></div>
          {topProds.loading ? <LoadingState /> : topProds.error ? <ErrorState message={topProds.error} /> :
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topProds.data} layout="vertical" margin={{ top: 4, right: 16, left: 100, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="product_name" tick={{ fontSize: 10 }} width={100} />
                <Tooltip formatter={(v) => fmtNum(v)} />
                <Bar dataKey="order_count" fill={OLIVE2} radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          }
        </div>

        <div className="card">
          <div className="card-header"><h2>Category Revenue</h2></div>
          {catRev.loading ? <LoadingState /> : catRev.error ? <ErrorState message={catRev.error} /> :
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={catRev.data} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <Tooltip formatter={(v) => fmtINR(v)} />
                <Bar dataKey="recorded_revenue" fill={OLIVE3} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          }
        </div>
      </div>

      <div className="charts-row">
        <div className="card">
          <div className="card-header"><h2>Customers by City</h2></div>
          {cities.loading ? <LoadingState /> : cities.error ? <ErrorState message={cities.error} /> :
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={cities.data?.slice(0, 10)} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="city" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="customers" fill={OLIVE} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          }
        </div>

        <div className="card">
          <div className="card-header"><h2>Recent Orders</h2></div>
          {recent.loading ? <LoadingState /> : recent.error ? <ErrorState message={recent.error} /> :
            !recent.data?.length ? <EmptyState /> :
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>Order ID</th><th>Customer</th><th>Product</th>
                  <th>Date</th><th>Status</th><th>Amount</th>
                </tr></thead>
                <tbody>
                  {recent.data.map((r, i) => (
                    <tr key={i}>
                      <td style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{r.order_id}</td>
                      <td>{r.customer_id}</td>
                      <td>{r.product_name}</td>
                      <td style={{ whiteSpace: "nowrap" }}>{fmtDate(r.order_ts)}</td>
                      <td><Badge status={r.status} /></td>
                      <td>{fmtINR(r.order_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          }
        </div>
      </div>
    </>
  );
}
