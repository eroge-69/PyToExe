# app.py (YOLO + Ultrasonic + Flask UI + Arduino) - updated for multi-item handling
import os
import time
import json
import threading
import collections
from collections import deque
import math

import torch
import numpy as np
from ultralytics import YOLO

import serial
from serial import SerialException
import serial.tools.list_ports

from flask import jsonify, Flask, render_template, Response
from flask_socketio import SocketIO
import cv2

from queue import Queue

# ---------- CONFIG ----------
SERIAL_PORT = "COM5"
BAUDRATE = 115200
ESP_STREAM_URL = "http://192.168.1.115:81/stream?width=640&height=480&quality=10"
PRESET_FILE = "presets.json"
YOLO_MODEL_PATH = "my_model.pt"
ULTRA_THRESHOLD = 7
STABILIZE_DELAY = 3
AFTER_PUSH_DELAY = 4
INFER_IMG_SIZE = 640
MAX_FPS = 10
CONVEY_DELAY = 2.6

STEP_TIMEOUT = 10.0
WATCHDOG_INTERVAL = 0.5
DETECTION_DEBOUNCE_SEC = 0.8   # don't add duplicate detection on same side within this time
DETECTION_TTL = 30.0           # seconds; stale detections removed
# ----------------------------

# ---------- GLOBALS ----------
arm_busy = threading.Lock()          # authoritative lock for any push operation
push_queue = Queue()
servo_ready_event = threading.Event()
latest_frame = None
annotated_frame = None
frame_lock = threading.Lock()
last_positions = [90, 90, 90, 90]
last_sensors = [200.0, 200.0, 200.0]
auto_mode = False
presets = {"LEFT": [], "RIGHT": [], "CENTER": []}
ser = None
serial_lock = threading.Lock()

# multi-item structures
detection_queue = deque()   # each entry: {id, side, label, conf, t}
pending_item = None         # currently being serviced (dict from queue)
last_detection_time = {"LEFT": 0.0, "RIGHT": 0.0}
# Track last step send time so watchdog can detect stuck states
last_step_time = None
last_step_side = None
# ----------------------------

# Load presets at startup
if os.path.exists(PRESET_FILE):
    try:
        with open(PRESET_FILE, "r") as f:
            presets = json.load(f)
            print("✅ Loaded presets from", PRESET_FILE)
    except Exception as e:
        print("⚠️ Could not load presets:", e)


# ---------- UTILITIES ----------
def detect_arduino():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in p.description or "CH340" in p.description:
            print(f"✅ Detected Arduino on {p.device}")
            return p.device
    if ports:
        print(f"⚠️ No Arduino detected, using first available port {ports[0].device}")
        return ports[0].device
    print("❌ No serial ports found")
    return None


def open_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.2)
        print("Opened serial", SERIAL_PORT)
    except SerialException as e:
        print("Could not open serial port:", e)


def serial_write_line(line):
    """Write to serial if available. If not opened, attempt to detect/open once."""
    global ser
    if ser is None:
        # try detecting a port once
        detected = SERIAL_PORT
        if detected:
            try:
                ser = serial.Serial(detected, BAUDRATE, timeout=0.2)
                print("Opened serial", detected)
            except Exception as e:
                print("Serial open retry failed:", e)
                ser = None
    if ser is None or not ser.is_open:
        print("Serial not opened, cannot write:", line)
        try:
            socketio.emit('log', f"[SERIAL_MISS] {line}")
        except:
            pass
        return
    with serial_lock:
        try:
            ser.write((line.strip() + "\r\n").encode('utf-8'))
            socketio.emit('log', f"Sent: {line}")
        except Exception as e:
            print("Serial write error:", e)


def save_presets():
    with open(PRESET_FILE, "w") as f:
        json.dump(presets, f, indent=2)
# ----------------------------


# ---------- SERIAL READER ----------
def serial_reader_thread():
    global ser, last_positions, last_sensors, last_step_time
    buf = b""
    while True:
        with serial_lock:
            current_ser = ser
        if current_ser is None or not current_ser.is_open:
            time.sleep(0.5)
            continue
        try:
            data = current_ser.read(512)
            if data:
                buf += data
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    try:
                        s = line.decode('utf-8', errors='ignore').strip()
                        if not s:
                            continue

                        if s.startswith("SENS:"):
                            parts = [float(p.strip()) if p.strip() else 200.0 for p in s.split("SENS:")[1].split(",")[:3]]
                            last_sensors = parts
                            socketio.emit('sensors', {'L': parts[0], 'M': parts[1], 'R': parts[2]})
                        elif s.startswith("POS:"):
                            parts = [int(p.strip()) for p in s.split("POS:")[1].split(",")[:4]]
                            last_positions = parts
                            socketio.emit('pos', {'positions': last_positions})
                            if last_step_time is not None and not servo_ready_event.is_set():
                                servo_ready_event.set()
                        elif s == "MOVING":
                            socketio.emit('log', "Arduino: MOVING")
                        elif s == "SERVOS_READY":
                            servo_ready_event.set()
                            last_step_time = None
                            socketio.emit('log', "Arduino: SERVOS_READY")
                        else:
                            socketio.emit('log', s)
                    except Exception as e:
                        print("Error processing serial line:", e)
        except Exception as e:
            print("Serial read error:", e)
            time.sleep(0.5)
# ----------------------------


# ---------- RUN SEQUENCE ----------
def run_sequence(side, steps, push=False):
    """
    Send RUN_STEP for each step and wait for SERVOS_READY (or POS fallback).
    """
    global last_positions, last_step_time, last_step_side
    timeout_per_step = STEP_TIMEOUT

    for i, st in enumerate(steps):
        angles = st.get("angles", [90, 90, 90, 90])
        step_delay = st.get("delay", 0.25)
        angles_str = ",".join(str(a) for a in angles)
        socketio.emit('log', f"{side} step {i+1}/{len(steps)}: {angles}")

        # Prepare to wait
        servo_ready_event.clear()
        last_step_time = time.time()
        last_step_side = side

        # Send RUN_STEP
        serial_write_line(f"RUN_STEP {angles_str}")

        # Wait for Arduino reply (SERVOS_READY or POS)
        if not servo_ready_event.wait(timeout_per_step):
            socketio.emit('log', f"⚠️ Timeout on {side} step {i+1} — attempting resync")
            serial_write_line("GET_POS")
            if not servo_ready_event.wait(2.0):
                socketio.emit('log', f"⚠️ Resync failed on {side} step {i+1}, aborting sequence")
                last_step_time = None
                last_step_side = None
                return

        # Accept the step as done (update UI)
        last_positions = angles.copy()
        socketio.emit('pos', {'positions': last_positions})

        # clear markers
        last_step_time = None
        last_step_side = None

        # small delay between steps
        time.sleep(step_delay)

    if push:
        socketio.emit('log', f"PUSH done for {side}")


# ---------- run_push (public) ----------
def run_push(side, item_id=None):
    """
    Public push. Acquires arm_busy lock non-blocking and spawns a worker thread.
    If arm is busy it will be skipped.
    """
    steps = presets.get(side, [])
    if not steps:
        socketio.emit('log', f"No steps for {side}")
        return

    # Try to take the arm lock. If busy, skip.
    if not arm_busy.acquire(blocking=False):
        socketio.emit('log', f"⚠️ Arm busy, skipped PUSH_{side}")
        return

    def worker():
        global last_step_time, last_step_side
        try:
            socketio.emit('log', f"🤖 Executing PUSH_{side} (item_id={item_id})")
            run_sequence(side, steps, push=True)
            socketio.emit('log', f"✅ Finished PUSH_{side} (item_id={item_id})")
            if item_id is not None:
                socketio.emit('detection_pushed', {'id': item_id, 'side': side})
        except Exception as e:
            socketio.emit('log', f"❌ Error during PUSH_{side}: {e}")
        finally:
            last_step_time = None
            last_step_side = None
            servo_ready_event.clear()
            time.sleep(0.05)
            arm_busy.release()
            socketio.emit('log', "🔄 Arm reset — ready for next PUSH")

    threading.Thread(target=worker, daemon=True).start()


# ---------- push_worker (for queued pushes / auto) ----------
def push_worker():
    while True:
        side = push_queue.get()
        try:
            steps = presets.get(side, [])
            if not steps:
                socketio.emit('log', f"No steps for {side}")
                push_queue.task_done()
                continue
            with arm_busy:
                socketio.emit('log', f"🤖 Executing PUSH_{side} (from queue)")
                run_sequence(side, steps, push=True)
                socketio.emit('log', f"✅ Finished PUSH_{side} (from queue)")
        except Exception as e:
            socketio.emit('log', f"❌ Error in queued push: {e}")
        finally:
            push_queue.task_done()


def async_push(side, item_id=None):
    # We want to keep history in socket UI; still queue pushes so they don't overlap arm.
    # We'll immediately enqueue a push with knowledge of the item_id so UI can match events.
    if item_id is None:
        push_queue.put(side)
    else:
        # store a tuple so the worker can see item_id if needed — keep compatibility: just put side (worker ignores item_id)
        # Use run_push for item_id awareness instead of queue for simplicity:
        run_push(side, item_id=item_id)


# ---------- WATCHDOG ----------
def servo_watchdog_thread():
    global last_step_time, last_step_side
    while True:
        try:
            if last_step_time is not None:
                elapsed = time.time() - last_step_time
                if elapsed > STEP_TIMEOUT:
                    socketio.emit('log', f"⏱️ Watchdog: step for {last_step_side} exceeded {STEP_TIMEOUT}s — forcing ready and requesting POS")
                    servo_ready_event.set()
                    serial_write_line("GET_POS")
                    last_step_time = None
                    last_step_side = None
        except Exception as e:
            print("Watchdog error:", e)
        time.sleep(WATCHDOG_INTERVAL)
# ----------------------------


# ---------- ULTRASONIC MONITOR ----------
def ultrasonic_monitor_thread():
    """
    Watches last_sensors feed and when a sensor crosses threshold and there's an
    item queued for that side, it will stop conveyor and start the push for that queued item.
    State machine is nearly identical but now operates on pending_item dicts.
    """
    global last_sensors, detection_queue, pending_item
    state = "IDLE"
    state_time = 0.0

    while True:
        try:
            L, M, R = last_sensors
            now = time.time()

            # cleanup stale detections occasionally
            if detection_queue:
                while detection_queue and (now - detection_queue[0]['t'] > DETECTION_TTL):
                    old = detection_queue.popleft()
                    socketio.emit('log', f"🧹 Removed stale detection {old['id']} ({old['side']})")
                    socketio.emit('detections', list(detection_queue))

            if state == "IDLE":
                # If nothing currently pending and sensors show arrival, select earliest detection for that side
                if pending_item is None:
                    # left arrival
                    if 0 < L < ULTRA_THRESHOLD:
                        # find earliest LEFT detection
                        for idx, d in enumerate(detection_queue):
                            time.sleep(1.3)
                            if d['side'] == "LEFT":
                                # pop that detection
                                pending_item = detection_queue[idx]
                                del detection_queue[idx]
                                socketio.emit('log', f"📡 Ultrasonic confirms arrival for item {pending_item['id']} on LEFT (L={L:.1f})")
                                socketio.emit('detections', list(detection_queue))
                                serial_write_line("CONVEY_STOP")
                                serial_write_line("FEEDER_OFF")
                                socketio.emit('log', "Conveyor STOPpppppppp")
                                state = "WAIT_STABLE"
                                state_time = now
                                break
                    # right arrival
                    elif 0 < R < ULTRA_THRESHOLD:
                        for idx, d in enumerate(detection_queue):
                            if d['side'] == "RIGHT":
                                pending_item = detection_queue[idx]
                                del detection_queue[idx]
                                socketio.emit('log', f"📡 Ultrasonic confirms arrival for item {pending_item['id']} on RIGHT (R={R:.1f})")
                                socketio.emit('detections', list(detection_queue))
                                serial_write_line("CONVEY_STOP")
                                serial_write_line("FEEDER_OFF")
                                socketio.emit('log', "Conveyor STOP")
                                state = "WAIT_STABLE"
                                state_time = now
                                break
                # else if already pending, ignore (handled by other states)
            elif state == "WAIT_STABLE":
                if now - state_time >= STABILIZE_DELAY:
                    if pending_item:
                        # queue the push (this will either run immediately or be queued by arm_busy)
                        socketio.emit('log', f"🔁 Scheduling push for item {pending_item['id']} ({pending_item['side']})")
                        async_push(pending_item['side'], item_id=pending_item['id'])
                        state = "WAIT_PUSH_DONE"
                        state_time = now
            elif state == "WAIT_PUSH_DONE":
                # We can't reliably observe push completion directly from Arduino UI besides POS/SERVOS_READY,
                # so use the AFTER_PUSH_DELAY as previously designed, then restart conveyor.
                if now - state_time >= AFTER_PUSH_DELAY:
                    serial_write_line("CONVEY_START")
                    serial_write_line("FEEDER_ON")
                    socketio.emit('log', "Conveyor START")
                    # Remember which item was pushed, emit event (push_worker/run_push will also emit detection_pushed)
                    if pending_item:
                        socketio.emit('log', f"Item {pending_item['id']} processed; restarting conveyor")
                        # optionally: socketio.emit('detection_pushed', {'id': pending_item['id'], 'side': pending_item['side']})
                    pending_item = None
                    state = "WAIT_CLEAR"
            elif state == "WAIT_CLEAR":
                # Wait until sensors clear under threshold to resume normal detection for new arrivals
                if L >= ULTRA_THRESHOLD and R >= ULTRA_THRESHOLD:
                    state = "IDLE"
        except Exception as e:
            print("Ultrasonic monitor error:", e)
        time.sleep(0.05)
# ----------------------------


# ---------- CAPTURE + DETECTION ----------
def capture_thread():
    global latest_frame
    while True:
        cap = cv2.VideoCapture(ESP_STREAM_URL)
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        if not cap.isOpened():
            cap.release()
            time.sleep(2)
            continue
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.release()
                break
            h, w = frame.shape[:2]
            scale = INFER_IMG_SIZE / max(h, w)
            frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
            with frame_lock:
                latest_frame = frame
            time.sleep(0.001)


device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = YOLO(YOLO_MODEL_PATH)
try:
    model.to(device)
except Exception:
    pass


def detection_thread():
    global latest_frame, annotated_frame, detection_queue, last_detection_time
    min_period = 1.0 / MAX_FPS
    last_time = 0
    next_det_id = 1

    while True:
        now = time.time()
        if now - last_time < min_period:
            time.sleep(0.001)
            continue
        last_time = now
        with frame_lock:
            frame = None if latest_frame is None else latest_frame.copy()
        if frame is None:
            time.sleep(0.01)
            continue
        annotated = frame.copy()
        try:
            results = model(frame, imgsz=INFER_IMG_SIZE, device=device, verbose=False)
            detected_this_frame = []
            if results and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    conf = float(box.conf.item())
                    if conf < 0.45:
                        continue
                    cls_id = int(box.cls.item())
                    label = model.names[cls_id] if hasattr(model, "names") else str(cls_id)
                    xyxy = box.xyxy.cpu().numpy().squeeze().astype(int)
                    xmin, ymin, xmax, ymax = xyxy
                    center_x = (xmin + xmax) // 2
                    w = frame.shape[1]
                    # divide frame into three vertical bands; center we ignore for pushes; you can route CENTER as needed
                    if center_x < w // 3:
                        detected_side = "LEFT"
                    elif center_x > (w * 2) // 3:
                        detected_side = "LEFT"
                    else:
                        detected_side = "LEFT"

                    # Debounce: only add if enough time since last detection on that side
                    t_since = time.time() - last_detection_time.get(detected_side, 0.0)
                    if detected_side in ("LEFT", "RIGHT") and t_since >= DETECTION_DEBOUNCE_SEC:
                        det = {'id': int(time.time() * 1000), 'side': detected_side, 'label': label, 'conf': conf, 't': time.time()}
                        detection_queue.append(det)
                        last_detection_time[detected_side] = time.time()
                        socketio.emit('log', f"📸 Detected {label} ({conf:.2f}) -> {detected_side} (queued id={det['id']})")
                        socketio.emit('detections', list(detection_queue))
                    elif detected_side == "CENTER":
                        # optional: handle center detections as needed (we don't push them)
                        socketio.emit('log', f"📸 Detected {label} ({conf:.2f}) -> CENTER (ignored for push)")

                    cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                    cv2.putText(annotated, f"{label} {int(conf*100)}% {detected_side}", (xmin, max(ymin-8, 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # break after first box to avoid drawing too many; YOLO may detect multiple boxes per frame if desired remove break
                    # but we want to allow multiple items: we still add multiple boxes in same frame above (so do not break)
                # end for boxes
            with frame_lock:
                annotated_frame = annotated
        except Exception as e:
            print("YOLO error:", e)
            time.sleep(0.05)


def video_feed_generator():
    global annotated_frame
    while True:
        with frame_lock:
            frame = None if annotated_frame is None else annotated_frame.copy()
        if frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "Waiting for frames...", (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        ret, buf = cv2.imencode('.jpg', frame)
        if not ret:
            time.sleep(0.01)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
        time.sleep(0.01)


# ---------- FLASK ----------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/list_ports")
def list_ports():
    return jsonify([p.device for p in serial.tools.list_ports.comports()])


@app.route("/video_feed")
def video_feed():
    return Response(video_feed_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect')
def on_connect():
    socketio.emit('log', 'Welcome! Server connected.')
    socketio.emit('sensors', {'L': last_sensors[0], 'M': last_sensors[1], 'R': last_sensors[2]})
    socketio.emit('pos', {'positions': last_positions})
    socketio.emit('auto_state', {'auto': auto_mode})
    socketio.emit('detections', list(detection_queue))


@socketio.on('command')
def handle_command(data):
    global last_positions, presets, auto_mode, pending_item
    cmd = data.get('cmd')
    idx = data.get('idx')
    angle = data.get('angle')
    if cmd == "SET_SERVO":
        serial_write_line(f"SET_SERVO {int(idx)-1} {int(angle)}")
        return
    if cmd in ("SAVE_LEFT", "SAVE_RIGHT", "SAVE_CENTER"):
        side = "LEFT" if "LEFT" in cmd else ("RIGHT" if "RIGHT" in cmd else "CENTER")
        step = {"angles": list(last_positions), "delay": 0.25}
        if side not in presets:
            presets[side] = []
        presets[side].append(step)
        save_presets()
        socketio.emit('log', f"Saved {side} step #{len(presets[side])}: {step}")
        return
    if cmd.startswith("PUSH") or cmd.startswith("GOTO"):
        # fix: correct side mapping
        if "LEFT" in cmd:
            side = "LEFT"
        elif "RIGHT" in cmd:
            side = "RIGHT"
        else:
            side = "LEFT"
        # Manual immediate push
        run_push(side)
        return
    if cmd == "CONVEY_START":
        serial_write_line("CONVEY_START")
        return
    if cmd == "CONVEY_STOP":
        serial_write_line("CONVEY_STOP")
        return
    if cmd == "FEEDER_ON":
        serial_write_line("FEEDER_ON")
        socketio.emit('log', 'Feeder turned ON')
        return
    if cmd == "FEEDER_OFF":
        serial_write_line("FEEDER_OFF")
        socketio.emit('log', 'Feeder turned OFF')
        return
    if cmd == "AUTO_TOGGLE":
        auto_mode = not auto_mode
        socketio.emit('auto_state', {'auto': auto_mode}, broadcast=True)
        return
    socketio.emit('log', f"Unknown command: {cmd}")


# ---------- MAIN ----------
if __name__ == "__main__":
    open_serial()
    threading.Thread(target=serial_reader_thread, daemon=True).start()
    threading.Thread(target=push_worker, daemon=True).start()
    threading.Thread(target=ultrasonic_monitor_thread, daemon=True).start()
    threading.Thread(target=capture_thread, daemon=True).start()
    threading.Thread(target=detection_thread, daemon=True).start()
    threading.Thread(target=servo_watchdog_thread, daemon=True).start()
    print("Server starting...")
    socketio.run(app, host="0.0.0.0", port=5000)
