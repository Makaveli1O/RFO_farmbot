import os

class CascadeHelper:    
    def createPathFolder(self):
        with open("negative.txt", "w") as file:
            for filename in os.listdir("negative"):
                file.write("negative/" + filename + "\n")