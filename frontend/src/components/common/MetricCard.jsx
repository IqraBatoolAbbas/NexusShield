import React from "react";

export default function MetricCard({ label, value, change, Icon }) {
  return <div className="kpi interactive-card"><div className="kpi-top"><span>{label}</span><Icon size={17} /></div><strong>{value}</strong><small>↗ {change} <em>vs last 24h</em></small></div>;
}
