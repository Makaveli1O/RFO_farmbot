import pybboxes as pbx
import os

DIM_21_9 = (1785, 1071) # imshow screens filip
DIM_16_9 = (1540, 846) #filip screens

# Read in annotations from text file
with open('annotations.txt', 'r') as f:
    annotations = f.readlines()
# Convert annotations to YOLO format
for annotation in annotations:
    parts = annotation.strip().split()
    filename = parts[0][12:-4]
    numObjects = int(parts[1])
    boxes = []
    if numObjects > 0:
        base_offset = 1 #filename -> [0], num files -> [1]
        coords_offset = 4 # x,y,w,h
        # extract each bbox from the line
        # and convert to YOLO format
        for objNum in range(0, numObjects):
            x_min, y_min, width, height = (int(parts[base_offset + 1 + (coords_offset * objNum)]),
                    int(parts[base_offset + 2 + (coords_offset * objNum)]),
                    int(parts[base_offset + 3 + (coords_offset * objNum)]),
                    int(parts[base_offset + 4 + (coords_offset * objNum)]))
            x_max = x_min + width
            y_max = y_min + height
            bbox = [x_min, y_min, x_max, y_max]
            
            voc_bbox = pbx.BoundingBox.from_voc(*bbox, image_size=DIM_16_9)
            yolo_bbox = voc_bbox.to_yolo()
            boxes.append(yolo_bbox)
        # Write the YOLO bbox to a new file
        box_strings = []
        for i, box in enumerate(boxes):
            i = 0 # only one obj to detect
            vals = box.values
            box_string = f"{i} {vals[0]} {vals[1]} {vals[2]} {vals[3]}"
            box_strings.append(box_string)
            with open("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\labels\\"+filename+".txt", 'a') as f_out:
                f_out.write(box_string)
                f_out.write("\n")
    else :
        continue
print("Annotations successfully converted to YOLOv5 Pytorch")