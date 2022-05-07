import logging
import threading
from typing import Union, Tuple

import cv2
import numpy as np
import mediapipe as mp

from camera import Camera


LEFT_SHOULDER   = 11
LEFT_ELBOW      = 13
LEFT_WRIST      = 15
# LEFT_HIP        = 23

RIGHT_SHOULDER  = 12
RIGHT_ELBOW     = 14
RIGHT_WRIST     = 16
# RIGHT_HIP       = 24


connections = (
    # (LEFT_HIP, LEFT_SHOULDER),
    (LEFT_SHOULDER, LEFT_ELBOW),
    (LEFT_ELBOW, LEFT_WRIST),
    # (RIGHT_HIP, RIGHT_SHOULDER),
    (RIGHT_SHOULDER, RIGHT_ELBOW),
    (RIGHT_ELBOW, RIGHT_WRIST),
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    # (LEFT_HIP, RIGHT_HIP),
)


class MotionTracker:
    def __init__(self,
            camera: Camera,
            accuracy: int = 1,
            show_landmarks: bool = False,
            landmarks_color: tuple = (255, 255, 255),
        ) -> None:
        
        # create a threading lock used for making the motion
        # tracker thread safe when reading/writing to memory
        self._lock = threading.Lock()
        
        self._camera = camera
        
        self._running = False
        self._current_frame = None
        self._last_processed = None
        self._landmarks = None
        self._accuracy = accuracy
        self._show_landmarks = False
        self._landmarks_color = landmarks_color

        # use the property setters for the constructor arguments
        self.accuracy = accuracy
        self.show_landmarks = show_landmarks

        width, height = camera.resolution
        self._width = width
        self._height = height

        # create a mediapipe solution for tracking human poses
        self._mp_pose = self._create_pose_solution()


    def _create_pose_solution(self) -> mp.python.solution_base.SolutionBase:
        solution = mp.solutions.pose.Pose(
            model_complexity=self._accuracy,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        return solution


    @property
    def frame(self) -> Union[np.ndarray, None]:
        with self._lock:
            return self._current_frame


    @property
    def landmarks(self) -> Union[dict, None]:
        with self._lock:
            return self._landmarks


    @property
    def accuracy(self) -> int:
        return self._accuracy
    

    @accuracy.setter
    def accuracy(self, value: int) -> None:
        if not value in range(3):
            raise ValueError("value must be an int value from 0 to 2")
        
        with self._lock:
            self._accuracy = value
            self._mp_pose = self._create_pose_solution()


    @property
    def show_landmarks(self) -> bool:
        return self._show_landmarks
    

    @show_landmarks.setter
    def show_landmarks(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("show_landmarks must be a bool")
        self._show_landmarks = value


    def _convert_landmarks(self, x: int, y: int) -> Tuple[int, int]:
        x = round(x * self._width)
        y = round(y * self._height)

        return x, y
    

    def _process_frame(self, frame: np.ndarray) -> dict:
        pose_landmarks = {
            LEFT_SHOULDER:  None,
            LEFT_ELBOW:     None,
            LEFT_WRIST:     None,
            # LEFT_HIP:       None,
            RIGHT_SHOULDER: None,
            RIGHT_ELBOW:    None,
            RIGHT_WRIST:    None,
            # RIGHT_HIP:      None,
        }

        results = self._mp_pose.process(frame)

        if results.pose_landmarks is not None:
            h, w = frame.shape[:2]

            for landmark in pose_landmarks.keys():
                point = results.pose_landmarks.landmark[landmark]
                
                if 0 <= point.x <= 1 and 0 <= point.y <= 1:
                    landmark_pos = self._convert_landmarks(point.x, point.y)
                    pose_landmarks[landmark] = landmark_pos
                
                    if self._show_landmarks:
                        cv2.circle(frame, landmark_pos, 5, self._landmarks_color, -1, cv2.LINE_AA)

            if self._show_landmarks:
                for p1, p2 in connections:
                    point1 = pose_landmarks[p1]
                    point2 = pose_landmarks[p2]

                    if point1 is not None and point2 is not None:
                        cv2.line(frame, point1, point2, self._landmarks_color, 2, cv2.LINE_AA)

        return frame, pose_landmarks


    def update(self) -> None:
        # read and flip a new frame from the camera
        new_frame = self._camera.read()

        if new_frame is not None:
            # process the frame to detect pose landmarks
            processed_frame, new_landmarks = self._process_frame(new_frame)

            # update the internal landmarks and frame while using a thread lock
            with self._lock:
                self._current_frame = processed_frame
                self._landmarks = new_landmarks
    

    def _update_thread(self) -> None:
        while self._running:
            self.update()


    def start_thread(self) -> None:
        self._running = True
        
        thread = threading.Thread(
            target=self._update_thread,
            daemon=True
        )

        logging.debug("starting daemon motion tracker thread")
        thread.start()
    
    
    def stop_thread(self) -> None:
        logging.debug("stopping daemon motion tracker thread")
        self._running = False
