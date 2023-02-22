from ultralytics import YOLO
import cv2 as cv
from windowCaptureYOLO import WindowCapture
from time import time
import supervision as sv
from perception import Perception
from rfbot import RFBot, BotState
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
# font constants
font = cv.FONT_HERSHEY_SIMPLEX
fontScale = 0.8
fontColor = (0, 255, 0)
fontPosition = (0,0)
thickness = 2

# detection constants
DETECTION_CONFIDENCE = 0.72
if __name__ == '__main__':
    wincap = WindowCapture('RF Online')
    perception = Perception(None)
    fontPosition = (wincap.w - 300, wincap.h)
    bot = RFBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))
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
            f"{model.model.names[class_id]} {confidence:0.72f}"
            for _, confidence, class_id, _
            in detections
        ]
        targets = perception.getPoints(detections.xyxy)
        # bot stuff
        if targets:
            bot.updateFrame(frame)
            # hover over target
            bot.run(targets)
            
            #xpos, ypos = bot.getScreenPosition(targets[0])
            #pyautogui.moveTo(x = xpos, y = ypos, _pause = False)
            #pyautogui.click()
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
            break
        
    wincap.stop()