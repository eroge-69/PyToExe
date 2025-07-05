import cv2
import os
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import socket
import time
import mediapipe as mp
import mss

# Приховати warning-и від TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ========== Константи ==========
VIDEO_DIR = "videos"
FRAME_DIR = "frames"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

# ========== MediaPipe ініціалізація ==========
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ========== Глобальні змінні ==========
cap = None
video_writer = None
recording = False
streaming = False
manual_recording = False
fps_counter = 0
fps_time = time.time()
last_fps = 0
source_info = "Невідомо"
smoothed_landmarks = {}
ALPHA = 0.5
screen_capture = None
streaming_screen = False
show_video = True

# ========== Функції ==========
def init_video_writer(shape):
    global video_writer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"record_{timestamp}.avi"
    filepath = os.path.join(VIDEO_DIR, filename)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filepath, fourcc, 20.0, (shape[1], shape[0]))
    log(f"▶️ Запис у файл: {filename}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Невідомо"

def detect_people(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(rgb)
    h, w, _ = frame.shape
    keypoints = []

    # === Тіло ===
    if results.pose_landmarks:
        allowed_pose_ids = list(range(11, 33))  # від плечей до стоп
        for i in allowed_pose_ids:
            lm = results.pose_landmarks.landmark[i]
            if lm.visibility > 0.5:
                cx, cy = int(lm.x * w), int(lm.y * h)
                smoothed_x, smoothed_y = smooth_point(f"pose_{i}", cx, cy)
                cv2.circle(frame, (int(smoothed_x), int(smoothed_y)), 2, (0, 255, 0), -1)
                keypoints.append((i, int(smoothed_x), int(smoothed_y)))

    # === Руки ===
    for hand_landmarks in [results.left_hand_landmarks, results.right_hand_landmarks]:
        if hand_landmarks:
            for i, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 2, (0, 0, 255), -1)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    # === Обличчя: тільки ключові риси ===
    if results.face_landmarks:
        facial_ids = [1, 33, 61, 199, 263, 291]  # очі, ніс, рот
        for i in facial_ids:
            lm = results.face_landmarks.landmark[i]
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 1, (255, 255, 255), -1)

    return keypoints

def smooth_point(id, x, y):
    global smoothed_landmarks
    if id not in smoothed_landmarks:
        smoothed_landmarks[id] = (x, y)
    else:
        prev_x, prev_y = smoothed_landmarks[id]
        new_x = ALPHA * x + (1 - ALPHA) * prev_x
        new_y = ALPHA * y + (1 - ALPHA) * prev_y
        smoothed_landmarks[id] = (new_x, new_y)
    return smoothed_landmarks[id]

def log(message):
    log_text.configure(state='normal')
    log_text.insert(tk.END, message + "\n")
    log_text.configure(state='disabled')
    log_text.see(tk.END)

def video_loop():
    global cap, recording, video_writer, streaming, manual_recording
    global fps_counter, fps_time, last_fps, source_info

    while streaming:
        ret, frame = cap.read()
        if not ret:
            break

        fps_counter += 1
        if time.time() - fps_time >= 1.0:
            last_fps = fps_counter
            fps_counter = 0
            fps_time = time.time()

        keypoints = detect_people(frame)

        if keypoints and manual_recording and not recording:
            init_video_writer(frame.shape)
            recording = True
            log("⏺ Запис розпочато вручну.")

        if recording and manual_recording:
            video_writer.write(frame)

        cv2.putText(frame, f"FPS: {last_fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Джерело: {source_info}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    log("🛑 Потік завершено")

def save_frame_sequence(frame, boxes):
    for i in range(5):
        frame_copy = frame.copy()
        timestamp = datetime.now().strftime('%H%M%S') + f"_{i}"
        path = os.path.join(FRAME_DIR, f"frame_{timestamp}.jpg")
        cv2.imwrite(path, frame_copy)
        log(f"💾 Збережено кадр: {path}")

def start_camera():
    global source_info, cap, streaming, recording
    source_info = f"Вебкамера ({get_local_ip()})"
    stop_stream()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        messagebox.showerror("Помилка", "Не вдалося відкрити камеру.")
        return

    log(f"⚙️ Параметри камери: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)} @ {cap.get(cv2.CAP_PROP_FPS):.1f} FPS")

    streaming = True
    recording = False
    threading.Thread(target=video_loop).start()
    log("🎥 Камера активована")

def start_screen_capture():
    global streaming, streaming_screen, cap, recording, source_info
    stop_stream()
    streaming = True
    streaming_screen = True
    recording = False
    source_info = "Демонстрація екрану"
    threading.Thread(target=screen_loop, daemon=True).start()
    log("🖥 Запущено демонстрацію екрану")

def screen_loop():
    global streaming, recording, video_writer, streaming_screen
    global fps_counter, fps_time, last_fps, manual_recording, show_video
    with mss.mss() as screen_capture:
        monitor = screen_capture.monitors[1]
        while streaming and streaming_screen:
            img = np.array(screen_capture.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            fps_counter += 1
            if time.time() - fps_time >= 1.0:
                last_fps = fps_counter
                fps_counter = 0
                fps_time = time.time()

            keypoints = detect_people(frame)

            if keypoints and manual_recording and not recording:
                init_video_writer(frame.shape)
                recording = True
                log("⏺ Запис розпочато вручну.")

            if recording and manual_recording:
                video_writer.write(frame)

            # Показуємо відео тільки якщо увімкнено
            if show_video:
                cv2.putText(frame, f"FPS: {last_fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Джерело: {source_info}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(rgb)

                # Зменшуємо розмір зображення до розміру video_label (наприклад 640x480)
                img_pil = img_pil.resize((640, 480))
                imgtk = ImageTk.PhotoImage(image=img_pil)
                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)
            else:
                # Якщо приховано відео, очищуємо зображення
                video_label.configure(image='')

    log("🛑 Потік демонстрації екрану завершено")

def toggle_video_display():
    global show_video
    show_video = not show_video
    if not show_video:
        video_label.configure(image='')  # Очищаємо приховане відео
    else:
        log("🎥 Відео показано")

def toggle_manual_recording():
    global manual_recording, recording, video_writer
    manual_recording = not manual_recording
    if not manual_recording:
        if recording and video_writer:
            video_writer.release()
            log("⏹ Запис зупинено.")
        recording = False

def storyboard_frames():
    if cap is None:
        return
    ret, frame = cap.read()
    if not ret:
        return

    keypoints = detect_people(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    important_parts = {
        "Голова": [0],
        "Ліва рука": [11, 13, 15],
        "Права рука": [12, 14, 16],
        "Ліва нога": [23, 25, 27],
        "Права нога": [24, 26, 28]
    }

    for label, ids in important_parts.items():
        points = [(x, y) for (i, x, y) in keypoints if i in ids]
        if not points:
            continue
        x_min = min(x for x, y in points)
        x_max = max(x for x, y in points)
        y_min = min(y for x, y in points)
        y_max = max(y for x, y in points)
        crop = gray[y_min:y_max, x_min:x_max]
        if crop.size > 0:
            cv2.imshow(f"{label}", crop)

    log("📸 Створено розкадровку частин тіла.")

def start_file():
    global cap, streaming, recording, source_info
    source_info = "Файл (локальний)"
    stop_stream()
    filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
    if not filepath:
        return
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        messagebox.showerror("Помилка", "Не вдалося відкрити файл.")
        return
    streaming = True
    recording = False
    threading.Thread(target=video_loop).start()
    log(f"📁 Відкрито файл: {filepath}")

def stop_stream():
    global cap, video_writer, streaming, recording, streaming_screen, screen_capture
    streaming = False
    streaming_screen = False
    recording = False
    if cap is not None:
        cap.release()
        cap = None
    if video_writer:
        video_writer.release()
        video_writer = None
    if screen_capture:
        screen_capture.close()
        screen_capture = None

def quit_app():
    stop_stream()
    root.destroy()

def save_current_frames():
    if cap is None:
        return
    ret, frame = cap.read()
    if not ret:
        return
    keypoints = detect_people(frame)
    save_frame_sequence(frame, keypoints)

# ========== GUI ==========
root = tk.Tk()
root.title("🎛 Система відеоаналітики")
root.geometry("1000x750")
root.configure(bg="#1e1e1e")

video_label = tk.Label(root, bg="#000000")
video_label.pack(pady=10)

btns = tk.Frame(root, bg="#1e1e1e")
btns.pack(pady=5)

tk.Button(btns, text="📷 Камера", command=start_camera, width=20).grid(row=0, column=0, padx=10, pady=5)
tk.Button(btns, text="🎞 Відеофайл", command=start_file, width=20).grid(row=0, column=1, padx=10, pady=5)
tk.Button(btns, text="💾 Зберегти кадри", command=save_current_frames, width=20).grid(row=0, column=2, padx=10, pady=5)
tk.Button(btns, text="🖥 Демонстрація екрану", command=start_screen_capture, width=20).grid(row=0, column=3, padx=10, pady=5)
tk.Button(btns, text="❌ Вихід", command=quit_app, width=20).grid(row=0, column=4, padx=10, pady=5)

tk.Button(btns, text="⏺ Запис відеоряду", command=toggle_manual_recording, width=20).grid(row=1, column=0, padx=10, pady=10)
tk.Button(btns, text="🖼 Розкадровка", command=storyboard_frames, width=20).grid(row=1, column=1, padx=10, pady=10)
tk.Button(btns, text="👁 Показати/Приховати відео", command=toggle_video_display, width=20).grid(row=1, column=2, padx=10, pady=10)

log_text = tk.Text(root, height=8, bg="#111", fg="#0f0", font=("Consolas", 10), state='disabled')
log_text.pack(pady=10, fill=tk.X, padx=20)

log("🔵 Програма запущена")

root.protocol("WM_DELETE_WINDOW", quit_app)
root.mainloop()
