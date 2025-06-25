from flask import Flask, Response
import mss
import time
import io
from PIL import Image
import subprocess
import threading

# ---- CONFIG ----
NGROK_PATH = "ngrok.exe"
NGROK_AUTHTOKEN = "2yCDvyTwazQKWSujoPRXAVxdR48_4VYjzRxKCkqTnwU8hPg4U"
PORT = "5000"
# ----------------

app = Flask(__name__)
sct = mss.mss()

def generate_frames():
    while True:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        img_pil = Image.frombytes("RGB", img.size, img.rgb)
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG")
        frame = buffer.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.route('/')
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_ngrok():
    subprocess.run([NGROK_PATH, "config", "add-authtoken", NGROK_AUTHTOKEN])
    subprocess.Popen([NGROK_PATH, "http", PORT])

if __name__ == '__main__':
    threading.Thread(target=run_ngrok).start()
    app.run(host="0.0.0.0", port=int(PORT))
