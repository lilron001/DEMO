# detection/camera_manager.py
import logging
import cv2
import numpy as np
from typing import Optional, Tuple

class CameraManager:
    """Manage camera inputs and video processing"""
    
    def __init__(self, camera_index: int = 0):
        self.logger = logging.getLogger(__name__)
        self.camera: Optional[cv2.VideoCapture] = None
        self.camera_index = camera_index
        self.is_running = False
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera capture"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            if self.camera.isOpened():
                self.is_running = True
                self.logger.info(f"Camera {camera_index} initialized successfully")
                return True
            else:
                self.logger.error(f"Camera {camera_index} failed to open")
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from camera"""
        if self.camera and self.camera.isOpened():
            try:
                ret, frame = self.camera.read()
                if ret:
                    return frame
                else:
                    self.logger.warning("Failed to read frame from camera")
                    return None
            except Exception as e:
                self.logger.error(f"Error reading frame: {e}")
                return None
        return None
    
    def get_frame_resized(self, width: int = 640, height: int = 480) -> Optional[np.ndarray]:
        """Get frame and resize it"""
        frame = self.get_frame()
        if frame is not None:
            return cv2.resize(frame, (width, height))
        return None
    
    def release(self):
        """Release camera resource"""
        if self.camera:
            self.is_running = False
            self.camera.release()
            self.logger.info("Camera released")
    
    def __del__(self):
        """Destructor to ensure camera is released"""
        self.release()
