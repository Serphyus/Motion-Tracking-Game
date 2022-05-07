from pathlib import Path

import cv2

from camera import Camera


camera = Camera(1)
assert camera.resolution

while True:
    frame = camera.read()
    assert frame is not None
    
    cv2.imshow('%s | Press Q to exit' % Path(__file__).name, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

camera.close()