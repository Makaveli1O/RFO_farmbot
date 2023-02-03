import cv2 
import numpy as np
from time import time
from windowCapture import WindowCapture
from detector import Detector, DebugModes

# initialize window capture class
wincap = WindowCapture('RF Online')
WindowCapture.list_window_names()

loop_time = time()
threshold = 0.5

#mob_detector = Detector(None)

while(True):
    # get image from the window
    screenshot = wincap.get_screenshot()
    
    cv2.imshow("unprocessed", screenshot)

    # object detection
    #boundingBoxes = mob_detector.find(screenshot, 0.8)
    
    # draw bounding boxes
    #output_image = mob_detector.drawBoundingBoxes(screenshot, boundingBoxes)
    
    # display processed image
    #cv2.imshow("Matches", output_image)

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