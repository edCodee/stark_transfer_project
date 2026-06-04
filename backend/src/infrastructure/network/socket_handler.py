# # from typing import Any, Dict, List
# # from fastapi import WebSocket
# # from src.application.interfaces.websocket_manager import IWebSocketManager

# # class ConnectionManager(IWebSocketManager):
# #     def __init__(self):
# #         # Diccionario para guardar las salas. 
# #         # Formato: { "sala_123": [conexion_pc, conexion_iphone] }
# #         self.active_rooms: Dict[str, List[WebSocket]] = {}

# #     async def connect(self, room_id: str, connection: WebSocket) -> None:
# #         """Acepta la conexión y la mete en la sala correspondiente."""
# #         await connection.accept()
# #         if room_id not in self.active_rooms:
# #             self.active_rooms[room_id] = []
# #         self.active_rooms[room_id].append(connection)
# #         print(f"Nueva conexión en la sala: {room_id}")

# #     def disconnect(self, room_id: str, connection: WebSocket) -> None:
# #         """Elimina la conexión de la sala. Si la sala queda vacía, se borra."""
# #         if room_id in self.active_rooms:
# #             self.active_rooms[room_id].remove(connection)
# #             if not self.active_rooms[room_id]: 
# #                 del self.active_rooms[room_id]
# #                 print(f"Sala {room_id} eliminada por inactividad.")

# #     async def broadcast_event(self, room_id: str, event_type: str, payload: Dict[str, Any] = None) -> None:
# #         """Envía el evento a todos los dispositivos dentro de la misma sala."""
# #         if room_id in self.active_rooms:
# #             message = {
# #                 "type": event_type, 
# #                 "data": payload or {}
# #             }
# #             for connection in self.active_rooms[room_id]:
# #                 await connection.send_json(message)1

# # from typing import Any, Dict, List
# # from fastapi import WebSocket
# # from src.application.interfaces.websocket_manager import IWebSocketManager

# # class ConnectionManager(IWebSocketManager):
# #     def __init__(self):
# #         # Diccionario para guardar las salas. 
# #         # Formato: { "sala_123": [conexion_pc, conexion_iphone] }
# #         self.active_rooms: Dict[str, List[WebSocket]] = {}

# #     async def connect(self, room_id: str, connection: WebSocket) -> None:
# #         """Acepta la conexión y la mete en la sala correspondiente."""
# #         await connection.accept()
# #         if room_id not in self.active_rooms:
# #             self.active_rooms[room_id] = []
# #         self.active_rooms[room_id].append(connection)
# #         print(f"✅ Nueva conexión establecida en la sala: {room_id}")

# #     def disconnect(self, room_id: str, connection: WebSocket) -> None:
# #         """Elimina la conexión de forma segura, previniendo errores si ya no existe."""
# #         if room_id in self.active_rooms:
# #             # BLINDAJE: Verificamos que la conexión realmente siga en la lista antes de borrarla
# #             if connection in self.active_rooms[room_id]:
# #                 self.active_rooms[room_id].remove(connection)
                
# #             # Si la sala quedó vacía, la destruimos para liberar memoria (Garbage Collection)
# #             if not self.active_rooms[room_id]: 
# #                 del self.active_rooms[room_id]
# #                 print(f"🧹 Sala '{room_id}' eliminada por inactividad.")

# #     async def broadcast_event(self, room_id: str, event_type: str, payload: Dict[str, Any] = None) -> None:
# #         """Envía el evento a todos, manejando caídas abruptas sin crashear el servidor."""
# #         if room_id in self.active_rooms:
# #             message = {
# #                 "type": event_type, 
# #                 "data": payload or {}
# #             }
            
# #             # BLINDAJE SENIOR: Iteramos sobre una copia de la lista usando list()
# #             # Si modificamos la lista original mientras iteramos, Python lanzará un error.
# #             conexiones_actuales = list(self.active_rooms[room_id])
            
# #             for connection in conexiones_actuales:
# #                 try:
# #                     # Intentamos enviar el paquete al cliente
# #                     await connection.send_json(message)
# #                 except Exception as e:
# #                     # Si falla (ej: el iPhone se bloqueó o perdió Wi-Fi), atrapamos el error
# #                     print(f"⚠️ Cliente inalcanzable ({e}). Expulsando de la sala {room_id}...")
# #                     # Limpiamos la conexión muerta
# #                     self.disconnect(room_id, connection)

# from typing import Any, Dict, List
# from fastapi import WebSocket
# from src.application.interfaces.websocket_manager import IWebSocketManager

# class ConnectionManager(IWebSocketManager):
#     def __init__(self):
#         self.active_rooms: Dict[str, List[WebSocket]] = {}

#     async def connect(self, room_id: str, connection: WebSocket) -> None:
#         await connection.accept()
#         if room_id not in self.active_rooms:
#             self.active_rooms[room_id] = []
#         self.active_rooms[room_id].append(connection)
#         print(f"✅ Nueva conexión establecida en la sala: {room_id}")

#     def disconnect(self, room_id: str, connection: WebSocket) -> None:
#         if room_id in self.active_rooms:
#             if connection in self.active_rooms[room_id]:
#                 self.active_rooms[room_id].remove(connection)
#             if not self.active_rooms[room_id]: 
#                 del self.active_rooms[room_id]
#                 print(f"🧹 Sala '{room_id}' eliminada por inactividad.")

#     # --- LA SOLUCIÓN: Agregamos "sender: WebSocket = None" ---
#     async def broadcast_event(self, room_id: str, event_type: str, payload: Dict[str, Any] = None, sender: WebSocket = None) -> None:
#         if room_id in self.active_rooms:
#             message = {
#                 "type": event_type, 
#                 "data": payload or {}
#             }
            
#             conexiones_actuales = list(self.active_rooms[room_id])
#             for connection in conexiones_actuales:
#                 # Filtramos al emisor para no crear un eco mortal
#                 if connection != sender:
#                     try:
#                         await connection.send_json(message)
#                     except Exception as e:
#                         print(f"⚠️ Cliente inalcanzable ({e}). Expulsando...")
#                         self.disconnect(room_id, connection)

from typing import Any, Dict, List, Optional
from fastapi import WebSocket
from src.application.interfaces.websocket_manager import IWebSocketManager


class ConnectionManager(IWebSocketManager):
    """
    Gestor de salas WebSocket.
    Thread-safe para FastAPI (event loop único de asyncio).
    """

    def __init__(self):
        # { "sala_stark": [ws_pc, ws_mobile] }
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    # ── CONNECT ───────────────────────────────────────────────────────────────

    async def connect(self, room_id: str, connection: WebSocket) -> None:
        """Acepta la conexión y la registra en la sala."""
        await connection.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
        self.active_rooms[room_id].append(connection)
        total = len(self.active_rooms[room_id])
        print(f"✅ Nueva conexión en sala '{room_id}' ({total} activa/s)")

    # ── DISCONNECT ────────────────────────────────────────────────────────────

    def disconnect(self, room_id: str, connection: WebSocket) -> None:
        """
        Elimina la conexión de la sala de forma segura.
        No lanza excepción si la conexión ya fue removida (doble-llamada segura).
        """
        room = self.active_rooms.get(room_id)
        if room is None:
            return  # La sala ya no existe, nada que hacer

        if connection in room:
            room.remove(connection)

        # Garbage collection: sala vacía → la destruimos
        if not room:
            del self.active_rooms[room_id]
            print(f"🧹 Sala '{room_id}' destruida (sin conexiones activas)")

    # ── BROADCAST ─────────────────────────────────────────────────────────────

    async def broadcast_event(
        self,
        room_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        sender: Optional[WebSocket] = None,
    ) -> None:
        """
        Envía el evento a todos los clientes de la sala excepto al emisor.
        Si un cliente falla (cayó su red), lo expulsamos sin crashear el broadcast.
        """
        room = self.active_rooms.get(room_id)
        if not room:
            return  # Sala vacía o inexistente, nada que hacer

        message = {
            "type": event_type,
            "data": payload or {},
        }

        # Iteramos sobre una COPIA de la lista.
        # Si disconnect() modifica la lista original durante el loop,
        # no obtenemos RuntimeError: "list changed size during iteration".
        for connection in list(room):
            if connection is sender:
                continue  # No le mandamos eco al emisor

            try:
                await connection.send_json(message)
            except Exception as e:
                # El cliente se cayó (perdió Wi-Fi, se bloqueó, etc.)
                print(f"⚠️  Cliente inalcanzable en sala '{room_id}': {e}. Expulsando...")
                self.disconnect(room_id, connection)