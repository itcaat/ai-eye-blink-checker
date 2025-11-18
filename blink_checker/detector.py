"""Eye blink detection using MediaPipe and Eye Aspect Ratio (EAR)."""

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Tuple, Optional, List


class BlinkDetector:
    """Detects eye blinks using facial landmarks and Eye Aspect Ratio."""
    
    # MediaPipe Face Mesh landmark indices for eyes
    # Left eye indices
    LEFT_EYE = [362, 385, 387, 263, 373, 380]
    # Right eye indices
    RIGHT_EYE = [33, 160, 158, 133, 153, 144]
    
    # EAR threshold - values below this indicate a blink
    EAR_THRESHOLD = 0.21
    # Consecutive frames eye must be below threshold to count as blink
    CONSECUTIVE_FRAMES = 2
    
    def __init__(self, alarm_threshold: int = 10):
        """
        Initialize the blink detector with MediaPipe Face Mesh.
        
        Args:
            alarm_threshold: Seconds without blinking before alarm (0 = disabled)
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.blink_counter = 0
        self.frame_counter = 0
        self.alarm_threshold = alarm_threshold
        self.last_blink_time = time.time()
        self.alarm_active = False
        
    def calculate_ear(self, eye_landmarks: List[Tuple[float, float]]) -> float:
        """
        Calculate Eye Aspect Ratio (EAR).
        
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        
        Args:
            eye_landmarks: List of 6 (x, y) coordinates for eye landmarks
            
        Returns:
            Eye Aspect Ratio value
        """
        # Vertical distances
        A = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[5]))
        B = np.linalg.norm(np.array(eye_landmarks[2]) - np.array(eye_landmarks[4]))
        
        # Horizontal distance
        C = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[3]))
        
        # EAR calculation
        ear = (A + B) / (2.0 * C)
        return ear
    
    def get_eye_landmarks(
        self, 
        landmarks, 
        eye_indices: List[int], 
        frame_width: int, 
        frame_height: int
    ) -> List[Tuple[float, float]]:
        """
        Extract eye landmark coordinates.
        
        Args:
            landmarks: MediaPipe facial landmarks
            eye_indices: Indices of eye landmarks
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            
        Returns:
            List of (x, y) coordinates for the eye
        """
        coords = []
        for idx in eye_indices:
            landmark = landmarks[idx]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            coords.append((x, y))
        return coords
    
    def detect_blink(self, frame: np.ndarray) -> Tuple[bool, float, np.ndarray]:
        """
        Detect if a blink occurred in the current frame.
        
        Args:
            frame: BGR image from camera
            
        Returns:
            Tuple of (blink_detected, average_ear, annotated_frame)
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        blink_detected = False
        avg_ear = 0.0
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            h, w = frame.shape[:2]
            
            # Get eye landmarks
            left_eye = self.get_eye_landmarks(
                face_landmarks.landmark, self.LEFT_EYE, w, h
            )
            right_eye = self.get_eye_landmarks(
                face_landmarks.landmark, self.RIGHT_EYE, w, h
            )
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Draw eye landmarks
            for point in left_eye + right_eye:
                cv2.circle(frame, point, 2, (0, 255, 0), -1)
            
            # Check if eyes are closed
            if avg_ear < self.EAR_THRESHOLD:
                self.frame_counter += 1
            else:
                # Eyes were closed and now opened - blink detected
                if self.frame_counter >= self.CONSECUTIVE_FRAMES:
                    self.blink_counter += 1
                    blink_detected = True
                    self.last_blink_time = time.time()
                    self.alarm_active = False
                self.frame_counter = 0
            
            # Display info on frame
            cv2.putText(
                frame,
                f"Blinks: {self.blink_counter}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            cv2.putText(
                frame,
                f"EAR: {avg_ear:.2f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
        else:
            # No face detected
            cv2.putText(
                frame,
                "No face detected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )
        
        return blink_detected, avg_ear, frame
    
    def should_alarm(self) -> bool:
        """
        Check if alarm should be triggered.
        
        Returns:
            True if user hasn't blinked for too long
        """
        if self.alarm_threshold <= 0:
            return False
        
        time_since_last_blink = time.time() - self.last_blink_time
        
        # Trigger alarm if threshold exceeded and alarm not already active
        if time_since_last_blink >= self.alarm_threshold and not self.alarm_active:
            self.alarm_active = True
            return True
        
        return False
    
    def get_time_since_last_blink(self) -> float:
        """Get time in seconds since last blink."""
        return time.time() - self.last_blink_time
    
    def reset(self):
        """Reset blink counter."""
        self.blink_counter = 0
        self.frame_counter = 0
        self.last_blink_time = time.time()
        self.alarm_active = False
    
    def get_blink_count(self) -> int:
        """Get total number of blinks detected."""
        return self.blink_counter
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()

