from threading import Lock, Thread
import pyautogui
from time import time, sleep, monotonic
from enum import Enum
import math
import cv2
from threadingInterface import ThreadInterface
from logger import Logger
from drawer import Drawer
from fontUtils import FontUtils


class BotState(Enum):
    SEARCHING = 0
    ATTACKING = 1
    INITIALIZING = 2
    MOVING = 3
    WAITING = 4
    
class BotMode(Enum):
    AUTO_ATTACK = 0
    SUMMONER = 1 # check for animus and attack with macro instead of spacebar
    #MACRO_ATTACK_NOT_IMPLEMENTED = 2 # attack with macro instead of spacebar defaults to f1

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
    logger = Logger()
    mode = None
    moving_frames = 0
    
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
    TOOLTIP_MATCH_THRESHOLD = 0.5 # tooltip over other mobs is around 0.60, match is 0.90 +/-
    HEALTHBAR_MATCH_THRESHOLD = 0.7
    ANIMUS_MATCH_THRESHOLD = 0.85
    
    def __init__(self, 
                 window_offset,
                 window_size,
                 wincapRef,
                 debug_mode = False,
                 mode = BotMode.AUTO_ATTACK,
                 ):
        self.lock = Lock()
        self.last_click_time = monotonic()
        self.wincapRef = wincapRef
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]
        self.logger.enabled(debug_mode)
        self.mode = mode
        
        self.tooltips.append(cv2.imread('tooltip_crew.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltip_atrock.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltip_crew_red.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltip_atrock_red.jpg', cv2.IMREAD_UNCHANGED))
        
        self.state = BotState.INITIALIZING
        self.timestamp = time()
        # IMPORTANT THIS ELIMINATES "fail-safe" feature to help in case your script is buggy
        # https://stackoverflow.com/questions/46736652/pyautogui-press-causing-lag-when-called
        pyautogui.PAUSE = 0
        
        self.__setup()
        
        self.logger.log("Starting RF bot ------------------------------\n")
        self.logger.log("Window offset: " + str(window_offset))
        self.logger.log("Window size: " + str(window_size))
        self.logger.log("Debug mode: " + str(debug_mode))
        self.logger.log("Bot mode: " + str(self.mode))
        self.logger.log("Keybinding: F1 macro attack, F2 animus recovery macro")
        self.logger.log("------------------------------------------------\n")
        
    def __setup(self):
        """ Setup bot observable areas"""
        # set custom observable crops for animus and healthbar(resolutions different solutions)
        self.drawer = Drawer(self.wincapRef.get_screenshot().getImage())
        if self.mode == BotMode.SUMMONER:
            self.drawer.defineAnimusRectangle()
            self.drawer.defineHealthBarRectangle()
            self.saveAnimusImage()
            self.saveHealthBarImage()
        else:
            self.drawer.defineHealthBarRectangle()
        return
    
    def saveAnimusImage(self):
        """ Save animus bar image for template matching"""
        self.screenshot = self.wincapRef.get_screenshot().getImage()
        cropped = self.__cropFrameCustom(self.drawer.getAnimusRectangle())
        cv2.imwrite("animusbar.jpg", cropped, [cv2.IMWRITE_JPEG_QUALITY, 100])
        self.animusBar = cv2.imread('animusbar.jpg', cv2.IMREAD_UNCHANGED)
        self.logger.notice("Animus bar saved")
        return
    
    def saveHealthBarImage(self):
        """ Save Healthbar bar image for template matching"""
        self.screenshot = self.wincapRef.get_screenshot().getImage()
        cropped = self.__cropFrameCustom(self.drawer.getHealthBarRectangle())
        cv2.imwrite("healthbar_big_full.jpg", cropped)
        self.healthbar = cv2.imread('healthbar_big_full.jpg', cv2.IMREAD_UNCHANGED)
        self.logger.notice("Healthbar saved")
        return
        
    def update_targets(self, targets):
        self.targets = targets
        
    def update_screenshot(self, screenshot):
        self.screenshot = screenshot
        
    def updateFrame(self, frame):
        self.screenshot = frame
        
    def start(self):
        self.last_click_time = monotonic()
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
        
    def runAutoAttack(self) -> bool:
        #if self.detectCharacterMovement():
        #    self.stopMovement()
        #    return 
        # first check for animus bar if corresponding bot mode is set
        if self.mode == BotMode.SUMMONER:
            if not self.__animusBarFound():
                self.logger.notice("Animus bar not found! Recovering animus...")
                pyautogui.press('f2')
                # return dunno whether autoattack when not animus is not present or not test required
        # check for healthbar
        if self.__healthBarFound():
            self.logger.log("Searchbar is present!")
            self.logger.log("Attack")
            current_time = monotonic()
            time_since_last_click = current_time - self.last_click_time
            if time_since_last_click < 1: # only allow a new click after 1 second
                return True

            # perform attack press
            if self.mode == BotMode.AUTO_ATTACK:
                pyautogui.press("space")
            elif self.mode == BotMode.SUMMONER:
                pyautogui.press('f1')
            else:
                raise("Bot mode not supported")
            # update last click time
            self.last_click_time = current_time
        else:
            # meanwhile loot
            self.logger.log("Looting")
            pyautogui.press("x")
            self.state = BotState.SEARCHING
            return False
        
    def run(self):
        if self.detectCharacterMovement():
            self.stopMovement()
            return 
        if self.mode == BotMode.SUMMONER:
            if not self.__animusBarFound():
                self.logger.log("Animus bar not found! Recovering animus...")
                pyautogui.press('f2')
                # return dunno whether autoattack when not animus is not present or not test required
        # sometimes, healthbar is present but state changes to searching
        if self.__healthBarFound():
            self.logger.log("Searchbar is present!")
            current_time = monotonic()
            time_since_last_click = current_time - self.last_click_time
            if time_since_last_click < 1: # only allow a new click after 1 second
                return

            # perform attack
            if self.mode == BotMode.AUTO_ATTACK:
                pyautogui.press("space")
                print("SPACE")
            elif self.mode == BotMode.SUMMONER:
                pyautogui.press('f1')
            else:
                raise("Bot mode not supported")

            # update last click time
            self.last_click_time = current_time
        else:
            self.state = BotState.SEARCHING
            # target found
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                self.logger.log("Initializing bot..")
                if time() > self.timestamp + self.INITIALIZINT_TIME:
                    self.state = BotState.SEARCHING

            elif self.state == BotState.SEARCHING:
                success = self.clickTarget()

                # if successful, switch state to attacking
                if success:
                    self.state = BotState.ATTACKING
                else:
                    self.logger.log("clicktarget was not succesfull returning to main loop. Clearing targets")
                    self.update_targets([])
                    return
                
    def stopMovement(self):
        """Clicks the center of the screen to prevent character from moving"""
        # TODO make this be configurable during loading
        offsetY = 70
        offsetX = 0
        self.logger.log("Clicking center")
        center_x, center_y = self.screenshot.shape[1] // 2 + offsetX, self.screenshot.shape[0] // 2 + offsetY
        pyautogui.moveTo(x = center_x, y = center_y, _pause = False)
        pyautogui.click()
    
    def clickTarget(self):
        """Targets are ordered by distance from center. Closest target is selected to move
        mouse over. Afterwards tooltip above the mob is cross matched to confirm the correctness
        of the finding.

        Returns:
            tuple: found target
        """
        targets = self.targets
        targets = self.__orderByDistance(targets)
        targetFound = False
        i = 0
        # pick one and click
        #while not targetFound and i < len(targets):
        # load next target and get coords
        try:
            target = targets[i]
        except:
            self.logger.log("Targets are empty")
            return


        xpos, ypos = self.getScreenPosition(target)
        # move mouse
        self.logger.log("moving mouse to {0}, {1}".format(xpos, ypos))
        pyautogui.moveTo(x = xpos, y = ypos, _pause = False)
        
        #toolbar check
        offsetY = 25
        if self.__tooltipFound((xpos,ypos - offsetY)):
            self.logger.log("tooltip found! CLICK!", True)         
            # click target
            if monotonic() - self.last_click_time > 0.3 or self.last_click_time == 0:
                pyautogui.click()
                self.last_click_time = monotonic()
            else:
                self.logger.log("Clicking too fast!")
            #pyautogui.click()
            #self.last_click_time = monotonic()
            return True
        else:
            #tooltip not found give few new frames to check
            self.logger.log("Tooltip not found!")
            i = 0
            while not self.__tooltipFound((xpos,ypos - offsetY)):
                if i > 5:
                    self.logger.log("Tooltip not found.")
                    return False
                self.logger.log("Update frame " + str(i))
                self.update_screenshot(self.wincapRef.screenshot.getImage())
                i += 1
            # tooltip found  
            self.logger.log("tooltip found! CLICK two", True)
            if monotonic() - self.last_click_time > 0.3:
                pyautogui.click()
                self.last_click_time = monotonic()
            else:
                self.logger.log("Clicking too fast!")
            #pyautogui.click()
            return True
            
    #TODO merge __tooltipFound and __healthBarFound into one more abstract function
    def __healthBarFound(self):
        # check screenshot for healthbar
        height, width = self.screenshot.shape[:2]
        partial_frame = self.__cropFrameCustom(self.drawer.getHealthBarRectangle())
        # resize, since saved .jpeg can be different size than current screen part
        self.healthbar = cv2.resize(self.healthbar, (partial_frame.shape[1], partial_frame.shape[0]))
        result = cv2.matchTemplate(partial_frame, self.healthbar, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        self.logger.log("Healthbar found: " + str(max_val))
        if max_val >= self.HEALTHBAR_MATCH_THRESHOLD:
            return True
        return False
    
    def __animusBarFound(self):
        # check screenshot for healthbar
        height, width = self.screenshot.shape[:2]
        partial_frame = self.__cropFrameCustom(self.drawer.getAnimusRectangle())
        # resize, since saved .jpeg can be different size than current screen part
        self.animusBar = cv2.resize(self.animusBar, (partial_frame.shape[1], partial_frame.shape[0]))
        result = cv2.matchTemplate(partial_frame, self.animusBar, cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        self.logger.log("AnimusBar found: " + str(max_val))
        if max_val >= self.ANIMUS_MATCH_THRESHOLD:
            return True
        return False
    
    def __tooltipFound(self, mousePos: tuple):
        # check screenshot for tooltip
        height, width = self.screenshot.shape[:2]
        partial_frame = self.__cropFrame(template_size = (200, 200), x=mousePos[0], y=mousePos[1])
        for tooltip in self.tooltips:
            result = cv2.matchTemplate(partial_frame, tooltip, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            self.logger.log("Tooltip ("+str(tooltip)+") val: " + str(max_val))
            if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
                return True
            return False
    
    def __cropFrameCustom(self, rect : Drawer.Rectangle, debug_mode: bool = False):
        """Crops a part of the frame based on the given parameters.
        Replaces @__cropFrame fro healthbar and animus check

        Args:
            rect (Drawer.Rectangle): Drawed rectangle object
            debug_mode (bool, optional): Logs to the console. Defaults to True.

        Returns:
            _type_: Cropped part of the frame
        """
        portion = self.screenshot[rect.top_left[1]:rect.bottom_right[1], rect.top_left[0]:rect.bottom_right[0]]
        #portion = self.screenshot[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
        if debug_mode:
            cv2.imshow("cropped", portion)
        return portion
    
    def __cropFrame(self, template_size: tuple, x: int, y: int, debug_mode: bool = False):
        """Crops a part of the frame based on the given parameters. This is used to crop the frame
        to a smaller size to speed up the template matching. Also is used only for checking tooltip.
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
        #empty
        if len(targets) == 0:
            return targets
        # our character is always in the center of the screen
        my_pos = (self.window_w / 2, self.window_h / 2)
        def pythagorean_distance(pos):
            return math.sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)

        targets = [t for t in targets if pythagorean_distance(t) > self.IGNORE_RADIUS]

        return targets
    
    def detectCharacterMovement(self, debug_mode: bool = True) -> bool:
        """Detects if the character is moving.

        Returns:
            bool: True if the character is moving.
        """
        MOVEMENT_THRESHOLD = 17   # need to experiment with this value 
        CONSECUTIVE_FRAMES_THRESHOLD = 5 # adjust this threshold as needed
        
        center_x, center_y = self.screenshot.shape[1] // 2, self.screenshot.shape[0] // 2
        offsetX, offsetY = 300, 0 #make roi center a bit to the right
        # define the ROI
        roi_size = 200
        x, y = center_x - roi_size // 2 + offsetX, center_y - roi_size // 2 + offsetY
        w, h = roi_size, roi_size
        
        # get avg 
        avg = self.wincapRef.get_avg()
        # Make sure both images have the same size and number of channels
        if self.screenshot.shape != avg.shape:
            avg = cv2.resize(avg, (self.screenshot.shape[1], self.screenshot.shape[0]))
        if self.screenshot.shape[-1] != avg.shape[-1]:
            avg = cv2.cvtColor(avg, cv2.COLOR_BGR2GRAY)
        
        # Compute the running average
        alpha = 0.5  # adjust this parameter to control the rate of update
        cv2.accumulateWeighted(self.screenshot, avg, alpha)
        background = cv2.convertScaleAbs(avg)

        
        # Convert the current frame and background to grayscale
        frame_gray = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2GRAY)
        background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        
        # Compute the absolute difference between the frame and background
        frame_diff = cv2.absdiff(background_gray, frame_gray)

        # Apply a threshold to obtain a binary image
        thresh = cv2.threshold(frame_diff, MOVEMENT_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        
        # Apply a morphological operation to remove noise and fill gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # For some reason freezes main YOLO capture
        if debug_mode is True:
            fontUtils = FontUtils()
            cv2.putText(self.screenshot, "ROI", 
                   (center_x - 20 + offsetX, center_y),
                   fontUtils.font, 
                   fontUtils.fontScale,
                   (0, 0, 255),
                   fontUtils.thickness)
            cv2.rectangle(self.screenshot, (x, y), (x+ w , y + h), (0, 0, 255), thickness=2)

        # Compute the number of non-zero pixels in the ROI
        roi = thresh[y:y+h, x:x+w]
        num_pixels = cv2.countNonZero(roi)
        #print(num_pixels)
        # Check if the character has moved
        if num_pixels > 50:  # adjust this threshold as needed
            self.moving_frames += 1
            self.logger.log("Character has moved!")
            if self.moving_frames >= CONSECUTIVE_FRAMES_THRESHOLD:
                self.logger.log("Character has been moving for {} frames!".format(self.moving_frames))
                return True
        else:
            self.moving_frames = 0
            return False

    
    
    def getScreenPosition(self, pos):
        """Converts position into screen position.

        Args:
            pos (tuple): Calculated position

        Returns:
            tuple: New screen position
        """
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])
    
    def setMode(self, mode: BotMode) -> None:
        """Sets the bot mode.

        Args:
            mode (BotMode): The new mode.
        """
        self.mode = mode