import cv2
import json
import time
from websocket import create_connection, WebSocketException, WebSocketConnectionClosedException
from src.infrastructure.computer_vision.mediapipe_adapter import MediaPipeAdapter
from src.application.use_cases.process_transfer import TransferUseCase

# ─── CONFIG ───────────────────────────────────────────────────────────────────
WS_URL        = "ws://127.0.0.1:8000/ws/pc/sala_stark"
MAX_REINTENTOS = 5
BACKOFF_BASE   = 2   # segundos: 2, 4, 8, 16, 32

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def crear_conexion() -> object | None:
    """Conecta al servidor con backoff exponencial. Retorna socket o None."""
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            ws = create_connection(WS_URL, timeout=5)
            print(f"✅ Conectado al servidor WebSocket (intento {intento})")
            return ws
        except Exception as e:
            espera = BACKOFF_BASE ** intento
            print(f"⚠️  Intento {intento}/{MAX_REINTENTOS} fallido: {e}")
            if intento < MAX_REINTENTOS:
                print(f"   Reintentando en {espera}s...")
                time.sleep(espera)
    print("❌ No se pudo conectar tras todos los intentos. ¿Está Uvicorn corriendo?")
    return None


def cerrar_socket(ws) -> None:
    """Cierra el socket ignorando cualquier error (ya puede estar muerto)."""
    if ws:
        try:
            ws.close()
        except Exception:
            pass


def enviar_paquete(ws, paquete: dict) -> bool:
    """
    Envía un paquete JSON al servidor.
    Retorna True si OK, False si la conexión está muerta.
    Captura tanto errores de WebSocket como del SO (WinError 10053, ECONNRESET…).
    """
    try:
        ws.send(json.dumps(paquete))
        return True
    except (WebSocketConnectionClosedException, WebSocketException) as e:
        print(f"⚠️  WebSocket cerrado por el servidor: {e}")
        return False
    except OSError as e:
        # WinError 10053 / 10054, ECONNRESET, EPIPE, etc.
        print(f"⚠️  Error de red del SO: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Error inesperado al enviar: {e}")
        return False


def reconectar(ws_actual) -> object | None:
    """Cierra el socket actual y abre uno nuevo."""
    print("🔄 Reconectando al servidor...")
    cerrar_socket(ws_actual)
    return crear_conexion()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("Iniciando Sistema de Visión Stark...")

    ws = crear_conexion()
    if ws is None:
        return

    vision_adapter = MediaPipeAdapter(camera_index=0)
    use_case       = TransferUseCase(gesture_repo=vision_adapter)
    print("Listo. Presiona 'q' para salir.\n")

    try:
        while True:
            action, state = use_case.execute_frame()

            # ── Render del frame ──────────────────────────────────────────────
            if vision_adapter.cap.isOpened():
                success, frame = vision_adapter.cap.read()
                if success:
                    frame = cv2.flip(frame, 1)
                    h, w, _ = frame.shape
                    cv2.rectangle(
                        frame,
                        (int(w * 0.3), int(h * 0.3)),
                        (int(w * 0.7), int(h * 0.7)),
                        (255, 0, 0), 2,
                    )
                    cv2.putText(
                        frame, f"STATUS: {action}",
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    )
                    cv2.imshow("Tony Stark Vision", frame)

            # ── Envío de eventos ──────────────────────────────────────────────
            if action in ("IMAGE_GRABBED", "IMAGE_THROWN", "IMAGE_DROPPED"):
                print(f"📡 Emitiendo: {action}")
                paquete = {
                    "event": action,
                    "payload": {
                        "mensaje":     "La imagen está en movimiento",
                        "imagen_demo": "https://picsum.photos/400/600",
                    },
                }

                enviado = enviar_paquete(ws, paquete)

                if not enviado:
                    ws = reconectar(ws)
                    if ws is None:
                        print("❌ Sin conexión tras reconexión. Apagando sistema.")
                        break
                    # Reintentamos el paquete que quedó pendiente
                    if not enviar_paquete(ws, paquete):
                        print("❌ Fallo persistente. Apagando sistema.")
                        break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Tecla 'q' presionada. Apagando...")
                break

    except KeyboardInterrupt:
        print("\nInterrupción manual. Apagando...")

    finally:
        vision_adapter.release_camera()
        cv2.destroyAllWindows()
        cerrar_socket(ws)
        print("✅ Sistema apagado correctamente.")


if __name__ == "__main__":
    main()