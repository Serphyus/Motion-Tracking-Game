import cv2
from camera import Camera


with Camera(1) as camera:
    assert camera.resolution

    while True:
        frame = camera.read()
        assert frame is not None
        
        cv2.imshow('%s | Press Q to exit' % __file__, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break