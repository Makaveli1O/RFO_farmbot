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

# load trained model
cascade_model = cv2.CascadeClassifier("cascadeModel_v1/cascade.xml")
# load an empty detector class
detector = Detector(None)

while(True):
    # get image from the window
    screenshot = wincap.get_screenshot()
    
    # unprocessed image from the game
    #cv2.imshow("unprocessed", screenshot)

    # object detection
    boundingBoxes = cascade_model.detectMultiScale(screenshot)
    
    # draw bounding boxes
    output_image = detector.drawBoundingBoxes(screenshot, boundingBoxes)
    
    # display processed image
    cv2.imshow("Matches", output_image)

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