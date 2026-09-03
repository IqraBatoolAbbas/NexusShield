import React from "react";
import { Bell, Menu, RefreshCw, ShieldCheck } from "lucide-react";

export default function Navbar({ title, tenant, onRefresh, onMenu }) {
  return <header className="topbar">
    <button className="icon-button menu-button" onClick={onMenu} aria-label="Open navigation"><Menu size={20} /></button>
    <div><div className="eyebrow">TENANT: {tenant} / <span>REAL-TIME PROTECTION</span></div><h1>{title}</h1></div>
    <div className="header-actions"><div className="live-dot"><span className="pulse" /> LIVE MONITORING</div><button className="icon-button" onClick={onRefresh} aria-label="Refresh"><RefreshCw size={18} /></button><button className="icon-button" aria-label="Notifications"><Bell size={18} /></button></div>
    <div className="mobile-brand"><ShieldCheck size={20} /> NEXUS<span>SHIELD</span></div>
  </header>;
}
