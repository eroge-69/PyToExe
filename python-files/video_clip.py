import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QListWidget
)

class VideoFrameExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频切帧工具")
        self.resize(400, 300)
        self.video_files = []
        self.output_dir = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("请选择视频文件和保存文件夹")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_select_video = QPushButton("选择视频文件")
        btn_select_video.clicked.connect(self.select_video)
        layout.addWidget(btn_select_video)

        btn_select_output = QPushButton("选择保存文件夹")
        btn_select_output.clicked.connect(self.select_output)
        layout.addWidget(btn_select_output)

        btn_start = QPushButton("开始切帧")
        btn_start.clicked.connect(self.start_extract)
        layout.addWidget(btn_start)

        self.setLayout(layout)

    def select_video(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv)")
        if files:
            self.video_files = files
            self.list_widget.clear()
            self.list_widget.addItems(files)

    def select_output(self):
        dir_ = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if dir_:
            self.output_dir = dir_
            self.label.setText(f"保存文件夹: {dir_}")

    def start_extract(self):
        if not self.video_files or not self.output_dir:
            self.label.setText("请先选择视频和保存文件夹")
            return
        for video_path in self.video_files:
            video_name = os.path.basename(video_path)
            video_output_dir = os.path.join(self.output_dir, os.path.splitext(video_name)[0])
            os.makedirs(video_output_dir, exist_ok=True)
            cap = cv2.VideoCapture(video_path)
            frame_idx = 0
            saved_idx = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 25
            frame_interval = int(round(fps / 10))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % frame_interval == 0:
                    img_path = os.path.join(video_output_dir, f'{saved_idx:05d}.jpg')
                    cv2.imwrite(img_path, frame)
                    saved_idx += 1
                frame_idx += 1
            cap.release()
            self.label.setText(f"{video_name} 转换完成，共 {saved_idx} 帧")
        self.label.setText("全部视频转换完成。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoFrameExtractor()
    window.show()
    sys.exit(app.exec_())
