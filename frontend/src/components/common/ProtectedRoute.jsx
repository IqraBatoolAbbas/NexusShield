import React from "react";

export default function ProtectedRoute({ allowedRoles, role, children, fallback }) {
  return allowedRoles.includes(role) ? children : (fallback || <div className="access-denied panel"><h2>Access denied</h2><p>Your role is not authorized for this view.</p></div>);
}
