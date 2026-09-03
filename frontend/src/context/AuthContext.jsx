import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";

export const AuthContext = createContext(null);

function readAuth() {
  try {
    const value = JSON.parse(localStorage.getItem("nexus_auth") || "null");
    return value ? { ...value, user: { ...value.user, role: value.user?.role || "admin" } } : null;
  } catch { return null; }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(readAuth);
  const signIn = useCallback((value) => {
    const next = { ...value, user: { ...value.user, role: value.user?.role || "admin" } };
    localStorage.setItem("nexus_auth", JSON.stringify(next));
    setAuth(next);
  }, []);
  const signOut = useCallback(() => {
    localStorage.removeItem("nexus_auth");
    setAuth(null);
  }, []);
  useEffect(() => {
    const onUnauthorized = () => signOut();
    window.addEventListener("nexus:unauthorized", onUnauthorized);
    return () => window.removeEventListener("nexus:unauthorized", onUnauthorized);
  }, [signOut]);
  const value = useMemo(() => ({ auth, signIn, signOut }), [auth, signIn, signOut]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export default AuthProvider;
