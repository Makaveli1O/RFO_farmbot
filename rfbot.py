from threading import Lock, Thread
import pyautogui
from time import time, sleep, monotonic
from enum import Enum
import math
import cv2
from interfaces.threadingInterface import ThreadInterface
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
        self.last_animus_call_time = monotonic()
        #zig-zag stuff
        self.last_zig_zag = monotonic()
        self.zig_zag_direction = True
        
        self.wincapRef = wincapRef
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]
        self.logger.enabled(debug_mode)
        self.mode = mode
        
        # remove white names for now
        # self.tooltips.append(cv2.imread('tooltips/tooltip_crew.jpg', cv2.IMREAD_UNCHANGED))
        # self.tooltips.append(cv2.imread('tooltips/tooltip_atrock.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltips/tooltip_crew_red.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltips/tooltip_atrock_red.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltips/tooltip_atrock_black_bg.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltips/tooltip_atrock_blue_bg.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltips/tooltip_crew_black_bg.jpg', cv2.IMREAD_UNCHANGED))
        self.tooltips.append(cv2.imread('tooltips/tooltip_crew_blue_bg.jpg', cv2.IMREAD_UNCHANGED))
        
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
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
        
    def runNoTargets(self) -> bool:
        """This loop is performed when bot is in autoattack mode. It will perform autoattack on mobs in range.
        IWhen no mobs are in range it will perform zig-zag to prevent dieing. Only updates frame, because healthbar
        should be present.

        Returns:
            bool: _description_
        """
        # first check for animus bar if corresponding bot mode is set
        if self.mode == BotMode.SUMMONER:
            if not self.__animusBarFound():
                self.attemptSummonAnimus()
                
        # check for healthbar
        if self.__healthBarFound():
            self.logger.log("Searchbar is present!")
            self.logger.log("Attack")
            self.performAttack()
        else:
            # meanwhile loot
            #self.logger.log("Looting")
            #pyautogui.press("x")
            self.__performZig_zag(delay = 3)
            self.state = BotState.SEARCHING
            return False
        
    def run(self):
        if self.mode == BotMode.SUMMONER:
            if not self.__animusBarFound():
                self.attemptSummonAnimus()
                        
        # sometimes, healthbar is present but state changes to searching
        if self.__healthBarFound():
            self.logger.log("Searchbar is present!")
            self.performAttack()
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
                
    def attemptSummonAnimus(self):
        if monotonic() - self.last_animus_call_time > 3: # prevent returning just summoned animus
            self.logger.log("Animus bar not found! Recovering animus...")
            pyautogui.press('f2') # call animus
            self.last_animus_call_time = monotonic()
        # if still not summoned, after each 5 sec attempt perform zig-zag
        else:
            if not self.__animusBarFound():
                self.logger.log("Performing zig-zag")
                self.__performZig_zag(length = 50, delay = 5)
                
    def performAttack(self):
        # perform attack
        if self.mode == BotMode.AUTO_ATTACK:
            pyautogui.press("space")
        elif self.mode == BotMode.SUMMONER:
            pyautogui.press("f3") # FIXES bug with running towards newly selected target
            pyautogui.press('f1')
        else:
            raise("Bot mode not supported")
                
    def __performZig_zag(self, length = 30, delay = 3) -> None:
        """Performs moving from left rto right. This prevents mobs from cotinuosly hitting staying target,
        and finds close enemies on top of character's head.

        Args:
            length (int, optional): length of moving to the left or right(in cycles). Defaults to 30.
            delay (float, optional): Delay between performing zigzag. Defaults to 3(seconds).
        """
        if monotonic() - self.last_zig_zag > delay:
            self.__zig_zag(length)
            self.last_zig_zag = monotonic()
        else: # when cant zigzag, loot
             # tihs probably breaks zigzag purpose
             pyautogui.press('x')
        return
            
    def __zig_zag(self, length):
        # FIXME this causes freezing of the frames, since it is not in separate thread
        if self.zig_zag_direction:
            for i in range(0, length):
                pyautogui.keyDown('d')
            pyautogui.keyUp('d')
            self.zig_zag_direction = not self.zig_zag_direction
        else:
            for i in range(0, length):
                pyautogui.keyDown('a')
            pyautogui.keyUp('a')
            self.zig_zag_direction = not self.zig_zag_direction
    
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
            self.logger.log("tooltip found! CLICK!")         
            # click target
            self.__performClick()
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
            self.__performClick()

            return True
        
    def __performClick(self) -> None:
        """
        Fail save to prevent double clicking target resulting in moving towerds him
        with a staff in the hand(or any other meele weapon)If it is found do not click.
        
        edit: actually do not fix this issue. Its game related. Still will keep it like this.
        """
        if not self.__healthBarFound():
            pyautogui.click()
            
    #TODO merge __tooltipFound and __healthBarFound into one more abstract function
    def __healthBarFound(self) -> bool:
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
    
    def __animusBarFound(self) ->bool:
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
    
    def __tooltipFound(self, mousePos: tuple) -> bool:
        """Checks if tooltip is present above the target. If yes, returns True.
        Crops the capturet screenshot to 200x200 rectangle around mouse position
        with the usage of __cropFrame method.

        Args:
            mousePos (tuple): Current position of the mouse

        Returns:
            boolean: True if tooltip is found, False otherwise
        """
        # check screenshot for tooltip
        height, width = self.screenshot.shape[:2]
        partial_frame = self.__cropFrame(template_size = (200, 200), x=mousePos[0], y=mousePos[1])
        for tooltip in self.tooltips:
            result = cv2.matchTemplate(partial_frame, tooltip, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(max_val)
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
    
    def getScreenPosition(self, pos):
        """Converts position into screen position.

        Args:
            pos (tuple): Calculated position

        Returns:
            tuple: New screen position
        """
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])