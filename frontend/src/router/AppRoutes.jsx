import React, { useCallback, useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import { useAuth } from "../hooks/useAuth";
import { DEFAULT_POLICY, INITIAL_ANALYTICS, NAV_ITEMS } from "../utils/constants";
import { shieldApi } from "../api/shieldApi";
import LoginPage, { PricingAuthPage } from "../pages/LoginPage";
import SignupPage from "../pages/SignupPage";
import LandingPage from "../pages/LandingPage";
import CommandCenter from "../pages/CommandCenter";
import SecurityPlayground from "../pages/SecurityPlayground";
import HoneypotConsole from "../pages/HoneypotConsole";
import ThreatAnalytics from "../pages/ThreatAnalytics";
import PolicyConfig from "../pages/PolicyConfig";
import AuditLog from "../pages/AuditLog";
import ApiKeyManager from "../pages/ApiKeyManager";
import { TeamManager, Billing } from "../pages/DashboardPages";

function currentPath() {
  return window.location.hash.replace(/^#\/?/, "") || "home";
}

export default function AppRoutes() {
  const { auth, signOut } = useAuth();
  const [route, setRoute] = useState(currentPath);
  const [analytics, setAnalytics] = useState(INITIAL_ANALYTICS);
  const [events, setEvents] = useState([]);
  const [honeypots, setHoneypots] = useState([]);
  const [policy, setPolicy] = useState(DEFAULT_POLICY);
  const [toast, setToast] = useState("");
  const navigate = useCallback((next) => { window.location.hash = next; setRoute(next); }, []);
  useEffect(() => { const onHash = () => setRoute(currentPath()); window.addEventListener("hashchange", onHash); return () => window.removeEventListener("hashchange", onHash); }, []);
  useEffect(() => { if (auth && ["login", "signup", "landing", "home", "pricing"].includes(route)) navigate("overview"); }, [auth, route, navigate]);

  const refresh = useCallback(async () => {
    if (!auth) return;
    try {
      const [nextAnalytics, nextEvents, nextHoneypots, nextPolicy] = await Promise.all([shieldApi.analytics(), shieldApi.events(), shieldApi.honeypots(), shieldApi.policy()]);
      setAnalytics(nextAnalytics); setEvents(nextEvents); setHoneypots(nextHoneypots); setPolicy(nextPolicy);
    } catch (error) { if (error.status === 401) signOut(); }
  }, [auth, signOut]);
  useEffect(() => { if (!auth) return undefined; refresh(); const timer = setInterval(refresh, 10000); return () => clearInterval(timer); }, [auth, refresh]);

  if (!auth) {
    if (route === "home" || route === "landing") return <LandingPage onGetStarted={() => navigate("signup")} onLogin={() => navigate("login")} onPricing={() => navigate("pricing")} />;
    if (route === "signup") return <SignupPage onSwitch={() => navigate("login")} onPricing={() => navigate("pricing")} />;
    if (route === "pricing") return <PricingAuthPage onBack={() => navigate("login")} />;
    return <LoginPage onSwitch={() => navigate("signup")} onPricing={() => navigate("pricing")} />;
  }
  const allowed = NAV_ITEMS.filter(([, , , roles]) => roles.includes(auth.user.role)).map(([id]) => id);
  const knownRoute = NAV_ITEMS.some(([id]) => id === route);
  const page = allowed.includes(route) ? route : allowed[0] || "overview";
  const forbidden = knownRoute && !allowed.includes(route);
  const savePolicy = (next) => { setPolicy(next); shieldApi.savePolicy(next).catch(() => {}); };
  const content = {
    overview: <CommandCenter analytics={analytics} events={events} onNavigate={navigate} />,
    playground: <SecurityPlayground analytics={analytics} refresh={refresh} notify={setToast} />,
    honeypot: <HoneypotConsole honeypots={honeypots} />,
    analytics: <ThreatAnalytics analytics={analytics} />,
    policy: <PolicyConfig policy={policy} onSave={savePolicy} />,
    audit: <AuditLog events={events} refresh={refresh} />,
    keys: <ApiKeyManager />,
    team: <TeamManager />,
    billing: <Billing />,
  };
  return <DashboardLayout auth={auth} page={forbidden ? "" : page} onNavigate={navigate} onLogout={signOut} onRefresh={refresh}>{forbidden ? <AccessDenied role={auth.user.role} route={route} onBack={() => navigate(allowed[0] || "overview")} /> : content[page]}{toast && <button className="toast-alert" onClick={() => setToast("")}>⚠ {toast} <span>×</span></button>}</DashboardLayout>;
}

function AccessDenied({ role, route, onBack }) {
  return <section className="access-denied panel"><div className="empty-icon">403</div><span className="section-kicker">ROLE-AWARE ROUTE GUARD</span><h2>Access denied</h2><p>The <b>{role}</b> role cannot open <code>/{route}</code>. This route is hidden and protected by the backend authorization policy.</p><button onClick={onBack}>RETURN TO AUTHORIZED VIEW <span>→</span></button></section>;
}
