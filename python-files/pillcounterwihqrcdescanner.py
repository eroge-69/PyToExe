import sys
import cv2
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QRadioButton, QButtonGroup,
    QFileDialog, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
import numpy as np
import os
from datetime import datetime


# -------------------------------
# Background Worker for Video
# -------------------------------
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = True
        self.is_running = False  # Video processing starts off
        self.cap = None
        self.model = YOLO("best.pt")  # Make sure 'best.pt' is in the same folder
        self.names = self.model.names
        self.source = 0  # default: webcam
        self.counter = 0
        self.reset_counter_flag = False

    def set_source(self, source):
        self.source = source
        print(f"Debug: Setting source to: {self.source}")
        if isinstance(source, int):  # Webcam source
            print(f"📷 Webcam source selected: {self.source}, waiting for Start Webcam")
            self.stop_webcam()  # Ensure stopped state
        else:  # Video file
            self.restart()

    def start_webcam(self):
        if self.cap:
            self.cap.release()
            print("🛑 Released previous capture device")
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"❌ Cannot open webcam: {self.source}")
            self.cap = None
            self.is_running = False
            self.change_pixmap_signal.emit(np.zeros((600, 800, 3), dtype=np.uint8))  # Black screen
        else:
            print(f"✅ Webcam started: {self.source}")
            self.is_running = True

    def restart(self):
        if self.cap:
            self.cap.release()
            print("🛑 Released previous capture device")
        print(f"Debug: Attempting to open video file: {self.source}")
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"❌ Cannot open video source: {self.source}")
            self.cap = None
            self.is_running = False
            self.change_pixmap_signal.emit(np.zeros((600, 800, 3), dtype=np.uint8))  # Black screen
        else:
            print(f"✅ Video source opened: {self.source}")
            self.is_running = True

    def reset_counter(self):
        self.counter = 0
        self.reset_counter_flag = True

    def stop_webcam(self):
        print("Debug: Stopping webcam, current cap:", self.cap)
        if self.cap:
            self.cap.release()
            self.cap = None
            self.msleep(50)  # Brief delay to ensure release
            print("🛑 Webcam stopped and released successfully")
        self.is_running = False
        self.counter = 0
        self.change_pixmap_signal.emit(np.zeros((600, 800, 3), dtype=np.uint8))  # Black screen
        print("Debug: Black frame emitted, is_running:", self.is_running)

    def run(self):
        frame_count = 0
        while self.running:
            if not self.is_running or self.cap is None:
                self.msleep(100)
                self.change_pixmap_signal.emit(np.zeros((600, 800, 3), dtype=np.uint8))  # Black screen
                continue

            ret, frame = self.cap.read()
            if not ret:
                if isinstance(self.source, str):  # Video file
                    print("Debug: Video reached end, restarting")
                    self.restart()  # Restart video on loop
                    continue
                else:  # Webcam
                    print("⚠️ Frame not read. Reopening webcam...")
                    self.msleep(100)
                    self.start_webcam()
                    continue

            frame_count += 1
            if isinstance(self.source, str) and frame_count % 3 != 0:
                continue

            frame = cv2.resize(frame, (800, 600))
            results = self.model.track(frame, persist=True)

            current_ids = set()

            if results[0].boxes.id is not None:
                ids = results[0].boxes.id.cpu().numpy().astype(int)
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

                for track_id, box, cls_id in zip(ids, boxes, class_ids):
                    x1, y1, x2, y2 = box
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    current_ids.add(track_id)

            if not self.reset_counter_flag:
                self.counter = len(current_ids)
            else:
                self.counter = 0
                self.reset_counter_flag = False

            cv2.putText(frame, f'Count: {self.counter}', (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            self.change_pixmap_signal.emit(frame)

        if self.cap:
            self.cap.release()
            self.cap = None
            print("🛑 Video thread terminated, capture device released")

    def stop(self):
        self.running = False
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
            print("🛑 Video thread stopped, capture device released")
        self.wait()


# -------------------------------
# Main GUI Application
# -------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💊 Pill Detection Counter")
        self.resize(1200, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Arial';
            }
        """)
        self.thread = VideoThread()
        self.init_ui()
        self.video_label.setPixmap(QPixmap())  # Initial black screen

    def init_ui(self):
        layout = QHBoxLayout()

        # Left: Video Display
        self.video_label = QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #333333;
            border-radius: 10px;
            color: #ffffff;
            font-size: 16px;
        """)

        # Right Panel
        right_panel = QFrame(self)
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_panel.setStyleSheet("""
            background-color: #252525;
            border-radius: 15px;
            padding: 15px;
        """)
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout()

        # Date and Time Label
        self.datetime_label = QLabel(self.get_current_datetime())
        self.datetime_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.datetime_label.setAlignment(Qt.AlignCenter)
        self.datetime_label.setStyleSheet("""
            color: #4da8ff;
            margin: 10px;
            padding: 10px;
            background-color: #333333;
            border-radius: 8px;
        """)

        # Timer for live date and time update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second

        self.counter_label = QLabel("0")
        self.counter_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("""
            color: #ff4d4d;
            background-color: #000000;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #444444;
        """)

        # Source Selection
        self.webcam_btn = QRadioButton("📹 Webcam")
        self.video_btn = QRadioButton("📁 Video File")
        self.webcam_btn.setChecked(True)
        self.webcam_btn.setStyleSheet("""
            QRadioButton {
                color: #ffffff;
                font-size: 14px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.video_btn.setStyleSheet("""
            QRadioButton {
                color: #ffffff;
                font-size: 14px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        self.source_group = QButtonGroup()
        self.source_group.addButton(self.webcam_btn)
        self.source_group.addButton(self.video_btn)

        self.select_btn = QPushButton("📂 Select Video File")
        self.select_btn.clicked.connect(self.select_video)
        self.select_btn.setEnabled(False)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #4da8ff;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
        """)

        self.start_webcam_btn = QPushButton("▶ Start Webcam")
        self.start_webcam_btn.clicked.connect(self.start_webcam)
        self.start_webcam_btn.setEnabled(True)  # Enabled at launch
        self.start_webcam_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
           hyun
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
        """)

        self.stop_webcam_btn = QPushButton("⏹ Stop Webcam")
        self.stop_webcam_btn.clicked.connect(self.stop_webcam)
        self.stop_webcam_btn.setEnabled(False)  # Disabled at launch
        self.stop_webcam_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9500;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
        """)

        self.reset_btn = QPushButton("🔄 Reset Counter")
        self.reset_btn.clicked.connect(self.reset_counter)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
        """)

        self.quit_btn = QPushButton("❌ Quit")
        self.quit_btn.clicked.connect(self.quit_application)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
        """)

        # Add to layout
        right_layout.addWidget(self.datetime_label)
        right_layout.addWidget(self.counter_label)
        right_layout.addSpacing(20)
        right_layout.addWidget(QLabel("Input Source:"))
        right_layout.addWidget(self.webcam_btn)
        right_layout.addWidget(self.video_btn)
        right_layout.addWidget(self.select_btn)
        right_layout.addWidget(self.start_webcam_btn)
        right_layout.addWidget(self.stop_webcam_btn)
        right_layout.addWidget(self.reset_btn)
        right_layout.addWidget(self.quit_btn)
        right_layout.addStretch()

        right_panel.setLayout(right_layout)

        layout.addWidget(self.video_label, stretch=3)
        layout.addWidget(right_panel, stretch=1)
        self.setLayout(layout)

        # Connect thread
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        # Connect radio buttons
        self.webcam_btn.toggled.connect(self.on_webcam_toggled)
        self.video_btn.toggled.connect(self.on_video_toggled)

    def get_current_datetime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_datetime(self):
        self.datetime_label.setText(self.get_current_datetime())

    def on_webcam_toggled(self, checked):
        if checked:
            print("Debug: Webcam radio button toggled ON")
            self.on_source_change(is_video=False)

    def on_video_toggled(self, checked):
        if checked:
            print("Debug: Video File radio button toggled ON")
            self.on_source_change(is_video=True)

    def on_source_change(self, is_video):
        print(f"Debug: Source change triggered, is_video: {is_video}")
        self.thread.stop_webcam()  # Stop any current feed
        if is_video:
            self.select_btn.setEnabled(True)
            self.start_webcam_btn.setEnabled(False)
            self.stop_webcam_btn.setEnabled(False)
            self.select_video()
        else:
            self.select_btn.setEnabled(False)
            self.start_webcam_btn.setEnabled(True)
            self.stop_webcam_btn.setEnabled(False)
            self.thread.set_source(0)  # Set webcam source but don't start
            self.video_label.setPixmap(QPixmap())  # Ensure black screen
            self.video_label.repaint()

    def select_video(self):
        print("Debug: select_video called")
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if filename:
            print(f"📁 Selected video: {filename}")
            if os.path.exists(filename):
                self.setup_video_source(filename)
            else:
                print(f"❌ Video file does not exist: {filename}")
                QMessageBox.warning(self, "Error", "Selected video file does not exist!")
                self.video_label.setPixmap(QPixmap())  # Black screen
                self.video_label.repaint()

    def setup_video_source(self, source):
        print(f"Debug: Setting up video source: {source}")
        self.thread.set_source(source)
        self.start_webcam_btn.setEnabled(not self.thread.is_running and isinstance(source, int))
        self.stop_webcam_btn.setEnabled(self.thread.is_running and isinstance(source, int))
        self.video_label.repaint()  # Ensure GUI updates

    def start_webcam(self):
        print("Debug: start_webcam called")
        self.thread.start_webcam()
        self.start_webcam_btn.setEnabled(False)
        self.stop_webcam_btn.setEnabled(True)

    def stop_webcam(self):
        print("Debug: MainWindow.stop_webcam called")
        self.thread.stop_webcam()
        self.counter_label.setText("0")
        self.start_webcam_btn.setEnabled(True)
        self.stop_webcam_btn.setEnabled(False)
        self.video_label.setPixmap(QPixmap())  # Clear display
        self.video_label.repaint()  # Force GUI update
        print("Debug: Stop webcam triggered, black screen set")

    def reset_counter(self):
        self.thread.reset_counter()
        self.counter_label.setText("0")

    def quit_application(self):
        print("Debug: Quit button clicked")
        reply = QMessageBox.question(
            self, "Confirm Quit", "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            print("🛑 Initiating application shutdown")
            self.thread.stop_webcam()  # Ensure webcam is stopped
            self.thread.stop()  # Stop the thread
            self.timer.stop()  # Stop the timer
            self.video_label.setPixmap(QPixmap())  # Clear display
            self.video_label.repaint()  # Force GUI update
            self.close()  # Trigger closeEvent
            print("✅ Application closed successfully (exit code 0 is normal, indicating successful termination)")
        else:
            print("Debug: Quit cancelled by user")

    def update_image(self, cv_img):
        print("Debug: Updating image with shape", cv_img.shape, "sum of pixels:", cv_img.sum())
        qt_img = self.convert_cv_qt(cv_img)
        self.video_label.setPixmap(qt_img)
        self.counter_label.setText(str(self.thread.counter))

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)

    def closeEvent(self, event):
        print("🛑 Handling close event")
        self.thread.stop_webcam()  # Ensure webcam is stopped
        self.thread.stop()
        self.timer.stop()
        event.accept()
        print("✅ Application closed successfully (exit code 0 is normal, indicating successful termination)")


# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())