from pathlib import Path

import cv2

from camera import Camera
from tracker import MotionTracker

accuracy = 1
show_landmarks = True

camera = Camera(1)
tracker = MotionTracker(camera, accuracy, True)

assert tracker.landmarks is None
assert tracker.accuracy == accuracy
assert tracker.show_landmarks == show_landmarks

tracker.update()
tracker.start_thread()

while True:
    cv2.imshow('%s | Press Q to exit' % Path(__file__).name, tracker.frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

tracker.stop_thread()
camera.close()
