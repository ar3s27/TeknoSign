from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import base64
import cv2
import numpy as np
from model import predict_gesture  # Kendi model tahmin fonksiyonun

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('image')
def handle_image(data):
    image_data = data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = predict_gesture(frame)  # Örnek: "Selam", "Nasılsın" gibi

    emit('result', result)

if __name__ == '__main__':
    socketio.run(app, debug=True)
