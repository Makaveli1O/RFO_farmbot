import cv2 
import numpy as np
from time import time,sleep
from windowCapture import WindowCapture
from perception import Perception, DebugModes
from detection import Detection
from rfbot import RFBot
import pyautogui
from threading import Thread

# initialize window capture class
wincap = WindowCapture('RF Online')
# load trained model into detector
detector = Detection("cascadeModel_v1/cascade.xml")
# load an empty detector class
perception = Perception(None)
# initialize the bot
bot = RFBot()

loop_time = time()
# notify when thread is created
thread_active = False

# start threads 
wincap.start()
detector.start()
bot.start()

def doBotStuff(boundingBoxes):
    """
    if len(boundingBoxes) > 0:
        targets = perception.getPoints(boundingBoxes)
        target = wincap.get_screen_position(targets[0])
        pyautogui.moveTo(x=target[0], y=target[1])
        sleep(5)
    global thread_active
    thread_active=False
    """
    pass

while(True):
    
    # prevent from processing empty screenshot
    if wincap.screenshot is None:
        continue

    # object detection
    detector.update(wincap.screenshot)
    
    # draw bounding boxes
    output_image = perception.drawBoundingBoxes(wincap.screenshot, detector.boundingBoxes)
        
    # display processed image
    cv2.imshow("Matches", output_image)

    if not thread_active:
        thread_active = True
        t = Thread(target = doBotStuff, args = (detector.boundingBoxes, ))
        t.start()

    # debug loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    
    print(detector.boundingBoxes)
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
    elif key == ord("f"):
        cv2.imwrite('positive/{}.jpg'.format(loop_time), wincap.screenshot)
    # save negative image 
    elif key == ord("g"):
        cv2.imwrite('negative/{}.jpg'.format(loop_time), wincap.screenshot)