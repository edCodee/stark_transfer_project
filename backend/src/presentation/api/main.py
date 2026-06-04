# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # from fastapi.middleware.cors import CORSMiddleware
# # from src.infrastructure.network.socket_handler import ConnectionManager

# # # Inicializamos la app y nuestro gestor de conexiones
# # app = FastAPI(title="Stark Transfer API")
# # manager = ConnectionManager()

# # # Configuramos CORS (Crucial para que la web en React de la Fase 5 pueda conectarse)
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"], # En producción se pone la IP de tu frontend
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # @app.get("/")
# # def read_root():
# #     return {"status": "El túnel cuántico está operativo."}

# # # ENDPOINT 1: Para el iPhone (Receptor)
# # @app.websocket("/ws/mobile/{room_id}")
# # async def websocket_mobile(websocket: WebSocket, room_id: str):
# #     await manager.connect(room_id, websocket)
# #     try:
# #         while True:
# #             # El iPhone es un receptor pasivo, pero necesitamos este "await" 
# #             # para mantener el túnel abierto y escuchando.
# #             await websocket.receive_text()
# #     except WebSocketDisconnect:
# #         manager.disconnect(room_id, websocket)

# # # ENDPOINT 2: Para la PC (Emisor)
# # @app.websocket("/ws/pc/{room_id}")
# # async def websocket_pc(websocket: WebSocket, room_id: str):
# #     await manager.connect(room_id, websocket)
# #     try:
# #         while True:
# #             # La PC procesará la visión y enviará JSONs hacia acá.
# #             # Ejemplo: {"event": "IMAGE_THROWN", "payload": {"image_id": "123"}}
# #             data = await websocket.receive_json()
            
# #             # Al recibir el evento de la PC, lo retransmitimos a la sala (al iPhone)
# #             await manager.broadcast_event(
# #                 room_id=room_id, 
# #                 event_type=data.get("event"), 
# #                 payload=data.get("payload")
# #             )
# #     except WebSocketDisconnect:
# #         manager.disconnect(room_id, websocket)
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from src.infrastructure.network.socket_handler import ConnectionManager

# app = FastAPI(title="Stark Transfer API")
# manager = ConnectionManager()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.websocket("/ws/mobile/{room_id}")
# async def websocket_mobile(websocket: WebSocket, room_id: str):
#     await manager.connect(room_id, websocket)
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         print(f"📱 Cliente (Web/iPhone) desconectado de la sala {room_id}")
#         manager.disconnect(room_id, websocket)

# @app.websocket("/ws/pc/{room_id}")
# async def websocket_pc(websocket: WebSocket, room_id: str):
#     await manager.connect(room_id, websocket)
#     try:
#         while True:
#             data = await websocket.receive_json()
            
#             # --- LA SOLUCIÓN: Pasamos el 'sender' al manager ---
#             await manager.broadcast_event(
#                 room_id=room_id, 
#                 event_type=data.get("event"), 
#                 payload=data.get("payload"),
#                 sender=websocket 
#             )
#     except WebSocketDisconnect:
#         print(f"💻 Cámara de PC desconectada de la sala {room_id}")
#         manager.disconnect(room_id, websocket)
#     except Exception as e:
#         print(f"🚨 Error crítico en el túnel de la PC: {e}")
#         manager.disconnect(room_id, websocket)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.network.socket_handler import ConnectionManager

app = FastAPI(title="Stark Transfer API")
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── ENDPOINT MOBILE (receptor / iPhone) ──────────────────────────────────────

@app.websocket("/ws/mobile/{room_id}")
async def websocket_mobile(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            # Mantenemos la conexión viva leyendo pings/mensajes entrantes.
            # receive_text() lanza WebSocketDisconnect si el cliente cierra.
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"📱 Mobile desconectado de la sala '{room_id}'")
    except Exception as e:
        # Cualquier otro error (timeout, red caída) → desconectamos limpio
        print(f"🚨 Error inesperado en mobile (sala '{room_id}'): {e}")
    finally:
        # finally garantiza que SIEMPRE limpiamos el estado,
        # sin importar cómo se salió del try.
        manager.disconnect(room_id, websocket)


# ─── ENDPOINT PC (emisor / cámara) ────────────────────────────────────────────

@app.websocket("/ws/pc/{room_id}")
async def websocket_pc(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            # receive_json() lanza ValueError si el JSON está malformado,
            # y WebSocketDisconnect si el cliente se va.
            data = await websocket.receive_json()

            event_type = data.get("event")
            payload    = data.get("payload")

            # Validación mínima: descartamos paquetes sin 'event'
            if not event_type:
                print(f"⚠️  Paquete sin 'event' recibido en sala '{room_id}'. Ignorando.")
                continue

            await manager.broadcast_event(
                room_id=room_id,
                event_type=event_type,
                payload=payload,
                sender=websocket,
            )

    except WebSocketDisconnect:
        print(f"💻 PC desconectada de la sala '{room_id}'")
    except ValueError as e:
        # JSON malformado → no crasheamos el servidor, solo logueamos
        print(f"⚠️  JSON inválido recibido en sala '{room_id}': {e}")
    except Exception as e:
        print(f"🚨 Error crítico en PC (sala '{room_id}'): {e}")
    finally:
        # El finally es la clave: antes faltaba esto en el path del except Exception,
        # lo que dejaba el WebSocket en estado zombie → WinError 10053 en el cliente.
        manager.disconnect(room_id, websocket)