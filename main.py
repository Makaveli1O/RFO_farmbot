import cv2 
import numpy as np
from time import time
from windowCapture import WindowCapture
from perception import Perception, DebugModes
from detection import Detection
from rfbot import RFBot, BotState
import yappi
import sys
# initialize window capture class
wincap = WindowCapture('RF Online')
# loads perception class for visualization and points calculations
perception = Perception(None)
# load trained model into detector
detector = Detection("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\runs\\detect\\train3\\weights\\best.pt")
# initialize the bot
bot = RFBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

loop_time = time()
# notify when thread is created
thread_active = False
#yappi.start(False, True)
# start threads 
wincap.start()
bot.start() #bot is slowing it down a lot
detector.start()


def getFps() -> int:
    """Get fps calculation. When too early during initialization
    return 0 instead of excepion.

    Returns:
        int
    """
    
    try:
        fps = round(1 / (time() - loop_time))
    except Exception as e:
        fps = 0
    return fps 
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
        """
        elif bot.state == BotState.ATTACKING:
            bot.update_screenshot(wincap.screenshot)
        """
        # draw bounding boxes
        output_image = perception.drawVision(wincap.screenshot, detector.detections)
        output_image = perception.drawMidPoints(wincap.screenshot, perception.getPoints(detector.boundingBoxes))
        # debug loop rate
        perception.drawFPS(output_image,
                           getFps(),
                           (wincap.w - 100, wincap.h - 10)) # wincap.dims + padding
        # display processed image
        cv2.imshow("Matches", output_image)
        
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
    print("EXCEPTION IN THE MAIN WHILE LOOP: \n------------------------------------\n")
    print(e)
    detector.stop()
    wincap.stop()
    bot.stop()
    cv2.destroyAllWindows()
#yappi.stop()
#stats = yappi.get_func_stats().sort('tsub').strip_dirs()
#stats.print_all(out=sys.stderr, columns={0: ('name', 45), 1: ('ncall', 10), 2: ('tsub', 8), 3: ('ttot', 8), 4: ('tavg', 8)})