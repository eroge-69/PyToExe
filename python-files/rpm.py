Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import sys
import cv2
import numpy as np
import pyautogui
import datetime
import time
import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# ---------- Screen Recorder Thread ----------
class ScreenRecorder(QThread):
    rpm_updated = pyqtSignal(float)
    finished = pyqtSignal()

    def run(self):
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        filename = datetime.datetime.now().strftime("Recording_%Y-%m-%d_%H-%M-%S.avi")
        out = cv2.VideoWriter(filename, fourcc, 20.0, screen_size)

        # RPM Tracker variables
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        revolutions = 0
        prev_angle = None
        start_time = time.time()
        center_defined = False
        center = (screen_size[0]//2, screen_size[1]//2)

        self.running = True
        while self.running:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ---------- RPM Tracker ----------
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_red, upper_red)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                if radius > 5:
                    if not center_defined:
                        center = (int(x), int(y))
                        center_defined = True
                    angle = math.degrees(math.atan2(y - center[1], x - center[0]))
                    if prev_angle is not None:
                        if prev_angle < -150 and angle > 150:
                            revolutions += 1
                    prev_angle = angle

            # RPM Calculation
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                rpm = (revolutions / elapsed_time) * 60
                self.rpm_updated.emit(rpm)

            out.write(frame)

        out.release()
        self.finished.emit()

    def stop(self):
        self.running = False

# ---------- Main GUI ----------
class RecorderApp(QWidget):
    def init(self):
        super().init()
        self.setWindowTitle("Screen Recorder + RPM Tracker")
        self.recorder = ScreenRecorder()

...         self.start_button = QPushButton("Start Recording")
...         self.start_button.clicked.connect(self.start_recording)
... 
...         self.stop_button = QPushButton("Stop Recording")
...         self.stop_button.clicked.connect(self.stop_recording)
...         self.stop_button.setEnabled(False)
... 
...         self.rpm_label = QLabel("RPM: 0.00")
...         self.rpm_label.setFont(QFont("Arial", 14))
...         self.rpm_label.setAlignment(Qt.AlignCenter)
... 
...         layout = QVBoxLayout()
...         layout.addWidget(self.start_button)
...         layout.addWidget(self.stop_button)
...         layout.addWidget(self.rpm_label)
... 
...         self.setLayout(layout)
...         self.recorder.rpm_updated.connect(self.update_rpm)
... 
...     def start_recording(self):
...         self.recorder.start()
...         self.start_button.setEnabled(False)
...         self.stop_button.setEnabled(True)
... 
...     def stop_recording(self):
...         self.recorder.stop()
...         self.recorder.wait()
...         self.start_button.setEnabled(True)
...         self.stop_button.setEnabled(False)
... 
...     def update_rpm(self, rpm):
...         self.rpm_label.setText(f"RPM: {rpm:.2f}")
... 
... # ---------- Main Function ----------
... if name == "main":
...     app = QApplication(sys.argv)
...     window = RecorderApp()
...     window.resize(300, 150)
...     window.show()
