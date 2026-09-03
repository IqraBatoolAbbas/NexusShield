import { useEffect, useRef, useState } from "react";

export default function useWebSocket(url, { onMessage } = {}) {
  const socket = useRef(null);
  const [connected, setConnected] = useState(false);
  useEffect(() => {
    if (!url) return undefined;
    try {
      socket.current = new WebSocket(url);
      socket.current.onopen = () => setConnected(true);
      socket.current.onclose = () => setConnected(false);
      socket.current.onmessage = (event) => onMessage?.(event);
    } catch { setConnected(false); }
    return () => socket.current?.close();
  }, [url, onMessage]);
  return { socket: socket.current, connected };
}
