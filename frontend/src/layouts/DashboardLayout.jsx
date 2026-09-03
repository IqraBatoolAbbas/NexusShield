import React, { useState } from "react";
import Footer from "../components/common/Footer";
import Sidebar from "../components/common/Sidebar";
import Navbar from "../components/common/Navbar";
import { titleForRoute } from "../utils/constants";

export default function DashboardLayout({ auth, page, onNavigate, onLogout, onRefresh, children }) {
  const [drawer, setDrawer] = useState(false);
  return <div className="app-shell"><Sidebar role={auth.user.role} page={page} onNavigate={onNavigate} user={auth.user} onLogout={onLogout} open={drawer} onClose={() => setDrawer(false)} />
    {drawer && <button className="drawer-scrim" aria-label="Close navigation" onClick={() => setDrawer(false)} />}
    <main><Navbar title={titleForRoute(page)} tenant={auth.user.id} onRefresh={onRefresh} onMenu={() => setDrawer(true)} />{children}<Footer /></main>
  </div>;
}
