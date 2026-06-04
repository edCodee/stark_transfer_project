import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class GestureType(Enum):
    OPEN = "OPEN"
    GRAB = "GRAB"
    THROW = "THROW"
    UNKNOWN = "UNKNOWN"

@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def distance_to(self, other: 'Point3D') -> float:
        """Calcula la distancia euclidiana entre dos puntos 3D."""
        return math.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )

@dataclass
class HandState:
    thumb_tip: Point3D
    index_tip: Point3D
    wrist: Point3D
    velocity_x: float = 0.0  # Velocidad de movimiento horizontal para detectar el lanzamiento

    @property
    def is_pinching(self) -> bool:
        """
        Regla de negocio: Determina si el usuario está haciendo un agarre.
        El umbral de 0.05 es relativo al tamaño de la pantalla (normalizado por MediaPipe).
        """
        PINCH_THRESHOLD = 0.05 
        distance = self.thumb_tip.distance_to(self.index_tip)
        return distance < PINCH_THRESHOLD

    def evaluate_gesture(self, previous_state: Optional['HandState'] = None) -> GestureType:
        """
        Evalúa el gesto actual basándose en el estado de la mano y el historial.
        """
        if self.is_pinching:
            return GestureType.GRAB
        
        # Si antes estaba agarrando, y ahora soltó con alta velocidad, es un lanzamiento
        if previous_state and previous_state.is_pinching:
            THROW_VELOCITY_THRESHOLD = 0.15 # Velocidad mínima requerida
            if abs(self.velocity_x) > THROW_VELOCITY_THRESHOLD:
                return GestureType.THROW
            
        return GestureType.OPEN