import sys
import os
import time
import threading
import psutil
import win32pipe
import win32file
import pywintypes
import win32con
import win32job
import win32api
import hashlib
import uuid
import json
import base64
from cryptography.fernet import Fernet
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit,
    QHBoxLayout, QStackedWidget, QMessageBox, QFrame, QSystemTrayIcon, 
    QMenu, QStyle
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QPixmap, QPainter, QLinearGradient

# Security and licensing
LICENSE_FILE = "tealip_license.tlp"
ENCRYPTION_KEY = b'pRmgMa8T0InjA48xctTd1Wv4a8mJ3X6S7FbPeShJyWo='  # In real use, generate dynamically
HWID = hashlib.sha256((str(win32api.GetVolumeInformation("C:\\")[1]) + 
                      uuid.getnode().to_bytes(6, 'big').hex()).encode()).hexdigest()

# Global state
valorant_running = False
stopped_once = False
current_job = None
pipe_threads = []
pipe_handles = []
monitor_thread = None
monitored_pids = set()
monitored_lock = threading.Lock()
monitoring_active = False
shutdown_event = threading.Event()
licensed = False

# System functions
def encrypt_data(data):
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(data.encode()).decode()

def decrypt_data(data):
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(data.encode()).decode()

def check_license(key):
    if key == "ZETA-OMNIPOTENT-ALPHA":  # Master key for Alpha
        return True
        
    try:
        if not os.path.exists(LICENSE_FILE):
            return False
            
        with open(LICENSE_FILE, 'r') as f:
            license_data = json.loads(decrypt_data(f.read()))
            
        return license_data['hwid'] == HWID and license_data['key'] == key
    except:
        return False

def save_license(key):
    license_data = {
        'hwid': HWID,
        'key': key,
        'timestamp': int(time.time())
    }
    with open(LICENSE_FILE, 'w') as f:
        f.write(encrypt_data(json.dumps(license_data)))

# Bypass core functions
def stop_and_restart_vgc():
    os.system('sc stop vgc')
    time.sleep(0.5)
    os.system('sc start vgc')
    time.sleep(0.5)

def override_vgc_pipe(pipe_name=r'\\.\pipe\933823D3-C77B-4BAE-89D7-A92B567236BC'):
    try:
        pipe = win32file.CreateFile(
            pipe_name,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0, None, win32con.OPEN_EXISTING, 0, None)
        win32file.CloseHandle(pipe)
    except Exception:
        pass

def handle_client(pipe):
    global stopped_once
    try:
        while not shutdown_event.is_set():
            try:
                data = win32file.ReadFile(pipe, 4096)
                if data:
                    if not stopped_once:
                        os.system('sc stop vgc')
                        stopped_once = True
                    win32file.WriteFile(pipe, data[1])
            except pywintypes.error as e:
                if e.winerror == 109:
                    break
                time.sleep(0.1)
    finally:
        try:
            win32file.CloseHandle(pipe)
        except Exception:
            pass

def create_named_pipe(pipe_name):
    global pipe_handles
    while not shutdown_event.is_set():
        try:
            pipe = win32pipe.CreateNamedPipe(
                pipe_name,
                win32con.PIPE_ACCESS_DUPLEX,
                win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_WAIT,
                win32con.PIPE_UNLIMITED_INSTANCES,
                1048576, 1048576, 500, None)
            pipe_handles.append(pipe)
            win32pipe.ConnectNamedPipe(pipe, None)
            t = threading.Thread(target=handle_client, args=(pipe,), daemon=True)
            t.start()
            pipe_threads.append(t)
        except Exception:
            time.sleep(1)

def create_job_object():
    job = win32job.CreateJobObject(None, "")
    extended_info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
    extended_info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, extended_info)
    return job

def assign_valorant_to_job():
    global current_job
    if current_job:
        win32job.TerminateJobObject(current_job, 0)
        current_job.Close()
        current_job = None
        time.sleep(2)
    current_job = create_job_object()
    found = False
    while not found and not shutdown_event.is_set():
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and "VALORANT-Win64-Shipping.exe" in proc.info['name']:
                    h_process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, proc.info['pid'])
                    win32job.AssignProcessToJobObject(current_job, h_process)
                    found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if not found:
            time.sleep(1)

def launch_valorant():
    os.system('"C:\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=valorant --launch-patchline=live')
    assign_valorant_to_job()

def start_valorant():
    global valorant_running, current_job
    if not valorant_running:
        threading.Thread(target=launch_valorant, daemon=True).start()
        valorant_running = True
    else:
        if current_job:
            win32job.TerminateJobObject(current_job, 0)
            current_job.Close()
            current_job = None
        os.system('taskkill /f /im VALORANT-Win64-Shipping.exe')
        valorant_running = False

def monitor_new_exes():
    global monitored_pids, monitoring_active
    prev_pids = set(p.info['pid'] for p in psutil.process_iter(['pid']))
    while monitoring_active and not shutdown_event.is_set():
        current_pids = set(p.info['pid'] for p in psutil.process_iter(['pid']))
        new_pids = current_pids - prev_pids
        with monitored_lock:
            for pid in new_pids:
                try:
                    proc = psutil.Process(pid)
                    exe = proc.exe()
                    if exe:
                        monitored_pids.add(pid)
                except Exception:
                    continue
        prev_pids = current_pids
        time.sleep(0.5)

def start_monitoring_exes():
    global monitoring_active, monitor_thread, monitored_pids
    with monitored_lock:
        monitored_pids.clear()
    monitoring_active = True
    monitor_thread = threading.Thread(target=monitor_new_exes, daemon=True)
    monitor_thread.start()

def stop_monitoring_exes():
    global monitoring_active, monitor_thread
    monitoring_active = False
    if monitor_thread:
        monitor_thread.join(timeout=2)
        monitor_thread = None

def kill_monitored_exes():
    killed = []
    with monitored_lock:
        for pid in list(monitored_pids):
            try:
                proc = psutil.Process(pid)
                exe = proc.exe()
                if exe and proc.is_running():
                    proc.kill()
                    killed.append(exe)
            except Exception:
                pass
        monitored_pids.clear()
    return killed

def reset_shutdown_event():
    global shutdown_event
    shutdown_event = threading.Event()

def close_all_pipes():
    global pipe_handles
    for h in pipe_handles:
        try:
            win32file.CloseHandle(h)
        except Exception:
            pass
    pipe_handles.clear()

def start_with_emulate():
    global stopped_once, valorant_running, current_job, pipe_threads
    stopped_once = False
    reset_shutdown_event()
    close_all_pipes()
    pipe_threads.clear()
    if current_job:
        win32job.TerminateJobObject(current_job, 0)
        current_job.Close()
        current_job = None
    stop_and_restart_vgc()
    override_vgc_pipe()
    threading.Thread(target=create_named_pipe, args=(r'\\.\pipe\933823D3-C77B-4BAE-89D7-A92B567236BC',), daemon=True).start()
    start_monitoring_exes()
    threading.Thread(target=launch_valorant, daemon=True).start()
    valorant_running = True

def safe_exit():
    global valorant_running, current_job, stopped_once, pipe_threads
    shutdown_event.set()
    stopped_once = False
    for t in pipe_threads:
        t.join(timeout=1)
    pipe_threads.clear()
    close_all_pipes()
    if current_job:
        win32job.TerminateJobObject(current_job, 0)
        current_job.Close()
        current_job = None
    os.system('taskkill /f /im VALORANT-Win64-Shipping.exe')
    os.system('sc stop vgc')
    valorant_running = False
    stop_monitoring_exes()
    kill_monitored_exes()

# UI Components
class GradientFrame(QFrame):
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(90, 0, 180))
        gradient.setColorAt(0.5, QColor(140, 0, 255))
        gradient.setColorAt(1.0, QColor(60, 0, 120))
        painter.fillRect(self.rect(), gradient)

class TealipBypassApp(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = None
        self.licensed = False
        self.tray_icon = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Tealip Bypass - Zeta Realm")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(450, 400)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Gradient title bar
        title_bar = GradientFrame()
        title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(15, 0, 15, 0)
        
        self.title_label = QLabel("Tealip Bypass")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #E81123;
                border-radius: 15px;
            }
        """)
        close_btn.clicked.connect(self.close_app)
        
        title_bar_layout.addWidget(self.title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.create_activation_page()
        self.create_main_page()
        
        self.setLayout(main_layout)
        
        # Check license
        self.check_existing_license()
        
        # Setup tray icon
        self.setup_tray_icon()
        
    def create_activation_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel()
        icon_pixmap = QPixmap(":lock.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title = QLabel("Activation Required")
        title.setStyleSheet("""
            QLabel {
                color: #5a00b4;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # HWID
        hwid_label = QLabel(f"HWID: {HWID[:16]}...{HWID[-16:]}")
        hwid_label.setStyleSheet("""
            QLabel {
                color: #444;
                font-size: 12px;
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        hwid_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter activation key")
        self.key_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #d0d0d0;
                border-radius: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #8a2be2;
            }
        """)
        
        # Buttons
        activate_btn = QPushButton("Activate")
        activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #8a2be2;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #7a1ad2;
            }
        """)
        activate_btn.clicked.connect(self.activate_license)
        
        copy_hwid_btn = QPushButton("Copy HWID")
        copy_hwid_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0d0f0;
                color: #5a00b4;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d0c0e0;
            }
        """)
        copy_hwid_btn.clicked.connect(self.copy_hwid)
        
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(hwid_label)
        layout.addWidget(self.key_input)
        layout.addWidget(activate_btn)
        layout.addWidget(copy_hwid_btn)
        layout.addStretch()
        
        page.setLayout(layout)
        self.stacked_widget.addWidget(page)
    
    def create_main_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #5a00b4;
                padding: 10px;
                background-color: #f0e6ff;
                border-radius: 10px;
                border: 1px solid #d0c0e0;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        self.start_button = QPushButton("Start Valorant")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #e0d0f0;
                color: #5a00b4;
                font-size: 16px;
                padding: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #d0c0e0;
            }
        """)
        self.start_button.clicked.connect(self.toggle_start_stop)
        
        self.emulate_button = QPushButton("Start with Emulate")
        self.emulate_button.setStyleSheet("""
            QPushButton {
                background-color: #d0c0e0;
                color: #5a00b4;
                font-size: 16px;
                padding: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #c0b0d0;
            }
        """)
        self.emulate_button.clicked.connect(self.start_with_emulate_ui)
        
        self.safe_exit_button = QPushButton("Safe Exit")
        self.safe_exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f0e0e0;
                color: #b45a5a;
                font-size: 16px;
                padding: 14px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e0d0d0;
            }
        """)
        self.safe_exit_button.clicked.connect(self.safe_exit_ui)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.emulate_button)
        layout.addWidget(self.safe_exit_button)
        layout.addStretch()
        
        # HWID info
        hwid_info = QLabel(f"Licensed to HWID: {HWID[:8]}...")
        hwid_info.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 10px;
            }
        """)
        hwid_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hwid_info)
        
        page.setLayout(layout)
        self.stacked_widget.addWidget(page)
    
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close_app)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def check_existing_license(self):
        global licensed
        try:
            if os.path.exists(LICENSE_FILE):
                with open(LICENSE_FILE, 'r') as f:
                    license_data = json.loads(decrypt_data(f.read()))
                    if license_data['hwid'] == HWID:
                        licensed = True
                        self.stacked_widget.setCurrentIndex(1)
                        return
        except:
            pass
            
        licensed = False
        self.stacked_widget.setCurrentIndex(0)
    
    def activate_license(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Invalid Key", "Please enter a valid activation key")
            return
            
        if check_license(key):
            save_license(key)
            global licensed
            licensed = True
            self.stacked_widget.setCurrentIndex(1)
            QMessageBox.information(self, "Activation Successful", "Product activated successfully!\nWelcome to Tealip Bypass")
        else:
            QMessageBox.critical(self, "Activation Failed", "Invalid activation key!\nPlease contact your provider")
    
    def copy_hwid(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(HWID)
        QMessageBox.information(self, "HWID Copied", "Your HWID has been copied to clipboard")
    
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
    
    def toggle_start_stop(self):
        global valorant_running
        if not licensed:
            QMessageBox.warning(self, "Not Licensed", "Please activate your copy first")
            return
            
        if not valorant_running:
            self.status_label.setText("Status: Starting Valorant...")
            threading.Thread(target=self.start_valorant_ui, daemon=True).start()
        else:
            self.status_label.setText("Status: Stopping Valorant...")
            start_valorant()
            self.update_status()
    
    def start_valorant_ui(self):
        start_valorant()
        self.update_status()
    
    def start_with_emulate_ui(self):
        if not licensed:
            QMessageBox.warning(self, "Not Licensed", "Please activate your copy first")
            return
            
        self.status_label.setText("Status: Starting with emulate...")
        threading.Thread(target=self.do_emulate_and_update, daemon=True).start()
    
    def do_emulate_and_update(self):
        start_with_emulate()
        self.update_status()
    
    def safe_exit_ui(self):
        if not licensed:
            QMessageBox.warning(self, "Not Licensed", "Please activate your copy first")
            return
            
        self.status_label.setText("Status: Safe exit...")
        threading.Thread(target=self.do_safe_exit_and_update, daemon=True).start()
    
    def do_safe_exit_and_update(self):
        safe_exit()
        self.update_status()
    
    def update_status(self):
        global valorant_running
        if valorant_running:
            self.start_button.setText("Stop Valorant")
            self.status_label.setText("Status: Valorant running")
        else:
            self.start_button.setText("Start Valorant")
            self.status_label.setText("Status: Valorant stopped")
    
    def close_app(self):
        safe_exit()
        self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(50, 0, 100))
    app.setPalette(palette)
    
    # Create and show window
    window = TealipBypassApp()
    window.show()
    sys.exit(app.exec())