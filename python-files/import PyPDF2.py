import sys
import os
import pickle
from pathlib import Path
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPainter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import win32com.client as win32

# --------------------------
# CONFIG
# --------------------------
APP_NAME = "Student Application"
TEMP_FILE = Path.home() / "AppData" / "Local" / "StudentApp" / "temp.dat"
TEMP_FILE.parent.mkdir(parents=True, exist_ok=True)
VIDEO_PATH = getattr(sys, '_MEIPASS', '.') + "/background.mp4"  # For PyInstaller

DEFAULT_DATA = {
    "page1": {"name": "", "email": "", "phone": ""},
    "page2": {"address_line1": "", "address_line2": "", "city": "", "state": "", "zip": ""},
    "page3": {"school": "", "grade": "", "dob": ""},
    "page4": {"guardian_name": "", "guardian_phone": "", "notes": ""},
}

# --------------------------
# PDF & EMAIL (Same as before)
# --------------------------
def generate_pdf(data, save_path):
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("Student Application Report", styles['Title']))
        story.append(Spacer(1, 12))
        for i in range(1, 5):
            page_key = f"page{i}"
            story.append(Paragraph(f"--- Page {i} ---", styles['Heading2']))
            for key, value in data[page_key].items():
                story.append(Paragraph(f"{key.replace('_', ' ').title()}: {value}", styles['Normal']))
            story.append(Spacer(1, 12))
        doc.build(story)
        return True
    except Exception as e:
        QMessageBox.critical(None, "PDF Error", f"Failed to generate PDF: {e}")
        return False

def send_email_with_attachment(pdf_path, to_email="admin@school.edu"):
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = to_email
        mail.Subject = "Student Application Report"
        mail.Body = "Please find the attached student application report."
        mail.Attachments.Add(pdf_path)
        mail.Display(True)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Email Error", f"Failed to open email client: {e}")
        return False

def save_temp_data(data):
    try:
        with open(TEMP_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Temp save failed: {e}")

def load_temp_data():
    if TEMP_FILE.exists():
        try:
            with open(TEMP_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()

# --------------------------
# VIDEO BACKGROUND WIDGET
# --------------------------
class VideoBackgroundWidget(QWidget):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / self.fps))
        self.frame = None
        self.setAttribute(Qt.WA_OpaquePaintEvent)  # Improve performance

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            self.frame = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.repaint()

    def paintEvent(self, event):
        if self.frame:
            painter = QPainter(self)
            scaled = self.frame.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            rect = QRect((self.width() - scaled.width()) // 2,
                         (self.height() - scaled.height()) // 2,
                         scaled.width(), scaled.height())
            painter.drawImage(rect, scaled)

    def closeEvent(self, event):
        self.cap.release()

# --------------------------
# FORM PAGE WIDGET
# --------------------------
class FormPage(QWidget):
    def __init__(self, page_num, data, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.data = data
        self.entries = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(f"Page {self.page_num} of 4")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; background-color: rgba(0,0,0,100); padding: 10px; border-radius: 10px;")
        layout.addWidget(title)

        fields = []
        if self.page_num == 1:
            fields = [("Name", "name"), ("Email", "email"), ("Phone", "phone")]
        elif self.page_num == 2:
            fields = [("Address Line 1", "address_line1"),
                      ("Address Line 2", "address_line2"),
                      ("City", "city"),
                      ("State", "state"),
                      ("ZIP", "zip")]
        elif self.page_num == 3:
            fields = [("School", "school"), ("Grade", "grade"), ("Date of Birth", "dob")]
        elif self.page_num == 4:
            fields = [("Guardian Name", "guardian_name"),
                      ("Guardian Phone", "guardian_phone"),
                      ("Notes", "notes")]

        for label_text, key in fields:
            row = QHBoxLayout()
            label = QLabel(label_text + ":")
            label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
            label.setFixedWidth(120)
            row.addWidget(label)

            if key == "notes":
                entry = QTextEdit()
                entry.setStyleSheet("background: rgba(255,255,255,180); border-radius: 5px; padding: 5px;")
                entry.setFixedHeight(80)
                if self.data[key]:
                    entry.setPlainText(self.data[key])
            else:
                entry = QLineEdit()
                entry.setStyleSheet("background: rgba(255,255,255,180); border-radius: 5px; padding: 5px;")
                if self.data[key]:
                    entry.setText(self.data[key])
            self.entries[key] = entry
            row.addWidget(entry)
            layout.addLayout(row)

        self.setLayout(layout)

    def save_data(self):
        for key, widget in self.entries.items():
            if isinstance(widget, QTextEdit):
                self.data[key] = widget.toPlainText().strip()
            else:
                self.data[key] = widget.text().strip()

# --------------------------
# MAIN WINDOW
# --------------------------
class StudentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1024, 600)
        self.data = load_temp_data()
        self.current_page = 0

        # Central widget with video background
        self.video_bg = VideoBackgroundWidget(VIDEO_PATH, self)
        self.video_bg.setGeometry(self.rect())

        # Overlay container
        self.overlay = QWidget(self)
        self.overlay.setAttribute(Qt.WA_TranslucentBackground)
        self.overlay.setGeometry(self.rect())

        # Stacked Widget for pages
        self.stacked = QStackedWidget()
        self.pages = []
        for i in range(1, 5):
            page_data = self.data[f"page{i}"]
            page = FormPage(i, page_data)
            self.pages.append(page)
            self.stacked.addWidget(page)

        # Navigation buttons
        self.btn_back = QPushButton("← Back")
        self.btn_back.clicked.connect(self.prev_page)
        self.btn_back.setEnabled(False)
        self.btn_back.setStyleSheet("background: rgba(0,120,215,200); color: white; padding: 10px; border-radius: 5px; font-weight: bold;")

        self.btn_next = QPushButton("Next →")
        self.btn_next.clicked.connect(self.next_page)
        self.btn_next.setStyleSheet("background: rgba(0,120,215,200); color: white; padding: 10px; border-radius: 5px; font-weight: bold;")

        self.btn_save_temp = QPushButton("💾 Save Temp")
        self.btn_save_temp.clicked.connect(self.save_temp)
        self.btn_save_temp.setStyleSheet("background: rgba(40,167,69,200); color: white; padding: 10px; border-radius: 5px;")

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save_temp)
        btn_layout.addWidget(self.btn_next)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked)
        main_layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(main_layout)
        container.setStyleSheet("background: transparent;")
        self.overlay.setLayout(main_layout)

        self.setCentralWidget(self.video_bg)
        self.stacked.setCurrentIndex(0)

    def resizeEvent(self, event):
        self.video_bg.setGeometry(self.rect())
        self.overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def next_page(self):
        current_widget = self.pages[self.current_page]
        current_widget.save_data()
        self.data[f"page{self.current_page+1}"] = current_widget.data

        if self.current_page < 3:
            self.current_page += 1
            self.stacked.setCurrentIndex(self.current_page)
            self.btn_back.setEnabled(True)
            if self.current_page == 3:
                self.btn_next.setText("📄 Generate Report")
        else:
            self.generate_report()

    def prev_page(self):
        if self.current_page > 0:
            current_widget = self.pages[self.current_page]
            current_widget.save_data()
            self.data[f"page{self.current_page+1}"] = current_widget.data

            self.current_page -= 1
            self.stacked.setCurrentIndex(self.current_page)
            self.btn_back.setEnabled(self.current_page > 0)
            self.btn_next.setText("Next →")

    def save_temp(self):
        current_widget = self.pages[self.current_page]
        current_widget.save_data()
        self.data[f"page{self.current_page+1}"] = current_widget.data
        save_temp_data(self.data)
        QMessageBox.information(self, "Saved", "Temporary data saved locally.")

    def generate_report(self):
        current_widget = self.pages[self.current_page]
        current_widget.save_data()
        self.data[f"page{self.current_page+1}"] = current_widget.data

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")
        if not save_path:
            return

        if generate_pdf(self.data, save_path):
            QMessageBox.information(self, "Success", f"PDF saved to:\n{save_path}")
            reply = QMessageBox.question(self, "Email Report", "Would you like to email this report?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                send_email_with_attachment(save_path)
        else:
            QMessageBox.critical(self, "Error", "Failed to generate PDF.")

    def closeEvent(self, event):
        current_widget = self.pages[self.current_page]
        current_widget.save_data()
        self.data[f"page{self.current_page+1}"] = current_widget.data
        save_temp_data(self.data)
        self.video_bg.close()
        event.accept()

# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentApp()
    window.show()
    sys.exit(app.exec_())