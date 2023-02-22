from threading import Lock, Thread
import pyautogui
from time import time, sleep
from enum import Enum
import math
import cv2
from threadingInterface import ThreadInterface


class BotState(Enum):
    SEARCHING = 0
    ATTACKING = 1
    INITIALIZING = 2
    MOVING = 3

class RFBot(ThreadInterface):
    """
    Returns:
        RFBot: Actual bot behaviour. !WORK IN PROGRESS!.
    """
    stopped = True
    lock = None
    window_offset = (0,0)
    window_w = 1920
    window_h = 1080
    
    state = None
    targets = []
    screenshot = None
    tooltips = []
    healthbar = None
    timestamp = None
    #constants
    INITIALIZINT_TIME = 5
    ATTACKING_TIME = 2
    IGNORE_RADIUS = 130
    TOOLTIP_MATCH_THRESHOLD = 0.75 # tooltip over other mobs is around 0.60, match is 0.90 +/-
    MOB_BAR_MATCH_THRESHOLD = 0.85
    HEALTHBAR_MATCH_THRESHOLD = 0.82 
    
    def __init__(self, window_offset, window_size):
        self.lock = Lock()
        
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]
        
        self.tooltips.append(cv2.imread('tooltip_crew.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltip_atrock.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltip_crew_red.jpg', cv2.IMREAD_UNCHANGED))
        
        self.healthbar = cv2.imread('healthbar_full.jpg', cv2.IMREAD_UNCHANGED)
        self.mobbar = cv2.imread('healthbar_big_full.jpg', cv2.IMREAD_UNCHANGED)
        
        self.state = BotState.INITIALIZING
        self.timestamp = time()
        
    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()
        
    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()
    def updateFrame(self, frame):
        self.lock.acquire()
        self.screenshot = frame
        self.lock.release()
        
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
    
    def run(self):
        while not self.stopped:
            success = self.clickTarget()
            # target found
            if success:
                print("attack")
                self.state = BotState.ATTACKING
            else:
                # keep searching
                return
    
    def clickTarget(self):
        """Targets are ordered by distance from center. Closest target is selected to move
        mouse over. Afterwards tooltip above the mob is cross matched to confirm the correctness
        of the finding.

        Returns:
            tuple: found target
        """
        #targets = self.orderByDistance(targets)
        targets = self.targets
        targetFound = False
        i = 0
        # pick one and click
        while not targetFound and i < len(targets):
            # load next target and get coords
            target = targets[i]
            #print(target)

            xpos, ypos = self.getScreenPosition(target)
            # move mouse
            #pyautogui.moveTo(x = xpos, y = ypos, _pause = False)
            # click target
            #pyautogui.click()
            
            if self.healthBarFound():
                # press space
                targetFound = True
                
            i += 1
        return targetFound
            
    def healthBarFound(self):
        # check screenshot for tooltip
        
        template_size = (250, 63)
        partial_frame = self.cropFrame(template_size)
        result = cv2.matchTemplate(partial_frame, self.healthbar, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(max_val)
        if max_val >= 0.99:
            return True
        return False
    
    def cropFrame(self, template_size : tuple, debug_mode = False):
        """Crops top-center part of the frame where healthbar should be.
        TODO crop a little better and try different resolutions
        Args:
            template_size (tuple): dimensions of the frame that is about to be cropped

        Returns:
            cv_image: _cropped image
        """
        height, width = self.screenshot.shape[:2]
        # calculate coords for the box
        top_left = (int(width / 2) - template_size[0]//2, 40 - template_size[1]//2)
        bottom_right = (int(width / 2) + template_size[0]//2, 100 + template_size[1]//2)
        # Extract portion of the frame
        portion = self.screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        if debug_mode:
            cv2.imshow("cropped", portion)
        return portion
    

    def orderByDistance(self, targets):
        """Order found bounding boxes by pythagorean distance from the center.

        Args:
            targets (_type_): _description_

        Returns:
            list: Ordered list of bounidng boxws
        """
        # our character is always in the center of the screen
        my_pos = (self.window_w / 2, self.window_h / 2)
        def pythagorean_distance(pos):
            return math.sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)

        targets = [t for t in targets if pythagorean_distance(t) > self.IGNORE_RADIUS]

        return targets
    
    def getScreenPosition(self, pos):
        """Converts position into screen position.

        Args:
            pos (tuple): Calculated position

        Returns:
            tuple: New screen position
        """
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])