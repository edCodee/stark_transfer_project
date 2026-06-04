import cv2
import mediapipe as mp
import time
import os
import urllib.request
from typing import Optional

# Importamos del dominio y de las interfaces
from src.domain.entities import HandState, Point3D
from src.application.interfaces.gesture_repository import IGestureRepository

class MediaPipeAdapter(IGestureRepository):
    def __init__(self, camera_index: int = 0):
        """Inicializa la cámara y la nueva MediaPipe Tasks API."""
        self.cap = cv2.VideoCapture(camera_index)
        
        # --- TOQUE SENIOR: Auto-descarga del modelo si no existe ---
        model_path = "hand_landmarker.task"
        if not os.path.exists(model_path):
            print("Descargando modelo neuronal de MediaPipe (Tasks API)... por favor espera.")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            print("Modelo descargado con éxito.")

        # Configuración de la nueva Tasks API
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE, # Procesamiento síncrono frame a frame
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        self.landmarker = HandLandmarker.create_from_options(options)
        
        # Variables para calcular la velocidad
        self.prev_wrist_x: Optional[float] = None
        self.prev_time: Optional[float] = None

    def get_current_hand_state(self) -> Optional[HandState]:
        """Lee un frame, lo procesa con la Tasks API y retorna el HandState puro."""
        success, frame = self.cap.read()
        if not success:
            return None

        # OpenCV usa BGR, MediaPipe necesita RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.flip(frame_rgb, 1) # Efecto espejo

        # Convertimos la imagen al formato que exige la Tasks API
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Detectamos las manos
        result = self.landmarker.detect(mp_image)

        if result.hand_landmarks:
            # Tomamos la primera mano
            hand_landmarks = result.hand_landmarks[0]
            
            # Índices de MediaPipe: 0=Muñeca, 4=Punta Pulgar, 8=Punta Índice
            wrist = hand_landmarks[0]
            thumb = hand_landmarks[4]
            index = hand_landmarks[8]

            # Mapeo a nuestro Dominio
            pt_wrist = Point3D(x=wrist.x, y=wrist.y, z=wrist.z)
            pt_thumb = Point3D(x=thumb.x, y=thumb.y, z=thumb.z)
            pt_index = Point3D(x=index.x, y=index.y, z=index.z)

            current_time = time.time()
            velocity_x = 0.0

            if self.prev_wrist_x is not None and self.prev_time is not None:
                dt = current_time - self.prev_time
                if dt > 0:
                    velocity_x = (pt_wrist.x - self.prev_wrist_x) / dt

            self.prev_wrist_x = pt_wrist.x
            self.prev_time = current_time

            return HandState(
                thumb_tip=pt_thumb,
                index_tip=pt_index,
                wrist=pt_wrist,
                velocity_x=velocity_x
            )

        return None

    def release_camera(self) -> None:
        """Libera los recursos."""
        self.cap.release()
        self.landmarker.close()