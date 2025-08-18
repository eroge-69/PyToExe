import cv2
import time
import math
import threading
import pyautogui
import mediapipe as mp
import tkinter as tk  
from tkinter import ttk
import subprocess
import psutil
pyautogui.FAILSAFE = False

class GestureMouseApp:
    BLINK_THRESH = 0.23
    BLINK_FRAMES_REQ = 2
    BLINK_MIN_INTERVAL = 0.8

    def __init__(self, root):
        self.root = root
        self.root.title("برنامه هوشمند")
        self.root.geometry("440x280")
        self.root.configure(bg="#e6f7f1")
        self.root.resizable(False, False)
        from tkinter import PhotoImage

        icon = PhotoImage(file="C:/Users/farza/OneDrive/Desktop/New folder/m.png")

        self.root.iconphoto(True, icon)

        self.running = False
        self.speed = 0.5
        self.screen_w, self.screen_h = pyautogui.size()
        self.curr_x, self.curr_y = pyautogui.position()

        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]

        self.build_ui()
        self.start()  # شروع خودکار

    def build_ui(self):
        container = tk.Frame(self.root, bg="#40e0d0", padx=14, pady=14)
        container.pack(fill="x")

        self.status_lbl = tk.Label(container, text=" اجرا", font=("Tahoma", 13, "bold"), 
                                   bg="#e6f7f1", fg="#28a745")
        self.status_lbl.pack(anchor="center", pady=(0, 12))

        btn_row = tk.Frame(container, bg="#50d085")
        btn_row.pack(pady=(0, 14))

        tk.Button(btn_row, text="شروع", width=11, bg="#28a745", fg="white", 
                  command=self.start).grid(row=0, column=0, padx=3, pady=3)
        tk.Button(btn_row, text="توقف", width=11, bg="#dc3545", fg="white", 
                  command=self.stop).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(btn_row, text="باز کردن کیبورد", width=11, bg="#17a2b8", fg="white", 
                  command=self.open_keyboard).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(btn_row, text="بستن کیبورد", width=11, bg="#ffc107", fg="black", 
                  command=self.close_keyboard).grid(row=1, column=1, padx=3, pady=3)
        tk.Button(btn_row, text="خروج", width=11, bg="#6c757d", fg="white", 
                  command=self.exit_app).grid(row=2, column=0, padx=3, pady=3)

        self.speed_lbl = tk.Label(container, text=f"سرعت موس: {self.speed:.2f}", 
                                  bg="#e6f7f1", font=("Tahoma", 10))
        self.speed_lbl.pack(anchor="w")

        ttk.Scale(container, from_=0.1, to=2.0, value=self.speed, 
                  orient="horizontal", command=self.on_speed_change).pack(fill="x", pady=(4, 10))

    def start(self):
        if not self.running:
            self.running = True
            self.status_lbl.config(text="در حال اجرا", fg="#28a745")
            threading.Thread(target=self.process_loop, daemon=True).start()

    def stop(self):
        if self.running:
            self.running = False
            self.status_lbl.config(text="توقف", fg="#dc3545")

    def exit_app(self):
        self.running = False
        self.root.destroy()

    def open_keyboard(self):
        try:
            subprocess.Popen("osk", shell=True)
        except Exception:
            self.status_lbl.config(text="خطا در باز کردن کیبورد", fg="#ff3b30")

    

    def close_keyboard(self):
        closed = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in ['osk.exe', 'TabTip.exe']:
                    proc.terminate()
                    closed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed:
            self.status_lbl.config(text="کیبورد بسته شد", fg="#28a745")
        else:
            self.status_lbl.config(text="کیبوردی برای بستن پیدا نشد", fg="#6c757d")

    def on_speed_change(self, val):
        self.speed = float(val)
        self.speed_lbl.config(text=f"سرعت موس: {self.speed:.2f}")

    def _eye_ear(self, landmarks, idxs):
        p = landmarks
        def dist(a, b):
            return math.hypot(p[a].x - p[b].x, p[a].y - p[b].y)
        A = dist(idxs[1], idxs[5])
        B = dist(idxs[2], idxs[4])
        C = dist(idxs[0], idxs[3]) + 1e-6
        return (A + B) / (2.0 * C)

    def process_loop(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

        with self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                        min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh, \
             self.mp_hands.Hands(max_num_hands=2, model_complexity=1,
                                 min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

            blink_frames = {"right": 0}
            last_click_time = {"right": 0.0}

            while self.running:
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.01)
                    continue

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                face_res = face_mesh.process(rgb)
                hand_res = hands.process(rgb)

                if face_res.multi_face_landmarks:
                    lms = face_res.multi_face_landmarks[0].landmark
                    l_ear = self._eye_ear(lms, self.LEFT_EYE)
                    r_ear = self._eye_ear(lms, self.RIGHT_EYE)

                    if l_ear < self.BLINK_THRESH:
                        pyautogui.mouseDown(button='left')
                    else:
                        pyautogui.mouseUp(button='left')

                    if r_ear < self.BLINK_THRESH:
                        blink_frames["right"] += 1
                    else:
                        if blink_frames["right"] >= self.BLINK_FRAMES_REQ:
                            now = time.time()
                            if now - last_click_time["right"] >= self.BLINK_MIN_INTERVAL:
                                pyautogui.rightClick()
                                last_click_time["right"] = now
                        blink_frames["right"] = 0

                # فقط دست چپ برای حرکت موس
                if hand_res.multi_hand_landmarks and hand_res.multi_handedness:
                    for lm, info in zip(hand_res.multi_hand_landmarks, hand_res.multi_handedness):
                        if info.classification[0].label == "Left":
                            tip = lm.landmark[8]
                            x = int(tip.x * self.screen_w)
                            y = int(tip.y * self.screen_h)
                            self.curr_x += (x - self.curr_x) * self.speed
                            self.curr_y += (y - self.curr_y) * self.speed
                            pyautogui.moveTo(self.curr_x, self.curr_y)
                            break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureMouseApp(root)
    root.mainloop()
