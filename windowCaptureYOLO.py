import numpy as np
import win32gui, win32ui, win32con
from threading import Thread,Lock
from screenshot import Screenshot
from time import sleep


class WindowCapture:
    # threading
    stopped = True
    lock = None
    screenshot = None
    runningAvg = 0
    
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # window name defaults to none because sometimes black screen occurs while capturing
    def __init__(self, window_name=None):
        self.lock = Lock()
        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 0
        titlebar_pixels = 0
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y
        
    def set_avg(self):
        """Can be called only after start() is called"""
        # determine the average
        self.avg = np.float32(self.screenshot.getImage())
        
    def get_avg(self):
        return self.avg
    
    def get_screenshot(self) -> Screenshot:
        # get the window image data
        try:
            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
        except win32ui.error as e:
            print(f"Error creating compatible DC: {e}")
        dataBitMap = win32ui.CreateBitmap()
        
        # create a new bitmap object each time
        try:
            dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        except:
            sleep(0.5)
            self.get_screenshot()
            return
            

        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        
        #img = np.fromstring(signedIntsArray, dtype='uint8')
        img = np.frombuffer(signedIntsArray, dtype='uint8')

        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)
        scrn = Screenshot((self.w, self.h), img)
        return scrn

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)
    

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()
        
    def stop(self):
        self.stopped = True
        
    def run(self):
        while not self.stopped:
            screenshot = self.get_screenshot()
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()