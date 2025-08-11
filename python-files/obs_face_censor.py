import sys
import cv2
import numpy as np
import mediapipe as mp
from PyQt6 import QtCore, QtGui, QtWidgets
import pyvirtualcam
from pyvirtualcam import PixelFormat
import time

# Settings
CAM_INDEX = 0
FPS = 20
PERSISTENCE_TIME = 0.5  # seconds

mp_face = mp.solutions.face_detection

def apply_solid(frame, bbox, color_bgr):
    x1, y1, x2, y2 = bbox
    cv2.rectangle(frame, (x1, y1), (x2, y2), color_bgr, thickness=-1)

def apply_blur(frame, bbox, ksize):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    k = max(1, (ksize // 2) * 2 + 1)
    blurred = cv2.GaussianBlur(roi, (k, k), 0)
    frame[y1:y2, x1:x2] = blurred

def apply_mosaic(frame, bbox, block_size):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    h, w = roi.shape[:2]
    bs = max(1, block_size)
    small = cv2.resize(roi, (max(1, w//bs), max(1, h//bs)), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    frame[y1:y2, x1:x2] = pixelated

def apply_edges(frame, bbox):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    edges = cv2.Canny(roi, 100, 200)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    frame[y1:y2, x1:x2] = edges_colored

def apply_invert(frame, bbox):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    inverted = cv2.bitwise_not(roi)
    frame[y1:y2, x1:x2] = inverted

def apply_mosaic_gray(frame, bbox, block_size):
    x1, y1, x2, y2 = bbox
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    bs = max(1, block_size)
    small = cv2.resize(gray, (max(1, w//bs), max(1, h//bs)), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    pixelated_bgr = cv2.cvtColor(pixelated, cv2.COLOR_GRAY2BGR)
    frame[y1:y2, x1:x2] = pixelated_bgr

def bbox_from_detection(detection, w, h, pad=0.15):
    r = detection.location_data.relative_bounding_box
    xmin = int(r.xmin * w)
    ymin = int(r.ymin * h)
    bw = int(r.width * w)
    bh = int(r.height * h)
    px = int(bw * pad)
    py = int(bh * pad)
    x1 = max(0, xmin - px)
    y1 = max(0, ymin - py)
    x2 = min(w, xmin + bw + px)
    y2 = min(h, ymin + bh + py)
    return x1, y1, x2, y2

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OBS Face Censor with Cool Modes")
        self.setGeometry(100, 100, 900, 700)

        self.cap = cv2.VideoCapture(CAM_INDEX)
        if not self.cap.isOpened():
            QtWidgets.QMessageBox.critical(self, "Error", f"Cannot open webcam index {CAM_INDEX}")
            sys.exit(1)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.last_bbox = None
        self.last_detect_time = 0
        self.paused = False

        self.mode_names = [
            "Solid Color Box",
            "Gaussian Blur",
            "Mosaic",
            "Edge Detection",
            "Invert Colors",
            "Mosaic + Grayscale"
        ]

        # Default mode
        self.mode = 0

        # UI Elements
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: black;")

        # Controls Layout
        controls_layout = QtWidgets.QFormLayout()

        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(self.mode_names)
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        controls_layout.addRow("Censor Mode:", self.mode_combo)

        # Color sliders for solid box
        self.color_b_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.color_b_slider.setRange(0, 255)
        self.color_b_slider.setValue(0)
        controls_layout.addRow("Color - Blue:", self.color_b_slider)

        self.color_g_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.color_g_slider.setRange(0, 255)
        self.color_g_slider.setValue(0)
        controls_layout.addRow("Color - Green:", self.color_g_slider)

        self.color_r_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.color_r_slider.setRange(0, 255)
        self.color_r_slider.setValue(0)
        controls_layout.addRow("Color - Red:", self.color_r_slider)

        # Blur size slider
        self.blur_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.blur_slider.setRange(1, 101)
        self.blur_slider.setValue(21)
        controls_layout.addRow("Blur Size:", self.blur_slider)

        # Mosaic block size slider
        self.mosaic_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.mosaic_slider.setRange(1, 100)
        self.mosaic_slider.setValue(20)
        controls_layout.addRow("Mosaic Block:", self.mosaic_slider)

        # Detection confidence slider
        self.det_conf_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.det_conf_slider.setRange(0, 100)
        self.det_conf_slider.setValue(60)
        controls_layout.addRow("Detection Conf %:", self.det_conf_slider)

        # Pause Button
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        controls_layout.addRow(self.pause_button)

        # Layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)

        # Face detector
        self.detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.6)

        # Timer for frame update
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / FPS))

    def change_mode(self, index):
        self.mode = index

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.setText("Resume" if self.paused else "Pause")

    def update_frame(self):
        if self.paused:
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        height, width = frame.shape[:2]

        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        det_conf = self.det_conf_slider.value() / 100.0

        results = self.detector.process(frame_rgb)

        bbox = None
        if results.detections:
            best = max(results.detections, key=lambda d: d.location_data.relative_bounding_box.width * d.location_data.relative_bounding_box.height)
            score = best.score[0] if best.score else 0.0
            if score >= det_conf:
                bbox = bbox_from_detection(best, width, height, pad=0.20)
                self.last_bbox = bbox
                self.last_detect_time = time.time()

        # Use last bbox if recent
        if bbox is None and self.last_bbox and (time.time() - self.last_detect_time) < PERSISTENCE_TIME:
            bbox = self.last_bbox

        # Apply censor based on mode
        if bbox:
            if self.mode == 0:  # Solid Color
                b = self.color_b_slider.value()
                g = self.color_g_slider.value()
                r = self.color_r_slider.value()
                apply_solid(frame, bbox, (b, g, r))
            elif self.mode == 1:  # Blur
                ksize = self.blur_slider.value()
                apply_blur(frame, bbox, ksize)
            elif self.mode == 2:  # Mosaic
                bs = self.mosaic_slider.value()
                apply_mosaic(frame, bbox, bs)
            elif self.mode == 3:  # Edge Detection
                apply_edges(frame, bbox)
            elif self.mode == 4:  # Invert colors
                apply_invert(frame, bbox)
            elif self.mode == 5:  # Mosaic + grayscale
                bs = self.mosaic_slider.value()
                apply_mosaic_gray(frame, bbox, bs)

        # Convert BGR to RGB for Qt display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)

        scaled_img = qt_image.scaled(self.video_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.video_label.setPixmap(QtGui.QPixmap.fromImage(scaled_img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
