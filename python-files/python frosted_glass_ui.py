from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QToolButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QCursor, QColor
import sys


class FrostedGlassWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Executor")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 400)
        self.old_pos = None
        self.script_count = 1
        self.tabs = []
        self.tab_contents = {}
        self.max_tabs = 5

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Main container
        self.container = QWidget()
        self.container.setStyleSheet("""
            background: rgba(255, 255, 255, 0.92);
            border-radius: 18px;
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(12)

        # --- Top bar ---
        self.tab_layout = QHBoxLayout()
        container_layout.addLayout(self.tab_layout)

        # "+" button to add tabs
        self.add_tab_btn = QToolButton()
        self.add_tab_btn.setText("+")
        self.add_tab_btn.setFont(QFont("SF Pro Text", 12, QFont.Weight.Bold))
        self.add_tab_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_tab_btn.setStyleSheet("""
            QToolButton {
                background: rgba(142, 142, 147, 0.15);
                border-radius: 12px;
                padding: 4px 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background: rgba(142, 142, 147, 0.25);
            }
        """)
        self.add_tab_btn.clicked.connect(self.new_tab)
        self.tab_layout.addWidget(self.add_tab_btn)
        self.tab_layout.addStretch()

        # Close app button
        main_close_btn = QToolButton()
        main_close_btn.setText("X")
        main_close_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        main_close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        main_close_btn.setStyleSheet("""
            QToolButton {
                color: #ff3b30;
                border: none;
                background: transparent;
            }
            QToolButton:hover {
                background: rgba(255, 59, 48, 0.15);
                border-radius: 6px;
            }
        """)
        main_close_btn.clicked.connect(self.close)
        self.tab_layout.addWidget(main_close_btn)

        # Buttons row
        button_names = [
            ("Execute", "▶️"),
            ("Clear", "✖️"),
            ("Open", "📂"),
            ("Save", "💾"),
            ("Attach", "🖊️"),
            ("Clients", "👥")
        ]
        button_layout = QHBoxLayout()
        for name, icon in button_names:
            btn = QPushButton(f"{icon} {name}")
            self.style_button(btn)
            button_layout.addWidget(btn)
        button_layout.addStretch()
        container_layout.addLayout(button_layout)

        # Text editor
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            background: rgba(255,255,255,0.95);
            border: 1px solid #d1d1d6;
            font-family: SF Pro Text, Consolas, monospace;
            font-size: 14px;
            color: #1c1c1e;
            border-radius: 10px;
        """)
        self.editor.setPlaceholderText("Type your script here...")
        container_layout.addWidget(self.editor)

        main_layout.addWidget(self.container)

        # Add first tab
        self.add_tab("Script #1", closable=False, switch=True)

    def style_button(self, btn):
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(142, 142, 147, 0.15);
                border: none;
                color: #333;
                font-weight: 600;
                padding: 6px 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: rgba(255, 59, 48, 0.12);
                color: #ff3b30;
            }
        """)

    def add_tab(self, name, closable=True, switch=False):
        if len(self.tabs) >= self.max_tabs:
            return

        # Button with name + X (if closable)
        if closable:
            tab_btn = QPushButton(f"{name}  ✖")
        else:
            tab_btn = QPushButton(name)

        tab_btn.setFont(QFont("SF Pro Text", 10, QFont.Weight.Medium))
        tab_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        tab_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.85);
                padding: 6px 16px;
                border-radius: 16px;
                color: #ff3b30;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 59, 48, 0.10);
            }
        """)

        tab_btn.clicked.connect(lambda _, t=name: self.switch_tab(t))
        if closable:
            tab_btn.clicked.connect(lambda _, t=name, tb=tab_btn: self.close_tab(t, tb) if self.cursor_over_x(tb) else None)

        self.tab_layout.insertWidget(len(self.tabs), tab_btn)
        self.tabs.append(tab_btn)

        if switch:
            self.switch_tab(name)

    def cursor_over_x(self, button):
        # Rough detection of X hover based on cursor position
        pos = button.mapFromGlobal(QCursor.pos())
        return pos.x() > button.width() - 20  # last 20px for X

    def new_tab(self):
        if len(self.tabs) >= self.max_tabs:
            return
        new_number = len(self.tabs) + 1
        self.add_tab(f"Script #{new_number}", closable=True, switch=True)

    def switch_tab(self, name):
        if hasattr(self, "current_tab") and self.current_tab:
            self.tab_contents[self.current_tab] = self.editor.toPlainText()
        self.current_tab = name
        self.editor.setText(self.tab_contents.get(name, ""))

    def close_tab(self, name, tab_widget):
        if hasattr(self, "current_tab") and self.current_tab == name:
            self.tab_contents[name] = self.editor.toPlainText()
        self.tab_layout.removeWidget(tab_widget)
        tab_widget.deleteLater()
        self.tabs = [t for t in self.tabs if t != tab_widget]
        if self.current_tab == name:
            if self.tabs:
                self.switch_tab(self.tabs[0].text().replace(" ✖", ""))
            else:
                self.editor.clear()
                self.current_tab = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FrostedGlassWindow()
    window.show()
    sys.exit(app.exec())
