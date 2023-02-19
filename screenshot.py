class Screenshot:
    dimensions = ()
    image = None
    def __init__(self, dimensions, image):
        self.dimensions = dimensions
        self.image = image
        
    def getImage(self):
        return self.image
    
    def getDimensions(self):
        return self.dimensions