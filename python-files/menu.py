import sys
import webbrowser
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

# Define shortcuts
shortcuts = {
    "Google": "https://www.google.com",
    "VBT Release Board": "https://nghs.service-now.com/now/nav/ui/classic/params/target/%24vtb.do%3Fsysparm_board%3Dcc2e17801b074110245ccb35624bcbd0",
    "ServiceNow Dashboard": "https://nghs.service-now.com/now/nav/ui/classic/params/target/%24pa_dashboard.do",
    "Epic Data Handbook" : "https://datahandbook.epic.com/",
    "Epic Galaxy": "https://galaxy.epic.com/",
    "VS Code": r"C:\Users\82856\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "Change Ticket": "https://nghs.service-now.com/now/nav/ui/classic/params/target/change_request.do%3Fsys_id%3D-1%26sysparm_stack%3Dchange_request_list.do%26sysparm_query%3Dactive%3Dtrue",
    "Notepad": "notepad.exe",
    "SSRS PRD": "http://vesqlprdrs01/Reports/browse/",
    "SSRS HIE": "http://vesqlhieclar01/Reports/browse/"
}   

class ShortcutApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Shortcut Launcher")
        self.setGeometry(100, 100, 320,600)

        # Remove window frame & make background transparent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create rounded widget overlay
        self.rounded_widget = QWidget(self)
        self.rounded_widget.setGeometry(0, 0, 320, 600)
        self.rounded_widget.setStyleSheet("""
            background-color: gray;
            border-radius: 20px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
        """)

        layout = QVBoxLayout(self.rounded_widget)
        
        for name in shortcuts:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #333;
                    font-size: 16px;
                    padding: 12px;
                    border-radius: 10px;
                    border: 1px solid #DDD;
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)
            btn.clicked.connect(lambda _, n=name: self.openShortcut(n))
            layout.addWidget(btn)

            # Add Close App button
        close_button = QPushButton("Close App")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5C5C;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF2E2E;
            }
        """)
        close_button.clicked.connect(QApplication.instance().quit)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def openShortcut(self, name):
        path = shortcuts[name]
        if path.startswith("http"):
            webbrowser.open(path)
        else:
            os.startfile(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShortcutApp()
    window.show()
    sys.exit(app.exec_())
