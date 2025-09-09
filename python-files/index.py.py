# app.py
"""
Robust FocusCam app:
- 5s splash showing FocusCamOwner.jpeg + "FocusCam by Godfred Bio" + progress bar
- Neat main UI (clean card, live preview, simple controls)
- Background camera worker (mediapipe + optional YOLO if installed)
- Safe: optional libraries wrapped so UI always opens
"""

import sys, os, time, threading, math, json, csv, random
from datetime import datetime

# core libs
try:
    import cv2
except Exception as e:
    print("ERROR: OpenCV (cv2) is required. Install with: pip install opencv-python")
    raise e

# optional libs (wrap)
HAVE_MEDIAPIPE = False
HAVE_YOLO = False
HAVE_TTS = False
try:
    import mediapipe as mp
    HAVE_MEDIAPIPE = True
except Exception:
    print("mediapipe not available — focus estimation will be limited. Install with: pip install mediapipe")

try:
    from ultralytics import YOLO
    HAVE_YOLO = True
except Exception:
    print("ultralytics/YOLO not available — phone detection disabled. Install with: pip install ultralytics and place yolov8n.pt")

try:
    import pyttsx3
    HAVE_TTS = True
except Exception:
    print("pyttsx3 not available — TTS alerts disabled. Install with: pip install pyttsx3")

from PyQt6 import QtCore, QtGui, QtWidgets

# -------------------------
# Files + storage
# -------------------------
YOLO_MODEL_PATH = "yolov8n.pt"
DATA_DIR = "data"
LOGS_DIR = "logs"
SNAPSHOT_DIR = "snapshots"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
QUOTE_FILE = os.path.join(DATA_DIR, "quotes.json")
LOG_FILE = os.path.join(LOGS_DIR, "focuscam_session_log.csv")

# defaults
def load_settings():
    default = {"username": "User", "duration": 30, "goal": ""}
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f, indent=4)
    with open(SETTINGS_FILE) as f:
        return json.load(f)

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=4)

def load_quotes():
    default = {"motivational": ["Stay focused."], "punishing": ["Discipline matters."]}
    if not os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "w") as f:
            json.dump(default, f, indent=4)
    with open(QUOTE_FILE) as f:
        return json.load(f)

settings = load_settings()
quotes = load_quotes()

# -------------------------
# small helpers
# -------------------------
def speak_async(text: str):
    if not HAVE_TTS:
        return
    def _t():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
    threading.Thread(target=_t, daemon=True).start()

def save_snapshot(frame_bgr):
    fname = os.path.join(SNAPSHOT_DIR, f"snapshot_{int(time.time())}.jpg")
    cv2.imwrite(fname, frame_bgr)
    return fname

def get_quote_for_percent(p: int):
    if p >= 90: return random.choice(quotes.get("motivational", ["Great job!"]))
    if p >= 70: return "Good job — keep going!"
    return random.choice(quotes.get("punishing", ["Refs: stay focused"]))

# -------------------------
# Splash (custom widget)
# -------------------------
class SplashWindow(QtWidgets.QWidget):
    def __init__(self, image_path: str, title_text: str = "FocusCam\nby Godfred Bio", duration_ms: int = 5000):
        super().__init__(flags=QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.duration_ms = int(duration_ms)
        self.setFixedSize(520, 480)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # image
        if os.path.exists(image_path):
            pix = QtGui.QPixmap(image_path).scaled(320, 320, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                   QtCore.Qt.TransformationMode.SmoothTransformation)
            img_label = QtWidgets.QLabel()
            img_label.setPixmap(pix)
            img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(img_label)
        else:
            # placeholder colored circle
            placeholder = QtWidgets.QLabel("FocusCam")
            placeholder.setFixedSize(160,160)
            placeholder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("background:#2d7aef; color:white; border-radius:80px; font-weight:700;")
            layout.addWidget(placeholder)

        # title under image
        title = QtWidgets.QLabel(title_text)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:700; color:#222;")
        layout.addWidget(title)

        # progress bar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setFixedHeight(18)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar { border: 1px solid #cbd5e1; border-radius: 9px; text-align: center; background: #f0f4f8; }
            QProgressBar::chunk { background-color: #2d7aef; border-radius: 8px; }
        """)
        layout.addWidget(self.progress)

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(max(10, self.duration_ms // 100))  # ~duration/100 steps
        self._timer.timeout.connect(self._step)
        self._step_val = 0

    def start(self):
        self._step_val = 0
        self.progress.setValue(0)
        self._timer.start()

    def _step(self):
        self._step_val += 1
        pct = min(100, int(self._step_val * (100.0 * self._timer.interval() / max(1, self.duration_ms))))
        self.progress.setValue(pct)
        if pct >= 100:
            self._timer.stop()
            self.close()  # caller should show main window after calling start()

# -------------------------
# Camera worker
# -------------------------
class CameraWorker(QtCore.QObject):
    frame_ready = QtCore.pyqtSignal(QtGui.QImage)
    stats_update = QtCore.pyqtSignal(float, float, int)
    session_finished = QtCore.pyqtSignal(float, float, int, str)
    error = QtCore.pyqtSignal(str)

    def __init__(self, duration_min: int, username: str, goal: str):
        super().__init__()
        self.duration = max(1, int(duration_min)) * 60.0
        self.username = username
        self.goal = goal
        self._running = False
        self._paused = False
        self.last_alert = 0
        self.distraction_count = 0

        # runtime load of heavy models, safe-guarded
        self.yolo = None
        if HAVE_YOLO and os.path.exists(YOLO_MODEL_PATH):
            try:
                self.yolo = YOLO(YOLO_MODEL_PATH)
            except Exception as e:
                print("YOLO model load error:", e)
                self.yolo = None

        self.face_mesh = None
        if HAVE_MEDIAPIPE:
            try:
                self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
            except Exception as e:
                print("mediapipe init failed:", e)
                self.face_mesh = None

    def start(self):
        self._running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._running = False

    def pause(self, val: bool):
        self._paused = val

    def _convert_to_qimage(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bpl = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bpl, QtGui.QImage.Format.Format_RGB888)
        return qimg

    def _run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error.emit("Cannot open webcam. Make sure it is connected and not used by another app.")
            return

        start_time = time.time()
        last_time = time.time()
        focused_s = 0.0
        distracted_s = 0.0

        while self._running and (time.time() - start_time) < self.duration:
            ret, frame = cap.read()
            if not ret:
                break

            now = time.time()
            elapsed = now - last_time
            last_time = now

            if self._paused:
                # show paused overlay (frame unchanged but label added)
                overlay = frame.copy()
                cv2.putText(overlay, "PAUSED", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
                try:
                    self.frame_ready.emit(self._convert_to_qimage(overlay))
                except Exception:
                    pass
                time.sleep(0.04)
                continue

            # default: not focused (if we have no mediapipe)
            is_focused = False

            # mediapipe focus estimation
            if self.face_mesh is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                try:
                    res = self.face_mesh.process(rgb)
                except Exception:
                    res = None
                if res and getattr(res, "multi_face_landmarks", None):
                    face = res.multi_face_landmarks[0]
                    nose = face.landmark[1]; chin = face.landmark[152]
                    left_eye = face.landmark[33]; right_eye = face.landmark[263]
                    pitch = math.degrees(math.atan2(chin.y - nose.y, 0.1))
                    gaze_val = (left_eye.y + right_eye.y) / 2.0
                    is_focused = (-10 <= pitch <= 70) and (gaze_val < 0.5)
                    # draw markers
                    h, w = frame.shape[:2]
                    nx, ny = int(nose.x*w), int(nose.y*h)
                    cx, cy = int(chin.x*w), int(chin.y*h)
                    cv2.circle(frame, (nx, ny), 3, (0,255,0), -1)
                    cv2.circle(frame, (cx, cy), 3, (255,0,0), -1)
            else:
                # fallback simple face detection to avoid immediate distraction
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
                is_focused = len(faces) > 0

            # YOLO phone detection (optional)
            phone_detected = False
            if self.yolo is not None:
                try:
                    yres = self.yolo(frame, verbose=False)
                    for r in yres:
                        for box in getattr(r, "boxes", []):
                            cls = int(box.cls[0])
                            label = self.yolo.names.get(cls, "").lower()
                            if "phone" in label or "mobile" in label:
                                x1,y1,x2,y2 = [int(x) for x in box.xyxy[0]]
                                cv2.rectangle(frame, (x1,y1),(x2,y2),(0,0,255),2)
                                cv2.putText(frame, "Phone", (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
                                phone_detected = True
                                break
                        if phone_detected:
                            break
                except Exception as e:
                    # don't kill loop if ultralytics format differs
                    print("YOLO detection error (ignored):", e)

            # timers update
            if is_focused and not phone_detected:
                focused_s += elapsed
            else:
                distracted_s += elapsed
                # throttled alerts
                if now - self.last_alert > 5:
                    self.distraction_count += 1
                    if phone_detected:
                        speak_async("Put the phone down and focus.")
                    else:
                        speak_async(f"{self.username}, please focus.")
                    save_snapshot(frame)
                    if self.distraction_count == 5 and self.goal:
                        speak_async(f"Remember your goal: {self.goal}")
                    elif self.distraction_count == 10:
                        speak_async(random.choice(quotes.get("punishing", ["Focus up"])) )
                    self.last_alert = now

            total = focused_s + distracted_s
            pct = int((focused_s / total) * 100) if total > 0 else 0

            # overlay small info
            h,w = frame.shape[:2]
            cv2.putText(frame, f"{self.username} | Focus: {pct}%", (w-300,28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0) if is_focused and not phone_detected else (0,0,255), 2)
            remaining = max(0, self.duration - (now - start_time))
            mins = int(remaining)//60; secs = int(remaining)%60
            cv2.putText(frame, f"Time Left: {mins:02}:{secs:02}", (12,28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

            # emit frame and stats
            try:
                self.frame_ready.emit(self._convert_to_qimage(frame))
                self.stats_update.emit(focused_s, distracted_s, pct)
            except Exception:
                pass

            # tiny sleep
            time.sleep(0.01)

        # done: log and emit session_finished
        try:
            with open(LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.username, round(focused_s/60,2), round(distracted_s/60,2)])
        except Exception as e:
            print("Log write error:", e)

        self.session_finished.emit(round(focused_s/60,2), round(distracted_s/60,2), pct, get_quote_for_percent(pct))
        cap.release()
        if self.face_mesh:
            self.face_mesh.close()

# -------------------------
# Main UI
# -------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusCam")
        self.setFixedSize(980, 700)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        # global layout
        outer = QtWidgets.QVBoxLayout(central)
        outer.setContentsMargins(18,18,18,18)

        # card-like frame
        card = QtWidgets.QFrame()
        card.setStyleSheet("QFrame { background: white; border-radius: 12px; }")
        outer.addWidget(card)
        main_layout = QtWidgets.QHBoxLayout(card)
        main_layout.setContentsMargins(16,16,16,16)
        main_layout.setSpacing(16)

        # left: video
        left = QtWidgets.QVBoxLayout()
        lbl = QtWidgets.QLabel("📸 Live Preview")
        lbl.setStyleSheet("font-weight:700; font-size:16px;")
        left.addWidget(lbl)
        self.video_label = QtWidgets.QLabel()
        self.video_label.setFixedSize(680,500)
        self.video_label.setStyleSheet("background:#f3f5f7; border-radius:10px;")
        left.addWidget(self.video_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(left)

        # right: controls
        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel("Session Settings"))
        right.addSpacing(4)
        right.addWidget(QtWidgets.QLabel("Name:"))
        self.name_edit = QtWidgets.QLineEdit(settings.get("username", "User"))
        right.addWidget(self.name_edit)
        right.addWidget(QtWidgets.QLabel("Duration (minutes):"))
        self.duration_edit = QtWidgets.QLineEdit(str(settings.get("duration", 30)))
        right.addWidget(self.duration_edit)
        right.addWidget(QtWidgets.QLabel("Goal:"))
        self.goal_edit = QtWidgets.QLineEdit(settings.get("goal", ""))
        right.addWidget(self.goal_edit)
        right.addSpacing(8)

        self.start_btn = QtWidgets.QPushButton("▶ Start Session")
        self.start_btn.setStyleSheet("background:#2d7aef;color:white;border-radius:8px;padding:8px;font-weight:700;")
        self.start_btn.clicked.connect(self.start_session)
        right.addWidget(self.start_btn)

        self.pause_btn = QtWidgets.QPushButton("⏸ Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("background:#f0ad4e;color:white;border-radius:8px;padding:8px;font-weight:700;")
        self.pause_btn.clicked.connect(self.toggle_pause)
        right.addWidget(self.pause_btn)

        self.quotes_btn = QtWidgets.QPushButton("📝 Edit Quotes")
        self.quotes_btn.clicked.connect(self.edit_quotes)
        right.addWidget(self.quotes_btn)

        self.export_btn = QtWidgets.QPushButton("📤 Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        right.addWidget(self.export_btn)

        right.addStretch()
        footer = QtWidgets.QLabel("Made by Godfred Bio | GitHub: godfredsprim | GoddAura")
        footer.setStyleSheet("color:#666; font-size:11px;")
        right.addWidget(footer)

        main_layout.addLayout(right)

        # statusbar
        self.status = self.statusBar()
        self.status.showMessage("Ready")
        self.worker = None
        self.thread = None

    # actions
    def start_session(self):
        try:
            settings["username"] = self.name_edit.text().strip() or "User"
            settings["duration"] = int(self.duration_edit.text())
            settings["goal"] = self.goal_edit.text().strip()
            save_settings(settings)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Duration must be an integer.")
            return

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.status.showMessage("Starting session...")

        # worker + thread
        self.worker = CameraWorker(settings["duration"], settings["username"], settings["goal"])
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start)
        self.worker.frame_ready.connect(self.update_frame)
        self.worker.stats_update.connect(self.update_stats)
        self.worker.session_finished.connect(self.session_finished)
        self.worker.error.connect(self.show_error)
        self.thread.start()

    def toggle_pause(self):
        if not self.worker:
            return
        # toggle
        paused = getattr(self.worker, "_paused", False)
        self.worker.pause(not paused)
        self.pause_btn.setText("▶ Resume" if not paused else "⏸ Pause")
        self.status.showMessage("Paused" if not paused else "Session running...")

    def update_frame(self, qimg):
        pix = QtGui.QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pix)

    def update_stats(self, focused_s, distracted_s, pct):
        self.status.showMessage(f"Focus {pct}% — Focused: {focused_s/60:.1f}m — Distracted: {distracted_s/60:.1f}m")

    def session_finished(self, focus_min, distract_min, pct, quote):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        QtWidgets.QMessageBox.information(self, "Session Complete",
                                          f"Focus: {focus_min} min\nDistracted: {distract_min} min\nFocus %: {pct}%\n\n{quote}")
        self.status.showMessage("Ready")
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.worker = None
        self.thread = None

    def show_error(self, text):
        QtWidgets.QMessageBox.critical(self, "Error", text)
        self.start_btn.setEnabled(True); self.pause_btn.setEnabled(False)

    def edit_quotes(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Edit Quotes")
        layout = QtWidgets.QVBoxLayout(dlg)
        combo = QtWidgets.QComboBox(); combo.addItems(["motivational", "punishing"]); layout.addWidget(combo)
        listw = QtWidgets.QListWidget(); layout.addWidget(listw)
        def refresh():
            listw.clear()
            for q in quotes.get(combo.currentText(), []):
                listw.addItem(q)
        refresh()
        btn_add = QtWidgets.QPushButton("Add"); btn_del = QtWidgets.QPushButton("Delete")
        def addq():
            text, ok = QtWidgets.QInputDialog.getText(self, "Add Quote", "Quote:")
            if ok and text.strip():
                quotes.setdefault(combo.currentText(),[]).append(text.strip()); save_settings(settings); refresh()
        def delq():
            r = listw.currentRow()
            if r >= 0:
                quotes[combo.currentText()].pop(r); refresh()
        btn_add.clicked.connect(addq); btn_del.clicked.connect(delq)
        layout.addWidget(btn_add); layout.addWidget(btn_del)
        dlg.exec()

    def export_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export CSV", "focus_log.csv", "CSV Files (*.csv)")
        if path:
            try:
                with open(LOG_FILE, "r") as src, open(path, "w", newline="") as dst:
                    dst.writelines(src.readlines())
                QtWidgets.QMessageBox.information(self, "Exported", f"Saved to {path}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Export failed: {e}")

# -------------------------
# App launch sequence (show splash then main window)
# -------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)

    # show splash
    splash = SplashWindow("FocusCamOwner.jpeg", title_text="FocusCam\nby Godfred Bio", duration_ms=5000)
    splash.show()
    splash.start()

    # main window will be shown automatically when splash closes
    # we connect splash.progress finishing to show the main window
    # but here SplashWindow closes itself; we'll show main after the splash closes by using a single-shot timer
    main_win = MainWindow()
    QtCore.QTimer.singleShot(5100, main_win.show)  # slightly after splash finishes

    sys.exit(app.exec())

if __name__ == "__main__":
    # ensure log file exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "username", "focus_min", "distract_min"])
    # warn about YOLO file when module present but file missing
    if HAVE_YOLO and not os.path.exists(YOLO_MODEL_PATH):
        print(f"Note: {YOLO_MODEL_PATH} is not present — phone detection will be disabled until you add the model file.")
    main()
