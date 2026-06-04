// import { useEffect, useState, useRef } from 'react';

// export const useWebSocket = (role, roomId = 'sala_stark') => {
//   const [eventData, setEventData] = useState({ event: 'IDLE', payload: null });
//   const ws = useRef(null);

//   useEffect(() => {
//     // Detecta la IP actual automáticamente
//     const host = window.location.hostname;
//     const wsUrl = `ws://${host}:8000/ws/${role}/${roomId}`;
    
//     ws.current = new WebSocket(wsUrl);

//     ws.current.onmessage = (message) => {
//       try {
//         const data = JSON.parse(message.data);
//         setEventData({ event: data.type || data.event, payload: data.data || data.payload });
//       } catch (error) {
//         console.error("Error parseando WebSocket:", error);
//       }
//     };

//     return () => {
//       if (ws.current) ws.current.close();
//     };
//   }, [role, roomId]);

//   return eventData;
// };

import { useEffect, useState, useRef, useCallback } from 'react';

export const useWebSocket = (role, roomId = 'sala_stark') => {
  const [eventData, setEventData] = useState({ event: 'IDLE', payload: null });
  const ws = useRef(null);

  useEffect(() => {
    const host = window.location.hostname;
    const wsUrl = `ws://${host}:8000/ws/${role}/${roomId}`;
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onmessage = (message) => {
      try {
        const data = JSON.parse(message.data);
        setEventData({ event: data.type || data.event, payload: data.data || data.payload });
      } catch (error) {
        console.error("Error parseando WebSocket:", error);
      }
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [role, roomId]);

  // NUEVO: Función para enviar datos reales por el túnel
  const sendMessage = useCallback((eventName, payload) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ event: eventName, payload: payload }));
    }
  }, []);

  return { event: eventData.event, payload: eventData.payload, sendMessage };
};