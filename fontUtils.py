import cv2
class FontUtils:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self): 
        # font constants
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 0.8
        self.fontColor = (0, 255, 0)
        self.fontPosition = (0,0)
        self.thickness = 2