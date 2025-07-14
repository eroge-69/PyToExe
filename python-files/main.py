# main.py
import cv2
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from screeninfo import get_monitors
import time
import json
import os

CONFIG_FILE = "config.json"

class VideoSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player Manager")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.monitors = get_monitors()
        self.num_videos = 3
        self.video_paths = [tk.StringVar() for _ in range(self.num_videos)]
        self.monitor_choices = [tk.StringVar() for _ in range(self.num_videos)]

        for i, m in enumerate(self.monitor_choices):
            m.set(str(i if i < len(self.monitors) else 0))

        self.load_config()
        self.build_ui()

    def build_ui(self):
        for i in range(self.num_videos):
            row = i * 2
            tk.Label(self.root, text=f"Video {i + 1}:").grid(row=row, column=0, padx=10, pady=5, sticky="e")
            tk.Entry(self.root, textvariable=self.video_paths[i], width=40).grid(row=row, column=1, padx=5)
            tk.Button(self.root, text="Sfoglia", command=lambda idx=i: self.select_file(idx)).grid(row=row, column=2, padx=5)

            tk.Label(self.root, text="Monitor:").grid(row=row + 1, column=0, sticky="e")
            tk.OptionMenu(self.root, self.monitor_choices[i], *[str(i) for i in range(len(self.monitors))]).grid(row=row + 1, column=1, sticky="w")

        tk.Button(self.root, text="Avvia Riproduzione", command=self.start_videos, bg="green", fg="white").grid(row=6, column=1, pady=20)

    def select_file(self, idx):
        filepath = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if filepath:
            self.video_paths[idx].set(filepath)

    def start_videos(self):
        for i in range(self.num_videos):
            if not self.video_paths[i].get():
                messagebox.showerror("Errore", f"Seleziona un file per Video {i + 1}")
                return

        self.save_config()

        for i in range(self.num_videos):
            video_path = self.video_paths[i].get()
            monitor_idx = int(self.monitor_choices[i].get())

            if monitor_idx >= len(self.monitors):
                messagebox.showerror("Errore", f"Monitor {monitor_idx} non disponibile.")
                return

            t = threading.Thread(target=self.play_video_on_monitor, args=(video_path, self.monitors[monitor_idx]))
            t.daemon = True
            t.start()
            time.sleep(0.3)

 def play_video_on_monitor(self, video_path, monitor):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Errore nell'apertura del video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30  # fallback
    frame_delay = 1.0 / fps  # in seconds

    window_name = f"Video_{monitor.x}_{monitor.y}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(window_name, monitor.x, monitor.y)

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            start_time = time.time()
            continue

        # Calcolo della differenza tra tempo reale e timestamp del video
        video_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        target_time = start_time + (video_time_ms / 1000.0)
        now = time.time()
        sleep_time = target_time - now

        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            # siamo in ritardo → frame skipping automatico
            pass

        frame = cv2.resize(frame, (monitor.width, monitor.height))
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(window_name)
