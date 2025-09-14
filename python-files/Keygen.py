import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator

class ArchplanKeygen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Archplan Code Generator 2026')
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Input group box
        input_group = QGroupBox('Input')
        input_layout = QVBoxLayout(input_group)
        
        # Key input
        key_layout = QHBoxLayout()
        key_label = QLabel('Enter Key:')
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText('Enter a number (e.g., 558249052)...')
        # Set validator to accept only integers
        self.key_input.setValidator(QIntValidator())
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        input_layout.addLayout(key_layout)
        
        layout.addWidget(input_group)
        
        # Output group box
        output_group = QGroupBox('Output')
        output_layout = QVBoxLayout(output_group)
        
        # Result display
        result_layout = QHBoxLayout()
        result_label = QLabel('Generated Code:')
        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        result_layout.addWidget(result_label)
        result_layout.addWidget(self.result_output)
        output_layout.addLayout(result_layout)
        
        # AutoCAD Version display
        autocad_layout = QHBoxLayout()
        autocad_label = QLabel('AutoCAD Version:')
        self.autocad_output = QLineEdit()
        self.autocad_output.setReadOnly(True)
        autocad_layout.addWidget(autocad_label)
        autocad_layout.addWidget(self.autocad_output)
        output_layout.addLayout(autocad_layout)
        
        layout.addWidget(output_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Generate button
        self.generate_button = QPushButton('Generate Code')
        self.generate_button.clicked.connect(self.generate_code)
        button_layout.addWidget(self.generate_button)
        
        # Clear button
        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # Set style
        self.apply_style()
        
    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                font-size: 12px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
    def generate_code(self):
        key = self.key_input.text().strip()
        
        # Validate input
        if not key:
            QMessageBox.warning(self, 'Input Error', 'Please enter a key.')
            return
            
        if len(key) < 4:
            QMessageBox.warning(self, 'Input Error', 'Key must be at least 4 digits long.')
            return
            
        try:
            # Step 1: Remove last 3 digits
            step1 = key[:-3]
            
            # Step 2: Subtract 1234 (this step is not shown)
            step2 = int(step1) - 1234
            
            # Step 3: Add 853306
            step3 = step2 + 853306
            
            # Display the result
            self.result_output.setText(str(step3))
            
            # AutoCAD Version calculation
            last_two_digits = key[-2:]
            autocad_version = int(last_two_digits) / 2
            self.autocad_output.setText(str(autocad_version))
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            
    def clear_fields(self):
        self.key_input.clear()
        self.result_output.clear()
        self.autocad_output.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ArchplanKeygen()
    window.show()
    sys.exit(app.exec_())