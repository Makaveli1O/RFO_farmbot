import pybboxes as pbx
import os

cv_img_dim = (1540, 846)
scrn_img_dim = (1785, 1071)

# Read in annotations from text file
with open('new_annotations.txt', 'r') as f:
    annotations = f.readlines()
classIdxOffset = 0 # offset
prevClassIdx = 0 # save previous index each iter
# Convert annotations to YOLO format
with open("new_yolo_annotations.txt", 'a') as f_out:
    for annotation in annotations:
        parts = annotation.strip().split()
        filename = parts[0]
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
                i = classIdxOffset + i
                box_string = f"{i} {box[0]} {box[1]} {box[2]} {box[3]}"
                box_strings.append(box_string)
                prevClassIdx += 1
            classIdxOffset = prevClassIdx
            f_out.write(' '.join(box_strings))
            f_out.write("\n")
        else :
            continue