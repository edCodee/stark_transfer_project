from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities import HandState


class IGestureRepository(ABC):
    """
    Puerto para la obtencion de datos de la mano.
    La implementacion concreta conectara con la camara y OpenCV/MediaPipe.
    """

    @abstractmethod
    def get_current_hand_state(self) -> Optional[HandState]:
        """Captura el frame actual y devuelve el estado espacial de la mano."""
        pass

    @abstractmethod
    def release_camera(self) -> None:
        """Libera los recursos de hardware."""
        pass
