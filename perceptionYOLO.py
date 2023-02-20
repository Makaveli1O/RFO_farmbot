import cv2 as cv
import numpy as np
from enum import Enum
import supervision as sv
from perception import Perception

class DebugModes(Enum):
    CONSOLE_ONLY = "console"
    FULL_DEBUG = "full"
    
class PerceptionYOLO(Perception):
    """Class that is responsible for detection of the objects within 
    the images. Computes midpoints, find objects and draws vision stuff
    to the debug window for the user.
    """
    
    def __init__(self):

            self.box_annotator = sv.BoxAnnotator(
                thickness=2,
                text_thickness=2,
                text_scale=1
            )
    
    def drawVision(self, input_frame, result):
        output_frame = self.box_annotator.annotate(scene=input_frame, detections=detections)
        return output_frame