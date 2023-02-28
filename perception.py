import cv2 as cv
import numpy as np
from enum import Enum
import supervision as sv
from fontUtils import FontUtils

class DebugModes(Enum):
    CONSOLE_ONLY = "console"
    FULL_DEBUG = "full"
     
class Perception:
    """Class that is responsible for detection of the objects within 
    the images. Computes midpoints, find objects and draws vision stuff
    to the debug window for the user.
    """
    FPS_LOW = 15
    FPS_MID = 20
    FPS_MID_HIGH = 25
    FPS_HIGH = 35
    FPS_ULTRA = 60
    
    RED = (255, 0, 0)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    LIGHT_GREEN = (144, 238, 144)
    LIME = (0, 255, 0)
    box_annotator = sv.BoxAnnotator(
                        thickness=2,
                        text_thickness=2,
                        text_scale=1
                    )
    def __init__(self, needle_img_path, algorithm = cv.TM_CCOEFF_NORMED):
        if needle_img_path:
            # load image to find
            self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)  
            # images dimensions
            self.needle_w = self.needle_img.shape[1]
            self.needle_h = self.needle_img.shape[0]
            # select comparison algorithm
            self.algorithm = algorithm
            # TODO all above probably deprecated
    
    def find(   self,
                heystack_img,
                threshold = 0.5,
                maxResults = 10):
        """Finds sub image within image given heystack image. Uses TM_COEFF_NORMED
        algorithm to recieve number btwn 0 and 1. 1 indicading closest matched pixels.
        min, max values from minMaxLoc is ALWAYS returned. This is why there is a 
        threshold to detect real matches from the fake ones.
        Args:
            needle_img_path (_type_): _description_
            heystack_img (_type_): _description_
            threshold (float, optional): _description_. Defaults to 0.5.
            debug_mode (_type_, optional): _description_. Defaults to None.
        """
        # returns coefficients for every row/cols on every position even hanging over
        result = cv.matchTemplate(heystack_img, self.needle_img, self.algorithm)
        
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        # get all locations over the threshold and store it into np array
        locations = np.where(result >= threshold)
        # merge indeces on to tuples (0,0), (1,1)
        locations = list(zip(*locations[::-1]))
        
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        
        boundingBoxes = self.__buildBoundingBoxes(  locations,
                                                    self.needle_w,
                                                    self.needle_h)
        
        eps = 0.5 # how close the rectangles should be to group them
        groupThreshold = 1
        # group overlapping rectangles
        boundingBoxes, weights = cv.groupRectangles(boundingBoxes, groupThreshold, eps)
        
        # performance -> return limited number of results
        if len(rectangles) > maxResults:
            print('Warning: too many results, raise the threshold.')
            rectangles = rectangles[:maxResults]

        return rectangles
    
    def getPoints(self, boundingBoxes):
        """Converts bounding boxes into clickable midpoints
        Args:
            boundingBoxes (_type_): _description_
        Returns:
            _type_: _description_
        """
        # modpoints of boundingBoxes of found objects
        midPoints = []    
        # loop over unpacked bounding box rectangles
        for (x1, y1, x2, y2) in boundingBoxes:
            midPoints.append(self.__getMidPointYolo(x1, y1, x2 ,y2))
        return midPoints
        
    def __buildBoundingBoxes(self, locations, needle_w, needle_h) -> int | None:
        """
        @Deprecated
        Returns a list of rectangles {x,y,w,h}
        x,y -> coordinates of upper left corner
        w,h -> width and height 
        Args:
            locations (_type_): _description_
        """
        rectangles = []
        # append list of rectangles twice, since groupRectangles function
        # requires overlapping of at least 2 rectangles meaning single would not
        # be accounted in result
        for location in locations:
            rect = [int(location[0]), int(location[1]), needle_w, needle_h]
            rectangles.append(rect)
            rectangles.append(rect)
            
        return rectangles

    def __getMidPoint(self, x, y, w, h) -> int :
        """@DEPRECATED

        Args:
            x (_type_): _description_
            y (_type_): _description_
            w (_type_): _description_
            h (_type_): _description_

        Returns:
            int: _description_
        """
        return (x + int(w / 2), y + int(h / 2))
    
    def __getMidPointYolo(self, x1, y1, x2, y2) -> int:
        return (int((x1+x2)/2), int((y1+y2)/2))
    
    def drawFPS(self, frame, fps,
                fontPosition = (0,0),
                fontColor = (0, 255, 0),
                thickness = 2,
                font = cv.FONT_HERSHEY_SIMPLEX,
                fontScale = 0.8) -> None:
        """Draws a fps to bottom right corner. Color changes based on performance

        Args:
            frame (cv_im): processed frame
            fps (int): calculated fps
            fontPosition (tuple, optional): _description_. Defaults to (0,0).
            fontColor (tuple, optional): _description_. Defaults to (0, 255, 0).
            thickness (int, optional): _description_. Defaults to 2.
            font (_type_, optional): _description_. Defaults to cv.FONT_HERSHEY_SIMPLEX.
            fontScale (float, optional): _description_. Defaults to 0.8.

        Returns:
            _type_: _description_
        """
        if frame is None:
            return frame
        if fps < self.FPS_MID:
            fontColor = self.RED
        elif fps >= self.FPS_MID and fps <= self.FPS_MID_HIGH:
            fontColor = self.ORANGE
        elif fps >= self.FPS_MID_HIGH and fps <= self.FPS_HIGH:
            fontColor = self.YELLOW
        elif fps >= self.FPS_HIGH and fps <= self.FPS_ULTRA:
            fontColor = self.LIGHT_GREEN
        elif fps <= self.FPS_ULTRA:
            fontColor = self.FPS_LIME
        cv.putText(frame, str(fps)+" fps", 
                   fontPosition,
                   font, 
                   fontScale,
                   fontColor,
                   thickness)
        return frame
    
    def drawVision(self, input_frame, detections, labels):
        """Draws annotations to detected objects

        Args:
            input_frame (cv_im): Processed image
            detections (sv.Detection): Detected objects

        Returns:
            _type_: _description_
        """
        if detections is None:
            return input_frame
        output_frame = self.box_annotator.annotate(scene=input_frame, detections=detections, labels=labels)
        return output_frame
    
    def drawSecondaryVision(self, input_frame, textPos: tuple, recPos : tuple, recDim: tuple):
        """Important: Call this method after drawVision() to see detections!

        Args:
            input_frame (_type_): _description_
        """
        # draw ROI rectangle
        fontUtils = FontUtils()
        cv.putText(input_frame, "ROI", 
                (textPos[0] - 20, textPos[1]),
                fontUtils.font, 
                fontUtils.fontScale,
                (0, 0, 255),
                fontUtils.thickness)
        cv.rectangle(input_frame, (recPos[0], recPos[1]), (recPos[0]+ recDim[0] , recPos[1] + recPos[1]), (0, 0, 255), thickness=2)
        return input_frame

    def drawMidPoints(self, heystack_img, points):
        """@Deprecated: draws mitPoints of the bounding boxes

        Args:
            heystack_img (img): processed img
            points (array)
        """
        if points is []:
            return heystack_img
        # until all threads are activated (detector takes long to load YOLO)
        # do not annotate at all
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in self.__getMidPointYolo(points):
            # draw the center point
            try:
                cv.drawMarker(heystack_img, (int(center_x), int(center_y)), marker_color, marker_type)
            except Exception as e:
                print(e)

        return heystack_img