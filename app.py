from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import base64
import cv2
import numpy as np
import os
from model import predict_gesture  # Hareketten metin tahmini yapan fonksiyon

app = Flask(__name__)
socketio = SocketIO(app)

KELIMELER_KLASORU = "kelimeler"  # Videoların olduğu klasör

@app.route('/')
def index():
    return render_template('index.html')

def find_video_for_word(word):
    for file in os.listdir(KELIMELER_KLASORU):
        if file.lower().startswith(word.lower()) and file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            return os.path.join(KELIMELER_KLASORU, file)
    return None

@socketio.on('image')
def handle_image(data):
    image_data = data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    metin = predict_gesture(frame)  # Ör: "Selam"
    video_path = find_video_for_word(metin)
    if video_path:
        emit('play_video', {'video_path': video_path, 'text': metin})
    else:
        emit('no_video', {'text': metin})

if __name__ == '__main__':
    socketio.run(app, debug=True)
