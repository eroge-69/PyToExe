import sys
import os
import subprocess
import threading
import time
import requests
import socket
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QFrame, QProgressBar, QGroupBox, QGridLayout, QComboBox, QSpinBox, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QLinearGradient, QBrush


class StreamingThread(QThread):
    log_signal = pyqtSignal(str, str)
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)

    def __init__(self, output_dir, rtmp_url, ffmpeg_old, ffmpeg_new):
        super().__init__()
        self.output_dir = output_dir
        self.rtmp_url = rtmp_url
        self.ffmpeg_old = ffmpeg_old
        self.ffmpeg_new = ffmpeg_new
        self.running = False

    def run(self):
        self.running = True
        self.log_signal.emit('🔍 Mencari file part di folder...', 'blue')
        video_parts = []
        try:
            for file in Path(self.output_dir).glob('*-part*.mp4'):
                video_parts.append(file)
            video_parts.sort(key=lambda x: x.name)
            if not video_parts:
                self.log_signal.emit(f'❌ Tidak ditemukan file part di folder {self.output_dir}', 'red')
            return None
        except Exception as e:
            self.log_signal.emit(f'❌ Error: {str(e)}', 'red')
            return None

    def run_ffmpeg_old(self, part_file, rtmp_url):
        try:
            cmd = [self.ffmpeg_old, '-re', '-i', part_file, '-vf', 'scale=720:1280,fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-f', 'flv', rtmp_url]
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                process.wait(timeout=15)
                return process.returncode == 0
            except subprocess.TimeoutExpired:
                process.kill()
                pass
            return False
        except Exception as e:
            self.log_signal.emit(f'❌ Error ffmpeg lawas: {str(e)}', 'red')
            return False

    def run_ffmpeg_new(self, part_file, rtmp_url):
        try:
            cmd = [self.ffmpeg_new, '-re', '-i', part_file, '-vf', 'scale=720:1280,fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-f', 'flv', rtmp_url]
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                process = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
            return None
        except Exception as e:
            self.log_signal.emit(f'❌ Error ffmpeg baru: {str(e)}', 'red')

    def stop(self):
        self.running = False

class ShopeeStreamingGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.streaming_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('🛍️ Shopee Live Streaming Tool - www.reyrocks.net')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("\n            QMainWindow {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, \n                    stop:0 #1a1a2e, stop:1 #16213e);\n            }\n            QGroupBox {\n                font: bold 12px;\n                border: 2px solid #4a4a4a;\n                border-radius: 10px;\n                margin-top: 10px;\n                padding-top: 10px;\n                background: rgba(255, 255, 255, 0.1);\n                color: #ffffff;\n            }\n            QGroupBox::title {\n                subcontrol-origin: margin;\n                left: 10px;\n                padding: 0 5px 0 5px;\n                color: #00d4ff;\n            }\n            QLineEdit {\n                padding: 8px;\n                font-size: 11px;\n                border: 2px solid #4a4a4a;\n                border-radius: 8px;\n                background: rgba(255, 255, 255, 0.1);\n                color: #ffffff;\n            }\n            QLineEdit:focus {\n                border: 2px solid #00d4ff;\n            }\n            QPushButton {\n                padding: 10px 20px;\n                font: bold 12px;\n                border: none;\n                border-radius: 8px;\n                color: white;\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n                    stop:0 #667eea, stop:1 #764ba2);\n            }\n            QPushButton:hover {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n                    stop:0 #f093fb, stop:1 #f5576c);\n            }\n            QPushButton:pressed {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n                    stop:0 #4facfe, stop:1 #00f2fe);\n            }\n            QPushButton:disabled {\n                background: #4a4a4a;\n                color: #888888;\n            }\n            QTextEdit {\n                border: 2px solid #4a4a4a;\n                border-radius: 8px;\n                background: rgba(0, 0, 0, 0.8);\n                color: #ffffff;\n                font-family: 'Courier New', monospace;\n                font-size: 10px;\n            }\n            QProgressBar {\n                border: 2px solid #4a4a4a;\n                border-radius: 8px;\n                text-align: center;\n                font: bold 11px;\n                color: #ffffff;\n                background: rgba(255, 255, 255, 0.1);\n            }\n            QProgressBar::chunk {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n                    stop:0 #667eea, stop:1 #764ba2);\n                border-radius: 6px;\n            }\n            QLabel {\n                color: #ffffff;\n                font-size: 11px;\n            }\n        ")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        header = QLabel('🛍️ Shopee Live Streaming Tool')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('\n            font: bold 24px;\n            color: #00d4ff;\n            padding: 20px;\n            background: rgba(255, 255, 255, 0.1);\n            border-radius: 10px;\n            margin-bottom: 10px;\n        ')
        layout.addWidget(header)
        config_group = QGroupBox('⚙️ Konfigurasi')
        config_layout = QGridLayout(config_group)
        config_layout.addWidget(QLabel('📁 Folder Hasil Split:'), 0, 0)
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText('C:\\SplitResult')
        config_layout.addWidget(self.output_dir_input, 0, 1)
        browse_btn = QPushButton('📂 Browse')
        browse_btn.clicked.connect(self.browse_folder)
        config_layout.addWidget(browse_btn, 0, 2)
        config_layout.addWidget(QLabel('🔗 RTMP URL Shopee Live:'), 1, 0)
        self.rtmp_input = QLineEdit()
        self.rtmp_input.setPlaceholderText('rtmp://live.shopee.co.id/live/...')
        config_layout.addWidget(self.rtmp_input, 1, 1, 1, 2)
        config_layout.addWidget(QLabel('🎬 FFmpeg Lawas:'), 2, 0)
        self.ffmpeg_old_input = QLineEdit('C:\\ffmpeg\\bin\\ffmpeg.exe')
        config_layout.addWidget(self.ffmpeg_old_input, 2, 1, 1, 2)
        config_layout.addWidget(QLabel('🎬 FFmpeg Baru:'), 3, 0)
        self.ffmpeg_new_input = QLineEdit('C:\\Windows\\System32\\ffmpeg.exe')
        config_layout.addWidget(self.ffmpeg_new_input, 3, 1, 1, 2)
        layout.addWidget(config_group)
        control_group = QGroupBox('🎮 Kontrol')
        control_layout = QHBoxLayout(control_group)
        self.start_btn = QPushButton('▶️ Mulai Streaming')
        self.start_btn.clicked.connect(self.start_streaming)
        control_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton('⏹️ Stop Streaming')
        self.stop_btn.clicked.connect(self.stop_streaming)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        layout.addWidget(control_group)
        status_group = QGroupBox('📊 Status')
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel('📡 Status: Siap untuk streaming')
        self.status_label.setStyleSheet('font: bold 12px; color: #00ff00;')
        status_layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        layout.addWidget(status_group)
        log_group = QGroupBox('📋 Log Streaming')
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(250)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        self.add_log("🚀 Aplikasi siap digunakan! Masukkan konfigurasi dan klik 'Mulai Streaming'", 'green')

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Pilih Folder Hasil Split')
        if folder:
            self.output_dir_input.setText(folder)
        return None

    def start_streaming(self):
        output_dir = self.output_dir_input.text().strip()
        rtmp_url = self.rtmp_input.text().strip()
        ffmpeg_old = self.ffmpeg_old_input.text().strip()
        ffmpeg_new = self.ffmpeg_new_input.text().strip()
        if not all([output_dir, rtmp_url, ffmpeg_old, ffmpeg_new]):
            self.add_log('❌ Harap lengkapi semua field konfigurasi!', 'red')
        return None

    def stop_streaming(self):
        if self.streaming_thread:
            self.streaming_thread.stop()
            self.streaming_thread.wait()
        self.add_log('⏹️ Streaming dihentikan', 'yellow')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText('📡 Status: Siap untuk streaming')
        self.status_label.setStyleSheet('font: bold 12px; color: #00ff00;')

    def add_log(self, message, color='white'):
        color_map = {'red': '#ff6b6b', 'green': '#51cf66', 'blue': '#74c0fc', 'yellow': '#ffd43b', 'cyan': '#22d3ee', 'magenta': '#d946ef', 'white': '#ffffff'}
        color_code = color_map.get(color, '#ffffff')
        self.log_text.append(f'<span style="color: {color_code};">{message}</span>')
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def update_progress(self, current_part):
        return

    def update_status(self, status):
        self.status_label.setText(f'📡 Status: {status}')
        self.status_label.setStyleSheet('font: bold 12px; color: #00d4ff;')

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Shopee Live Streaming Tool')
    app.setOrganizationName('www.reyrocks.net')
    streaming_window = ShopeeStreamingGUI()
    streaming_window.show()

    sys.exit(app.exec_())
if __name__ == '__main__':
    main()