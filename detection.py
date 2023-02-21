from threading import Thread, Lock
import cv2
from threadingInterface import ThreadInterface
import supervision as sv
from ultralytics import YOLO

class Detection(ThreadInterface):
    """Thread-safe detection of the object class. 
    Uses mutex semaphores to prevent multiple threads
    from reading and updating at the same time. Also uses
    detector.py and cascade classifier.
    """
    stopped = True
    lock = None
    boundingBoxes = []
    detections = None
    model = None
    screenshot = None
    
    def __init__(self, model_path) -> None:
        self.lock = Lock() # mutex semaphore
        self.model = YOLO(model_path)
        
    def getBoundingBoxes(self) -> list:
        """
        Returns:
            list:  all bounding boxes on the current screenshot
        """
        return self.boundingBoxes
        
    def update(self, screenshot):
        """Recieves screenshot of the captured game. Locking
        the semaphore before assigning it and releasing it
        afterwards is crucial for multi threading.
        Args:
            screenshot (_type_): _description_
        """
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()
    
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
        
    def run(self):
        """Implementation of the run method"""
        while not self.stopped:
            if not self.screenshot is None:
                # do object detection
                result = self.model(self.screenshot)[0] # 0th index because cuda returns list for some reason
                detections = sv.Detections.from_yolov8(result)
                boundingBoxes = detections.xyxy
                # lock the thread while updating the results
                self.lock.acquire()
                self.detections = detections
                self.boundingBoxes = boundingBoxes
                self.lock.release()