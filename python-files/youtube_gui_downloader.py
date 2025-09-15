import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QTextEdit,
    QLabel, QComboBox, QFileDialog, QProgressBar, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL


class DownloaderThread(QThread):
    progress_signal = pyqtSignal(int)
    output_signal = pyqtSignal(str)

    def __init__(self, url, format_choice, output_dir, audio_only):
        super().__init__()
        self.url = url
        self.format_choice = format_choice
        self.output_dir = output_dir
        self.audio_only = audio_only

    def run(self):
        if self.audio_only:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.hook],
                'quiet': True,
                'noprogress': True,
                'writethumbnail': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.format_choice,
                        'preferredquality': '192',
                    },
                    {
                        'key': 'FFmpegMetadata',
                    },
                    {
                        'key': 'EmbedThumbnail',
                        'already_have_thumbnail': False
                    }
                ],
            }
        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio',
                'merge_output_format': self.format_choice,
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.hook],
                'quiet': True,
                'noprogress': True,
                'writethumbnail': False,
            }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                self.output_signal.emit("🔄 Download started...")
                ydl.download([self.url])
                self.output_signal.emit("✅ Download finished.")
        except Exception as e:
            self.output_signal.emit(f"❌ Error: {e}")

    def hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0.0%').strip().replace('%', '')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = d.get('filename', 'Unknown file')

            try:
                self.progress_signal.emit(int(float(percent)))
            except ValueError:
                self.progress_signal.emit(0)

            self.output_signal.emit(
                f"⬇ Downloading: {percent}% | Speed: {speed} | ETA: {eta} | File: {os.path.basename(filename)}"
            )

        elif d['status'] == 'finished':
            self.progress_signal.emit(100)
            self.output_signal.emit("🎉 Download complete. Processing file...")


class YouTubeDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mark's Bang Tidy YouTube Downloader")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here")

        self.audio_only_checkbox = QCheckBox("Download Audio Only")
        self.audio_only_checkbox.stateChanged.connect(self.toggle_format_options)

        self.format_selector = QComboBox()
        self.update_format_options(audio_only=False)

        self.folder_button = QPushButton("Choose Output Folder")
        self.folder_button.clicked.connect(self.choose_folder)
        self.output_dir = os.getcwd()

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("YouTube URL:"))
        layout.addWidget(self.url_input)

        layout.addWidget(self.audio_only_checkbox)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.format_selector)
        layout.addLayout(format_layout)

        layout.addWidget(self.folder_button)
        layout.addWidget(self.download_button)
        layout.addWidget(QLabel("Download Progress:"))
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Log Output:"))
        layout.addWidget(self.output_log)

        self.setLayout(layout)

    def toggle_format_options(self):
        self.update_format_options(audio_only=self.audio_only_checkbox.isChecked())

    def update_format_options(self, audio_only: bool):
        self.format_selector.clear()
        if audio_only:
            self.format_selector.addItems(["mp3", "aac", "flac", "opus"])
        else:
            self.format_selector.addItems(["mp4", "mkv", "webm"])

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
            self.output_log.append(f"📁 Output folder set to: {folder}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.output_log.append("❌ Please enter a YouTube URL.")
            return

        format_choice = self.format_selector.currentText()
        audio_only = self.audio_only_checkbox.isChecked()

        self.output_log.append(f"▶ Starting download in {format_choice.upper()} format ({'Audio Only' if audio_only else 'Video'})...")
        self.progress_bar.setValue(0)

        self.thread = DownloaderThread(url, format_choice, self.output_dir, audio_only)
        self.thread.output_signal.connect(self.output_log.append)
        self.thread.progress_signal.connect(self.progress_bar.setValue)
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloaderGUI()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())

