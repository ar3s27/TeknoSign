from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
import cv2
import base64
import numpy as np
import os

app = Flask(__name__)

model = YOLO("best.pt")

@app.route("/")
def index():
    return render_template("index.html")

def decode_base64_image(data_url):
    header, encoded = data_url.split(",", 1)
    img_data = base64.b64decode(encoded)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

@app.route("/detect", methods=["POST"])
def detect():
    data = request.json
    image_data = data.get("image", "")
    frame = decode_base64_image(image_data)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(img_rgb, conf=0.5, verbose=False)

    for result in results:
        boxes = result.boxes
        if len(boxes) > 0:
            cls_id = int(boxes[0].cls[0].item())
            label = model.names[cls_id]
            return jsonify({"result": label})
    return jsonify({"result": "Tanımlanamadı"})

@app.route("/get_video", methods=["POST"])
def get_video():
    data = request.json
    text = data.get("text", "").lower().strip()

    videos_folder = os.path.join(app.static_folder, "videos")
    try:
        files = os.listdir(videos_folder)
    except FileNotFoundError:
        return jsonify({"video_urls": []})

    # Dosyaları küçük harfli isim -> dosya tam ismi olarak eşle
    file_map = {os.path.splitext(f)[0].lower(): f for f in files}

    words = text.split()
    video_urls = []

    for word in words:
        if word in file_map:
            video_path = f"/static/videos/{file_map[word]}"
            video_urls.append(video_path)

    return jsonify({"video_urls": video_urls})
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
