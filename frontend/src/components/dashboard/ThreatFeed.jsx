import React from "react";
export default function ThreatFeed({ events = [], onViewAll }) {
  return <section className="panel quick-panel"><div className="panel-heading"><div><span className="section-kicker">◉ RECENT ACTIVITY</span><h2>Latest events</h2></div><button className="text-button" onClick={onViewAll}>View all</button></div><div className="mini-events">{events.slice(0, 4).map((event) => <div className="mini-event" key={event.id}><span className={`event-dot ${event.decision}`} /><div><b>{event.signature}</b><small>{event.decision} · {event.client_id}</small></div><time>{new Date(event.created_at).toLocaleTimeString()}</time></div>)}{!events.length && <div className="empty-state">No events yet. Run a prompt scan to populate the audit stream.</div>}</div></section>;
}
