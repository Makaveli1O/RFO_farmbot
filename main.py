import cv2 
import numpy as np
from time import time
from windowCapture import WindowCapture
from perception import Perception, DebugModes
from detection import Detection
from rfbot import RFBot, BotState
from threading import Thread
import os

# initialize window capture class
wincap = WindowCapture('RF Online')
# load trained model into detector
detector = Detection("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\yolov8n_downloaded.pt")
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
        detector.update(wincap.screenshot.getImage())
        if bot.state == BotState.INITIALIZING:
            targets = perception.getPoints(detector.getBoundingBoxes())
            bot.update_targets(targets)
        elif bot.state == BotState.SEARCHING:
            targets = perception.getPoints(detector.getBoundingBoxes())
            bot.update_targets(targets)
            bot.update_screenshot(wincap.screenshot.getImage())
        elif bot.state == BotState.ATTACKING:
            bot.update_screenshot(wincap.screenshot.getImage())
        
        # draw bounding boxes
        output_image = perception.drawBoundingBoxes(wincap.screenshot.getImage(), detector.getBoundingBoxes())
        #output_image = perception.drawFPS(output_image,
        #                                  int(1 / (time() - loop_time)),
        #                                  wincap.h,
        #                                  wincap.w)
            
        # display processed image
        cv2.imshow("Matches", output_image)

        # debug loop rate
        print('FPS {}'.format(1 / (time() - loop_time)))
        
        # print(detector.getBoundingBoxes())
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
        #    cv2.imwrite('positive/{}.jpg'.format(loop_time), wincap.screenshot.getImage()
        # save negative image 
        #elif key == ord("g"):
        #    cv2.imwrite('negative/{}.jpg'.format(loop_time), wincap.screenshot.getImage()
except KeyboardInterrupt as e:
    detector.stop()
    wincap.stop()
    bot.stop()
    cv2.destroyAllWindows()
    print ('\n! Received keyboard interrupt, quitting threads.\n')