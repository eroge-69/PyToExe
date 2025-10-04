import sys
import os
import time
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtCore import Qt

class LaunchSoftwareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Launch Two Software")
        self.setGeometry(100, 100, 400, 300)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # First software path
        self.path_layout1 = QHBoxLayout()
        self.label1 = QLabel("Software 1 Path:")
        self.path_input1 = QLineEdit()
        self.browse_button1 = QPushButton("Browse")
        self.browse_button1.clicked.connect(self.browse_software1)
        self.path_layout1.addWidget(self.label1)
        self.path_layout1.addWidget(self.path_input1)
        self.path_layout1.addWidget(self.browse_button1)
        
        # Second software path
        self.path_layout2 = QHBoxLayout()
        self.label2 = QLabel("Software 2 Path:")
        self.path_input2 = QLineEdit()
        self.browse_button2 = QPushButton("Browse")
        self.browse_button2.clicked.connect(self.browse_software2)
        self.path_layout2.addWidget(self.label2)
        self.path_layout2.addWidget(self.path_input2)
        self.path_layout2.addWidget(self.browse_button2)
        
        # Delay input
        self.delay_layout = QHBoxLayout()
        self.delay_label = QLabel("Delay (seconds):")
        self.delay_input = QLineEdit("0")
        self.delay_input.setFixedWidth(100)
        self.delay_layout.addWidget(self.delay_label)
        self.delay_layout.addWidget(self.delay_input)
        self.delay_layout.addStretch()
        
        # Launch button
        self.launch_button = QPushButton("Launch Software")
        self.launch_button.clicked.connect(self.launch_software)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add all to main layout
        self.layout.addLayout(self.path_layout1)
        self.layout.addLayout(self.path_layout2)
        self.layout.addLayout(self.delay_layout)
        self.layout.addWidget(self.launch_button)
        self.layout.addWidget(self.status_label)
        self.layout.addStretch()
        
    def browse_software1(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Software 1", "", "Executable Files (*.exe)")
        if file_path:
            self.path_input1.setText(file_path)
            
    def browse_software2(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Software 2", "", "Executable Files (*.exe)")
        if file_path:
            self.path_input2.setText(file_path)
            
    def launch_software(self):
        path1 = self.path_input1.text()
        path2 = self.path_input2.text()
        try:
            delay = float(self.delay_input.text())
        except ValueError:
            self.status_label.setText("Error: Invalid delay value")
            return
            
        if not os.path.exists(path1) or not os.path.exists(path2):
            self.status_label.setText("Error: One or both paths invalid")
            return
            
        self.status_label.setText("Launching software...")
        try:
            # Launch first software
            subprocess.Popen([path1], shell=True)
            
            # Wait for delay
            time.sleep(delay)
            
            # Launch second software
            subprocess.Popen([path2], shell=True)
            
            self.status_label.setText("Software launched successfully!")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LaunchSoftwareApp()
    window.show()
    sys.exit(app.exec_())