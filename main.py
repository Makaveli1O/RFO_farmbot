import cv2 
import numpy as np
from time import time
from io import StringIO

# from windowcapture import WindowCapture
import WinCapture

# initialize window capture class
wincap = WinCapture('Window Name')

loop_time = time()

while(True):
    # get image from the window
    screenshot = wincap.get_screenshot()

    # display the images
    cv2.imshow('Unprocessed', screenshot)

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