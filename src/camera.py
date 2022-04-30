import atexit
import logging
from typing import Union, Tuple

import cv2
import numpy as np


class Camera:
    def __init__(self, device: int) -> None:
        logging.debug("connecting to capture device id: %s" % device)
        self._cap = cv2.VideoCapture(device, cv2.CAP_DSHOW)

        if not self._cap.isOpened():
            raise RuntimeError("unable to connect to capture device %i" % device)

        atexit.register(self._close_capture)


    def _close_capture(self) -> None:
        logging.debug("releasing video capture device")
        self._cap.release()


    def close(self) -> None:
        atexit.unregister(self._close_capture)
        if self._cap.isOpened():
            self._close_capture()
        else:
            raise RuntimeError("unable to close capture device")

    
    @property
    def resolution(self) -> Tuple[int, int]:
        w = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return (w, h)

    
    def read(self) -> Union[np.ndarray, None]:
        if not self._cap.isOpened():
            raise RuntimeError("can\"t read from a closed capture device")
        
        ret, frame = self._cap.read()

        if not ret:
            logging.warning_msg("unable to read from capture device")
            return

        return cv2.flip(frame, 1)