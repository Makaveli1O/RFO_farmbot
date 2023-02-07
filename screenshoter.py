import cv2 
import numpy as np
from time import time
from windowCapture import WindowCapture
from perception import Perception, DebugModes
from detection import Detection
from rfbot import RFBot, BotState
from threading import Thread

wincap = WindowCapture('RF Online')
perception = Perception(None)

loop_time = time()
wincap.start()
while(True):
        
    # display processed image
    cv2.imshow("Matches", wincap.screenshot)

    # debug loop rate
    #print('FPS {}'.format(1 / (time() - loop_time)))
    
    # print(detector.boundingBoxes)
    loop_time = time()

    # exit loop
    key = cv2.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        cv2.destroyAllWindows()
        break
    # save positive image
    elif key == ord("f"):
        cv2.imwrite('positiveNew/{}.jpg'.format(loop_time), wincap.screenshot)
    # save negative image 
    elif key == ord("g"):
        cv2.imwrite('negativeNew/{}.jpg'.format(loop_time), wincap.screenshot)