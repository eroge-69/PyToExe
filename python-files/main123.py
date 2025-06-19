import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPalette, QColor
from ChatBot import ChatBot  # Your ChatBot function

class PremiumCopilotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shinchan AI Premium")
        self.setGeometry(100, 100, 1000, 700)  # Larger window size
        self.initUI()
        
    def initUI(self):
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)  # Wider sidebar
        self.sidebar.setStyleSheet("""
            background-color: #252525;
            border-right: 1px solid #333;
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 15, 10, 15)  # Better padding
        sidebar_layout.setSpacing(15)
        
        # New chat button (improved)
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #40414F;
                color: white;
                border: 1px solid #4D4D4F;
                padding: 12px;
                text-align: center;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #50525F;
            }
        """)
        sidebar_layout.addWidget(new_chat_btn)
        
        # Chat history (improved)
        self.chat_history = QListWidget()
        self.chat_history.setFont(QFont("Segoe UI", 12))
        self.chat_history.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                color: #ECECF1;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 6px;
                margin-bottom: 5px;
            }
            QListWidget::item:hover {
                background-color: #2A2A2A;
            }
            QListWidget::item:selected {
                background-color: #3E3F4B;
            }
        """)
        
        # Sample chat items with better styling
        sample_chats = ["Python Coding Help", "Shinchan Jokes", "Homework Questions", "Tech Support", "General Knowledge"]
        for chat in sample_chats:
            item = QListWidgetItem(f"💬 {chat}")
            item.setFont(QFont("Segoe UI", 12))
            self.chat_history.addItem(item)
            
        sidebar_layout.addWidget(self.chat_history)
        self.sidebar.setLayout(sidebar_layout)
        
        # Main content area
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #343541;")
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header (improved)
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            background-color: #343541; 
            border-bottom: 1px solid #4D4D4F;
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.sidebar_toggle = QPushButton()
        self.sidebar_toggle.setIcon(QIcon.fromTheme("menu"))
        self.sidebar_toggle.setIconSize(QSize(24, 24))
        self.sidebar_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4D4D4F;
            }
        """)
        
        title = QLabel("Shinchan AI Premium")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        header_layout.addWidget(self.sidebar_toggle)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        header.setLayout(header_layout)
        content_layout.addWidget(header)
        
        # Chat area (improved with larger fonts)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #343541;
                color: #ECECF1;
                font-size: 16px;
                border: none;
                padding: 25px;
                line-height: 1.6;
            }
        """)
        self.chat_area.setFont(QFont("Segoe UI", 14))
        content_layout.addWidget(self.chat_area)
        
        # Input area (improved)
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #40414F; border-top: 1px solid #4D4D4F;")
        input_frame.setFixedHeight(120)
        
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(20, 15, 20, 25)
        
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Message Shinchan AI...")
        self.input_box.setFont(QFont("Segoe UI", 14))
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: #40414F;
                color: white;
                font-size: 16px;
                border: 1px solid #565869;
                border-radius: 12px;
                padding: 15px;
                min-height: 60px;
            }
        """)
        self.input_box.setMaximumHeight(80)
        
        self.send_btn = QPushButton()
        self.send_btn.setIcon(QIcon.fromTheme("mail-send"))
        self.send_btn.setIconSize(QSize(24, 24))
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10A37F;
                border: none;
                border-radius: 12px;
                min-width: 50px;
                min-height: 50px;
                margin-left: 15px;
            }
            QPushButton:hover {
                background-color: #0D8E6D;
            }
            QPushButton:pressed {
                background-color: #0B7A5F;
            }
        """)
        
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_btn)
        input_frame.setLayout(input_layout)
        content_layout.addWidget(input_frame)
        
        content_frame.setLayout(content_layout)
        
        # Add widgets to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        # Connect signals
        self.send_btn.clicked.connect(self.send_message)
        self.input_box.installEventFilter(self)
        
        # Add welcome message
        self.add_welcome_message()
    
    def eventFilter(self, obj, event):
        if obj == self.input_box and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers():
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        user_input = self.input_box.toPlainText().strip()
        if not user_input:
            return

        # Add user message
        self.add_message(user_input, "user")
        self.input_box.clear()
        
        # Get response from ChatBot
        try:
            bot_response = ChatBot(user_input)
            self.add_message(bot_response, "ai")
        except Exception as e:
            self.add_message(f"Error: {str(e)}", "error")
            
    def add_welcome_message(self):
        welcome_msg = """
        <div style='margin-bottom: 30px;'>
            <div style='color: white; font-weight: bold; margin-bottom: 10px; font-size: 18px;'>
                <span style='color: #10A37F;'>Shinchan AI Premium</span>
            </div>
            <div style='color: #ECECF1; font-size: 16px; line-height: 1.7;'>
                Hello! I'm Shinchan AI, your premium assistant. I can help you with:<br><br>
                • Coding problems (Python, JavaScript, etc.)<br>
                • General knowledge questions<br>
                • Creative writing<br>
                • And much more!<br><br>
                How can I help you today?
            </div>
        </div>
        """
        self.chat_area.setHtml(welcome_msg)
            
    def add_message(self, content, sender):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if sender == "user":
            html = f"""
            <div style='margin-bottom: 40px;'>
                <div style='color: white; font-weight: bold; margin-bottom: 8px; font-size: 16px;'>You</div>
                <div style='color: #ECECF1; white-space: pre-wrap; font-size: 16px; line-height: 1.7;'>{content}</div>
            </div>
            """
        else:
            html = f"""
            <div style='margin-bottom: 40px;'>
                <div style='color: white; font-weight: bold; margin-bottom: 8px; font-size: 16px; display: flex; align-items: center;'>
                    <span style='color: #10A37F; margin-right: 5px;'>Shinchan AI</span>
                </div>
                <div style='color: #ECECF1; white-space: pre-wrap; font-size: 16px; line-height: 1.7;'>{content}</div>
            </div>
            """
            
        cursor.insertHtml(html)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()

# Run application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set premium dark theme palette
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(40, 40, 40))
    palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipText, QColor(40, 40, 40))
    palette.setColor(QPalette.Text, QColor(240, 240, 240))
    palette.setColor(QPalette.Button, QColor(60, 60, 60))
    palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
    palette.setColor(QPalette.BrightText, QColor(255, 100, 100))
    palette.setColor(QPalette.Link, QColor(100, 170, 255))
    palette.setColor(QPalette.Highlight, QColor(16, 163, 127))
    palette.setColor(QPalette.HighlightedText, QColor(240, 240, 240))
    app.setPalette(palette)
    
    # Set default font
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    window = PremiumCopilotUI()
    window.show()
    sys.exit(app.exec_())
