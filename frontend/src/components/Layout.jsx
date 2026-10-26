import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard, ShoppingCart, Package, Users,
  BarChart2, MessageSquare, ShieldCheck, Activity
} from "lucide-react";

const NAV = [
  { to: "/",          label: "Overview",           Icon: LayoutDashboard },
  { to: "/orders",    label: "Orders",             Icon: ShoppingCart },
  { to: "/products",  label: "Products",           Icon: Package },
  { to: "/customers", label: "Customers",          Icon: Users },
  { to: "/analytics", label: "Analytics",          Icon: BarChart2 },
  { to: "/assistant", label: "Business Assistant", Icon: MessageSquare },
  { to: "/quality",   label: "Data Quality",       Icon: ShieldCheck },
  { to: "/status",    label: "System Status",      Icon: Activity },
];

export default function Layout({ children, apiStatus }) {
  const loc = useLocation();
  const current = NAV.find((n) => n.to === loc.pathname)?.label ?? "Instamart Copilot";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>Instamart Copilot</h1>
          <span>Business Analytics</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            >
              <Icon size={15} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">Python · FastAPI · SQLite · React</div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <span className="topbar-title">{current}</span>
          <div className="topbar-actions">
            <span className={`status-dot${apiStatus === "ok" ? " ok" : apiStatus === "error" ? " error" : ""}`}>
              <span className="dot" />
              {apiStatus === "ok" ? "API connected" : apiStatus === "error" ? "API offline" : "Connecting…"}
            </span>
          </div>
        </header>
        <main className="page-content">{children}</main>
      </div>
    </div>
  );
}
