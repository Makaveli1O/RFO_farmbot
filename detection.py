from threading import Thread, Lock
import cv2
from threadingInterface import ThreadInterface

class Detection:
    """Thread-safe detection of the object class. 
    Uses mutex semaphores to prevent multiple threads
    from reading and updating at the same time. Also uses
    detector.py and cascade classifier.
    """
    stopped = True
    lock = None
    boundingBoxes = []
    cascade = None
    screenshot = None
    
    def __init__(self, model_path):
        self.lock = Lock() # mutex semaphore
        self.cascade = cv2.CascadeClassifier(model_path)
        
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
                boundingBoxes = self.cascade.detectMultiScale(self.screenshot)
                # lock the thread while updating the results
                self.lock.acquire()
                self.boundingBoxes = boundingBoxes
                self.lock.release()