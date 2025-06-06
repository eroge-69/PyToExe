import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout
from moviepy.editor import VideoFileClip, AudioFileClip

class VideoAudioMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Видеоро бо овози нав якҷо кун")
        self.setGeometry(300, 300, 400, 200)

        self.video_path = ""
        self.audio_path = ""

        layout = QVBoxLayout()

        self.label = QLabel("Видео ва овозро интихоб кунед")
        layout.addWidget(self.label)

        self.video_btn = QPushButton("Интихоби Видео")
        self.video_btn.clicked.connect(self.select_video)
        layout.addWidget(self.video_btn)

        self.audio_btn = QPushButton("Интихоби Овоз")
        self.audio_btn.clicked.connect(self.select_audio)
        layout.addWidget(self.audio_btn)

        self.process_btn = QPushButton("Сохтани Видео бо овози нав")
        self.process_btn.clicked.connect(self.merge_audio_video)
        layout.addWidget(self.process_btn)

        self.setLayout(layout)

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Интихоби Видео", "", "Видео (*.mp4 *.mov)")
        if path:
            self.video_path = path
            self.label.setText(f"Видео: {path}")

    def select_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Интихоби Овоз", "", "Аудио (*.mp3 *.wav)")
        if path:
            self.audio_path = path
            self.label.setText(f"Овоз: {path}")

    def merge_audio_video(self):
        if self.video_path and self.audio_path:
            video = VideoFileClip(self.video_path).without_audio()
            audio = AudioFileClip(self.audio_path)
            final = video.set_audio(audio)
            final.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac")
            self.label.setText("✅ Видео бо овози нав сабт шуд: output_video.mp4")
        else:
            self.label.setText("❌ Илтимос, ҳам видео ва ҳам овозро интихоб кунед!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoAudioMerger()
    window.show()
    sys.exit(app.exec_())
