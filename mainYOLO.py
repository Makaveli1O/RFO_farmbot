from ultralytics import YOLO
import cv2 as cv
from windowCaptureYOLO import WindowCapture
from time import time
import supervision as sv
from perception import Perception
from rfbot import RFBot, BotState, BotMode
from drawer import Drawer
import os
import pyautogui
    
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

def inputPromp():
    """ A function to prompt the user to select a bot mode"""
    print("Please select a bot mode:")
    for mode in BotMode:
        print(f"{mode.value + 1}: {mode.name}")

    choice = input("Enter the number of your choice: ")
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice Defaulting to auto attack mode")
        selected_mode = BotMode.AUTO_ATTACK
        return selected_mode
    
    if choice == 1:
        selected_mode = BotMode.AUTO_ATTACK
    elif choice == 3:
        selected_mode = BotMode.MACRO_ATTACK
    elif choice == 2:
        selected_mode = BotMode.SUMMONER
    else:
        print("Invalid choice Defaulting to auto attack mode")
        selected_mode = BotMode.AUTO_ATTACK
    print(f"You selected: {selected_mode.name}")

    return selected_mode

def printInfo():
    print("------------------------------------")
    print("-------Welcome to RFO Farmbot-------")
    print("------------------------------------")
    print("This bot is designed to farm Caliana mobs in RF Online. Please read following instructions carefully")
    print("If you with to exit the bot, click into 'yolov8' frame capture and press 'q' to quit")
    print("If you wish to change the bot mode, please restart the bot")
    print("Next you will be prompted to select a bot mode, followed by selection of rectangle area to capture healthbar and animus respectively(depends on selected mode)")
    print("Draw animus rectangle(only 1), then submit with q. Then draw healthbar rectangle and submit with q")
    #print("IMPORTANT: Make sure to click into the game after rectangles are drawn.")
    print("Note: This script uses CUDA -> NVIDIA GPU is required for this bot to work. If you do not have one the bot will not work")

# get the root path of your project
root_path = os.path.abspath(os.path.dirname(__file__))

# detection constants
DETECTION_CONFIDENCE = 0.55
if __name__ == '__main__':
    printInfo()
    # get the desired bot mode
    bot_mode = inputPromp()
    wincap = WindowCapture('RF Online')
    perception = Perception(None)
    fontPosition = (wincap.w - 300, wincap.h)
    
    # relative path to the model
    relative_path = "YOLO\\runs\\detect\\train3\\weights\\best.pt"
    # combine the root path and the relative path
    model_path = os.path.join(root_path, relative_path)    
    # load a model
    model = YOLO(model=model_path)
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )
    loop_time = time()
    # capture window screens 
    wincap.start()
    while(wincap.screenshot is None):
        continue # wait till the first frame is captured
    wincap.set_avg()
    # init bot
    bot = RFBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), wincap, False, mode = bot_mode)
    while(True):
        if wincap.screenshot is None:
            continue
        # capture the frame
        frame = wincap.screenshot.getImage()
        result = model.predict(
                    source=frame,
                    verbose=False,
                    conf=DETECTION_CONFIDENCE
                 )[0]#model(frame)[0] # 0th index because cuda returns list for some reason
        detections = sv.Detections.from_yolov8(result)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.55f}"
            for _, confidence, class_id, _
            in detections
        ]
        targets = perception.getPoints(detections.xyxy)
        # bot stuff
        if targets:
            bot.updateFrame(frame)
            bot.update_targets(targets)
            bot.run()
            
        else:
            bot.updateFrame(frame)
            bot.runNoTargets()
            
        
        # annotations, vision etc.
        frame = perception.drawVision(frame, detections, labels)#box_annotator.annotate(scene=frame, detections=detections)
        perception.drawFPS(frame,
                           getFps(),
                           (wincap.w - 100, wincap.h - 10)) # wincap.dims + padding
        cv.imshow("yolov8", frame)
        
        loop_time = time()
        key = cv.waitKey(1)
        if key == ord('q'):
            wincap.stop()
            bot.stop()
            break
        
        # save positive image
        #elif key == ord("f"):
        #    cv.imwrite('newSamples/{}.jpg'.format(loop_time), wincap.screenshot.getImage())
        #bot.stop()
    wincap.stop()