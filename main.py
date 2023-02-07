import cv2 
import numpy as np
from time import time
from windowCapture import WindowCapture
from perception import Perception, DebugModes
from detection import Detection
from rfbot import RFBot, BotState
from threading import Thread

# initialize window capture class
wincap = WindowCapture('RF Online')
# load trained model into detector
detector = Detection("cascadeModel_v1/cascade.xml")
# load an empty detector class
perception = Perception(None)
# initialize the bot
bot = RFBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

loop_time = time()
# notify when thread is created
thread_active = False

# start threads 
wincap.start()
detector.start()
bot.start()

try: # to be able to interrupt the program from console without showing cv2 imshow output
    while(True):
        
        # prevent from processing empty screenshot
        if wincap.screenshot is None:
            continue

        # object detection
        detector.update(wincap.screenshot)
        if bot.state == BotState.INITIALIZING:
            targets = perception.getPoints(detector.boundingBoxes)
            bot.update_targets(targets)
        elif bot.state == BotState.SEARCHING:
            targets = perception.getPoints(detector.boundingBoxes)
            bot.update_targets(targets)
            bot.update_screenshot(wincap.screenshot)
        elif bot.state == BotState.ATTACKING:
            bot.update_screenshot(wincap.screenshot)
        
        # draw bounding boxes
        output_image = perception.drawBoundingBoxes(wincap.screenshot, detector.boundingBoxes)
            
        # display processed image
        cv2.imshow("Matches", output_image)

        # debug loop rate
        #print('FPS {}'.format(1 / (time() - loop_time)))
        
        # print(detector.boundingBoxes)
        loop_time = time()

        # exit loop
        key = cv2.waitKey(1)
        if key == ord('q'):
            detector.stop()
            wincap.stop()
            bot.stop()
            cv2.destroyAllWindows()
            break
        # save positive image
        #elif key == ord("f"):
        #    cv2.imwrite('positive/{}.jpg'.format(loop_time), wincap.screenshot)
        # save negative image 
        #elif key == ord("g"):
        #    cv2.imwrite('negative/{}.jpg'.format(loop_time), wincap.screenshot)
except Exception as e:
    print(e)
    detector.stop()
    wincap.stop()
    bot.stop()
    cv2.destroyAllWindows()
    print ('\n! Received keyboard interrupt, quitting threads.\n')