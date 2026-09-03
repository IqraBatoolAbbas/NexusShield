import {
  Activity,
  ChartNoAxesCombined,
  Crosshair,
  Database,
  FileClock,
  Gauge,
  LockKeyhole,
  Radar,
  SlidersHorizontal,
  Users,
} from "lucide-react";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
export const INITIAL_ANALYTICS = {
  scanned: 0, blocked: 0, remediated: 0, honeypots: 0, latency_ms: 0, threats: {}, layers: {},
};
export const NAV_ITEMS = [
  ["overview", "Command Center", Gauge, ["admin", "developer"]],
  ["playground", "Security Playground", Crosshair, ["admin", "developer"]],
  ["honeypot", "Honeypot Console", Radar, ["admin", "auditor"]],
  ["analytics", "Threat Analytics", ChartNoAxesCombined, ["admin", "auditor"]],
  ["policy", "Policy & Feedback", SlidersHorizontal, ["admin", "developer"]],
  ["audit", "Audit Log", FileClock, ["admin", "auditor"]],
  ["keys", "API Keys", LockKeyhole, ["admin", "developer"]],
  ["team", "Team Members", Users, ["admin"]],
  ["billing", "Billing & Subscription", Database, ["admin"]],
];
export const DEFAULT_POLICY = {
  similarity_threshold: 0.85,
  enable_honeypot: true,
  strict_pii: true,
  strict_toxicity: true,
  auto_block_dos: true,
};
export const titleForRoute = (route) => NAV_ITEMS.find(([id]) => id === route)?.[1] || "Command Center";
