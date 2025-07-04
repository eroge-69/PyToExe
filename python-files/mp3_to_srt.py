import sys
import os
import whisper
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt, QUrl
from PyQt6.QtGui import QDesktopServices

# --- Worker cho việc phiên âm ---
# Lớp này xử lý tác vụ phiên âm nặng trong một luồng riêng biệt
# để không làm đóng băng giao diện người dùng.
class Worker(QObject):
    """
    Worker thực hiện việc phiên âm trong một luồng nền.
    """
    # Tín hiệu phát ra khi hoàn thành, mang theo thông báo thành công và đường dẫn tệp đầu ra
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)     # Tín hiệu phát ra khi có lỗi, mang theo thông báo lỗi
    progress = pyqtSignal(str)  # Tín hiệu phát ra để cập nhật trạng thái tiến trình

    def __init__(self, audio_path, model_name="base"):
        super().__init__()
        self.audio_path = audio_path
        self.model_name = model_name

    def run(self):
        """
        Bắt đầu quá trình phiên âm.
        """
        try:
            # 1. Tải mô hình
            self.progress.emit(f"Đang tải mô hình Whisper '{self.model_name}'...")
            model = whisper.load_model(self.model_name)
            self.progress.emit(f"Đang phiên âm tệp: {self.audio_path.split('/')[-1]}...")

            # 2. Thực hiện phiên âm
            result = model.transcribe(self.audio_path, fp16=False)
            self.progress.emit("Phiên âm hoàn tất. Đang lưu tệp SRT...")

            # 3. Lưu kết quả phiên âm ra tệp SRT
            output_srt_path = self.audio_path.rsplit('.', 1)[0] + ".srt"
            with open(output_srt_path, "w", encoding="utf-8") as srt_file:
                for i, segment in enumerate(result["segments"]):
                    start_time = segment["start"]
                    end_time = segment["end"]
                    
                    start_h = int(start_time // 3600)
                    start_m = int((start_time % 3600) // 60)
                    start_s = int(start_time % 60)
                    start_ms = int((start_time * 1000) % 1000)

                    end_h = int(end_time // 3600)
                    end_m = int((end_time % 3600) // 60)
                    end_s = int(end_time % 60)
                    end_ms = int((end_time * 1000) % 1000)

                    srt_file.write(f"{i + 1}\n")
                    srt_file.write(f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n")
                    srt_file.write(f"{segment['text'].strip()}\n\n")
            
            success_message = f"Hoàn tất! Đã lưu tệp phụ đề tại:\n{output_srt_path}"
            self.progress.emit(f"Đã lưu tệp SRT thành công tại: {output_srt_path}")
            # Phát tín hiệu hoàn thành cùng với đường dẫn tệp
            self.finished.emit(success_message, output_srt_path)

        except Exception as e:
            self.error.emit(f"Đã xảy ra lỗi: {e}")


# --- Giao diện người dùng chính ---
class TranscriberApp(QMainWindow):
    """
    Cửa sổ chính của ứng dụng phiên âm.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trình Phiên Âm Âm Thanh")
        self.setGeometry(100, 100, 500, 220)

        # Biến lưu đường dẫn tệp âm thanh và tệp đầu ra
        self.audio_file_path = None
        self.last_output_path = None

        # Thiết lập giao diện người dùng
        self.init_ui()

    def init_ui(self):
        """
        Khởi tạo các thành phần giao diện.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Layout chọn tệp
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Chưa có tệp nào được chọn.")
        self.file_label.setStyleSheet("font-style: italic; color: #555;")
        self.select_button = QPushButton("Chọn Tệp Âm Thanh")
        self.select_button.clicked.connect(self.select_audio_file)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        file_layout.addWidget(self.select_button)
        main_layout.addLayout(file_layout)

        # Layout cho các nút hành động
        button_layout = QHBoxLayout()
        self.transcribe_button = QPushButton("Bắt Đầu Phiên Âm")
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.transcribe_button.setStyleSheet("font-size: 14px; padding: 8px;")

        self.open_folder_button = QPushButton("Mở Thư Mục")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setVisible(False) # Ẩn ban đầu
        self.open_folder_button.setStyleSheet("font-size: 14px; padding: 8px;")
        
        button_layout.addWidget(self.transcribe_button)
        button_layout.addWidget(self.open_folder_button)
        main_layout.addLayout(button_layout)

        # Thanh tiến trình và nhãn trạng thái
        self.status_label = QLabel("Sẵn sàng.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)

    def select_audio_file(self):
        """
        Mở hộp thoại để người dùng chọn một tệp âm thanh.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn một tệp âm thanh", "",
            "Tệp Âm Thanh (*.wav *.mp3 *.flac);;Tất Cả Các Tệp (*.*)"
        )
        if file_path:
            self.audio_file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_label.setText(f"Đã chọn: {file_name}")
            self.file_label.setStyleSheet("font-style: normal; color: #000;")
            self.transcribe_button.setEnabled(True)
            self.open_folder_button.setVisible(False) # Ẩn nút khi chọn tệp mới

    def start_transcription(self):
        """
        Bắt đầu quá trình phiên âm trong một luồng mới.
        """
        if not self.audio_file_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một tệp âm thanh trước.")
            return

        self.set_ui_busy(True)
        self.thread = QThread()
        self.worker = Worker(self.audio_file_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_transcription_finished)
        self.worker.error.connect(self.on_transcription_error)
        self.worker.progress.connect(self.update_status)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def open_output_folder(self):
        """
        Mở thư mục chứa tệp SRT đã xuất.
        """
        if self.last_output_path:
            folder_path = os.path.dirname(self.last_output_path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def set_ui_busy(self, busy):
        """
        Cập nhật trạng thái của giao diện (bận hoặc sẵn sàng).
        """
        self.select_button.setEnabled(not busy)
        self.transcribe_button.setEnabled(not busy)
        self.progress_bar.setVisible(busy)
        
        # Luôn ẩn nút mở thư mục khi trạng thái bận thay đổi
        self.open_folder_button.setVisible(False)

        if not busy:
            self.status_label.setText("Sẵn sàng.")
            self.file_label.setText("Chưa có tệp nào được chọn.")
            self.file_label.setStyleSheet("font-style: italic; color: #555;")
            self.audio_file_path = None
            self.transcribe_button.setEnabled(False)

    def update_status(self, message):
        """
        Cập nhật nhãn trạng thái.
        """
        self.status_label.setText(message)

    def on_transcription_finished(self, message, output_path):
        """
        Xử lý khi phiên âm hoàn tất thành công.
        """
        self.last_output_path = output_path
        self.set_ui_busy(False)
        self.open_folder_button.setVisible(True) # Hiển thị nút khi thành công
        QMessageBox.information(self, "Thành công", message)

    def on_transcription_error(self, error_message):
        """
        Xử lý khi có lỗi xảy ra.
        """
        self.set_ui_busy(False)
        QMessageBox.critical(self, "Lỗi", error_message)

# # --- Chạy ứng dụng ---
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = TranscriberApp()
#     window.show()
#     sys.exit(app.exec())
import whisper
import os
print(os.path.join(os.path.dirname(whisper.__file__), 'assets'))