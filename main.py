import cv2 
import numpy as np
from time import time
from windowCapture import WindowCapture
from Detector import Detector, DebugModes

# initialize window capture class
wincap = WindowCapture('RF Online')
WindowCapture.list_window_names()

loop_time = time()
threshold = 0.5

mob_detector = Detector("needle.jpg")

while(True):
    # get image from the window
    screenshot = wincap.get_screenshot()

    # display the images
    mid_points = mob_detector.find(screenshot, 0.8, DebugModes.FULL_DEBUG)

    # debug loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # 'q' to exit loop
    key = cv2.waitKey(1)
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
    # save positive image
    elif key == ord("f"):
        cv2.imwrite('positive/{}.jpg'.format(loop_time), screenshot)
    # save negative image 
    elif key == ord("g"):
        cv2.imwrite('negative/{}.jpg'.format(loop_time), screenshot)

print("Done")