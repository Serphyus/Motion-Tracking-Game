import cv2
from camera import Camera
from tracker import MotionTracker


with Camera(1) as camera:
    tracker = MotionTracker(camera, 1, True)
    
    assert tracker.landmarks is None
    assert tracker.accuracy == 1
    assert tracker.show_landmarks

    while True:
        tracker.update()

        cv2.imshow('%s | Press Q to exit' % __file__, tracker.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break