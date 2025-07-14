import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QListWidget, QMessageBox, QLineEdit, QProgressBar, QListWidgetItem
)
from PyQt5.QtCore import Qt, QUrl

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.files = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                self.files.append(path)
                self.addItem(f"{os.path.basename(path)} - {size_mb:.2f} MB")

    def get_file_paths(self):
        return self.files

    def clear_files(self):
        self.files = []
        self.clear()


class FilePushApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Push Files to Android SD Card")
        self.setGeometry(200, 200, 600, 500)
        self.files = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("ADB Status: Unknown")

        self.label = QLabel("Selected Files (drag & drop supported):")
        self.file_list = DraggableListWidget()

        self.select_button = QPushButton("Choose Files")
        self.select_button.clicked.connect(self.choose_files)

        self.target_label = QLabel("Target path on Android:")
        self.target_path = QLineEdit("/sdcard/Download/")
        self.target_path.setPlaceholderText("/sdcard/Download/")

        self.push_button = QPushButton("Push to Android")
        self.push_button.clicked.connect(self.push_files)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)

        layout.addWidget(self.status_label)
        layout.addWidget(self.label)
        layout.addWidget(self.file_list)
        layout.addWidget(self.select_button)
        layout.addWidget(self.target_label)
        layout.addWidget(self.target_path)
        layout.addWidget(self.push_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.check_adb_connection()

    def choose_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*.*)")
        if files:
            for f in files:
                if f not in self.file_list.files:
                    size_mb = os.path.getsize(f) / (1024 * 1024)
                    self.file_list.files.append(f)
                    self.file_list.addItem(f"{os.path.basename(f)} - {size_mb:.2f} MB")

    def check_adb_connection(self):
        try:
            result = subprocess.run(["adb", "get-state"], capture_output=True, text=True)
            if "device" in result.stdout.strip():
                self.status_label.setText("ADB Status: Connected")
                return True
            else:
                self.status_label.setText("ADB Status: No device found")
                return False
        except Exception as e:
            self.status_label.setText(f"ADB Status: Error - {e}")
            return False

    def push_files(self):
        if not self.check_adb_connection():
            QMessageBox.critical(self, "ADB Error", "No connected Android device.")
            return

        files = self.file_list.get_file_paths()
        if not files:
            QMessageBox.warning(self, "No Files", "Please select or drop files first.")
            return

        target = self.target_path.text().strip()
        if not target:
            QMessageBox.warning(self, "Invalid Path", "Please enter a valid target path.")
            return

        try:
            subprocess.run(["adb", "shell", "mkdir", "-p", target], check=True)

            total_files = len(files)
            for idx, file_path in enumerate(files):
                if os.path.isfile(file_path):
                    self.status_label.setText(f"Pushing: {os.path.basename(file_path)}")
                    subprocess.run(["adb", "push", file_path, target], check=True)
                    self.progress_bar.setValue(int((idx + 1) / total_files * 100))

            self.status_label.setText("Push complete.")
            QMessageBox.information(self, "Success", "All files pushed successfully.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "ADB Error", f"Failed to push file:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilePushApp()
    window.show()
    sys.exit(app.exec_())
