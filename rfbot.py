from threading import Lock, Thread
import pyautogui
from time import time, sleep, monotonic
from enum import Enum
import math
import cv2
from threadingInterface import ThreadInterface


class BotState(Enum):
    SEARCHING = 0
    ATTACKING = 1
    INITIALIZING = 2
    MOVING = 3
    WAITING = 4

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
    wincapRef = None
    
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
    TOOLTIP_MATCH_THRESHOLD = 0.65 # tooltip over other mobs is around 0.60, match is 0.90 +/-
    HEALTHBAR_MATCH_THRESHOLD = 0.50
    
    def __init__(self, window_offset, window_size, wincapRef):
        self.lock = Lock()
        self.last_click_time = monotonic()
        self.wincapRef = wincapRef
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
        # IMPORTANT THIS ELIMINATES "fail-safe" feature to help in case your script is buggy
        # https://stackoverflow.com/questions/46736652/pyautogui-press-causing-lag-when-called
        pyautogui.PAUSE = 0
        
    def update_targets(self, targets):
        self.targets = targets
        
    def update_screenshot(self, screenshot):
        self.screenshot = screenshot
    def updateFrame(self, frame):
        self.screenshot = frame
        
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
        
    def runAutoAttack(self) -> bool:
        if self.__healthBarFound():
            print("Searchbar is present!")
            print("Press space")
            current_time = monotonic()
            time_since_last_click = current_time - self.last_click_time
            if time_since_last_click < 1: # only allow a new click after 1 second
                return True

            # perform space press
            pyautogui.press("space")

            # update last click time
            self.last_click_time = current_time
        else:
            self.state = BotState.SEARCHING
            return False
    def run(self):
        # simetimes, healthbar is present but state changes to searching
        if self.__healthBarFound():
            print("Searchbar is present!")
            print("Press space")
            current_time = monotonic()
            time_since_last_click = current_time - self.last_click_time
            if time_since_last_click < 1: # only allow a new click after 1 second
                return

            # perform space press
            pyautogui.press("space")

            # update last click time
            self.last_click_time = current_time
        else:
            self.state = BotState.SEARCHING
            # target found
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                print("Initializing bpt..")
                if time() > self.timestamp + self.INITIALIZINT_TIME:
                    self.state = BotState.SEARCHING

            elif self.state == BotState.SEARCHING:
                
                success = self.clickTarget()

                # if successful, switch state to attacking
                if success:
                    self.state = BotState.ATTACKING
                else:
                    print("clicktarget was not succesfull returning to main loop.")
                    print("Clearing targets")
                    self.update_targets([])
                    return
                
            
    
    def clickTarget(self):
        """Targets are ordered by distance from center. Closest target is selected to move
        mouse over. Afterwards tooltip above the mob is cross matched to confirm the correctness
        of the finding.

        Returns:
            tuple: found target
        """
        targets = self.__orderByDistance(targets)
        targets = self.targets
        targetFound = False
        i = 0
        # pick one and click
        #while not targetFound and i < len(targets):
        # load next target and get coords
        try:
            target = targets[i]
        except:
            print("Targets are empty")
            return

        xpos, ypos = self.getScreenPosition(target)
        # move mouse
        pyautogui.moveTo(x = xpos, y = ypos, _pause = False)
        
        #toolbar check
        offsetY = 25
        if self.__tooltipFound((xpos,ypos - offsetY)):
            print("tooltip found! CLICK!")         
            # click target
            pyautogui.click()
            return True
        else:
            #tooltip not found give few new frames to check
            print("not found!")
            i = 0
            while not self.__tooltipFound((xpos,ypos - offsetY)):
                if i > 5:
                    print("Tooltip not found.")
                    return False
                print("Update frame " + str(i))
                self.update_screenshot(self.wincapRef.screenshot.getImage())
                i += 1
            # tooltip found  
            pyautogui.click()
            return True
            
    def __healthBarFound(self):
        # check screenshot for tooltip
        
        height, width = self.screenshot.shape[:2]
        # TODO pixels exact numbers should be calculated by percentages
        partial_frame = self.__cropFrame(template_size = (223, 68), x=width//2, y=20)
        result = cv2.matchTemplate(partial_frame, self.healthbar, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= self.HEALTHBAR_MATCH_THRESHOLD:
            return True
        return False
    
    def __tooltipFound(self, mousePos: tuple):
        # check screenshot for tooltip
        height, width = self.screenshot.shape[:2]
        # TODO pixels exact numbers should be calculated by percentages
        partial_frame = self.__cropFrame(template_size = (200, 200), x=mousePos[0], y=mousePos[1])
        for tooltip in self.tooltips:
            result = cv2.matchTemplate(partial_frame, tooltip, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(max_val)
            if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
                return True
            return False
    
    def __cropFrame(self, template_size: tuple, x: int, y: int, debug_mode: bool = False):
        """Crops a part of the frame based on the given parameters.

        Args:
            template_size (tuple): The size of the frame to be cropped.
            x (int): The x-coordinate of the center of the crop area.
            y (int): The y-coordinate of the center of the crop area.
            debug_mode (bool, optional): Whether to display the cropped image for debugging purposes. Defaults to False.

        Returns:
            cv2_image: The cropped image.
        """
        height, width = self.screenshot.shape[:2]

        # Calculate coordinates for the box
        half_width = template_size[0] // 2
        half_height = template_size[1] // 2
        top_left_x = max(x - half_width, 0)
        top_left_y = max(y - half_height, 0)
        bottom_right_x = min(x + half_width, width)
        bottom_right_y = min(y + half_height, height)
        portion = self.screenshot[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
        if debug_mode:
            cv2.imshow("cropped", portion)

        return portion

    def __orderByDistance(self, targets):
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