import cv2 as cv
import numpy as np

def findClickPositions(needle_img_path,
                       heystack_img,
                       threshold = 0.8,
                       debug_mode = None):
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
    
    # returns coefficients for every row/cols on every position even hanging over
    result = cv.matchTemplate(heystack_img, needle_img, cv.TM_CCOEFF_NORMED)
    
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    # get all locations over the threshold and store it into np array
    locations = np.where(result >= threshold)
    # merge indeces on to tuples (0,0), (1,1)
    locations = list(zip(*locations[::-1]))
    
    if locations:
        needle_w = needle_img.shape[1]
        needle_h = needle_img.shape[0]
        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        
        for location in locations:
            # determine box around obj and draw box
            top_left = location
            bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
            cv.rectangle(heystack_img, top_left, bottom_right, line_color,1, line_type)
        
    cv.imshow("Matcher", heystack_img)
    cv.waitKey()
    
findClickPositions("needle2.jpg","heystack2.jpg")