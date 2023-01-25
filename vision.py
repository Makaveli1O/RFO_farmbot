import cv2 as cv
import numpy as np
from enum import Enum

class DebugModes(Enum):
    CONSOLE_ONLY = "console"
    FULL_DEBUG = "full"
    
def findClickPositions(needle_img_path,
                       heystack_img,
                       threshold = 0.8,
                       debugMode = None):
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
    # img searching through
    heystack_img = cv.imread(heystack_img, cv.IMREAD_UNCHANGED)
    # searching img
    needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)  
    
    # select comparison algorithm
    algorithm = cv.TM_CCOEFF_NORMED
    
    # returns coefficients for every row/cols on every position even hanging over
    result = cv.matchTemplate(heystack_img, needle_img, algorithm)
    
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    # get all locations over the threshold and store it into np array
    locations = np.where(result >= threshold)
    # merge indeces on to tuples (0,0), (1,1)
    locations = list(zip(*locations[::-1]))
    
    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]
    boundingBoxes = buildBoundingBoxes(locations,
                                       needle_w,
                                       needle_h)
    
    eps = 0.5 # how close the rectangles should be to group them
    groupThreshold = 1
    # group overlapping rectangles
    boundingBoxes, weights = cv.groupRectangles(boundingBoxes, groupThreshold, eps)
    
    # modpoints of boundingBoxes of found objects
    midPoints = []
    if len(boundingBoxes):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        
        # loop over unpacked bounding box rectangles
        for (x, y, w, h) in boundingBoxes:
            # determine box around obj and draw box
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            
            if debugMode is not None:
                cv.rectangle(heystack_img, top_left, bottom_right, line_color,1, line_type)
                cv.drawMarker(heystack_img, getMidPoint(x, y, w ,h), (0, 0, 255),cv.MARKER_CROSS)
                
            midPoints.append(getMidPoint(x, y, w ,h))
    if debugMode == DebugModes.FULL_DEBUG:
        cv.imshow("Result", heystack_img)
    cv.waitKey()
    
    return midPoints
    
def buildBoundingBoxes(locations, needle_w, needle_h) -> int | None:
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

def getMidPoint(x, y, w, h) -> int :
    return (x + int(w / 2), y + int(h / 2))
        
print(findClickPositions("needle2.jpg","heystack2.jpg", 0.8, True))