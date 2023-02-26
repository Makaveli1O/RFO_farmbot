from ultralytics import YOLO
import cv2 as cv
from windowCaptureYOLO import WindowCapture
from time import time
import supervision as sv
from perception import Perception
from rfbot import RFBot, BotState, BotMode
from drawer import Drawer
    
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

# font constants
font = cv.FONT_HERSHEY_SIMPLEX
fontScale = 0.8
fontColor = (0, 255, 0)
fontPosition = (0,0)
thickness = 2

# detection constants
DETECTION_CONFIDENCE = 0.55
if __name__ == '__main__':
    bot_mode = inputPromp()
    wincap = WindowCapture('RF Online')
    perception = Perception(None)
    fontPosition = (wincap.w - 300, wincap.h)
    # load a model
    model = YOLO(model="C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\runs\\detect\\train3\\weights\\best.pt")
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )
    loop_time = time()
    # capture window screens 
    wincap.start()
    # set custom observable crops for animus and healthbar(resolutions different solutions)
    drawer = Drawer(wincap.get_screenshot().getImage())
    if bot_mode == BotMode.SUMMONER:
        drawer.defineAnimusRectangle()
        drawer.defineHealthBarRectangle()
    else:
        drawer.defineHealthBarRectangle()
    
    bot = RFBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h), wincap, False)
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
            bot.runAutoAttack()
        
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
    #bot.stop()
    wincap.stop()