import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QPushButton, QLineEdit, QMessageBox, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont

class DraggableLabel(QLabel):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.name = name
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 10px;
                background-color: #e0e0e0;
                color: #333;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: #d0d0d0;
                border: 2px solid #333;
            }
        """)
        self.setMinimumSize(120, 80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            urls = event.mimeData().urls()
            
            # יצירת תיקיה אם לא קיימת
            folder_path = os.path.join(os.getcwd(), self.name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # העתקת הקבצים
            for url in urls:
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(folder_path, file_name)
                    shutil.copy2(file_path, dest_path)
                    
            QMessageBox.information(self, "הצלחה", f"הקבצים נשמרו בתיקייה: {self.name}")
        else:
            event.ignore()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ניהול קבצים על ידי גרירה")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget מרכזי
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout ראשי
        layout = QGridLayout(central_widget)
        layout.setSpacing(10)
        
        # אזור הוספת תיבות חדשות
        self.new_box_input = QLineEdit()
        self.new_box_input.setPlaceholderText("הכנס שם למרובע חדש")
        self.add_button = QPushButton("הוסף מרובע")
        self.add_button.clicked.connect(self.add_new_box)
        
        layout.addWidget(QLabel("הוסף מרובע חדש:"), 0, 0)
        layout.addWidget(self.new_box_input, 0, 1)
        layout.addWidget(self.add_button, 0, 2)
        
        # Widget שיכיל את התיבות
        self.boxes_widget = QWidget()
        self.boxes_layout = QGridLayout(self.boxes_widget)
        self.boxes_layout.setSpacing(15)
        
        layout.addWidget(self.boxes_widget, 1, 0, 1, 3)
        
        # טעינת תיבות קיימות (אם יש)
        self.load_existing_boxes()
        
    def add_new_box(self):
        box_name = self.new_box_input.text().strip()
        if not box_name:
            QMessageBox.warning(self, "שגיאה", "אנא הכנס שם למרובע")
            return
        
        # הוספת התיבה החדשה
        self.create_box(box_name)
        self.new_box_input.clear()
        
    def create_box(self, name):
        # חישוב המיקום הבא ברשת
        count = self.boxes_layout.count()
        row = count // 3
        col = count % 3
        
        new_label = DraggableLabel(name)
        self.boxes_layout.addWidget(new_label, row, col)
        
    def load_existing_boxes(self):
        # טעינת תיקיות קיימות מהתיקייה הנוכחית
        current_dir = os.getcwd()
        for item in os.listdir(current_dir):
            if os.path.isdir(os.path.join(current_dir, item)):
                self.create_box(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # הגדרות עברית
    font = QFont("Arial", 12)
    app.setFont(font)
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #f5f5f5;
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())