import pybboxes as pbx
import os

cv_img_dim = (1540, 846)
scrn_img_dim = (1785, 1071)

# Read in annotations from text file
with open('new_annotations.txt', 'r') as f:
    annotations = f.readlines()
# Convert annotations to YOLO format
for annotation in annotations:
    parts = annotation.strip().split()
    filename = parts[0][9:-4]
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
            
            voc_bbox = pbx.BoundingBox.from_voc(*bbox, image_size=scrn_img_dim)
            yolo_bbox = voc_bbox.to_yolo()
            boxes.append(bbox)
        # Write the YOLO bbox to a new file
        box_strings = []
        for i, box in enumerate(boxes):
            i = 0 # only one obj to detect
            box_string = f"{i} {box[0]} {box[1]} {box[2]} {box[3]}"
            box_strings.append(box_string)
        with open("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\labels\\"+filename+".txt", 'a') as f_out:
            f_out.write(' '.join(box_strings))
    else :
        continue