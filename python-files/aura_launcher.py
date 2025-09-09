import http.server
import socketserver
import webbrowser
import threading

PORT = 8000

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Aura Launcher - Developed by Zain</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin-top: 30px;
      background: #111;
      color: white;
    }
    h1 {
      color: #4cafef;
    }
    .controls {
      margin: 20px;
    }
    button, select {
      padding: 10px 15px;
      margin: 5px;
      font-size: 14px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      background: #4caf50;
      color: white;
    }
    button:disabled {
      background: gray;
    }
    video {
      margin-top: 20px;
      width: 70%;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.5);
      background: black;
    }
    #blurBox {
      position: absolute;
      width: 150px;
      height: 100px;
      background: rgba(0,0,0,0.4);
      backdrop-filter: blur(10px);
      border: 2px dashed #fff;
      cursor: move;
      display: none;
    }
  </style>
</head>
<body>
  <h1>🎥 Aura Launcher</h1>
  <p>Developed by Zain</p>
  
  <div class="controls">
    <button id="startBtn">Start Recording</button>
    <button id="stopBtn" disabled>Stop Recording</button>
    <button id="micToggle">Mic: ON</button>
    <button id="blurToggle">Toggle Blur</button>
  </div>
  
  <a id="downloadLink" style="display:none;">Download Recording</a>
  <br>
  <video id="preview" controls></video>
  
  <div id="blurBox"></div>
  
  <script>
    let mediaRecorder;
    let recordedChunks = [];
    let micEnabled = true;
    let micStream;
    let screenStream;

    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const micToggle = document.getElementById('micToggle');
    const blurToggle = document.getElementById('blurToggle');
    const preview = document.getElementById('preview');
    const downloadLink = document.getElementById('downloadLink');
    const blurBox = document.getElementById('blurBox');

    let isDragging = false;
    let offsetX, offsetY;

    // Dragging blur box
    blurBox.addEventListener('mousedown', (e) => {
      isDragging = true;
      offsetX = e.offsetX;
      offsetY = e.offsetY;
    });
    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        blurBox.style.left = (e.pageX - offsetX) + 'px';
        blurBox.style.top = (e.pageY - offsetY) + 'px';
      }
    });
    document.addEventListener('mouseup', () => isDragging = false);

    micToggle.onclick = () => {
      micEnabled = !micEnabled;
      micToggle.innerText = micEnabled ? "Mic: ON" : "Mic: OFF";
    };

    blurToggle.onclick = () => {
      blurBox.style.display = (blurBox.style.display === "none") ? "block" : "none";
    };

    startBtn.onclick = async () => {
      screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true
      });

      if (micEnabled) {
        micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Mix mic + system audio
        const context = new AudioContext();
        const dest = context.createMediaStreamDestination();
        const systemSource = context.createMediaStreamSource(screenStream);
        const micSource = context.createMediaStreamSource(micStream);
        systemSource.connect(dest);
        micSource.connect(dest);

        const combined = new MediaStream([
          ...screenStream.getVideoTracks(),
          ...dest.stream.getAudioTracks()
        ]);

        mediaRecorder = new MediaRecorder(combined);
      } else {
        mediaRecorder = new MediaRecorder(screenStream);
      }

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) recordedChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        preview.src = url;
        downloadLink.href = url;
        downloadLink.download = 'AuraRecording.webm';
        downloadLink.style.display = 'block';
        downloadLink.innerText = 'Download Recording';
        recordedChunks = [];
      };

      mediaRecorder.start();
      startBtn.disabled = true;
      stopBtn.disabled = false;
    };

    stopBtn.onclick = () => {
      mediaRecorder.stop();
      startBtn.disabled = false;
      stopBtn.disabled = true;
    };
  </script>
</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_error(404)

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
webbrowser.open(f"http://localhost:{PORT}")

print(f"Aura Launcher running on http://localhost:{PORT}")
print("Close the program to exit.")
