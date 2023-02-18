from threading import Lock, Thread
import pyautogui
from time import time, sleep
from enum import Enum
import math
import cv2

class BotState(Enum):
    SEARCHING = 0
    ATTACKING = 1
    INITIALIZING = 2
    MOVING = 3

class RFBot:
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
    HEALTHBAR_MATCH_THRESHOLD = 0.75 
    
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
        
        pass
    
    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()
        
    def update_screenshot(self, screenshot):
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
        while not self.stopped:
        
            if self.state == BotState.INITIALIZING:
                #print("Initializing")
               # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZINT_TIME:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                success = self.clickTarget()
                # target found
                if success:
                    self.lock.acquire()
                    self.state = BotState.ATTACKING
                    self.lock.release()
                else:
                    # keep searching
                    continue
                
            elif self.state == BotState.ATTACKING:
                if self.mobBarFound():
                    pyautogui.press("space")
                    self.lock.acquire()
                    self.state = BotState.ATTACKING
                    self.lock.release()
                else:
                    # Mob bar missing, continue searching (either dead or escaped)
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
            
    def healthBarFound(self):
        # check screenshot for tooltip
        result = cv2.matchTemplate(self.screenshot, self.healthbar, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= self.HEALTHBAR_MATCH_THRESHOLD:
            return True
        return False
    
    def mobBarFound(self):
        # check screenshot for tooltip
        result = cv2.matchTemplate(self.screenshot, self.mobbar, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= self.MOB_BAR_MATCH_THRESHOLD:
            return True
        return False
        
    def clickTarget(self):
        """Targets are ordered by distance from center. Closest target is selected to move
        mouse over. Afterwards tooltip above the mob is cross matched to confirm the correctness
        of the finding.

        Returns:
            tuple: found target
        """
        targets = self.orderByDistance(self.targets)
        targetFound = False
        i = 0
        while not targetFound and i < len(targets):
            if self.stopped:
                break
            # load next target and get coords
            target = targets[i]

            xpos, ypos = self.getScreenPosition(target)
            # print('Moving mouse to x:{} y:{}'.format(xpos, ypos))
            # move mouse
            pyautogui.moveTo(x = xpos, y = ypos)
            # confirm position by checking tooltip name
            if self.confirmTooltip(target):
                targetFound = True
                pyautogui.click()
            else:
                pass
                # print("Incorrect mob found.")
            i += 1

        return targetFound
    
    def confirmTooltip(self, target) -> bool:
        """Check whether given tooltip is in the screenshot.
        TODO: Optimization, only check near the mouse

        Args:
            target (_type_): _description_

        Returns:
            bool: True or false if correct tooltip is found.
        """
        # check screenshot for tooltips
        for tooltip in self.tooltips:
            result = cv2.matchTemplate(self.screenshot, tooltip, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
                print("Tooltip {} found: {}".format(tooltip, max_val))
                return True
   
        return False
        
        
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