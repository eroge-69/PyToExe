import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout,
    QSystemTrayIcon, QMenu
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint
from pycaw.pycaw import AudioUtilities
import comtypes


class AudioChannelController:
    def set_left_only(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.SimpleAudioVolume:
                session.SimpleAudioVolume.SetChannelVolume(0, 1.0, None)  # L
                session.SimpleAudioVolume.SetChannelVolume(1, 0.0, None)  # R off

    def set_right_only(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.SimpleAudioVolume:
                session.SimpleAudioVolume.SetChannelVolume(0, 0.0, None)  # L off
                session.SimpleAudioVolume.SetChannelVolume(1, 1.0, None)  # R

    def reset(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.SimpleAudioVolume:
                session.SimpleAudioVolume.SetChannelVolume(0, 1.0, None)
                session.SimpleAudioVolume.SetChannelVolume(1, 1.0, None)


class PopupWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 12px;")

        self.selected = None  # None, "L", or "R"

        # Buttons
        self.btnL = QPushButton("L")
        self.btnR = QPushButton("R")

        for btn in (self.btnL, self.btnR):
            btn.setFixedSize(60, 60)
            btn.setStyleSheet(self.style_inactive())
            btn.clicked.connect(self.handle_click)

        layout = QHBoxLayout()
        layout.addWidget(self.btnL)
        layout.addWidget(self.btnR)
        self.setLayout(layout)

    def style_active(self):
        return (
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #1976d2, stop:1 #0d47a1);"
            "color: white; font-weight: bold; font-size: 20px; border-radius: 15px;"
        )

    def style_inactive(self):
        return (
            "background-color: #555; color: #bbb; font-size: 20px; "
            "border-radius: 15px;"
        )

    def handle_click(self):
        sender = self.sender()
        if sender == self.btnL:
            if self.selected == "L":
                # Turn off
                self.selected = None
                self.controller.reset()
                self.btnL.setStyleSheet(self.style_inactive())
            else:
                # Select left
                self.selected = "L"
                self.controller.set_left_only()
                self.btnL.setStyleSheet(self.style_active())
                self.btnR.setStyleSheet(self.style_inactive())
        elif sender == self.btnR:
            if self.selected == "R":
                # Turn off
                self.selected = None
                self.controller.reset()
                self.btnR.setStyleSheet(self.style_inactive())
            else:
                # Select right
                self.selected = "R"
                self.controller.set_right_only()
                self.btnR.setStyleSheet(self.style_active())
                self.btnL.setStyleSheet(self.style_inactive())


class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.controller = AudioChannelController()

        # Tray
        self.tray = QSystemTrayIcon(QIcon.fromTheme("audio-volume-high"))
        self.menu = QMenu()
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(sys.exit)
        self.tray.setContextMenu(self.menu)

        self.popup = PopupWindow(self.controller)

        # Show popup on left click
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Left click
            if self.popup.isVisible():
                self.popup.hide()
            else:
                pos = QCursor.pos()
                self.popup.move(pos - QPoint(50, 80))  # place above cursor
                self.popup.show()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    TrayApp().run()
