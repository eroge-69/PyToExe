import sys
import os
import subprocess
import json
import re
from queue import Queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QTextEdit, QMessageBox, QHBoxLayout, QComboBox,
    QProgressBar, QFrame, QSizePolicy, QDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QMovie, QIcon, QFont, QColor, QPalette


def get_download_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")


class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #5D5D5D;
                border-radius: 5px;
                text-align: center;
                background: #2D2D2D;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, 
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 3px;
            }
        """)


class AnimatedButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B6B6B, stop:1 #4A4A4A);
                border: 1px solid #5D5D5D;
                border-radius: 5px;
                color: white;
                padding: 8px 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7B7B7B, stop:1 #5A5A5A);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A4A4A, stop:1 #6B6B6B);
            }
            QPushButton:disabled {
                background: #3A3A3A;
                color: #777777;
            }
        """)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        self.animation.start()
        super().leaveEvent(event)


class MultiDownloadWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Multiple Videos")
        self.setWindowIcon(QIcon("icons/add.png"))
        self.setMinimumSize(500, 400)

        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
                color: #E0E0E0;
            }
            QTextEdit {
                background: #3D3D3D;
                border: 2px solid #5D5D5D;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        instructions = QLabel("Enter one video URL per line:")
        instructions.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(instructions)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...\nhttps://vimeo.com/...\nhttps://...")
        layout.addWidget(self.url_input)

        button_layout = QHBoxLayout()

        self.cancel_button = AnimatedButton("Cancel", "icons/close.png")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.download_button = AnimatedButton("Download All", "icons/download.png")
        self.download_button.clicked.connect(self.accept)
        button_layout.addWidget(self.download_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_urls(self):
        text = self.url_input.toPlainText().strip()
        return [url.strip() for url in text.split('\n') if url.strip()]


class FormatFetcherThread(QThread):
    formatsFetched = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            command = ["yt-dlp", "-J", self.url, "--no-warnings"]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                self.error.emit("❌ Failed to fetch formats.")
                return

            data = json.loads(result.stdout)
            formats = []
            for fmt in data.get("formats", []):
                if fmt.get("vcodec") != "none":
                    height = fmt.get("height") or 0
                    resolution = f"{height}p" if height else fmt.get("format_note") or "unknown"
                    formats.append(resolution)

            def res_key(r):
                try:
                    return int(r.replace("p", ""))
                except:
                    return 0

            unique_res = sorted(set(formats), key=res_key, reverse=True)

            if not unique_res:
                unique_res = ["best"]

            self.formatsFetched.emit(unique_res)
        except Exception as e:
            self.error.emit(str(e))


class VideoDownloadThread(QThread):
    output = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, output_folder, quality, file_format):
        super().__init__()
        self.url = url
        self.output_folder = output_folder
        self.quality = quality
        self.file_format = file_format
        self._paused = False
        self._stop_flag = False
        self._progress = 0

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        try:
            if self.quality == "best":
                format_str = "bestvideo+bestaudio/best"
            elif self.quality.replace("p", "").isdigit():
                height = self.quality.replace("p", "")
                format_str = f"bestvideo[height<={height}]+bestaudio/best"
            else:
                format_str = "bestvideo+bestaudio/best"

            command = [
                "yt-dlp",
                "--newline",
                "-f", format_str,
                "--merge-output-format", self.file_format,
                "-o", os.path.join(self.output_folder, "%(title)s.%(ext)s"),
                "--no-warnings",
                "--progress",
                "--no-part",
                "--embed-thumbnail",
                "--console-title",
                self.url
            ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, bufsize=1, universal_newlines=True)

            while True:
                if self._stop_flag:
                    process.terminate()
                    break
                if self._paused:
                    QThread.msleep(100)
                    continue

                line = process.stdout.readline()
                if not line:
                    break

                progress_match = re.search(r'(\d+\.\d+)%|(\d+)%', line)
                if progress_match:
                    progress = progress_match.group(1) or progress_match.group(2)
                    self._progress = int(float(progress))
                    self.progress.emit(self._progress)

                self.output.emit(line.strip())

            process.wait()
            if process.returncode == 0:
                self.progress.emit(100)
                self.finished.emit(f"✅ Download completed! Saved as: {self.get_output_filename()}")
            else:
                self.error.emit("❌ Download failed. Check log for details.")
        except Exception as e:
            self.error.emit(f"Error: {e}")

    def get_output_filename(self):
        base = os.path.basename(self.url)
        safe_title = "".join(c for c in base if c.isalnum() or c in " -_")
        return os.path.join(self.output_folder, f"{safe_title}.{self.file_format}")


class ModernVideoDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nation YouTube Video Downloader")
        self.setWindowIcon(QIcon("icons/app_icon.ico"))
        self.setGeometry(100, 100, 680, 580)
        self.setMinimumSize(600, 500)

        # Set modern dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #E0E0E0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background: #3D3D3D;
                border: 2px solid #5D5D5D;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #4CAF50;
            }
            QComboBox {
                background: #3D3D3D;
                border: 2px solid #5D5D5D;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox QAbstractItemView {
                background: #3D3D3D;
                selection-background-color: #4CAF50;
            }
            QTextEdit {
                background: #3D3D3D;
                border: 2px solid #5D5D5D;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QLabel {
                font-size: 14px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header = QLabel("Nation YouTube Video Downloader")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                padding-bottom: 10px;
                border-bottom: 2px solid #4CAF50;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # URL Input
        url_group = QVBoxLayout()
        url_group.setSpacing(5)
        url_label = QLabel("Video URL:")
        url_label.setStyleSheet("font-weight: bold;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube or other video URL here...")
        url_group.addWidget(url_label)
        url_group.addWidget(self.url_input)
        self.url_input.textChanged.connect(self.on_url_changed)
        main_layout.addLayout(url_group)

        # Settings Frame
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.StyledPanel)
        settings_frame.setStyleSheet("""
            QFrame {
                background: #3D3D3D;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(20)

        # Quality Selection
        quality_group = QVBoxLayout()
        quality_label = QLabel("Quality:")
        quality_label.setStyleSheet("font-weight: bold;")
        self.quality_selector = QComboBox()
        self.quality_selector.addItems(["best", "1080p", "720p", "480p"])
        self.quality_selector.setStyleSheet("""
            QComboBox {
                min-width: 120px;
            }
        """)
        quality_group.addWidget(quality_label)
        quality_group.addWidget(self.quality_selector)
        settings_layout.addLayout(quality_group)

        # Format Selection
        format_group = QVBoxLayout()
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-weight: bold;")
        self.format_selector = QComboBox()
        self.format_selector.addItems(["mp4", "mkv", "webm"])
        format_group.addWidget(format_label)
        format_group.addWidget(self.format_selector)
        settings_layout.addLayout(format_group)

        settings_frame.setLayout(settings_layout)
        main_layout.addWidget(settings_frame)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.download_button = AnimatedButton("Download", "icons/download.png")
        self.download_button.clicked.connect(self.queue_download)
        button_layout.addWidget(self.download_button)

        self.new_download_button = AnimatedButton("Add URLs", "icons/add.png")
        self.new_download_button.clicked.connect(self.show_multi_download_window)
        button_layout.addWidget(self.new_download_button)

        self.pause_resume_button = AnimatedButton("Pause", "icons/pause.png")
        self.pause_resume_button.setEnabled(False)
        self.pause_resume_button.clicked.connect(self.toggle_pause_resume)
        button_layout.addWidget(self.pause_resume_button)

        self.cancel_button = AnimatedButton("Cancel", "icons/close.png")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Progress Bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setFormat("%p% - Ready")
        main_layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #AAAAAA;
            }
        """)
        main_layout.addWidget(self.status_label)

        # Loading Animation
        self.gif_label = QLabel()
        self.gif_label.setFixedSize(40, 40)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("icons/loading.gif")
        self.movie.setScaledSize(QSize(40, 40))
        self.gif_label.setMovie(self.movie)
        self.gif_label.hide()
        main_layout.addWidget(self.gif_label, 0, Qt.AlignCenter)

        # Output Log
        log_group = QVBoxLayout()
        log_group.setSpacing(5)
        log_label = QLabel("Download Log:")
        log_label.setStyleSheet("font-weight: bold;")
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        log_group.addWidget(log_label)
        log_group.addWidget(self.output_log)
        main_layout.addLayout(log_group)

        self.setLayout(main_layout)

        # Initialize
        self.queue = Queue()
        self.downloading = False
        self.current_thread = None
        self.paused = False

    def show_multi_download_window(self):
        dialog = MultiDownloadWindow(self)
        if dialog.exec_() == QDialog.Accepted:
            urls = dialog.get_urls()
            if urls:
                quality = self.quality_selector.currentText()
                file_format = self.format_selector.currentText()

                for url in urls:
                    self.queue.put((url, quality, file_format))

                if not self.downloading:
                    self.start_next_download()

    def on_url_changed(self):
        url = self.url_input.text().strip()
        if url:
            self.quality_selector.clear()
            self.quality_selector.addItem("Loading...")
            self.fetcher = FormatFetcherThread(url)
            self.fetcher.formatsFetched.connect(self.populate_formats)
            self.fetcher.error.connect(self.populate_default_formats)
            self.fetcher.start()

    def populate_formats(self, formats):
        self.quality_selector.clear()
        self.quality_selector.addItems(formats or ["best"])

    def populate_default_formats(self, _):
        self.quality_selector.clear()
        self.quality_selector.addItems(["best", "1080p", "720p", "480p"])

    def queue_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_error_message("Input Error", "Please enter a valid video URL.")
            return

        quality = self.quality_selector.currentText()
        file_format = self.format_selector.currentText()
        self.queue.put((url, quality, file_format))

        if not self.downloading:
            self.start_next_download()

        self.status_label.setText("Status: Queued")

    def start_next_download(self):
        if self.queue.empty():
            self.downloading = False
            self.status_label.setText("Status: Ready")
            self.pause_resume_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.progress_bar.setFormat("%p% - Ready")
            return

        self.downloading = True
        url, quality, file_format = self.queue.get()

        self.output_log.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - Downloading...")
        self.status_label.setText(f"Status: Downloading ({quality})")
        self.gif_label.show()
        self.movie.start()
        self.pause_resume_button.setText("Pause")
        self.pause_resume_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.paused = False

        output_folder = get_download_folder()
        self.current_thread = VideoDownloadThread(url, output_folder, quality, file_format)
        self.current_thread.output.connect(self.output_log.append)
        self.current_thread.progress.connect(self.update_progress)
        self.current_thread.finished.connect(self.on_finished)
        self.current_thread.error.connect(self.on_error)
        self.current_thread.start()

    def cancel_download(self):
        if self.current_thread and self.current_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Cancel Download',
                'Are you sure you want to cancel the current download?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.current_thread.stop()
                self.status_label.setText("Status: Cancelled")
                self.progress_bar.setFormat("%p% - Cancelled")
                self.output_log.append("⚠️ Download cancelled by user")
                self.current_thread = None
                QTimer.singleShot(100, self.start_next_download)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_bar.setFormat("%p% - Merging streams...")

    def toggle_pause_resume(self):
        if not self.current_thread or not self.current_thread.isRunning():
            return

        if self.paused:
            self.current_thread.resume()
            self.pause_resume_button.setText("Pause")
            self.status_label.setText(f"Status: Downloading ({self.quality_selector.currentText()})")
            self.progress_bar.setFormat("%p% - Downloading...")
            self.paused = False
        else:
            self.current_thread.pause()
            self.pause_resume_button.setText("Resume")
            self.status_label.setText(f"Status: Paused ({self.quality_selector.currentText()})")
            self.progress_bar.setFormat("%p% - Paused")
            self.paused = True

    def on_finished(self, message):
        self.status_label.setText("Status: Completed")
        self.gif_label.hide()
        self.movie.stop()
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("%p% - Completed")
        self.output_log.append(message)
        self.current_thread = None
        self.cancel_button.setEnabled(False)
        self.show_success_message("Download Complete", message)
        QTimer.singleShot(100, self.start_next_download)

    def on_error(self, message):
        self.status_label.setText("Status: Error")
        self.gif_label.hide()
        self.movie.stop()
        self.output_log.append(message)
        self.current_thread = None
        self.cancel_button.setEnabled(False)
        self.show_error_message("Download Error", message)
        QTimer.singleShot(100, self.start_next_download)

    def show_success_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #E0E0E0;
            }
        """)
        msg.exec_()

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #E0E0E0;
            }
        """)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and set palette for dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(65, 65, 65))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(76, 175, 80))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = ModernVideoDownloader()
    window.show()
    sys.exit(app.exec_())