import React from "react";
export default function ReplayModal({ event, onClose, onReplay }) {
  if (!event) return null;
  return <div className="modal-backdrop" onClick={onClose}><div className="panel modal-card" onClick={(e) => e.stopPropagation()}><h2>Replay event</h2><p className="mono">{event.id}</p><pre>{event.prompt || event.signature || "No payload available"}</pre><div className="modal-actions"><button className="outline-button" onClick={onClose}>Close</button><button className="composer button" onClick={() => onReplay?.(event)}>Replay scan</button></div></div></div>;
}
