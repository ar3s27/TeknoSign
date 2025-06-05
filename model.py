from ultralytics import YOLO
import cv2

model = YOLO("models/best.pt")

def predict_gesture(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(img_rgb, conf=0.3, verbose=False)

    for result in results:
        boxes = result.boxes
        if len(boxes) > 0:
            cls_id = int(boxes[0].cls[0].item())
            label = model.names[cls_id]
            return label
    return "Tanımlanamadı"
