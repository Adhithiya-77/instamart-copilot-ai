const BASE = "http://localhost:8000";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

function qs(params = {}) {
  const p = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== "" && v !== null))
  ).toString();
  return p ? "?" + p : "";
}

export const api = {
  health: () => req("/api/health"),
  dashboard: {
    summary: () => req("/api/dashboard/summary"),
    orderStatus: () => req("/api/dashboard/order-status"),
    orderTrends: () => req("/api/dashboard/order-trends"),
    topProducts: (limit = 10) => req(`/api/dashboard/top-products?limit=${limit}`),
    cityDistribution: () => req("/api/dashboard/city-distribution"),
    categoryRevenue: () => req("/api/dashboard/category-revenue"),
    recentOrders: (limit = 10) => req(`/api/dashboard/recent-orders?limit=${limit}`),
  },
  orders: {
    list: (params = {}) => req(`/api/orders${qs(params)}`),
    get: (id) => req(`/api/orders/${encodeURIComponent(id)}`),
  },
  products: {
    list: (params = {}) => req(`/api/products${qs(params)}`),
    categories: () => req("/api/products/categories"),
  },
  customers: {
    list: (params = {}) => req(`/api/customers${qs(params)}`),
    cities: () => req("/api/customers/cities"),
    get: (id) => req(`/api/customers/${encodeURIComponent(id)}`),
  },
  analytics: {
    products: () => req("/api/analytics/products"),
    customers: () => req("/api/analytics/customers"),
    cities: () => req("/api/analytics/cities"),
    delivery: () => req("/api/analytics/delivery"),
  },
  dataQuality: {
    summary: () => req("/api/data-quality/summary"),
    duplicates: () => req("/api/data-quality/duplicates"),
    missingAmounts: () => req("/api/data-quality/missing-amounts"),
    columnNulls: () => req("/api/data-quality/column-nulls"),
  },
  assistant: {
    chat: (message) =>
      req("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      }),
  },
};
