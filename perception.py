import cv2 as cv
import numpy as np
from enum import Enum

class DebugModes(Enum):
    CONSOLE_ONLY = "console"
    FULL_DEBUG = "full"
    
class Perception:
    """Class that is responsible for detection of the objects within 
    the images. Computes midpoints, find objects and draws vision stuff
    to the debug window for the user.
    """
    
    def __init__(self, needle_img_path, algorithm = cv.TM_CCOEFF_NORMED):
        if needle_img_path:
            # load image to find
            self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)  
            # images dimensions
            self.needle_w = self.needle_img.shape[1]
            self.needle_h = self.needle_img.shape[0]
        # select comparison algorithm
        self.algorithm = algorithm
    
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
        for (x, y, w, h) in boundingBoxes:
            # determine box around obj and draw box
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            midPoints.append(self.__getMidPoint(x, y, w ,h))
        return midPoints
        
    def __buildBoundingBoxes(self, locations, needle_w, needle_h) -> int | None:
        """Returns a list of rectangles {x,y,w,h}
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
        return (x + int(w / 2), y + int(h / 2))
    
    def drawBoundingBoxes(self, heystack_img, boundingBoxes):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in boundingBoxes:
            # determine the box positions
            top_left = (x, y) 
            bottom_right = (x + w, y + h)
            # draw the box
            cv.rectangle(heystack_img, top_left, bottom_right, line_color, lineType=line_type)
            
        return heystack_img

    def drawMidPoints(self, heystack_img, points):
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            # draw the center point
            cv.drawMarker(heystack_img, (center_x, center_y), marker_color, marker_type)

        return heystack_img