from ultralytics import YOLO
import cv2 as cv
from windowCaptureYOLO import WindowCapture
from time import time
from ultralytics import YOLO
import supervision as sv
from perceptionYOLO import PerceptionYOLO

class Detection:
    xyxy = None
    confidence = None
    class_id = None
    
font = cv.FONT_HERSHEY_SIMPLEX
fontScale = 0.8
fontColor = (0, 255, 0)
fontPosition = (0,0)
thickness = 2

if __name__ == '__main__':
    wincap = WindowCapture('RF Online')
    perception = PerceptionYOLO()
    fontPosition = (wincap.w - 300, wincap.h)
    # load a model
    model = YOLO("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\runs\\detect\\train3\\weights\\best.pt")
    
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
        result = model(frame)[0] # 0th index because cuda returns list for some reason
        detections = sv.Detections.from_yolov8(result)
        # get midpoints from boundingboxes
        targets = perception.getPoints(detections.xyxy)
        frame = box_annotator.annotate(scene=frame, detections=detections)
        cv.putText(frame, "FPS: "+str(round(1 / (time() - loop_time))), fontPosition, font, fontScale, fontColor, thickness)
        
        cv.imshow("yolov8", frame)
        
        loop_time = time()
        key = cv.waitKey(1)
        if key == ord('q'):
            wincap.stop()
            break
        
    wincap.stop()