from ultralytics import YOLO
import cv2 as cv
from windowCaptureYOLO import WindowCapture
from time import time
import supervision as sv
from perception import Perception
from rfbot import RFBot, BotMode
import os

# get the root path of your project
root_path = os.path.abspath(os.path.dirname(__file__))

# detection constants
DETECTION_CONFIDENCE = 0.55
    
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

def inputPromp() -> BotMode:
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

def printInfo() -> None:
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

def get_model_path() -> str:
    root_path = os.getcwd()
    relative_path = "YOLO/runs/detect/train3/weights/best.pt"
    model_path = os.path.join(root_path, relative_path)
    return model_path

def get_fps() -> float:
    return 1.0 / (time() - loop_time)

if __name__ == '__main__':
    printInfo() # print initial info about the bot to the user
    bot_mode = inputPromp() # ask for the input
    wincap = WindowCapture('RF Online')
    perception = Perception(None)
    font_position = (wincap.w - 300, wincap.h) # position for the fps display
    model_path = get_model_path() # path to the model
    model = YOLO(model=model_path) # initialize the model
    box_annotator = sv.BoxAnnotator(thickness=2, text_thickness=2, text_scale=1)
    loop_time = time()
    wincap.start() #start window capturing thread
    bot = RFBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), wincap, False, mode=bot_mode)
    while True:
        if wincap.screenshot is None:
            continue
        frame = wincap.screenshot.getImage()
        result = model.predict(source=frame, verbose=False, conf=DETECTION_CONFIDENCE)[0]
        detections = sv.Detections.from_yolov8(result)
        labels = [f"{model.model.names[class_id]} {confidence:0.55f}" for _, confidence, class_id, _ in detections]
        targets = perception.getPoints(detections.xyxy)
        if targets: # if there are targets, run routine
            bot.updateFrame(frame)
            bot.update_targets(targets)
            bot.run()
        else: # no targets, run different run routine
            bot.updateFrame(frame)
            bot.runNoTargets()
        frame = perception.drawVision(frame, detections, labels)
        perception.drawFPS(frame, get_fps(), (wincap.w - 100, wincap.h - 10))
        cv.imshow("yolov8", frame)
        loop_time = time()
        key = cv.waitKey(1)
        if key == ord('q'):
            wincap.stop()
            break
    wincap.stop()