#!/usr/bin/env python3
"""
NetLimiter Pro - Network Monitoring and Control Application
A Python application for real-time network monitoring and process management.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from login_window import LoginWindow

def main():
    # Enable high DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("NetLimiter Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NetLimiter Pro")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show login window
    login_window = LoginWindow()
    login_window.show()
    
    # Start the application event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())

