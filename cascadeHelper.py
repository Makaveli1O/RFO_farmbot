import os

class CascadeHelper:
    def __init__(self, name, age):
        pass
    
    def createPathFolder():
        with open("negative.txt", "w" as file):
            for filename in os.listdir("negative"):
                file.write("negative/" + filename + "\n")