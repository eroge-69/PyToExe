import cv2
import pyvirtualcam
import numpy as np
import threading
import tkinter as tk
import time
from datetime import datetime

# -------- CONFIG --------
PHONE_CAM_IDX = 0      # Phone camera index
PC_WEBCAM_IDX = 2      # Laptop webcam index
OUT_W, OUT_H  = 1280, 720
TARGET_FPS    = 20
PIP_RATIO     = 0.25   # size of webcam overlay
# ------------------------

running = False
break_mode = False
thread = None
thread_lock = threading.Lock()

cam_instance = None
rainbow_offset = 0

# Prebuild kernel once (faster)
SHARPEN_KERNEL = np.array([[0, -0.25, 0],
                           [-0.25, 2.0, -0.25],
                           [0, -0.25, 0]], dtype=np.float32)

# ----------------- Image Enhancement -----------------
def enhance_phone(frame, target_w, target_h):
    """Enhance phone feed using GPU (UMat if available) or CPU fallback."""
    h, w = frame.shape[:2]

    if h > w:  # portrait → rotate
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        h, w = frame.shape[:2]

    # Crop aspect ratio
    aspect_in = w / h
    aspect_out = target_w / target_h
    if aspect_in > aspect_out:
        new_w = int(h * aspect_out)
        x1 = (w - new_w) // 2
        frame = frame[:, x1:x1 + new_w]
    else:
        new_h = int(w / aspect_out)
        y1 = (h - new_h) // 2
        frame = frame[y1:y1 + new_h, :]

    try:
        # Upload to GPU (OpenCL)
        uframe = cv2.UMat(frame)

        # Resize
        uframe = cv2.resize(uframe, (target_w, target_h), interpolation=cv2.INTER_AREA)

        # Sharpen + contrast
        uframe = cv2.filter2D(uframe, -1, SHARPEN_KERNEL)
        uframe = cv2.convertScaleAbs(uframe, alpha=1.2, beta=10)

        frame = uframe.get()  # download back to CPU for compositing
    except Exception as e:
        # If GPU path fails → fallback to CPU
        frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
        frame = cv2.flip(frame, 1)
        frame = cv2.filter2D(frame, -1, SHARPEN_KERNEL)
        frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)

    return frame

# ----------------- Camera helpers -----------------
def open_cam(idx, width=1280, height=720):
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        try: cap.release()
        except: pass
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    return cap

def overlay_pip_top_right(bg, pip, ratio=0.25):
    if bg is None or pip is None:
        return bg
    h, w = bg.shape[:2]
    pip_w = int(w * ratio)
    pip_h = int(pip.shape[0] * (pip_w / pip.shape[1]))
    pip_resized = cv2.resize(pip, (pip_w, pip_h), interpolation=cv2.INTER_AREA)
    bg[0:pip_h, w - pip_w:w] = pip_resized
    return bg

def create_rainbow_break_slide():
    global rainbow_offset
    slide = np.zeros((OUT_H, OUT_W, 3), dtype=np.uint8)

    text = "Back in a bit"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 3.0
    thickness = 8

    (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)
    start_x = (OUT_W - text_w) // 2
    baseline_y = (OUT_H + text_h) // 2

    x = start_x
    for ch in text:
        (cw, _), _ = cv2.getTextSize(ch, font, scale, thickness)
        hue = int((rainbow_offset + (x / OUT_W) * 180) % 180)
        color_hsv = np.uint8([[[hue, 255, 255]]])
        color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0].tolist()
        cv2.putText(slide, ch, (int(x), int(baseline_y)), font, scale,
                    tuple(int(c) for c in color_bgr), thickness, cv2.LINE_AA)
        x += cw

    rainbow_offset = (rainbow_offset + 2) % 180
    return slide

# ----------------- Camera thread loop -----------------
def cam_loop():
    global running, break_mode, cam_instance
    phone_cap = None
    face_cap = None
    try:
        with pyvirtualcam.Camera(width=OUT_W, height=OUT_H, fps=TARGET_FPS) as cam:
            cam_instance = cam
            frame_interval = 1.0 / TARGET_FPS
            while True:
                t_start = time.time()

                with thread_lock:
                    if not running:
                        break

                if break_mode:
                    if phone_cap: phone_cap.release(); phone_cap = None
                    if face_cap: face_cap.release(); face_cap = None
                    frame_out = create_rainbow_break_slide()
                else:
                    if phone_cap is None:
                        phone_cap = open_cam(PHONE_CAM_IDX)
                    if face_cap is None:
                        face_cap = open_cam(PC_WEBCAM_IDX)

                    phone_fr = None
                    face_fr = None
                    if phone_cap is not None:
                        ret, fr = phone_cap.read()
                        if ret: phone_fr = fr
                    if face_cap is not None:
                        ret, fr = face_cap.read()
                        if ret: face_fr = fr

                    frame_out = None
                    if phone_fr is not None:
                        frame_out = enhance_phone(phone_fr, OUT_W, OUT_H)

                    if face_fr is not None:
                        if frame_out is None:
                            frame_out = cv2.resize(face_fr, (OUT_W, OUT_H), interpolation=cv2.INTER_AREA)
                        else:
                            frame_out = overlay_pip_top_right(frame_out, face_fr, PIP_RATIO)

                    if frame_out is None:
                        frame_out = np.zeros((OUT_H, OUT_W, 3), dtype=np.uint8)

                out_rgb = cv2.cvtColor(frame_out, cv2.COLOR_BGR2RGB)
                cam.send(out_rgb)
                cam.sleep_until_next_frame()

                elapsed = time.time() - t_start
                if elapsed < frame_interval:
                    time.sleep(frame_interval - elapsed)

    finally:
        if phone_cap: phone_cap.release()
        if face_cap: face_cap.release()
        cam_instance = None
        with thread_lock:
            running = False

# ----------------- GUI -----------------
def animate_button(btn, color, active_color):
    def on_press(e): btn.config(bg=active_color)
    def on_release(e): btn.config(bg=color)
    btn.bind("<ButtonPress-1>", on_press)
    btn.bind("<ButtonRelease-1>", on_release)

def start_cam():
    global running, thread, break_mode
    with thread_lock:
        if running:
            break_mode = False
            return
        break_mode = False
        running = True
        thread = threading.Thread(target=cam_loop, daemon=True)
        thread.start()

def stop_cam():
    global running, break_mode
    with thread_lock:
        running = False
        break_mode = False

def toggle_break():
    global break_mode
    with thread_lock:
        if running:
            break_mode = not break_mode

root = tk.Tk()
root.title("DualCam Controller")
root.geometry("480x120")
root.resizable(False, False)

frame_buttons = tk.Frame(root)
frame_buttons.pack(expand=True, pady=18)

btn_start = tk.Button(frame_buttons, text="Start", command=start_cam, width=12, height=2, bg="#2ecc71", fg="white", bd=0)
btn_break = tk.Button(frame_buttons, text="Break", command=toggle_break, width=12, height=2, bg="#f39c12", fg="black", bd=0)
btn_stop = tk.Button(frame_buttons, text="Stop", command=stop_cam, width=12, height=2, bg="#e74c3c", fg="white", bd=0)

animate_button(btn_start, "#2ecc71", "#58d68d")
animate_button(btn_break, "#f39c12", "#f6c26b")
animate_button(btn_stop, "#e74c3c", "#f1948a")

btn_start.pack(side="left", padx=10)
btn_break.pack(side="left", padx=10)
btn_stop.pack(side="left", padx=10)

status_var = tk.StringVar(value="Stopped")
def refresh_status():
    if running:
        status_var.set("Running - Break" if break_mode else "Running")
    else:
        status_var.set("Stopped")
    root.after(250, refresh_status)
status_label = tk.Label(root, textvariable=status_var, font=("Arial", 10))
status_label.pack(side="bottom")
refresh_status()

def on_close():
    stop_cam()
    time.sleep(0.2)
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
