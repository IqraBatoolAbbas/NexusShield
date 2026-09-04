import React, { useState } from "react";
import { ChevronRight, LockKeyhole, ShieldCheck } from "lucide-react";
import AuthLayout from "../layouts/AuthLayout";
import { authApi } from "../api/authApi";
import PricingPage from "../components/saas/PricingPage";
import { useAuth } from "../hooks/useAuth";

export function AuthForm({ signup = false, onSwitch, onPricing }) {
  const { signIn } = useAuth(); 
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "admin" }); 
  const [error, setError] = useState(""); 
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    if (form.password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }
    if (signup && form.name.trim().length < 2) {
      setError("Please enter your full name.");
      return;
    }
    setLoading(true);
    try {
      const credentials = signup ? form : { email: form.email, password: form.password };
      signIn(await (signup ? authApi.signup(credentials) : authApi.login(credentials)));
    } catch (reason) { 
      setError(reason.message); 
    } finally { 
      setLoading(false); 
    }
  };

  return <AuthLayout><div className="auth-card"><div className="brand"><div className="brand-mark"><ShieldCheck size={22} /></div><div><strong>NEXUS<span>SHIELD</span></strong><small>AI SECURITY FABRIC</small></div></div><div className="section-kicker"><LockKeyhole size={14} /> TENANT-ISOLATED WORKSPACE</div><h1>{signup ? "Create your secure workspace" : "Welcome back, operator"}</h1><p>Protect your GenAI perimeter with tenant-isolated telemetry and encrypted audit trails.</p><form onSubmit={submit}>{signup && <input placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />}<input type="email" placeholder="Work email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /><input type="password" placeholder="Password (8+ characters)" minLength="8" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />{signup && <label className="role-select-label">Workspace role<select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="admin">Organization Admin — full workspace access</option><option value="developer">AI Developer — testing and integrations</option><option value="auditor">Security Auditor — compliance and threat review</option></select></label>}{error && <div className="auth-error">{error}</div>}<button type="submit" disabled={loading}>{loading ? "AUTHENTICATING..." : signup ? "CREATE WORKSPACE" : "SIGN IN"} <ChevronRight size={15} /></button></form><div className="auth-switch"><button onClick={onPricing}>View SaaS pricing</button> · {signup ? "Already have an account?" : "New to NexusShield?"} <button onClick={onSwitch}>{signup ? "Sign in" : "Create an account"}</button></div></div></AuthLayout>;
}

export default function LoginPage({ onSwitch, onPricing }) { return <AuthForm onSwitch={onSwitch} onPricing={onPricing} />; }
export function PricingAuthPage({ onBack }) { return <div className="auth-shell pricing-auth"><PricingPage onGetStarted={onBack} /><button className="back-auth" onClick={onBack}>BACK TO SIGN IN</button></div>; }