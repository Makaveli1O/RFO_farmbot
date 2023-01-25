import cv2

cap = cv2.VideoCapture("video.mp4")

if cap.isOpened() == False:
    raise Exception("Video capture is not opened.")

while cap.isOpened():
    #read frames
    ret, frame = cap.read()
    # lead pre-trained model
    detector = cv2.CascadeClassifier("path_to_model")
    #use pre-trained model to detect obj in current frame
    objects = detector.detectMultiScale(frame,
                                        scaleFactor = 1.1,
                                        minNeighbors = 5,
                                        minSize = (30, 30)
                                        )

#Import only if not previously imported
#import cv2
# Create a Video Reader Object.
#cap = cv2.VideoCapture(VideoToRead)
#if cap.isOpened() == False:
#    print("Error in opening video stream or file")
#Define the codec for the Video
#fourcc = cv2.VideoWriter_fourcc("Fourcc Codec Eg-XVID")
#Create Video Writer Object
#writer = cv2.VideoWriter('Video Writing Address',fourcc, fps value, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
#while cap.isOpened():
#    ret, frame = cap.read()
#    if ret:
#        writer.write(frame)
#        cv2.imshow("Frame",frame)
#        # Exit on pressing esc
#        if cv2.waitKey(20) & 0xFF == 27:
#            break
#    else:
#        break
#cap.release()
#writer.release()
#cv2.destroyAllWindows()