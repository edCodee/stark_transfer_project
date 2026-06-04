from abc import ABC, abstractmethod
from typing import Any, Dict


class IWebSocketManager(ABC):
    """
    Puerto para la comunicacion en tiempo real.
    La implementacion concreta usara FastAPI Websockets
    """

    @abstractmethod
    async def connect(self, cliet_id: str, connection: Any) -> None:
        """Registra un nuevo cliente en la secion."""
        pass

    @abstractmethod
    def disconnect(self, client_id: str) -> None:
        """Elimina un cliente de la sesion"""
        pass

    @abstractmethod
    async def broadcast_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Emite un evento a todos los cliente (ej. notificar al iphone que la imagen ha sido
        lanzada)
        """
        pass
