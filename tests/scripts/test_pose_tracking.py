import cv2
from camera import Camera
from tracker import MotionTracker


with Camera(1) as camera:
    tracker = MotionTracker(camera)
    
    print(tracker.landmarks)

    tracker.accuracy = 2
    tracker.accuracy = 1

    tracker.show_landmarks = False
    tracker.show_landmarks = True

    while True:
        tracker.update()

        cv2.imshow('%s | Press Q to exit' % __file__, tracker.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break