import cv2
import base64
import threading
import socketio
import eventlet
eventlet.monkey_patch()

# -------------------------
# CONFIG
# -------------------------
SERVER_URL = 'https://camser-yy2o.onrender.com'  # Your deployed server
FPS = 10  # Frames per second
JPEG_QUALITY = 50  # JPEG compression (0-100)
# -------------------------

# Connect to the server
sio = socketio.Client()
sio.connect(SERVER_URL)

# Camera control variable
camera_on = True
cap = cv2.VideoCapture(0)

def send_frames():
    global camera_on
    while True:
        if camera_on:
            success, frame = cap.read()
            if success:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
                jpg_as_text = base64.b64encode(buffer).decode()
                # Send to server
                sio.emit('camera-stream', jpg_as_text)
        eventlet.sleep(1/FPS)

@sio.on('camera-command')
def handle_command(cmd):
    global camera_on
    if cmd == 'start':
        camera_on = True
    elif cmd == 'stop':
        camera_on = False

# Start sending frames in background thread
threading.Thread(target=send_frames, daemon=True).start()

# Keep the client running
sio.wait()