import sys
import time
import json
import os
import putil
import traceback

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QPushButton, QListWidget, QListWidgetItem, QLabel, 
                            QDialog, QLineEdit, QMessageBox, QSystemTrayIcon, 
                            QMenu, QAction, QTreeWidget, QTreeWidgetItem, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap, QPainter, QBrush

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Unhandled exception:\n{error_msg}")
    QMessageBox.critical(None, "Error", f"An error occurred:\n{error_msg}")
    sys.exit(1)

sys.excepthook = handle_exception

def create_tray_icon():
    """Create a simple clock icon for system tray"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw clock circle
    painter.setBrush(QBrush(QColor("#f26522")))
    painter.setPen(QColor("#ffffff"))
    painter.drawEllipse(2, 2, 28, 28)
    
    # Draw clock hands
    painter.setPen(QColor("#ffffff"))
    painter.drawLine(16, 16, 16, 8)  # Hour hand
    painter.drawLine(16, 16, 22, 16)  # Minute hand
    
    painter.end()
    return QIcon(pixmap)

class ProcessSelector(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setup_ui()
        except Exception as e:
            print(f"Error initializing ProcessSelector: {str(e)}")
            raise

    def setup_ui(self):
        self.setWindowTitle("Select Process to Track")
        self.setFixedSize(500, 500)
        self.selected_processes = []
        
        self.setStyleSheet("""
            QDialog {
                background-color: #36393f;
                color: #dcddde;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QListWidget {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 5px;
                color: #dcddde;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 8px;
                color: #dcddde;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #f26522;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search processes...")
        self.search_box.textChanged.connect(self.filter_processes)
        layout.addWidget(self.search_box)
        
        self.process_list = QListWidget()
        self.process_list.setSelectionMode(QListWidget.MultiSelection)
        self.populate_processes()
        layout.addWidget(self.process_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_btn = QPushButton("Add Selected")
        add_btn.clicked.connect(self.add_selected)
        button_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_processes(self):
        try:
            self.process_list.clear()
            processes = set()
            
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    if proc.info['exe']:
                        name = os.path.basename(proc.info['exe'])
                        processes.add((name, proc.info['exe']))
                except:
                    continue
            
            for name, exe in sorted(processes, key=lambda x: x[0]):
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, (name, exe))
                self.process_list.addItem(item)
        except Exception as e:
            print(f"Error populating processes: {str(e)}")
            raise

    def filter_processes(self):
        try:
            search = self.search_box.text().lower()
            for i in range(self.process_list.count()):
                item = self.process_list.item(i)
                item.setHidden(search not in item.text().lower())
        except Exception as e:
            print(f"Error filtering processes: {str(e)}")

    def add_selected(self):
        try:
            self.selected_processes = [
                item.data(Qt.UserRole) 
                for item in self.process_list.selectedItems()
            ]
            if self.selected_processes:
                self.accept()
        except Exception as e:
            print(f"Error adding selected processes: {str(e)}")
            self.reject()

class TimeTracker(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setup_app()
        except Exception as e:
            print(f"Failed to initialize TimeTracker: {str(e)}")
            raise

    def setup_app(self):
        self.setWindowTitle("Time Tracker")
        self.setGeometry(100, 100, 900, 600)
        
        self.time_data = {}
        self.process_info = {}
        self.active_processes = {}
        
        # Get the directory where the script/executable is located
        if getattr(sys, 'frozen', False):
            # If running as executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # If running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.data_file = os.path.join(app_dir, "time_tracker_data.json")
        print(f"Data file location: {self.data_file}")
        
        # Create a save timer to periodically save data
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_data)
        self.save_timer.start(5000)  # Save every 5 seconds
        
        self.load_data()
        self.setup_ui()
        self.setup_tray()
        self.setup_monitor()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    def setup_ui(self):
        try:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #36393f;
                    color: #dcddde;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLabel {
                    color: #dcddde;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #f26522;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    min-width: 100px;
                }
                QTreeWidget {
                    background-color: #2f3136;
                    border: 1px solid #202225;
                    border-radius: 4px;
                    color: #dcddde;
                    font-size: 14px;
                }
            """)
            
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(15)
            
            header = QLabel("Time Tracker")
            header.setFont(QFont("Segoe UI", 18, QFont.Bold))
            header.setStyleSheet("color: #f26522; margin-bottom: 5px;")
            layout.addWidget(header)
            
            self.status_label = QLabel("Ready to track applications")
            self.status_label.setStyleSheet("color: #b9bbbe; margin-bottom: 15px;")
            layout.addWidget(self.status_label)
            
            btn_frame = QFrame()
            btn_layout = QHBoxLayout(btn_frame)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(10)
            
            add_btn = QPushButton("Add Process")
            add_btn.clicked.connect(self.add_process)
            btn_layout.addWidget(add_btn)
            
            remove_btn = QPushButton("Remove Selected")
            remove_btn.clicked.connect(self.remove_process)
            btn_layout.addWidget(remove_btn)
            
            # Add reset times button
            reset_btn = QPushButton("Reset Times")
            reset_btn.clicked.connect(self.reset_times)
            btn_layout.addWidget(reset_btn)
            
            btn_layout.addStretch()
            layout.addWidget(btn_frame)
            
            self.tree = QTreeWidget()
            self.tree.setHeaderLabels(["Application", "Time", "Status"])
            self.tree.setColumnWidth(0, 250)
            self.tree.setColumnWidth(1, 150)
            self.tree.setColumnWidth(2, 100)
            layout.addWidget(self.tree)
        except Exception as e:
            print(f"Error setting up UI: {str(e)}")
            raise

    def setup_tray(self):
        try:
            # Check if system tray is available
            if not QSystemTrayIcon.isSystemTrayAvailable():
                QMessageBox.critical(None, "System Tray", 
                                   "System tray is not available on this system.")
                return
                
            self.tray = QSystemTrayIcon(self)
            
            # Use custom icon or fallback
            try:
                icon = create_tray_icon()
                self.tray.setIcon(icon)
            except:
                # Fallback to application icon if custom icon fails
                self.tray.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
            
            # Create tray menu
            menu = QMenu()
            
            show_action = QAction("Show Time Tracker", self)
            show_action.triggered.connect(self.show_window)
            menu.addAction(show_action)
            
            hide_action = QAction("Hide", self)
            hide_action.triggered.connect(self.hide)
            menu.addAction(hide_action)
            
            menu.addSeparator()
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_app)
            menu.addAction(quit_action)
            
            self.tray.setContextMenu(menu)
            
            # Handle tray icon double-click
            self.tray.activated.connect(self.tray_icon_activated)
            
            # Show tray icon
            self.tray.show()
            
            # Show notification on first run
            self.tray.showMessage(
                "Time Tracker",
                "Application is running in the system tray. Right-click the icon to access options.",
                QSystemTrayIcon.Information,
                3000
            )
            
        except Exception as e:
            print(f"Error setting up tray: {str(e)}")

    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def show_window(self):
        """Show and raise the window"""
        self.show()
        self.raise_()
        self.activateWindow()

    def setup_monitor(self):
        try:
            self.monitor = ActivityMonitor()
            self.monitor.activity_update.connect(self.update_activity)
            for name, (path, _) in self.process_info.items():
                self.monitor.add_process(name, path)
            self.monitor.start()
        except Exception as e:
            print(f"Error setting up monitor: {str(e)}")
            raise

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.time_data = data.get('time', {})
                self.process_info = data.get('processes', {})
                print(f"Loaded data for {len(self.time_data)} processes from {self.data_file}")
                
                # Debug: Print loaded times
                for name, time_val in self.time_data.items():
                    print(f"  {name}: {self.format_time(time_val)}")
            else:
                print(f"No data file found at {self.data_file}, starting fresh")
                self.time_data = {}
                self.process_info = {}
        except Exception as e:
            print(f"Error loading data from {self.data_file}: {str(e)}")
            self.time_data = {}
            self.process_info = {}

    def save_data(self):
        try:
            # Don't modify the times when saving, just save current state
            # Only update times for currently active processes in memory, not in saved data
            
            data_to_save = {
                'time': dict(self.time_data),  # Create a copy
                'processes': dict(self.process_info)
            }
            
            # Add current session time for active processes to the copy
            current_time = time.time()
            for name, start_time in self.active_processes.items():
                elapsed = current_time - start_time
                if name in data_to_save['time']:
                    data_to_save['time'][name] = self.time_data[name] + elapsed
                else:
                    data_to_save['time'][name] = elapsed
            
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            print(f"Data saved to {self.data_file}")
            # Debug: Print what was saved
            for name, time_val in data_to_save['time'].items():
                if time_val > 0:
                    print(f"  Saved {name}: {self.format_time(time_val)}")
                    
        except Exception as e:
            print(f"Error saving data to {self.data_file}: {str(e)}")

    def add_process(self):
        try:
            dialog = ProcessSelector(self)
            if dialog.exec_() == QDialog.Accepted:
                for name, path in dialog.selected_processes:
                    if name not in self.process_info:
                        self.process_info[name] = (path, "")
                        if name not in self.time_data:
                            self.time_data[name] = 0
                        self.monitor.add_process(name, path)
                self.save_data()
                self.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not add process: {str(e)}")

    def remove_process(self):
        try:
            item = self.tree.currentItem()
            if item:
                name = item.text(0)
                if name in self.process_info:
                    path = self.process_info[name][0]
                    self.monitor.remove_process(name, path)
                    del self.process_info[name]
                    del self.time_data[name]
                    if name in self.active_processes:
                        del self.active_processes[name]
                    self.save_data()
                    self.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not remove process: {str(e)}")

    def reset_times(self):
        """Reset all time data"""
        try:
            reply = QMessageBox.question(self, 'Reset Times', 
                                       'Are you sure you want to reset all tracked times to zero?',
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                for name in self.time_data:
                    self.time_data[name] = 0
                # Also reset any currently active processes
                current_time = time.time()
                for name in self.active_processes:
                    self.active_processes[name] = current_time
                self.save_data()
                self.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not reset times: {str(e)}")

    def update_activity(self, name, path, is_active):
        try:
            current_time = time.time()
            
            if is_active:
                if name not in self.active_processes:
                    self.active_processes[name] = current_time
                    if name not in self.process_info:
                        self.process_info[name] = (path, "")
                    if name not in self.time_data:
                        self.time_data[name] = 0
                    print(f"Process started: {name}")
            else:
                if name in self.active_processes:
                    elapsed = current_time - self.active_processes[name]
                    self.time_data[name] += elapsed
                    del self.active_processes[name]
                    print(f"Process stopped: {name}, added {elapsed:.1f} seconds")
        except Exception as e:
            print(f"Error updating activity: {str(e)}")

    def update_display(self):
        try:
            self.tree.clear()
            current_time = time.time()
            
            for name, total in sorted(self.time_data.items(), 
                                    key=lambda x: x[1], reverse=True):
                current_total = total
                if name in self.active_processes:
                    current_total += current_time - self.active_processes[name]
                
                time_str = self.format_time(current_total)
                
                item = QTreeWidgetItem([
                    name, 
                    time_str,
                    "Running" if name in self.active_processes else "Stopped"
                ])
                
                if name in self.active_processes:
                    item.setForeground(0, QColor("#f26522"))
                    item.setForeground(1, QColor("#f26522"))
                    item.setForeground(2, QColor("#f26522"))
                
                self.tree.addTopLevelItem(item)
            
            active = len(self.active_processes)
            self.status_label.setText(
                f"Tracking {len(self.time_data)} applications ({active} active)")
        except Exception as e:
            print(f"Error updating display: {str(e)}")

    def format_time(self, seconds):
        try:
            seconds = int(seconds)
            days = seconds // (24 * 3600)
            seconds %= (24 * 3600)
            hours = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0 or days > 0:
                parts.append(f"{hours:02d}h")
            if minutes > 0 or hours > 0 or days > 0:
                parts.append(f"{minutes:02d}m")
            parts.append(f"{seconds:02d}s")
            
            return " ".join(parts)
        except Exception as e:
            print(f"Error formatting time: {str(e)}")
            return "0s"

    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray.isVisible():
            self.save_data()  # Save before hiding
            self.tray.showMessage(
                "Time Tracker",
                "Application was minimized to tray. Double-click the tray icon to restore.",
                QSystemTrayIcon.Information,
                2000
            )
            self.hide()
            event.ignore()
        else:
            self.quit_app()

    def quit_app(self):
        """Properly quit the application"""
        try:
            print("Quitting application...")
            # Save current times before quitting
            current_time = time.time()
            for name, start_time in self.active_processes.items():
                elapsed = current_time - start_time
                self.time_data[name] += elapsed
                print(f"Final save for {name}: +{elapsed:.1f} seconds")
            
            self.save_data()  # Final save
            self.monitor.stop()
            self.monitor.wait(2000)
            if hasattr(self, 'tray'):
                self.tray.hide()
            QApplication.quit()
        except Exception as e:
            print(f"Error quitting: {str(e)}")
            QApplication.quit()

class ActivityMonitor(QThread):
    activity_update = pyqtSignal(str, str, bool)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.tracked_processes = {}
        self.active_processes = set()
    
    def add_process(self, name, path):
        try:
            self.tracked_processes[path.lower()] = name
        except Exception as e:
            print(f"Error adding process to monitor: {str(e)}")
    
    def remove_process(self, name, path):
        try:
            if path.lower() in self.tracked_processes:
                del self.tracked_processes[path.lower()]
        except Exception as e:
            print(f"Error removing process from monitor: {str(e)}")
    
    def run(self):
        try:
            while self.running:
                current = set()
                for proc in psutil.process_iter(['exe']):
                    try:
                        if proc.info['exe']:
                            path = proc.info['exe'].lower()
                            if path in self.tracked_processes:
                                name = self.tracked_processes[path]
                                current.add(name)
                                if name not in self.active_processes:
                                    self.activity_update.emit(name, path, True)
                    except:
                        continue
                
                stopped = self.active_processes - current
                for name in stopped:
                    self.activity_update.emit(name, "", False)
                
                self.active_processes = current
                time.sleep(2)
        except Exception as e:
            print(f"Monitor error: {str(e)}")
            self.activity_update.emit("", "", False)
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        window = TimeTracker()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {str(e)}")
        QMessageBox.critical(None, "Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)