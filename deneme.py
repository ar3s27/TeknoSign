import whisper

model = whisper.load_model("tiny")
result = model.transcribe("ab.m4a")
print(result["text"])