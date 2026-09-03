import { API_BASE_URL } from "../utils/constants";

export function getAuthHeaders(headers = {}) {
  const stored = JSON.parse(localStorage.getItem("nexus_auth") || "null");
  return {
    ...(stored?.access_token ? { Authorization: `Bearer ${stored.access_token}` } : {}),
    ...headers,
  };
}

export async function apiClient(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: getAuthHeaders(options.headers),
  });
  if (response.status === 401) {
    window.dispatchEvent(new CustomEvent("nexus:unauthorized"));
  }
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { detail = (await response.json()).detail || detail; } catch { /* non-json error */ }
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }
  if (response.status === 204) return null;
  return response.json();
}

export const apiRequest = apiClient;
