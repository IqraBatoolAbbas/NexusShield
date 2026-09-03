import React from "react";
import { CheckCircle2 } from "lucide-react";

export default function PipelineVisualizer({ logs = [], latency = 0 }) {
  const visible = logs.length ? logs : [{ layer: "—", status: "READY", message: "Awaiting prompt input..." }];
  return <section className="panel terminal-panel"><div className="panel-heading"><div><span className="section-kicker">◈ LIVE TRACE</span><h2>Defensive pipeline</h2></div><span className="terminal-status"><span className="pulse" /> STREAMING</span></div>
    <div className="terminal">{visible.map((log, i) => <div className={`log-line ${String(log.status).toLowerCase()}`} key={`${log.layer}-${i}`}><span className="log-time">00:{String(i + 12).padStart(2, "0")}.42</span><span className="log-layer">LAYER {log.layer}</span><span className="log-status">{log.status}</span><span>{log.message}</span></div>)}</div>
    <div className="pipeline-footer"><span><span className="dot green" /> <CheckCircle2 size={12} /> 7 layers active</span><span>CPU INFERENCE <b>{latency}ms</b></span></div>
  </section>;
}
