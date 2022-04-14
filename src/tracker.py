import threading
from typing import Union

import cv2
import numpy as np
import mediapipe as mp

from camera import Camera


LEFT_SHOULDER   = 11
LEFT_ELBOW      = 13
LEFT_WRIST      = 15
LEFT_HIP        = 23

RIGHT_SHOULDER  = 12
RIGHT_ELBOW     = 14
RIGHT_WRIST     = 16
RIGHT_HIP       = 24


connections = (
    (LEFT_HIP, LEFT_SHOULDER),
    (LEFT_SHOULDER, LEFT_ELBOW),
    (LEFT_ELBOW, LEFT_WRIST),
    (RIGHT_HIP, RIGHT_SHOULDER),
    (RIGHT_SHOULDER, RIGHT_ELBOW),
    (RIGHT_ELBOW, RIGHT_WRIST),
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_HIP, RIGHT_HIP),
)

cv2.LINE_AA
class MotionTracker:
    def __init__(self,
            camera: Camera,
            show_landmarks: bool = True,
            landmarks_color: tuple = (255, 255, 255),
        ) -> None:
        self._camera = camera
        
        self._last_frame = None
        self._landmarks = None
        self._show_landmarks = show_landmarks
        self._landmarks_color = landmarks_color

        width, height = camera.resolution
        self._width = width
        self._height = height

        self._mp_pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self._lock = threading.Lock()


    @property
    def frame(self) -> Union[np.ndarray, None]:
        with self._lock:
            return self._last_frame


    @property
    def landmarks(self) -> Union[dict, None]:
        with self._lock:
            return self._landmarks


    @property
    def show_landmarks(self) -> bool:
        return self._show_landmarks
    

    @show_landmarks.setter
    def show_landmarks(self, value: bool) -> bool:
        if not isinstance(value, bool):
            raise TypeError('show_landmarks must be a bool')
        self._show_landmarks = value


    def _process_frame(self) -> dict:
        pose_landmarks = {
            LEFT_SHOULDER:  None,
            LEFT_ELBOW:     None,
            LEFT_WRIST:     None,
            LEFT_HIP:       None,
            RIGHT_SHOULDER: None,
            RIGHT_ELBOW:    None,
            RIGHT_WRIST:    None,
            RIGHT_HIP:      None,
        }

        results = self._mp_pose.process(self._last_frame)

        if results.pose_landmarks is not None:
            h, w = self._last_frame.shape[:2]

            for landmark in pose_landmarks.keys():
                point = results.pose_landmarks.landmark[landmark]
                if 0 <= point.x <= 1 and 0 <= point.y <= 1:
                    x = round(point.x * self._width)
                    y = round(point.y * self._height)
                    pose_landmarks[landmark] = (x, y)
                
                    if self._show_landmarks:
                        cv2.circle(self._last_frame, pose_landmarks[landmark], 5, self._landmarks_color, -1, cv2.LINE_AA)

        if self._show_landmarks:
            for p1, p2 in connections:
                point1 = pose_landmarks[p1]
                point2 = pose_landmarks[p2]

                if point1 is not None and point2 is not None:
                    cv2.line(self._last_frame, point1, point2, self._landmarks_color, 2, cv2.LINE_AA)

        return pose_landmarks


    def update(self) -> None:
        self._last_frame = self._camera.read()
        new_landmarks = self._process_frame()
        with self._lock:
            self._landmarks = new_landmarks