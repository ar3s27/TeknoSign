import os
import subprocess as sp
import time

def play_videos(folder_path, sentence):
    words = sentence.split()

    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        print(f"Klasör bulunamadı: {folder_path}")
        return

    for word in words:
        for file in files:
            file_words = os.path.splitext(file)[0].lower().replace('_', ' ').replace('-', ' ').split()
            if word.lower() in file_words and file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                file_path = os.path.join(folder_path, file)
                print(f"Videoyu oynatılıyor: {file_path}")
                try:
                    if os.name == 'posix':  # macOS/Linux
                        sp.run(['open', file_path], check=True)
                    elif os.name == 'nt':  # Windows
                        sp.run(['start', file_path], shell=True, check=True)
                    else:
                        print(f"Bu işletim sistemi desteklenmiyor: {os.name}")
                    time.sleep(3)  # Bir sonraki video için gecikme
                except Exception as e:
                    print(f"Video oynatılamadı: {file_path}, Hata: {e}")

folder_path = "wordsFolder"  # Buraya video klasörünüzün yolu gelecek
sentence = input("Bir cümle girin: ").strip()
play_videos(folder_path, sentence)

