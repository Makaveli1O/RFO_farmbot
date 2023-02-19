from threading import Thread, Lock
import cv2
from threadingInterface import ThreadInterface
import numpy as np
import time
from screenshot import Screenshot

class Detection(ThreadInterface):
    """Thread-safe detection of the object class. 
    Uses mutex semaphores to prevent multiple threads
    from reading and updating at the same time. Also uses
    detector.py and cascade classifier.
    """
    stopped = True
    lock = None
    boundingBoxes = []
    screenshot = None
    net = None
    colors = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    
    def __init__(self, model_path):
        self.lock = Lock() # mutex semaphore
        self.net = cv2.dnn.readNetFromTorch(model_path) # load
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3)) # random bb color
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        
    def getBoundingBoxes(self) -> list:
        """
        Returns:
            list:  all bounding boxes on the current screenshot
        """
        return self.boundingBoxes
        
    def update(self, screenshot : Screenshot) -> None:
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
                (H, W) = self.screenshot.getDimensions()
                # create input blob
                blob = cv2.dnn.blobFromImage(self.screenshot, 1 / 255.0, (416, 416), swapRB=True, crop=False)
                # set input blob
                self.net.setInput(blob)
                # get output layer names
                layer_names = self.net.getLayerNames()
                layer_names = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
                # forward pass
                start = time.time()
                outputs = self.net.forward(layer_names)
                end = time.time()
                # process detections
                self.lock.acquire()
                self.boundingBoxes = []
                for output in outputs:
                    for detection in output:
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]
                        if confidence > self.threshold:
                            box = detection[0:4] * np.array([W, H, W, H])
                            (centerX, centerY, width, height) = box.astype("int")
                            x = int(centerX - (width / 2))
                            y = int(centerY - (height / 2))
                            self.boundingBoxes.append([x, y, int(width), int(height)])
                self.lock.release()