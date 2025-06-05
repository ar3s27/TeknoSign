// Sesli okuma fonksiyonu
function speak(text) {
    if ('speechSynthesis' in window) {
        if(text !== "Tanımlanamadı"){
            const utterance = new SpeechSynthesisUtterance(text);
            speechSynthesis.speak(utterance);
        }
    }
}

// Kamera ve hareket tespiti
const video = document.getElementById("video");
const gestureResult = document.getElementById("gestureResult");
let lastSpokenGesture = "";

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        alert("Kamera erişim hatası: " + err);
    });

setInterval(() => {
    if(video.videoWidth === 0) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const image = canvas.toDataURL("image/jpeg");

    fetch("/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: image })
    })
    .then(res => res.json())
    .then(data => {
        gestureResult.textContent = data.result;
        if (data.result !== lastSpokenGesture && data.result !== "Tanımlanamadı") {
            speak(data.result);
            lastSpokenGesture = data.result;
        }
    });
}, 2000);

// Yazı veya ses ile video oynatma
const textInput = document.getElementById("textInput");
const sendText = document.getElementById("sendText");
const recognizedText = document.getElementById("recognizedText");
const signVideo = document.getElementById("signVideo");

sendText.onclick = () => {
    const text = textInput.value.trim();
    if(text) playSignVideo(text);
};

// Speech recognition
let recognition;
if('webkitSpeechRecognition' in window){
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'tr-TR';
    recognition.interimResults = false;

    recognition.onresult = event => {
        const speechResult = event.results[0][0].transcript;
        recognizedText.textContent = speechResult;
        playSignVideo(speechResult);
    };

    recognition.onerror = event => {
        console.error(event.error);
    };
} else {
    alert("Tarayıcınız konuşma tanımayı desteklemiyor.");
}

document.getElementById("startSpeech").onclick = () => {
    if(recognition){
        recognition.start();
        document.getElementById("startSpeech").disabled = true;
        document.getElementById("stopSpeech").disabled = false;
    }
};

document.getElementById("stopSpeech").onclick = () => {
    if(recognition){
        recognition.stop();
        document.getElementById("startSpeech").disabled = false;
        document.getElementById("stopSpeech").disabled = true;
    }
};

function playSignVideo(text) {
    fetch('/get_video', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: text.toLowerCase()})
    })
    .then(res => res.json())
    .then(async data => {
        if (data.video_urls && data.video_urls.length > 0) {
            await playVideosSequentially(data.video_urls);
        } else {
            alert("İşaret dili videosu bulunamadı.");
        }
    });
}

async function playVideosSequentially(videoUrls) {
    const signVideo = document.getElementById("signVideo");

    for (const url of videoUrls) {
        signVideo.src = url;
        await signVideo.play();

        // Videonun bitmesini bekle
        await new Promise(resolve => {
            signVideo.onended = () => resolve();
        });
    }
}
