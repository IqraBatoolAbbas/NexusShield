import { shieldApi } from "./shieldApi";

export const analyticsApi = {
  getOverview: shieldApi.analytics,
  getEvents: shieldApi.events,
  getHoneypots: shieldApi.honeypots,
};
export default analyticsApi;
