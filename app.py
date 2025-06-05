from flask import Flask, request, jsonify, render_template, send_file
import os, re, cv2, numpy as np
from model import predict_gesture
from moviepy import VideoFileClip, concatenate_videoclips
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import base64


app = Flask(__name__)

# --- Yardımcı Fonksiyonlar ---

def metni_kelimelere_ayir(metin):
    return re.findall(r'\b\w+\b', metin.lower())

def videolari_al(kelimeler, video_klasoru="static/videos"):
    video_listesi = []
    for kelime in kelimeler:
        video_yolu = os.path.join(video_klasoru, f"{kelime}.mp4")
        if os.path.exists(video_yolu):
            video_listesi.append(video_yolu)
    return video_listesi

def videolari_birlestir(video_yollari, cikti_yolu="static/output/sonuc.mp4"):
    klipler = [VideoFileClip(v) for v in video_yollari]
    birlesmis = concatenate_videoclips(klipler, method="compose")
    os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    birlesmis.write_videofile(cikti_yolu, codec="libx264", audio=False, verbose=False, logger=None)
    return cikti_yolu

# --- Ana Sayfa ---
@app.route("/")
def index():
    return render_template("index.html")

# --- Canlı Kamera ile İşaret Dili Tahmini ---
@app.route("/predict_sign", methods=["POST"])
def predict_sign():
    data = request.json
    img_data = data.get("image")
    if not img_data:
        return jsonify({"error": "Görüntü verisi yok"}), 400

    # Base64'ten img decode
    header, base64_data = img_data.split(',', 1)
    img_bytes = BytesIO(base64.b64decode(base64_data))
    np_arr = np.frombuffer(img_bytes.read(), np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    label = predict_gesture(img)
    return jsonify({"text": label})

# --- Yazıdan İşaret Diline Video ---
@app.route("/text_to_sign", methods=["POST"])
def text_to_sign():
    metin = request.json.get("text", "")
    kelimeler = metni_kelimelere_ayir(metin)
    videolar = videolari_al(kelimeler)
    if not videolar:
        return jsonify({"error": "Hiç video bulunamadı"}), 404
    sonuc_video = videolari_birlestir(videolar)
    return jsonify({"video_path": "/" + sonuc_video})

# --- Ses → Yazı ---
@app.route("/speech_to_text", methods=["POST"])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "Ses dosyası eksik"}), 400
    audio_file = request.files['audio']
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language="tr-TR")
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Yazı → Ses ---
@app.route("/text_to_speech", methods=["POST"])
def text_to_speech():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Metin yok"}), 400
    tts = gTTS(text=text, lang='tr')
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    audio = AudioSegment.from_file(mp3_fp, format="mp3")
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    return send_file(wav_io, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(debug=True)
