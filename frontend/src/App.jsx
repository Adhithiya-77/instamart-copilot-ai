import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Overview    from "./pages/Overview";
import Orders      from "./pages/Orders";
import Products    from "./pages/Products";
import Customers   from "./pages/Customers";
import Analytics   from "./pages/Analytics";
import Assistant   from "./pages/Assistant";
import DataQuality from "./pages/DataQuality";
import SystemStatus from "./pages/SystemStatus";
import { api } from "./api/client";

export default function App() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    api.health()
      .then(() => setApiStatus("ok"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <BrowserRouter>
      <Layout apiStatus={apiStatus}>
        <Routes>
          <Route path="/"          element={<Overview />} />
          <Route path="/orders"    element={<Orders />} />
          <Route path="/products"  element={<Products />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/quality"   element={<DataQuality />} />
          <Route path="/status"    element={<SystemStatus />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
