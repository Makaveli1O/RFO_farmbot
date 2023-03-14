import cv2 as cv
from logger import Logger
from windowCaptureYOLO import WindowCapture

class Drawer:
    """A class to draw a rectangles to define the area of interest 
    for each detection object. These objects are further checked by
    RFBot class with the usage of matchTemplate if they are present
    or not
    """
    class Rectangle:
        """A class to store the coordinates of the rectangle
        """
        def __init__(self, top_left, bottom_right):
            self.top_left = top_left
            self.bottom_right = bottom_right
            
    logger = Logger(True) #implicitly log to true
    animusDrawedRectangle = None
    healthBarDrawedRectangle = None
            
    def __init__(self, img) -> None:
        self.drawing = False
        self.img = img
    
    def getAnimusRectangle(self):
        return self.animusDrawedRectangle
    
    def getHealthBarRectangle(self):
        return self.healthBarDrawedRectangle
    
    # Mouse callback function
    def drawAnimusRect(self, event, x, y, flags = None, param = None) -> None:
        """A function to draw a rectangle on the screen and store the
        rectangle coordinates into rectangle class
        """
        # Define global variables
        global x_init, y_init

        # If left mouse button is pressed, record starting (x,y) coordinates
        if event == cv.EVENT_LBUTTONDOWN:
            self.drawing = True
            x_init, y_init = x, y

        # While left mouse button is pressed, draw rectangle on the screen
        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing:
                img_temp = self.img.copy()
                cv.rectangle(img_temp, (x_init, y_init), (x, y), (0, 255, 0), thickness=2)
                cv.imshow("image", img_temp)

        # When left mouse button is released, record ending (x,y) coordinates
        elif event == cv.EVENT_LBUTTONUP:
            self.drawing = False
            x_end, y_end = x, y

            # Ensure upper-left coordinates are first and lower-right coordinates are second
            x_start, x_end = sorted([x_init, x_end])
            y_start, y_end = sorted([y_init, y_end])

            # Print rectangle coordinates
            #self.logger.log("Upper left coordinates: ({}, {})".format(x_start, y_start))
            #self.logger.log("Lower right coordinates: ({}, {})".format(x_end, y_end))

            # Draw rectangle on the image and show it
            cv.rectangle(self.img, (x_start, y_start), (x_end, y_end), (0, 255, 0), thickness=2)
            cv.imshow("image", self.img)
            
            # save found rectangle
            self.animusDrawedRectangle = self.Rectangle((x_start, y_start), (x_end, y_end))
            self.logger.log("Drawer: Animus rectangle defined and will be observed at this location")

        return

    # Mouse callback function
    def drawHealthBarRect(self, event, x, y, flags = None, param = None) -> None:
        """A function to draw a rectangle on the screen and store the
        rectangle coordinates into rectangle class
        """
        # Define global variables
        global x_init, y_init

        # If left mouse button is pressed, record starting (x,y) coordinates
        if event == cv.EVENT_LBUTTONDOWN:
            self.drawing = True
            x_init, y_init = x, y

        # While left mouse button is pressed, draw rectangle on the screen
        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing:
                img_temp = self.img.copy()
                cv.rectangle(img_temp, (x_init, y_init), (x, y), (0, 0, 255), thickness=2)
                cv.imshow("image", img_temp)

        # When left mouse button is released, record ending (x,y) coordinates
        elif event == cv.EVENT_LBUTTONUP:
            self.drawing = False
            x_end, y_end = x, y

            # Ensure upper-left coordinates are first and lower-right coordinates are second
            x_start, x_end = sorted([x_init, x_end])
            y_start, y_end = sorted([y_init, y_end])

            # Print rectangle coordinates
            #self.logger.log("Upper left coordinates: ({}, {})".format(x_start, y_start))
            #self.logger.log("Lower right coordinates: ({}, {})".format(x_end, y_end))

            # Draw rectangle on the image and show it
            cv.rectangle(self.img, (x_start, y_start), (x_end, y_end), (0, 0, 255), thickness=2)
            cv.imshow("image", self.img)
            
            self.healthBarDrawedRectangle = self.Rectangle((x_start, y_start), (x_end, y_end))
            self.logger.log("Drawer: Healthbar rectangle defined and will be observed at this location")

        return
    def defineAnimusRectangle(self):
        """A function to define the rectangle for animus detection
        defined rectangle is either saved ina  class attribute or returned
        """
        # Set mouse callback function
        self.logger.log("Click and drag to define the animus rectangle.Then 'q' to continue")
        cv.namedWindow('image')
        cv.setMouseCallback('image', self.drawAnimusRect)
        # Read in the captured frame
        img = self.img
        
        # Create a window and set mouse callback function
        cv.namedWindow("image")
        cv.setMouseCallback("image", self.drawAnimusRect)

        # Display the image and wait for a key press
        cv.imshow("image", img)
        cv.waitKey(0)

        # Clean up and exit
        cv.destroyAllWindows()
        return self.animusDrawedRectangle
    
    def defineHealthBarRectangle(self):
        """A function to define the rectangle for healthbar detection
        defined rectangle is either saved ina  class attribute or returned
        """
        # Set mouse callback function
        self.logger.log("Click and drag to define the healthbar rectangle. Then 'q' to continue")
        cv.namedWindow('image')
        cv.setMouseCallback('image', self.drawHealthBarRect)
        # Read in the captured frame
        img = self.img
        
        # Create a window and set mouse callback function
        cv.namedWindow("image")
        cv.setMouseCallback("image", self.drawHealthBarRect)

        # Display the image and wait for a key press
        cv.imshow("image", img)
        cv.waitKey(0)

        # Clean up and exit
        cv.destroyAllWindows()
        return self.healthBarDrawedRectangle
    

    
"""if __name__ == '__main__':
    wincap = WindowCapture('RF Online')
    wincap.start()
    drawer = Drawer(wincap.get_screenshot().getImage())
    drawer.defineAnimusRectangle()
    wincap.stop()
    """

   