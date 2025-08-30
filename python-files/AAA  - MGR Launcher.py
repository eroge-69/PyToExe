import sys
import subprocess
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QLabel, QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import Qt
import ctypes
from ctypes import wintypes

# Load user32.dll for Windows API functions
user32 = ctypes.windll.user32

# Constants for display device functions
ENUM_CURRENT_SETTINGS = -1
ENUM_REGISTRY_SETTINGS = -2

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmOrientation", ctypes.c_short),
        ("dmPaperSize", ctypes.c_short),
        ("dmPaperLength", ctypes.c_short),
        ("dmPaperWidth", ctypes.c_short),
        ("dmScale", ctypes.c_short),
        ("dmCopies", ctypes.c_short),
        ("dmDefaultSource", ctypes.c_short),
        ("dmPrintQuality", ctypes.c_short),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]

def change_resolution(width, height):
    """Change the screen resolution to the specified width and height"""
    devmode = DEVMODEW()
    devmode.dmSize = ctypes.sizeof(devmode)
    
    # Get current settings to preserve other values
    if user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode)) == 0:
        return False
    
    # Change the resolution values
    devmode.dmPelsWidth = width
    devmode.dmPelsHeight = height
    devmode.dmFields = 0x00040000 | 0x00080000  # DM_PELSWIDTH | DM_PELSHEIGHT
    
    # Try to change the display settings
    result = user32.ChangeDisplaySettingsW(ctypes.byref(devmode), 0)
    return result == 0  # Returns True if successful

def get_current_resolution():
    """Get the current screen resolution"""
    devmode = DEVMODEW()
    devmode.dmSize = ctypes.sizeof(devmode)
    
    if user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode)):
        return (devmode.dmPelsWidth, devmode.dmPelsHeight)
    return None

class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_resolution = get_current_resolution()
        self.game_process = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Game Launcher')
        self.setFixedSize(400, 300)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title label
        title_label = QLabel('Game Launcher')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold; margin: 20px;')
        layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel('This launcher will change your resolution to 1280x720 when you launch the game, and restore it to 1920x1080 when you exit.')
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('margin: 10px;')
        layout.addWidget(info_label)
        
        # Launch button
        self.launch_button = QPushButton('Launch Game')
        self.launch_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        ''')
        self.launch_button.clicked.connect(self.launch_game)
        layout.addWidget(self.launch_button)
        
        # Exit button
        exit_button = QPushButton('Exit Launcher')
        exit_button.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        ''')
        exit_button.clicked.connect(self.exit_launcher)
        layout.addWidget(exit_button)
        
        # Status label
        self.status_label = QLabel('Ready to launch game')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('margin: 10px; color: #666;')
        layout.addWidget(self.status_label)
        
        # Add some spacing at the bottom
        layout.addStretch()
        
    def launch_game(self):
        # Change resolution to 1280x720
        if change_resolution(1280, 720):
            self.status_label.setText('Resolution changed to 1280x720')
            self.launch_button.setEnabled(False)
            
            # In a real implementation, you would launch your game here
            # For demonstration, we'll just launch notepad
            try:
                self.game_process = subprocess.Popen(['notepad.exe'])
                self.status_label.setText('Game is running...')
                
                # Monitor the game process
                self.check_game_process()
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not launch game: {str(e)}')
                self.restore_resolution()
        else:
            QMessageBox.critical(self, 'Error', 'Could not change resolution to 1280x720')
            
    def check_game_process(self):
        # Check if the game process is still running
        if self.game_process and self.game_process.poll() is not None:
            # Game has exited, restore resolution
            self.restore_resolution()
            self.status_label.setText('Game exited. Resolution restored.')
            self.launch_button.setEnabled(True)
        else:
            # Check again after 1 second
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, self.check_game_process)
            
    def restore_resolution(self):
        # Restore to original resolution (or 1920x1080 if not available)
        if self.original_resolution:
            change_resolution(self.original_resolution[0], self.original_resolution[1])
        else:
            change_resolution(1920, 1080)
            
    def exit_launcher(self):
        # Make sure to restore resolution when exiting
        self.restore_resolution()
        QApplication.quit()
        
    def closeEvent(self, event):
        # Handle window close event
        self.restore_resolution()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    launcher = GameLauncher()
    launcher.show()
    
    # Ensure resolution is restored when application exits
    app.aboutToQuit.connect(launcher.restore_resolution)
    
    sys.exit(app.exec_())