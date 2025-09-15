# AttendanceApp.py
import os
import time
import csv
import threading
from datetime import datetime

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import cv2
import numpy as np
from PIL import ImageGrab
from deepface import DeepFace

# ---------------- CONFIG ----------------
MODEL_NAME = "Facenet"             # DeepFace model (adjust if needed)
ENFORCE_DETECTION = False          # set True if you want strict face detection
ATTENDANCE_FILE = "attendance_log.csv"
RECOGNITION_INTERVAL = 0.8        # seconds between processing frames
LOG_COOLDOWN = 60                 # seconds before same student can be re-logged
DISPLAY_WINDOW = False            # show cv2.imshow preview (True/False)
# ----------------------------------------

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Recognition System")
        self.root.geometry("760x520")

        # State
        self.known_faces = {}         # name -> cv2 image (BGR numpy array)
        self.running = False
        self.thread = None
        self.last_logged = {}        # name -> last timestamp logged (time.time())
        self.lock = threading.Lock()

        # UI
        top = tk.Frame(root)
        top.pack(pady=6)

        self.btn_load = tk.Button(top, text="Load Database Folder", command=self.load_database)
        self.btn_load.grid(row=0, column=0, padx=6)

        self.btn_start = tk.Button(top, text="Start Recognition", command=self.start_recognition)
        self.btn_start.grid(row=0, column=1, padx=6)

        self.btn_stop = tk.Button(top, text="Stop Recognition", command=self.stop_recognition, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=2, padx=6)

        self.btn_open = tk.Button(top, text="Open Attendance Log", command=self.open_log)
        self.btn_open.grid(row=0, column=3, padx=6)

        self.log_area = scrolledtext.ScrolledText(root, width=90, height=25, state='disabled')
        self.log_area.pack(padx=10, pady=8)

        # ensure attendance CSV header
        if not os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Date", "Time"])

        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.log("App ready. Load database folder to begin.")

    def log(self, text):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {text}\n"
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, line)
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def load_database(self):
        folder = filedialog.askdirectory(title="Select student photos folder")
        if not folder:
            return
        loaded = 0
        self.known_faces.clear()
        for fname in os.listdir(folder):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(folder, fname)
                img = cv2.imread(path)
                if img is None:
                    continue
                name = os.path.splitext(fname)[0]
                self.known_faces[name] = img
                loaded += 1

        self.log(f"Loaded {loaded} images from {folder}")
        if loaded == 0:
            messagebox.showwarning("No images", "No valid images found in selected folder.")

    def start_recognition(self):
        if not self.known_faces:
            messagebox.showwarning("No Database", "Please load the student photos folder first.")
            return
        if self.running:
            return
        self.running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.last_logged.clear()
        self.thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.thread.start()
        self.log("Recognition started.")

    def stop_recognition(self):
        if not self.running:
            return
        self.running = False
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.log("Stopping recognition...")

    def open_log(self):
        try:
            os.startfile(os.path.abspath(ATTENDANCE_FILE))
        except Exception:
            messagebox.showinfo("Log Path", f"Attendance log: {os.path.abspath(ATTENDANCE_FILE)}")

    def _recognition_loop(self):
        # Haar cascade for fast face detection on smaller frames
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)

        while self.running:
            try:
                # capture full screen (RGB -> convert to BGR for OpenCV)
                screen = ImageGrab.grab()
                frame_rgb = np.array(screen)         # RGB
                frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)  # BGR

                # small for detection
                scale = 0.5
                small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

                # detect faces
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
                # iterate each detected face
                for (x, y, w, h) in faces:
                    # scale coords back to original frame
                    x1 = int(x / scale)
                    y1 = int(y / scale)
                    x2 = int((x + w) / scale)
                    y2 = int((y + h) / scale)

                    # ensure coords in bounds
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                    face_img = frame[y1:y2, x1:x2]
                    if face_img.size == 0:
                        continue

                    # compare with known faces
                    for name, db_img in self.known_faces.items():
                        # cooldown check
                        last = self.last_logged.get(name, 0)
                        if time.time() - last < LOG_COOLDOWN:
                            continue

                        try:
                            # Use DeepFace.verify with numpy arrays (positional args safer across versions)
                            result = DeepFace.verify(face_img, db_img, model_name=MODEL_NAME, enforce_detection=ENFORCE_DETECTION)
                            verified = result.get("verified", False)
                        except Exception as e:
                            # sometimes DeepFace throws for empty/no-face; skip gracefully
                            self.log(f"DeepFace error for {name}: {e}")
                            verified = False

                        if verified:
                            # Log attendance
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            date_str, time_str = ts.split(" ")
                            with self.lock:
                                with open(ATTENDANCE_FILE, 'a', newline='', encoding='utf-8') as f:
                                    writer = csv.writer(f)
                                    writer.writerow([name, date_str, time_str])
                                self.last_logged[name] = time.time()
                            self.log(f"Recognized {name} - {time_str}")

                            # annotate frame
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, name, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            break   # stop checking other db faces for this detected face

                # show preview if desired
                if DISPLAY_WINDOW:
                    cv2.imshow("Attendance - press 'q' to quit preview", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        # treat as stop request
                        self.running = False
                        break

            except Exception as e:
                # log unexpected frame-level errors but keep running
                self.log(f"Frame error: {e}")

            # avoid busy loop
            for _ in range(int(RECOGNITION_INTERVAL * 10)):
                if not self.running:
                    break
                time.sleep(0.1)

        # cleanup
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        self.log("Recognition stopped.")
        # ensure UI buttons updated on main thread
        self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))

    def _on_closing(self):
        # stop if running, then close
        if self.running:
            self.running = False
            self.log("Stopping recognition before exit...")
            # give thread some time
            if self.thread:
                self.thread.join(timeout=2)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()