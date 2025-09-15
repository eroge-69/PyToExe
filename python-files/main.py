"""
Main entry point for the ModernBrowser application.

This module initializes and launches a Qt-based modern web browser application.
"""

import os
import sys
import logging

from PyQt6.QtWidgets import QApplication

from config.config import FLAGS
from modern_browser import ModernBrowser

if __name__ == "__main__":
    # Глобальная настройка логгирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("quilix_app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    def log_uncaught_exceptions(exctype, value, tb):
        logging.critical("Uncaught exception:", exc_info=(exctype, value, tb))
    sys.excepthook = log_uncaught_exceptions

    """
    Initialize and runs the ModernBrowser application.

    This main block performs the following operations:
    1. Updates the environment variables with configuration flags
    2. Creates the Qt application instance
    3. Initializes the ModernBrowser window
    4. Starts the application event loop

    The application will run until the main window is closed or the process
    is terminated.

    Environment Variables:
        Uses FLAGS from core.config.config to set environment variables before
        launching the application. These typically control runtime behavior
        and configuration options.

    Example:
        To run the browser application:
        >>> python main.py

        The FLAGS might include settings like:
        {'QTWEBENGINE_CHROMIUM_FLAGS': '--disable-web-security'}
    """
    os.environ.update(FLAGS)
    app = QApplication(sys.argv)
    browser = ModernBrowser(app)
    browser.show()
    sys.exit(app.exec())
