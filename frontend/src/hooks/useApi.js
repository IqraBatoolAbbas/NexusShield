import { useCallback } from "react";
import { apiClient } from "../api/client";

export function useApi() {
  return useCallback((path, options = {}) => apiClient(path, options), []);
}
export default useApi;
