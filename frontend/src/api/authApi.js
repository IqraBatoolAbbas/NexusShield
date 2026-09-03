import { apiClient } from "./client";

export const authApi = {
  login: (credentials) => apiClient("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(credentials) }),
  signup: (credentials) => apiClient("/auth/signup", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(credentials) }),
  me: () => apiClient("/me"),
};
export default authApi;
