const video = document.getElementById('video');
const videoPlayer = document.getElementById('videoPlayer');
const result = document.getElementById('result');
const socket = io();

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
    setInterval(captureFrame, 1000);
  })
  .catch(error => {
    result.textContent = "Kamera erişimi reddedildi.";
    console.error(error);
  });

function captureFrame() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0);
  const dataURL = canvas.toDataURL('image/jpeg');
  socket.emit('image', dataURL);
}

socket.on('play_video', function(data) {
  result.textContent = "Tahmin: " + data.text;
  videoPlayer.src = "/" + data.video_path.replace(/\\/g, "/");
  videoPlayer.style.display = "block";
  videoPlayer.play();
});

socket.on('no_video', function(data) {
  result.textContent = "Tahmin: " + data.text + " (Video bulunamadı)";
  videoPlayer.style.display = "none";
  videoPlayer.pause();
  videoPlayer.removeAttribute('src');
});