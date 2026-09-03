import React, { useState } from "react";
export default function ApiKeyModal({ open, onClose, onCreate }) {
  const [name, setName] = useState("");
  if (!open) return null;
  return <div className="modal-backdrop" onClick={onClose}><div className="panel modal-card" onClick={(event) => event.stopPropagation()}><h2>Generate API key</h2><p>Provision a tenant-isolated key for your integration.</p><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Key name" autoFocus /><div className="modal-actions"><button className="outline-button" onClick={onClose}>Cancel</button><button className="composer button" disabled={!name.trim()} onClick={() => { onCreate(name.trim()); setName(""); }}>Generate</button></div></div></div>;
}
