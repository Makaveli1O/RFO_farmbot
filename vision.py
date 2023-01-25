import cv2 as cv
import numpy as np

def findClickPositions(needle_img_path,
                       heystack_img,
                       threshold = 0.5,
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
    
    result = cv.matchTemplate(heystack_img, needle_img, cv.TM_CCOEFF_NORMED)
    
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    
    # found image within threshold
    if max_val >= threshold:
        # needle dimensions
        needle_w = needle_img.shape[1]
        needle_h = needle_img.shape[0]
        
        top_left = max_loc
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
        
        # draw rectangle around found obj
        cv.rectangle(heystack_img, top_left, bottom_right,
                     color = (0,255,0), thickness = 1, lineType = cv.LINE_4)
        cv.imshow("Result", heystack_img)
        cv.waitKey()
    else:
        print("Needle not found")
    
findClickPositions("needle.jpg","heystack.jpg")