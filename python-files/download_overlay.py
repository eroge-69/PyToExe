import sys
import psutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, 
                             QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
                             QSystemTrayIcon, QMenu, QAction, QStyle)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QMouseEvent

class DownloadRateOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Download-Rate Overlay")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initial position
        self.old_pos = None
        self.dragging = False
        
        # Create central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 50);
            }
        """)
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title bar
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Download-Rate Monitor")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 100, 100, 150);
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 200);
            }
        """)
        self.close_button.clicked.connect(self.hide_to_tray)
        title_layout.addWidget(self.close_button)
        layout.addLayout(title_layout)
        
        # Rate display
        self.rate_label = QLabel("0.0 KB/s")
        self.rate_label.setAlignment(Qt.AlignCenter)
        self.rate_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.rate_label.setStyleSheet("color: #4cd964;")
        layout.addWidget(self.rate_label)
        
        # Total display
        self.total_label = QLabel("Gesamt: 0.0 MB")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("color: rgba(255, 255, 255, 180);")
        layout.addWidget(self.total_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Zurücksetzen")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 70, 70, 150);
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 200);
            }
        """)
        self.reset_button.clicked.connect(self.reset_counter)
        button_layout.addWidget(self.reset_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(70, 70, 70, 150);
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 200);
            }
        """)
        self.pause_button.clicked.connect(self.toggle_pause)
        button_layout.addWidget(self.pause_button)
        layout.addLayout(button_layout)
        
        # Setup network monitoring
        self.old_value = psutil.net_io_counters().bytes_recv
        self.total_downloaded = 0
        self.is_paused = False
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_network_stats)
        self.timer.start(1000)  # Update every second
        
        # Setup system tray
        self.setup_tray()
        
        # Set window size and position
        self.resize(250, 150)
        self.move(50, 50)
        
    def setup_tray(self):
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Anzeigen", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            
    def hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "Download-Rate Monitor",
            "Die App läuft im Hintergrund weiter. Doppelklicke auf das Tray-Icon, um sie wieder anzuzeigen.",
            QSystemTrayIcon.Information,
            2000
        )
        
    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 30:
            self.old_pos = event.globalPos()
            self.dragging = True
            
    def mouseMoveEvent(self, event):
        if self.dragging and self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.old_pos = None
            
    def update_network_stats(self):
        if self.is_paused:
            return
            
        # Get current network usage
        new_value = psutil.net_io_counters().bytes_recv
        diff = new_value - self.old_value
        
        # Calculate download rate
        download_rate = diff / 1024  # KB/s
        self.total_downloaded += diff / (1024 * 1024)  # MB
        
        # Update display
        if download_rate < 1024:
            self.rate_label.setText(f"{download_rate:.1f} KB/s")
        else:
            self.rate_label.setText(f"{download_rate/1024:.1f} MB/s")
            
        self.total_label.setText(f"Gesamt: {self.total_downloaded:.1f} MB")
        
        # Store old value for next calculation
        self.old_value = new_value
        
    def reset_counter(self):
        self.total_downloaded = 0
        self.old_value = psutil.net_io_counters().bytes_recv
        self.total_label.setText("Gesamt: 0.0 MB")
        
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.setText("Fortsetzen")
            self.rate_label.setStyleSheet("color: rgba(255, 150, 50, 200);")
        else:
            self.pause_button.setText("Pause")
            self.rate_label.setStyleSheet("color: #4cd964;")
            # Update immediately when resuming
            self.old_value = psutil.net_io_counters().bytes_recv
            
    def closeEvent(self, event):
        event.ignore()
        self.hide_to_tray()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    overlay = DownloadRateOverlay()
    overlay.show()
    
    sys.exit(app.exec_())