import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QLabel, QLineEdit, QPushButton, QMessageBox, QAction)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QFont, QKeySequence

class GradientEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор градиентов для плагинов")
        self.setGeometry(100, 100, 900, 700)
        
        self._setup_ui()
        self._setup_shortcuts()
        
    def _setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Code input area
        self.code_label = QLabel("Вставьте ваш код с градиентом:")
        main_layout.addWidget(self.code_label)
        
        self.code_text = QTextEdit()
        self.code_text.setFontFamily("Consolas")
        self.code_text.setFontPointSize(12)
        self.code_text.textChanged.connect(self._update_preview)
        main_layout.addWidget(self.code_text, 1)
        
        # Preview area
        self.preview_label = QLabel("Предпросмотр:")
        main_layout.addWidget(self.preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(60)
        self.preview_text.setStyleSheet("background-color: #2b2b2b; color: white;")
        main_layout.addWidget(self.preview_text)
        
        # Text edit controls
        edit_layout = QHBoxLayout()
        
        self.edit_label = QLabel("Новый текст:")
        edit_layout.addWidget(self.edit_label)
        
        self.edit_entry = QLineEdit()
        edit_layout.addWidget(self.edit_entry, 1)
        
        self.apply_btn = QPushButton("Применить градиент (Ctrl+Enter)")
        self.apply_btn.clicked.connect(self._apply_gradient)
        edit_layout.addWidget(self.apply_btn)
        
        main_layout.addLayout(edit_layout)
        
        # Info area
        self.selection_info = QLabel("Выделите текст с градиентом для редактирования")
        self.selection_info.setStyleSheet("color: gray;")
        main_layout.addWidget(self.selection_info)
        
        # Help text
        help_text = """<b>Горячие клавиши:</b><br>
Ctrl+C - Копировать<br>
Ctrl+V - Вставить<br>
Ctrl+X - Вырезать<br>
Ctrl+A - Выделить всё<br>
Ctrl+Z - Отменить<br>
Ctrl+Y - Повторить<br>
Ctrl+Enter - Применить градиент"""
        self.help_label = QLabel(help_text)
        self.help_label.setTextFormat(Qt.RichText)
        main_layout.addWidget(self.help_label)
        
    def _setup_shortcuts(self):
        # Create actions properly
        self.copy_action = QAction(self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.code_text.copy)
        self.addAction(self.copy_action)
        
        self.paste_action = QAction(self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.code_text.paste)
        self.addAction(self.paste_action)
        
        self.cut_action = QAction(self)
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.triggered.connect(self.code_text.cut)
        self.addAction(self.cut_action)
        
        self.select_all_action = QAction(self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.code_text.selectAll)
        self.addAction(self.select_all_action)
        
        self.undo_action = QAction(self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.code_text.undo)
        self.addAction(self.undo_action)
        
        self.redo_action = QAction(self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.code_text.redo)
        self.addAction(self.redo_action)
        
        # Custom shortcut for apply gradient
        self.apply_action = QAction(self)
        self.apply_action.setShortcut(QKeySequence("Ctrl+Return"))
        self.apply_action.triggered.connect(self._apply_gradient)
        self.addAction(self.apply_action)
    
    def _update_preview(self):
        self.preview_text.clear()
        text = self.code_text.toPlainText()
        
        # Find all color codes and text
        pattern = r'(&#([0-9A-Fa-f]{6})|.)'
        matches = re.findall(pattern, text)
        
        cursor = self.preview_text.textCursor()
        format = QTextCharFormat()
        
        for match in matches:
            if match[0].startswith('&#'):
                color_code = match[1]
                color = QColor(f'#{color_code}')
                format.setForeground(color)
            else:
                char = match[0]
                if char.strip():  # Only show non-whitespace characters
                    format.setFont(QFont("Arial", 12))
                    cursor.insertText(char, format)
        
        self._update_selection_info()
    
    def _update_selection_info(self):
        cursor = self.code_text.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            color_codes = re.findall(r'&#([0-9A-Fa-f]{6})', selected_text)
            
            if len(color_codes) >= 2:
                info = f"Выделено: {len(color_codes)} цветов (от #{color_codes[0]} до #{color_codes[-1]})"
            else:
                info = "Выделите текст с градиентом (минимум 2 цветных кода)"
        else:
            info = "Выделите текст с градиентом для редактирования"
        
        self.selection_info.setText(info)
    
    def _apply_gradient(self):
        cursor = self.code_text.textCursor()
        if not cursor.hasSelection():
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выделите текст с градиентом")
            return
        
        selected_text = cursor.selectedText()
        new_text = self.edit_entry.text()
        
        if not new_text:
            QMessageBox.warning(self, "Внимание", "Введите новый текст для замены")
            return
        
        # Extract color codes from selected text
        color_codes = re.findall(r'&#([0-9A-Fa-f]{6})', selected_text)
        if len(color_codes) < 2:
            QMessageBox.warning(self, "Внимание", "Выделенный текст должен содержать хотя бы два цветовых кода")
            return
        
        start_color = color_codes[0]
        end_color = color_codes[-1]
        
        # Generate gradient colors for new text
        gradient_colors = self._generate_gradient(start_color, end_color, len(new_text))
        
        # Build new colored text
        colored_text = ""
        for i, char in enumerate(new_text):
            colored_text += f"&#{gradient_colors[i]}{char}"
        
        # Replace selected text with new colored text
        cursor.insertText(colored_text)
        
        # Select the new text
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(colored_text))
        self.code_text.setTextCursor(cursor)
        
        self._update_preview()
    
    def _generate_gradient(self, start_hex, end_hex, steps):
        """Generate gradient between two colors"""
        # Convert hex to RGB
        start_rgb = tuple(int(start_hex[i:i+2], 16) for i in (0, 2, 4))
        end_rgb = tuple(int(end_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate step size for each component
        step_size = tuple((end - start) / max(1, steps - 1) for start, end in zip(start_rgb, end_rgb))
        
        # Generate gradient colors
        gradient = []
        for i in range(steps):
            # Calculate intermediate color
            r = int(start_rgb[0] + step_size[0] * i)
            g = int(start_rgb[1] + step_size[1] * i)
            b = int(start_rgb[2] + step_size[2] * i)
            
            # Convert back to hex
            hex_color = f"{r:02X}{g:02X}{b:02X}"
            gradient.append(hex_color)
        
        return gradient

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = GradientEditor()
    editor.show()
    sys.exit(app.exec_())