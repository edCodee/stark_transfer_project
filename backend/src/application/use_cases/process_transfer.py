import time # Añadimos esta importación nativa
from typing import Tuple, Optional
from src.domain.entities import HandState, GestureType
from src.application.interfaces.gesture_repository import IGestureRepository

class TransferUseCase:
    def __init__(self, gesture_repo: IGestureRepository):
        self.gesture_repo = gesture_repo
        self.previous_state: Optional[HandState] = None
        self.is_image_grabbed: bool = False
        
        self.image_bounds = {
            "x_min": 0.3, "x_max": 0.7,
            "y_min": 0.3, "y_max": 0.7
        }
        
        # --- TOQUE SENIOR: Control de fluidez (Debounce) ---
        self.last_event_time = 0.0
        self.cooldown_seconds = 0.5  # Medio segundo de gracia entre acciones

    def _is_hand_over_image(self, hand: HandState) -> bool:
        x, y = hand.index_tip.x, hand.index_tip.y
        return (self.image_bounds["x_min"] <= x <= self.image_bounds["x_max"] and
                self.image_bounds["y_min"] <= y <= self.image_bounds["y_max"])

    def execute_frame(self) -> Tuple[str, Optional[HandState]]:
        current_state = self.gesture_repo.get_current_hand_state()
        if not current_state:
            return "NO_HAND_DETECTED", None

        gesture = current_state.evaluate_gesture(self.previous_state)
        event_action = "IDLE"

        # Verificamos si ya pasó el tiempo de gracia desde el último evento
        current_time = time.time()
        can_trigger_event = (current_time - self.last_event_time) > self.cooldown_seconds

        if can_trigger_event:
            if gesture == GestureType.GRAB and not self.is_image_grabbed:
                if self._is_hand_over_image(current_state):
                    self.is_image_grabbed = True
                    event_action = "IMAGE_GRABBED"
                    self.last_event_time = current_time
                    
            elif gesture == GestureType.THROW and self.is_image_grabbed:
                self.is_image_grabbed = False
                event_action = "IMAGE_THROWN"
                self.last_event_time = current_time
                
            elif gesture == GestureType.OPEN and self.is_image_grabbed:
                self.is_image_grabbed = False
                event_action = "IMAGE_DROPPED"
                self.last_event_time = current_time

        self.previous_state = current_state
        return event_action, current_state