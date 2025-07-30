import sys
import os
import subprocess
import requests
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# Worker class for background processing
class MediaProcessor(QThread):
    finished = pyqtSignal(str, bool)
    progress_update = pyqtSignal(str)
    overall_progress_update = pyqtSignal(int)
    current_download_progress = pyqtSignal(str, int)

    def __init__(self, video_url, audio_url, output_dir, output_filename):
        super().__init__()
        self.video_url = video_url
        self.audio_url = audio_url
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.temp_video_path = None
        self.temp_audio_path = None
        self.is_canceled = False

    def cancel(self):
        self.is_canceled = True
        self.progress_update.emit("Canceling operation...")

    def run(self):
        try:
            self.progress_update.emit("Starting processing...")
            self.overall_progress_update.emit(0)

            # Download video file
            if self.is_canceled: raise Exception("Operation canceled.")
            self.progress_update.emit("Downloading video file...")
            video_file_name = os.path.basename(self.video_url.split('?')[0]) or "deskshare_video.webm"
            self.temp_video_path = os.path.join(self.output_dir, f"temp_{video_file_name}")
            self._download_file(self.video_url, self.temp_video_path, "video", 0, 45)
            self.overall_progress_update.emit(45)

            # Download audio file
            if self.is_canceled: raise Exception("Operation canceled.")
            self.progress_update.emit("Downloading audio file...")
            audio_file_name = os.path.basename(self.audio_url.split('?')[0]) or "webcams_audio.webm"
            self.temp_audio_path = os.path.join(self.output_dir, f"temp_{audio_file_name}")
            self._download_file(self.audio_url, self.temp_audio_path, "audio", 45, 85)
            self.overall_progress_update.emit(85)

            # Merge video and audio
            if self.is_canceled: raise Exception("Operation canceled.")
            self.progress_update.emit("Merging files...")
            self.overall_progress_update.emit(88)

            output_file_name = self.output_filename if self.output_filename else f"merged_{os.path.splitext(os.path.basename(self.video_url.split('?')[0]))[0] or 'output'}.mp4"
            if not output_file_name.lower().endswith('.mp4'):
                output_file_name += '.mp4'
            output_path = os.path.join(self.output_dir, output_file_name)

            counter = 1
            original_output_path = output_path
            while os.path.exists(output_path):
                name_without_ext = os.path.splitext(original_output_path)[0]
                output_path = f"{name_without_ext}_{counter}.mp4"
                counter += 1

            cmd_merge = [
                "ffmpeg", "-i", self.temp_video_path, "-i", self.temp_audio_path,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-strict", "experimental",
                "-map", "0:v:0", "-map", "1:a:0", output_path
            ]
            subprocess.run(cmd_merge, check=True, capture_output=True, text=True)
            self.progress_update.emit("Merging completed.")
            self.overall_progress_update.emit(98)

            # Clean up
            self.progress_update.emit("Cleaning up temporary files...")
            self._cleanup_temp_files()
            self.overall_progress_update.emit(100)
            self.finished.emit(output_path, True)

        except requests.exceptions.RequestException as e:
            self.finished.emit(f"Download error: Network issue or invalid URL. ({e})", False)
        except subprocess.CalledProcessError as e:
            self.finished.emit(f"FFmpeg error (code {e.returncode}): {e.stderr.strip()}", False)
        except Exception as e:
            self.finished.emit(f"General error: {str(e)}", False)
        finally:
            self._cleanup_temp_files()

    def _download_file(self, url, dest_path, file_type, start_progress, end_progress):
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise Exception(f"Error: {file_type} download timed out.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error downloading {file_type}: {e}")

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        if os.path.exists(dest_path):
            current_size = os.path.getsize(dest_path)
            if total_size > 0 and current_size < total_size:
                downloaded_size = current_size
                headers = {'Range': f'bytes={downloaded_size}-'}
                response = requests.get(url, stream=True, headers=headers, timeout=60)
                response.raise_for_status()
            elif total_size > 0 and current_size == total_size:
                self.current_download_progress.emit(file_type, 100)
                self.overall_progress_update.emit(end_progress)
                return

        mode = 'ab' if downloaded_size > 0 else 'wb'
        with open(dest_path, mode) as f:
            for chunk in response.iter_content(chunk_size=8192):
                if self.is_canceled:
                    raise Exception("Download canceled.")
                f.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:
                    percent = int((downloaded_size / total_size) * 100)
                    self.current_download_progress.emit(file_type, percent)
                    overall_percent = start_progress + (percent / 100) * (end_progress - start_progress)
                    self.overall_progress_update.emit(int(overall_percent))

        self.progress_update.emit(f"{file_type} download completed.")

    def _cleanup_temp_files(self):
        if self.temp_video_path and os.path.exists(self.temp_video_path):
            os.remove(self.temp_video_path)
        if self.temp_audio_path and os.path.exists(self.temp_audio_path):
            os.remove(self.temp_audio_path)

# Main GUI class
class MediaDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.output_directory = os.path.expanduser("~/Downloads")
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        self.processor_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video & Audio Merger')
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(500, 400)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Input section
        self.video_url_input = QLineEdit()
        self.video_url_input.setPlaceholderText("Enter video URL (e.g., *.webm, *.mp4)")
        self.video_url_input.setMinimumHeight(35)
        layout.addWidget(QLabel("Video URL:"))
        layout.addWidget(self.video_url_input)

        self.audio_url_input = QLineEdit()
        self.audio_url_input.setPlaceholderText("Enter audio URL (e.g., *.webm, *.m4a)")
        self.audio_url_input.setMinimumHeight(35)
        layout.addWidget(QLabel("Audio URL:"))
        layout.addWidget(self.audio_url_input)

        # Output settings
        output_layout = QHBoxLayout()
        self.output_path_display = QLineEdit(self.output_directory)
        self.output_path_display.setReadOnly(True)
        self.output_path_display.setMinimumHeight(35)
        output_layout.addWidget(self.output_path_display)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output_directory)
        browse_button.setMinimumHeight(35)
        output_layout.addWidget(browse_button)
        layout.addWidget(QLabel("Output Directory:"))
        layout.addLayout(output_layout)

        self.output_filename_input = QLineEdit()
        self.output_filename_input.setPlaceholderText("Output filename (optional, e.g., MyVideo.mp4)")
        self.output_filename_input.setMinimumHeight(35)
        layout.addWidget(QLabel("Output Filename:"))
        layout.addWidget(self.output_filename_input)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setMinimumHeight(40)
        button_layout.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setMinimumHeight(40)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Progress and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready to start...")
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to start...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit[readOnly="true"] {
                background-color: #e0e0e0;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #007BFF;
                border-radius: 3px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)

    def browse_output_directory(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_directory)
        if dir_name:
            self.output_directory = dir_name
            self.output_path_display.setText(self.output_directory)

    def start_processing(self):
        video_url = self.video_url_input.text().strip()
        audio_url = self.audio_url_input.text().strip()
        output_filename = self.output_filename_input.text().strip()

        if not video_url or not audio_url:
            QMessageBox.warning(self, "Error", "Please enter both video and audio URLs.")
            return

        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Starting...")
        self.status_label.setText("Preparing to download...")

        self.processor_thread = MediaProcessor(video_url, audio_url, self.output_directory, output_filename)
        self.processor_thread.finished.connect(self.processing_finished)
        self.processor_thread.progress_update.connect(self.status_label.setText)
        self.processor_thread.overall_progress_update.connect(self.progress_bar.setValue)
        self.processor_thread.start()

    def cancel_processing(self):
        if self.processor_thread and self.processor_thread.isRunning():
            reply = QMessageBox.question(self, 'Cancel Operation',
                                        "Are you sure you want to cancel?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.processor_thread.cancel()
                self.status_label.setText("Canceling operation...")
                self.progress_bar.setFormat("Canceling...")

    def processing_finished(self, result_message, success):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if success:
            QMessageBox.information(self, "Success", f"Operation completed!\nVideo saved at: {result_message}")
            self.status_label.setText("Operation completed.")
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Completed!")
            try:
                subprocess.Popen(['xdg-open', os.path.dirname(result_message)])
            except Exception as e:
                print(f"Error opening folder: {e}")
        else:
            QMessageBox.critical(self, "Error", f"Processing error: {result_message}\n\nPlease check URLs, FFmpeg installation, and internet connection.")
            self.status_label.setText("Error occurred.")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Error!")
        self.processor_thread = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MediaDownloaderApp()
    ex.show()
    sys.exit(app.exec_())