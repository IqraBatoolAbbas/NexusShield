import React from "react";
import { ChevronRight, Database, ShieldCheck } from "lucide-react";
import { NAV_ITEMS } from "../../utils/constants";

export default function Sidebar({ role, page, onNavigate, user, onLogout, open = false, onClose }) {
  const allowed = NAV_ITEMS.filter(([, , , roles]) => roles.includes(role));
  return <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
    <div className="brand"><div className="brand-mark"><ShieldCheck size={22} /></div><div><strong>NEXUS<span>SHIELD</span></strong><small>AI SECURITY FABRIC</small></div></div>
    <div className="workspace-label">WORKSPACE <span>LIVE</span></div>
    <nav>{allowed.map(([id, label, Icon]) => <button className={page === id ? "nav-active" : ""} onClick={() => { onNavigate(id); onClose?.(); }} key={id}><Icon size={17} />{label}{page === id && <ChevronRight size={15} className="nav-arrow" />}</button>)}</nav>
    <div className="sidebar-bottom"><div className="system-status"><span className="pulse" />ALL SYSTEMS NOMINAL<small><Database size={11} /> SQLite persistence · API online</small></div>
      <div className="profile"><div className="avatar">{(user?.name || "OP").slice(0, 2).toUpperCase()}</div><div><b>{user?.name}</b><small>{user?.email}</small><span className="role-badge">{role.toUpperCase()}</span></div><button className="logout-button" onClick={onLogout}>Exit</button></div>
    </div>
  </aside>;
}
