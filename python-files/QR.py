import sys
import qrcode
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
import os

class QRGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator - Batch")
        self.setGeometry(100, 100, 500, 400)

        # Dark Theme Stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: "Segoe UI";
            }
            QTextEdit {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #5c5c5c;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ab7;
            }
        """)

        # Widgets
        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText("Enter links or messages, one per line...")
        self.text_input.setFont(QFont("Segoe UI", 12))

        self.generate_button = QPushButton("🚀 Generate QR Codes", self)
        self.generate_button.clicked.connect(self.generate_qr_codes)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_input)
        layout.addWidget(self.generate_button)
        self.setLayout(layout)

    def generate_qr_codes(self):
        data_list = self.text_input.toPlainText().strip().split('\n')
        if not data_list or data_list == ['']:
            QMessageBox.warning(self, "Error", "Please enter at least one message or link.")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Select Folder to Save QR Codes")
        if not save_dir:
            return

        for i, data in enumerate(data_list, start=1):
            qr = qrcode.make(data)

            # Sanitize filename
            safe_text = "".join(c for c in data if c.isalnum() or c in (' ', '_', '-')).strip()
            safe_text = safe_text.replace(' ', '_')[:50]
            if not safe_text:
                safe_text = f"QR_{i}"

            filename = os.path.join(save_dir, f"{safe_text}.png")

            # Avoid overwriting
            base_filename = filename
            counter = 1
            while os.path.exists(filename):
                filename = base_filename.replace(".png", f"_{counter}.png")
                counter += 1

            qr.save(filename)

        QMessageBox.information(self, "Success", f"Generated {len(data_list)} QR codes!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRGenerator()
    window.show()
    sys.exit(app.exec_())
