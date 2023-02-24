from ultralytics import YOLO


if __name__ == '__main__':
    # Load a model
    model = YOLO("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\runs\\detect\\train3\\weights\\last.pt")  # load a pretrained model (recommended for training)
    #416x234 or 608x342
    # Use the model
    model.train(data="C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\YOLO\\data_new_caliana_24.2\\data.yaml",epochs=200, batch=8,workers=4, imgsz=416)  # train the model
    metrics = model.val()  # evaluate model performance on the validation set

    #success = model.export(format="onnx")  # export the model to ONNX format
    #print(success)