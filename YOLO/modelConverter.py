from ultralytics import YOLO
import torch


if __name__ == '__main__':
    # Load a model shape (1, 3, 640, 640)
    #model = YOLO("C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\yolov8n.pt")  # load a pretrained model (recommended for training)
    #print(model)
    #success = model.export(format="saved_model")  # export the model to ONNX format
    #print(success)
    import onnx
    from onnx2tf import convert

    model = onnx.load('C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\yolov8n.t7')
    tf_model = convert(model)

    with open('C:\\Users\\Makaveli\\Desktop\\Work\\RFO_farmbot\\RFO_farmbot\\YOLO\\yolov8n.pb', 'wb') as f:
        f.write(tf_model.SerializeToString())
