import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QGridLayout, QLineEdit, QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SuperCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Calculator")
        self.setGeometry(100, 100, 400, 500)
        
        # Initialize calculator state
        self.current_input = ""
        self.previous_input = ""
        self.operation = None
        self.reset_on_next_input = False
        
        self.init_ui()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Display
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFont(QFont("Arial", 20))
        self.display.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f9fa;
                color: #333;
            }
        """)
        main_layout.addWidget(self.display)
        
        # History display
        self.history_label = QLabel()
        self.history_label.setAlignment(Qt.AlignRight)
        self.history_label.setFont(QFont("Arial", 12))
        self.history_label.setStyleSheet("color: #666;")
        main_layout.addWidget(self.history_label)
        
        # Button layout
        button_layout = QGridLayout()
        main_layout.addLayout(button_layout)
        
        # Button definitions
        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('/', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('⌫', 4, 2), ('=', 4, 3),
            ('√', 5, 0), ('x²', 5, 1), ('1/x', 5, 2), ('π', 5, 3)
        ]
        
        # Create buttons
        for text, row, col in buttons:
            button = self.create_button(text)
            button_layout.addWidget(button, row, col)
            
    def create_button(self, text):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 16))
        button.setMinimumSize(60, 60)
        
        # Style buttons based on their function
        if text in ['+', '-', '×', '/', '=']:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ff9500;
                    color: white;
                    border-radius: 30px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #ffaa33;
                }
                QPushButton:pressed {
                    background-color: #cc7700;
                }
            """)
        elif text in ['C', '±', '%', '⌫']:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #a5a5a5;
                    color: black;
                    border-radius: 30px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #b8b8b8;
                }
                QPushButton:pressed {
                    background-color: #8a8a8a;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: white;
                    border-radius: 30px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #1a1a1a;
                }
            """)
            
        button.clicked.connect(lambda: self.on_button_click(text))
        return button
        
    def on_button_click(self, text):
        if text == 'C':
            self.clear_all()
        elif text == '⌫':
            self.backspace()
        elif text == '=':
            self.calculate_result()
        elif text in ['+', '-', '×', '/']:
            self.set_operation(text)
        elif text == '±':
            self.toggle_sign()
        elif text == '%':
            self.percentage()
        elif text == '√':
            self.square_root()
        elif text == 'x²':
            self.square()
        elif text == '1/x':
            self.reciprocal()
        elif text == 'π':
            self.add_pi()
        elif text == '.':
            self.add_decimal()
        else:
            self.append_number(text)
            
    def append_number(self, number):
        if self.reset_on_next_input:
            self.current_input = ""
            self.reset_on_next_input = False
            
        if self.current_input == "0":
            self.current_input = number
        else:
            self.current_input += number
            
        self.update_display()
        
    def add_decimal(self):
        if self.reset_on_next_input:
            self.current_input = "0"
            self.reset_on_next_input = False
            
        if '.' not in self.current_input:
            if not self.current_input:
                self.current_input = "0"
            self.current_input += '.'
            self.update_display()
            
    def set_operation(self, op):
        if self.current_input:
            if self.operation and not self.reset_on_next_input:
                self.calculate_result()
                
            self.operation = op
            self.previous_input = self.current_input
            self.reset_on_next_input = True
            self.update_history()
            
    def calculate_result(self):
        if not self.operation or not self.previous_input or not self.current_input:
            return
            
        try:
            num1 = float(self.previous_input)
            num2 = float(self.current_input)
            
            if self.operation == '+':
                result = num1 + num2
            elif self.operation == '-':
                result = num1 - num2
            elif self.operation == '×':
                result = num1 * num2
            elif self.operation == '/':
                if num2 == 0:
                    self.display.setText("Error: Division by zero")
                    return
                result = num1 / num2
                
            # Format result to avoid unnecessary decimal places
            if result.is_integer():
                self.current_input = str(int(result))
            else:
                self.current_input = str(result)
                
            self.update_history_complete()
            self.operation = None
            self.reset_on_next_input = True
            self.update_display()
            
        except Exception as e:
            self.display.setText("Error")
            
    def clear_all(self):
        self.current_input = ""
        self.previous_input = ""
        self.operation = None
        self.reset_on_next_input = False
        self.update_display()
        self.history_label.setText("")
        
    def backspace(self):
        if self.current_input:
            self.current_input = self.current_input[:-1]
            if not self.current_input:
                self.current_input = "0"
            self.update_display()
            
    def toggle_sign(self):
        if self.current_input and self.current_input != "0":
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.update_display()
            
    def percentage(self):
        if self.current_input:
            try:
                value = float(self.current_input) / 100
                if value.is_integer():
                    self.current_input = str(int(value))
                else:
                    self.current_input = str(value)
                self.update_display()
            except:
                self.display.setText("Error")
                
    def square_root(self):
        if self.current_input:
            try:
                value = float(self.current_input)
                if value >= 0:
                    result = value ** 0.5
                    if result.is_integer():
                        self.current_input = str(int(result))
                    else:
                        self.current_input = str(result)
                    self.update_display()
                else:
                    self.display.setText("Error: Negative number")
            except:
                self.display.setText("Error")
                
    def square(self):
        if self.current_input:
            try:
                value = float(self.current_input)
                result = value ** 2
                if result.is_integer():
                    self.current_input = str(int(result))
                else:
                    self.current_input = str(result)
                self.update_display()
            except:
                self.display.setText("Error")
                
    def reciprocal(self):
        if self.current_input and self.current_input != "0":
            try:
                value = float(self.current_input)
                result = 1 / value
                if result.is_integer():
                    self.current_input = str(int(result))
                else:
                    self.current_input = str(result)
                self.update_display()
            except:
                self.display.setText("Error")
                
    def add_pi(self):
        self.current_input = str(3.141592653589793)
        self.update_display()
        
    def update_display(self):
        if not self.current_input:
            self.display.setText("0")
        else:
            self.display.setText(self.current_input)
            
    def update_history(self):
        if self.previous_input and self.operation:
            self.history_label.setText(f"{self.previous_input} {self.operation}")
            
    def update_history_complete(self):
        if self.previous_input and self.operation:
            self.history_label.setText(f"{self.previous_input} {self.operation} {self.current_input} =")
            
    def keyPressEvent(self, event):
        key = event.text()
        if key in '0123456789':
            self.append_number(key)
        elif key == '.':
            self.add_decimal()
        elif key == '+':
            self.set_operation('+')
        elif key == '-':
            self.set_operation('-')
        elif key == '*':
            self.set_operation('×')
        elif key == '/':
            self.set_operation('/')
        elif key == '\r' or key == '=':  # Enter or equals
            self.calculate_result()
        elif key == '\b':  # Backspace
            self.backspace()
        elif key == 'c' or key == 'C':
            self.clear_all()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    calculator = SuperCalculator()
    calculator.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()