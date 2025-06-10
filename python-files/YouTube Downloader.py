import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLineEdit, QLabel, QFileDialog, QComboBox, QMessageBox, QProgressBar
)
from pytube import YouTube
import threading

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube video URL")
        layout.addWidget(self.url_input)

        self.quality_box = QComboBox()
        self.quality_box.addItems(["144p", "360p", "720p", "1080p", "4k"])
        layout.addWidget(self.quality_box)

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.download_video)
        layout.addWidget(self.download_btn)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def download_video(self):
        url = self.url_input.text()
        quality = self.quality_box.currentText()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a video URL.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not folder:
            return

        threading.Thread(target=self.start_download, args=(url, quality, folder), daemon=True).start()

    def start_download(self, url, quality, folder):
        try:
            yt = YouTube(url, on_progress_callback=self.update_progress)
            streams = yt.streams.filter(progressive=True, file_extension='mp4')
            video = None

            if quality == "4k":
                video = yt.streams.filter(res="2160p", file_extension='mp4').first()
            elif quality == "1080p":
                video = streams.filter(res="1080p").first()
            elif quality == "720p":
                video = streams.filter(res="720p").first()
            elif quality == "360p":
                video = streams.filter(res="360p").first()
            elif quality == "144p":
                video = streams.filter(res="144p").first()

            if video:
                video.download(output_path=folder)
                QMessageBox.information(self, "Success", "Download completed!")
            else:
                QMessageBox.warning(self, "Error", "Requested quality not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = int(bytes_downloaded / total_size * 100)
        self.progress.setValue(percentage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
