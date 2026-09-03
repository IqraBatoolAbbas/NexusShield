import { apiClient } from "./client";

export const shieldApi = {
  scan: (payload) => apiClient("/scan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }),
  analytics: () => apiClient("/analytics"),
  events: () => apiClient("/events"),
  honeypots: () => apiClient("/honeypots"),
  policy: () => apiClient("/policy"),
  savePolicy: (policy) => apiClient("/policy", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(policy) }),
  keys: () => apiClient("/keys"),
  createKey: (name) => apiClient("/keys", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }) }),
  revokeKey: (id) => apiClient(`/keys/${id}`, { method: "DELETE" }),
  team: () => apiClient("/team"),
  updateRole: (id, role) => apiClient(`/team/${id}/role`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role }) }),
  billing: () => apiClient("/billing"),
};
export default shieldApi;
