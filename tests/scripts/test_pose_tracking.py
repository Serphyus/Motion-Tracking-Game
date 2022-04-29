import cv2
from camera import Camera
from tracker import MotionTracker


camera = Camera(1)
tracker = MotionTracker(camera, 1, True)

assert tracker.landmarks is None
assert tracker.accuracy == 1
assert tracker.show_landmarks

tracker.update()
tracker.start_thread()

while True:
    cv2.imshow('%s | Press Q to exit' % __file__, tracker.frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

tracker.stop_thread()
camera.close()