import sys
import cv2
import torch
import numpy as np
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6 import QtCore
from ultralytics import YOLO

class YOLOInferenceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.model = None
        self.video_path = None
        self.image_path = None

    def initUI(self):
        self.setWindowTitle("ДЕТЕКЦИЯ ОБЪЕКТОВ В/Ч 25623")
        self.setGeometry(100, 100, 640, 400)
        self.setWindowIcon(QtGui.QIcon('icon.ico'))

        layout = QVBoxLayout()
        
        self.image_label = QLabel(self)
        pixmap = QPixmap('army.png')
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.image_label)
        
        self.label = QLabel("Для запуска необходимо выбрать модель и видео-файл", self)
        layout.addWidget(self.label)

        self.modelButton = QPushButton("Выберите ONNX модель", self)
        self.modelButton.clicked.connect(self.load_model)
        layout.addWidget(self.modelButton)

        self.videoButton = QPushButton("Выберите видео", self)
        self.videoButton.clicked.connect(self.load_video)
        layout.addWidget(self.videoButton)

        self.inferButton = QPushButton("Запустить детекцию", self)
        self.inferButton.clicked.connect(self.run_inference)
        layout.addWidget(self.inferButton)
        self.inferButton.setEnabled(False)

        self.setLayout(layout)

    def load_model(self):
        model_path, _ = QFileDialog.getOpenFileName(self, "Выберите ONNX модель", "", "ONNX Files (*.onnx)")
        if model_path:
            self.model = YOLO(model_path)
            self.label.setText(f"Модель загружена: {model_path}")
            self.check_ready()

    def load_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if video_path:
            self.video_path = video_path
            self.label.setText(f"Видео загружено: {video_path}")
            self.check_ready()

    def check_ready(self):
        if self.model and (self.video_path or self.image_path):
            self.inferButton.setEnabled(True)

    def run_inference(self):
        if not self.model or not (self.video_path or self.image_path):
            return

        if self.video_path:
            output_path = "detected_model.mp4"
            cap = cv2.VideoCapture(self.video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
            if not cap.isOpened():
                self.label.setText("Ошибка при открытиии видео")
                return

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = self.model(frame)
                annotated_frame = results[0].plot()
                out.write(annotated_frame)

                cv2.imshow("YOLOv8 Interface", annotated_frame)
                cv2.resizeWindow("YOLOv8 Interface", (1280, 720))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
         

            out.release()
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YOLOInferenceApp()
    window.show()
    sys.exit(app.exec())
