import sys
import os
import random
import json
import logging
import threading
import subprocess
import time
import psutil
import winreg
from datetime import datetime, timedelta
from pathlib import Path
from obswebsocket import obsws, requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QGroupBox,
    QFileDialog, QPlainTextEdit, QTimeEdit, QGridLayout, QMessageBox, 
    QComboBox, QProgressBar, QFrame, QScrollArea, QSizePolicy, QSpacerItem,
    QSystemTrayIcon, QMenu, QSlider, QSpinBox, QTextEdit, QSplashScreen
)
from PyQt6.QtCore import (
    QThread, pyqtSignal, QTimer, QTime, Qt, QPropertyAnimation, QEasingCurve,
    QRect, QSettings, QStandardPaths
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QColor, QLinearGradient, QIcon, QAction,
    QPalette, QBrush
)

# --- ENHANCED CONFIGURATION & CONSTANTS ---
class Config:
    def __init__(self):
        self.app_name = "AutoStream Pro"
        self.version = "2.0"
        self.settings = QSettings("AutoStreamPro", "AutoStreamPro")
        
        # Smart paths
        self.config_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.log_file = self.config_dir / "autostream.log"
        
        # Default video directories (smart detection)
        self.default_video_dirs = [
            Path.home() / "Videos",
            Path.home() / "Desktop",
            Path.home() / "Documents" / "Videos",
            Path("C:/Users/Public/Videos") if os.name == 'nt' else Path("/Users/Shared/Videos")
        ]
        
        # OBS detection paths
        self.obs_paths = [
            r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
            r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
            "/Applications/OBS.app/Contents/MacOS/OBS",
            "/usr/bin/obs",
            "/snap/bin/obs-studio"
        ]

config = Config()

# Enhanced logging setup
logging.basicConfig(
    filename=config.log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

# --- ENHANCED HELPER FUNCTIONS & CLASSES ---

class SystemDetector:
    """Smart system detection and setup"""
    
    @staticmethod
    def find_obs_path():
        """Enhanced OBS detection with registry check on Windows"""
        # Check if OBS is already running
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if 'obs' in proc.info['name'].lower():
                    return proc.info['exe']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check registry on Windows
        if os.name == 'nt':
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    if 'obs' in subkey_name.lower():
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            obs_exe = Path(install_location) / "bin" / "64bit" / "obs64.exe"
                            if obs_exe.exists():
                                return str(obs_exe)
                        except FileNotFoundError:
                            pass
                        winreg.CloseKey(subkey)
                winreg.CloseKey(key)
            except Exception:
                pass
        
        # Check default paths
        for path in config.obs_paths:
            if Path(path).exists():
                return path
        
        return None
    
    @staticmethod
    def find_video_files():
        """Smart video file detection"""
        video_extensions = {'.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv', '.webm', '.m4v'}
        found_videos = []
        
        for video_dir in config.default_video_dirs:
            if video_dir.exists():
                for file_path in video_dir.rglob('*'):
                    if file_path.suffix.lower() in video_extensions:
                        found_videos.append(file_path)
        
        return found_videos[:50]  # Limit to 50 for performance
    
    @staticmethod
    def is_obs_running():
        """Check if OBS is currently running"""
        for proc in psutil.process_iter(['name']):
            try:
                if 'obs' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

class SetupWizard(QMainWindow):
    """First-time setup wizard with Apple-like design"""
    
    setup_complete = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_data = {}
        self.current_step = 0
        self.steps = ["Welcome", "OBS Detection", "Video Setup", "Streaming Setup", "Complete"]
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("AutoStream Pro - Setup")
        self.setFixedSize(600, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px;
            }
            QWidget {
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.steps) - 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                height: 20px;
            }
            QProgressBar::chunk {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        layout.addWidget(self.content_area)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Continue")
        self.next_btn.clicked.connect(self.go_next)
        
        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.next_btn)
        layout.addLayout(button_layout)
        
        self.show_step(0)
    
    def show_step(self, step):
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        self.progress_bar.setValue(step)
        
        if step == 0:  # Welcome
            self.show_welcome()
        elif step == 1:  # OBS Detection
            self.show_obs_detection()
        elif step == 2:  # Video Setup
            self.show_video_setup()
        elif step == 3:  # Streaming Setup
            self.show_streaming_setup()
        elif step == 4:  # Complete
            self.show_complete()
        
        self.back_btn.setEnabled(step > 0)
        self.next_btn.setText("Finish" if step == len(self.steps) - 1 else "Continue")
    
    def show_welcome(self):
        title = QLabel("Welcome to AutoStream Pro")
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Let's get you set up for effortless streaming")
        subtitle.setStyleSheet("font-size: 16px; opacity: 0.8; margin-bottom: 40px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        features = QLabel("✨ Automatic OBS detection\n🎥 Smart video discovery\n⏰ Intelligent scheduling\n🎛️ One-click streaming")
        features.setStyleSheet("font-size: 14px; line-height: 1.8;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.content_layout.addWidget(title)
        self.content_layout.addWidget(subtitle)
        self.content_layout.addWidget(features)
        self.content_layout.addStretch()
    
    def show_obs_detection(self):
        title = QLabel("OBS Studio Detection")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        
        self.obs_status = QLabel("Searching for OBS Studio...")
        self.obs_status.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        
        self.obs_path_label = QLabel("")
        self.obs_path_label.setStyleSheet("font-size: 12px; opacity: 0.7;")
        self.obs_path_label.setWordWrap(True)
        
        self.content_layout.addWidget(title)
        self.content_layout.addWidget(self.obs_status)
        self.content_layout.addWidget(self.obs_path_label)
        self.content_layout.addStretch()
        
        # Start OBS detection
        QTimer.singleShot(1000, self.detect_obs)
    
    def detect_obs(self):
        obs_path = SystemDetector.find_obs_path()
        if obs_path:
            self.obs_status.setText("✅ OBS Studio found!")
            self.obs_path_label.setText(f"Location: {obs_path}")
            self.setup_data['obs_path'] = obs_path
        else:
            self.obs_status.setText("⚠️ OBS Studio not found")
            self.obs_path_label.setText("Please install OBS Studio or manually set the path later.")
            self.setup_data['obs_path'] = None
    
    def show_video_setup(self):
        title = QLabel("Video Discovery")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        
        self.video_status = QLabel("Scanning for video files...")
        self.video_status.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        
        self.video_list = QLabel("")
        self.video_list.setStyleSheet("font-size: 12px; opacity: 0.7;")
        self.video_list.setWordWrap(True)
        
        self.content_layout.addWidget(title)
        self.content_layout.addWidget(self.video_status)
        self.content_layout.addWidget(self.video_list)
        self.content_layout.addStretch()
        
        QTimer.singleShot(1000, self.scan_videos)
    
    def scan_videos(self):
        videos = SystemDetector.find_video_files()
        if videos:
            self.video_status.setText(f"✅ Found {len(videos)} video files")
            video_names = [v.name for v in videos[:5]]
            if len(videos) > 5:
                video_names.append(f"... and {len(videos) - 5} more")
            self.video_list.setText("\n".join(video_names))
            self.setup_data['videos'] = [str(v) for v in videos]
        else:
            self.video_status.setText("⚠️ No video files found")
            self.video_list.setText("You can add videos later.")
            self.setup_data['videos'] = []
    
    def show_streaming_setup(self):
        title = QLabel("Streaming Configuration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        
        form_layout = QVBoxLayout()
        
        # Scene name
        form_layout.addWidget(QLabel("Scene Name:"))
        self.scene_input = QLineEdit("AutoStream")
        self.scene_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        form_layout.addWidget(self.scene_input)
        
        # Media source name
        form_layout.addWidget(QLabel("Media Source Name:"))
        self.media_input = QLineEdit("Video Source")
        self.media_input.setStyleSheet(self.scene_input.styleSheet())
        form_layout.addWidget(self.media_input)
        
        self.content_layout.addWidget(title)
        self.content_layout.addLayout(form_layout)
        self.content_layout.addStretch()
    
    def show_complete(self):
        title = QLabel("Setup Complete! 🎉")
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        message = QLabel("AutoStream Pro is ready to use.\nYou can now start streaming with just one click!")
        message.setStyleSheet("font-size: 16px; line-height: 1.6;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.content_layout.addWidget(title)
        self.content_layout.addWidget(message)
        self.content_layout.addStretch()
    
    def go_next(self):
        if self.current_step == 3:  # Streaming setup
            self.setup_data['scene_name'] = self.scene_input.text()
            self.setup_data['media_source_name'] = self.media_input.text()
        
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step(self.current_step)
        else:
            self.setup_complete.emit(self.setup_data)
            self.close()
    
    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step(self.current_step)

class ModernStreamWorker(QThread):
    """Enhanced streaming worker with better error handling and features"""
    
    finished = pyqtSignal()
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    
    def __init__(self, config_data):
        super().__init__()
        self.config = config_data
        self.is_running = True
        self.obs_ws = None
    
    def run(self):
        try:
            self.status_signal.emit("Connecting to OBS...")
            self.connect_to_obs()
            
            self.status_signal.emit("Starting stream...")
            self.setup_stream()
            
            self.status_signal.emit("Streaming live!")
            self.stream_loop()
            
        except Exception as e:
            self.log_signal.emit(f"Stream error: {e}")
            self.status_signal.emit("Stream failed")
        finally:
            self.cleanup()
    
    def connect_to_obs(self):
        """Enhanced OBS connection with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.obs_ws = obsws(
                    self.config.get('obs_websocket_ip', '127.0.0.1'),
                    self.config.get('obs_websocket_port', 4455)
                )
                self.obs_ws.connect()
                self.log_signal.emit("Connected to OBS WebSocket")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log_signal.emit(f"Connection attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    raise e
    
    def setup_stream(self):
        """Setup streaming with smart media source handling"""
        # Ensure scene exists
        try:
            self.obs_ws.call(requests.SetCurrentProgramScene(self.config['scene_name']))
        except:
            self.log_signal.emit(f"Scene '{self.config['scene_name']}' not found, using current scene")
        
        # Start streaming
        self.obs_ws.call(requests.StartStream())
        
        # Setup video playback if configured
        if self.config.get('videos') and self.config.get('randomize', True):
            video = random.choice(self.config['videos'])
            self.play_video(video)
    
    def play_video(self, video_path):
        """Play a specific video"""
        try:
            self.obs_ws.call(requests.SetInputSettings(
                inputName=self.config['media_source_name'],
                inputSettings={
                    "local_file": str(video_path),
                    "looping": False,
                    "restart_on_activate": True
                }
            ))
            self.log_signal.emit(f"Playing: {Path(video_path).name}")
        except Exception as e:
            self.log_signal.emit(f"Failed to play video: {e}")
    
    def stream_loop(self):
        """Main streaming loop with progress tracking"""
        duration = self.config.get('duration_minutes', 0)
        if duration > 0:
            total_seconds = duration * 60
            elapsed = 0
            while self.is_running and elapsed < total_seconds:
                time.sleep(1)
                elapsed += 1
                progress = int((elapsed / total_seconds) * 100)
                self.progress_signal.emit(progress)
        else:
            # Stream indefinitely
            while self.is_running:
                time.sleep(1)
    
    def cleanup(self):
        """Enhanced cleanup"""
        try:
            if self.obs_ws:
                self.obs_ws.call(requests.StopStream())
                self.obs_ws.disconnect()
                self.log_signal.emit("Disconnected from OBS")
        except Exception as e:
            self.log_signal.emit(f"Cleanup error: {e}")
        finally:
            self.finished.emit()
    
    def stop(self):
        self.is_running = False

class AutoStreamProApp(QMainWindow):
    """Enhanced main application with modern UI"""
    
    def __init__(self):
        super().__init__()
        self.config_data = {}
        self.stream_worker = None
        self.obs_process = None
        self.system_tray = None
        
        # Check if first run
        if not config.config_file.exists():
            self.show_setup_wizard()
        else:
            self.load_config()
            self.init_ui()
            self.show()
    
    def show_setup_wizard(self):
        """Show setup wizard for first-time users"""
        self.setup_wizard = SetupWizard()
        self.setup_wizard.setup_complete.connect(self.on_setup_complete)
        self.setup_wizard.show()
    
    def on_setup_complete(self, setup_data):
        """Handle setup completion"""
        # Create default config with setup data
        self.config_data = {
            'obs_path': setup_data.get('obs_path'),
            'scene_name': setup_data.get('scene_name', 'AutoStream'),
            'media_source_name': setup_data.get('media_source_name', 'Video Source'),
            'obs_websocket_ip': '127.0.0.1',
            'obs_websocket_port': 4455,
            'videos': setup_data.get('videos', []),
            'randomize': True,
            'duration_minutes': 0,
            'scheduler_enabled': False,
            'schedule': {},
            'auto_start_obs': True,
            'minimize_to_tray': True
        }
        self.save_config()
        self.init_ui()
        self.show()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(config.config_file, 'r') as f:
                self.config_data = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            self.config_data = {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(config.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def init_ui(self):
        """Initialize the modern UI"""
        self.setWindowTitle(f"{config.app_name} v{config.version}")
        self.setFixedSize(800, 900)
        
        # Set application icon (you would add your icon file)
        # self.setWindowIcon(QIcon("icon.png"))
        
        # Modern styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                color: #212529;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 15px;
                background: white;
                color: #495057;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4e63c6, stop:1 #5e3e7e);
            }
            QPushButton:disabled {
                background: #adb5bd;
                color: #6c757d;
            }
            QLineEdit, QComboBox, QSpinBox {
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #667eea;
            }
            QLabel {
                color: #495057;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #dee2e6;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #667eea;
                border-color: #667eea;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background: #e9ecef;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
            }
            QPlainTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-family: 'SF Mono', Monaco, monospace;
                font-size: 12px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        self.create_header(main_layout)
        
        # Status panel
        self.create_status_panel(main_layout)
        
        # Quick controls
        self.create_quick_controls(main_layout)
        
        # Settings panels
        self.create_video_panel(main_layout)
        self.create_streaming_panel(main_layout)
        self.create_scheduler_panel(main_layout)
        
        # Log panel
        self.create_log_panel(main_layout)
        
        # System tray
        self.setup_system_tray()
        
        # Auto-update UI
        self.update_ui_from_config()
        
        # Status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def create_header(self, layout):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # App title and version
        title_layout = QVBoxLayout()
        title = QLabel(config.app_name)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #667eea;")
        version = QLabel(f"Version {config.version}")
        version.setStyleSheet("font-size: 12px; color: #6c757d;")
        title_layout.addWidget(title)
        title_layout.addWidget(version)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 20px; color: #28a745;")
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Status:"))
        header_layout.addWidget(self.status_indicator)
        
        layout.addWidget(header_frame)
    
    def create_status_panel(self, layout):
        """Create status panel"""
        status_group = QGroupBox("System Status")
        status_layout = QGridLayout(status_group)
        
        # OBS Status
        self.obs_status_label = QLabel("OBS: Checking...")
        self.obs_status_icon = QLabel("⚪")
        status_layout.addWidget(QLabel("OBS Studio:"), 0, 0)
        status_layout.addWidget(self.obs_status_icon, 0, 1)
        status_layout.addWidget(self.obs_status_label, 0, 2)
        
        # Video Status
        self.video_status_label = QLabel("Videos: Checking...")
        self.video_status_icon = QLabel("⚪")
        status_layout.addWidget(QLabel("Video Files:"), 1, 0)
        status_layout.addWidget(self.video_status_icon, 1, 1)
        status_layout.addWidget(self.video_status_label, 1, 2)
        
        # Stream Status
        self.stream_status_label = QLabel("Ready to stream")
        self.stream_status_icon = QLabel("⚪")
        status_layout.addWidget(QLabel("Stream:"), 2, 0)
        status_layout.addWidget(self.stream_status_icon, 2, 1)
        status_layout.addWidget(self.stream_status_label, 2, 2)
        
        # Progress bar for active streams
        self.stream_progress = QProgressBar()
        self.stream_progress.setVisible(False)
        status_layout.addWidget(self.stream_progress, 3, 0, 1, 3)
        
        layout.addWidget(status_group)
    
    def create_quick_controls(self, layout):
        """Create quick control buttons"""
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        
        # Main stream button
        self.stream_btn = QPushButton("🔴 Go Live")
        self.stream_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 15px 30px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a52);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5252, stop:1 #e53935);
            }
        """)
        self.stream_btn.clicked.connect(self.toggle_stream)
        
        # Quick setup button
        self.quick_setup_btn = QPushButton("⚙️ Quick Setup")
        self.quick_setup_btn.clicked.connect(self.show_quick_setup)
        
        # Auto-start OBS button
        self.obs_btn = QPushButton("📺 Launch OBS")
        self.obs_btn.clicked.connect(self.launch_obs)
        
        controls_layout.addWidget(self.stream_btn)
        controls_layout.addWidget(self.quick_setup_btn)
        controls_layout.addWidget(self.obs_btn)
        
        layout.addWidget(controls_frame)
    
    def create_video_panel(self, layout):
        """Create video management panel"""
        video_group = QGroupBox("📹 Video Management")
        video_layout = QVBoxLayout(video_group)
        
        # Video selection buttons
        button_layout = QHBoxLayout()
        
        select_files_btn = QPushButton("Select Videos")
        select_files_btn.clicked.connect(self.select_video_files)
        
        select_folder_btn = QPushButton("Select Folder")
        select_folder_btn.clicked.connect(self.select_video_folder)
        
        auto_discover_btn = QPushButton("Auto-Discover")
        auto_discover_btn.clicked.connect(self.auto_discover_videos)
        
        button_layout.addWidget(select_files_btn)
        button_layout.addWidget(select_folder_btn)
        button_layout.addWidget(auto_discover_btn)
        
        # Video list display
        self.video_info_label = QLabel("No videos selected")
        self.video_info_label.setWordWrap(True)
        self.video_info_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        
        # Playback options
        options_layout = QHBoxLayout()
        
        self.randomize_cb = QCheckBox("🎲 Random playback")
        self.randomize_cb.setChecked(True)
        
        self.loop_cb = QCheckBox("🔄 Loop videos")
        self.loop_cb.setChecked(False)
        
        options_layout.addWidget(self.randomize_cb)
        options_layout.addWidget(self.loop_cb)
        options_layout.addStretch()
        
        video_layout.addLayout(button_layout)
        video_layout.addWidget(self.video_info_label)
        video_layout.addLayout(options_layout)
        
        layout.addWidget(video_group)
    
    def create_streaming_panel(self, layout):
        """Create streaming configuration panel"""
        stream_group = QGroupBox("🎛️ Streaming Configuration")
        stream_layout = QGridLayout(stream_group)
        
        # Scene settings
        stream_layout.addWidget(QLabel("Scene Name:"), 0, 0)
        self.scene_input = QLineEdit()
        stream_layout.addWidget(self.scene_input, 0, 1)
        
        stream_layout.addWidget(QLabel("Media Source:"), 1, 0)
        self.media_source_input = QLineEdit()
        stream_layout.addWidget(self.media_source_input, 1, 1)
        
        # Duration settings
        stream_layout.addWidget(QLabel("Stream Duration:"), 2, 0)
        duration_layout = QHBoxLayout()
        
        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 999)
        self.duration_input.setSuffix(" minutes")
        self.duration_input.setSpecialValueText("Unlimited")
        
        duration_layout.addWidget(self.duration_input)
        duration_layout.addStretch()
        
        stream_layout.addLayout(duration_layout, 2, 1)
        
        # WebSocket settings (advanced)
        advanced_btn = QPushButton("Advanced Settings")
        advanced_btn.clicked.connect(self.show_advanced_settings)
        stream_layout.addWidget(advanced_btn, 3, 0, 1, 2)
        
        layout.addWidget(stream_group)
    
    def create_scheduler_panel(self, layout):
        """Create scheduler panel"""
        scheduler_group = QGroupBox("⏰ Smart Scheduler")
        scheduler_layout = QVBoxLayout(scheduler_group)
        
        # Enable scheduler
        self.scheduler_enabled_cb = QCheckBox("Enable automatic scheduling")
        self.scheduler_enabled_cb.toggled.connect(self.toggle_scheduler)
        scheduler_layout.addWidget(self.scheduler_enabled_cb)
        
        # Schedule grid
        self.schedule_frame = QFrame()
        schedule_layout = QGridLayout(self.schedule_frame)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.schedule_controls = {}
        
        for i, day in enumerate(days):
            day_cb = QCheckBox(day)
            time_edit = QTimeEdit(QTime(19, 0))  # Default 7:00 PM
            duration_spin = QSpinBox()
            duration_spin.setRange(15, 480)  # 15 minutes to 8 hours
            duration_spin.setValue(60)
            duration_spin.setSuffix(" min")
            
            self.schedule_controls[day] = {
                'enabled': day_cb,
                'time': time_edit,
                'duration': duration_spin
            }
            
            schedule_layout.addWidget(day_cb, i, 0)
            schedule_layout.addWidget(time_edit, i, 1)
            schedule_layout.addWidget(duration_spin, i, 2)
        
        self.schedule_frame.setEnabled(False)
        scheduler_layout.addWidget(self.schedule_frame)
        
        layout.addWidget(scheduler_group)
    
    def create_log_panel(self, layout):
        """Create log panel"""
        log_group = QGroupBox("📋 Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        
        save_log_btn = QPushButton("Save Log")
        save_log_btn.clicked.connect(self.save_log)
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(save_log_btn)
        log_controls.addStretch()
        
        # Log display
        self.log_display = QPlainTextEdit()
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        
        log_layout.addLayout(log_controls)
        log_layout.addWidget(self.log_display)
        
        layout.addWidget(log_group)
    
    def setup_system_tray(self):
        """Setup system tray functionality"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.system_tray = QSystemTrayIcon(self)
            # self.system_tray.setIcon(QIcon("icon.png"))  # Add your icon
            
            tray_menu = QMenu()
            
            show_action = QAction("Show AutoStream Pro", self)
            show_action.triggered.connect(self.show)
            
            stream_action = QAction("Toggle Stream", self)
            stream_action.triggered.connect(self.toggle_stream)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_application)
            
            tray_menu.addAction(show_action)
            tray_menu.addAction(stream_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            
            self.system_tray.setContextMenu(tray_menu)
            self.system_tray.show()
    
    def update_ui_from_config(self):
        """Update UI elements from configuration"""
        self.scene_input.setText(self.config_data.get('scene_name', 'AutoStream'))
        self.media_source_input.setText(self.config_data.get('media_source_name', 'Video Source'))
        self.duration_input.setValue(self.config_data.get('duration_minutes', 0))
        self.randomize_cb.setChecked(self.config_data.get('randomize', True))
        self.scheduler_enabled_cb.setChecked(self.config_data.get('scheduler_enabled', False))
        
        # Update video info
        self.update_video_info()
        
        # Update schedule
        schedule = self.config_data.get('schedule', {})
        for day, controls in self.schedule_controls.items():
            if day in schedule:
                controls['enabled'].setChecked(True)
                time_str = schedule[day].get('time', '19:00')
                hour, minute = map(int, time_str.split(':'))
                controls['time'].setTime(QTime(hour, minute))
                controls['duration'].setValue(schedule[day].get('duration', 60))
    
    def update_video_info(self):
        """Update video information display"""
        videos = self.config_data.get('videos', [])
        if not videos:
            self.video_info_label.setText("🎥 No videos selected\n\nClick 'Auto-Discover' to find videos automatically, or use 'Select Videos' to choose manually.")
        else:
            video_count = len(videos)
            total_size = sum(Path(v).stat().st_size for v in videos if Path(v).exists()) / (1024*1024*1024)  # GB
            self.video_info_label.setText(f"📹 {video_count} videos selected\n💾 Total size: {total_size:.1f} GB\n\n📁 Recent videos:\n" + 
                                        "\n".join([f"• {Path(v).name}" for v in videos[:5]]))
    
    def update_status(self):
        """Update system status indicators"""
        # Check OBS status
        if SystemDetector.is_obs_running():
            self.obs_status_label.setText("Running")
            self.obs_status_icon.setText("🟢")
            self.obs_status_icon.setStyleSheet("color: #28a745;")
        else:
            self.obs_status_label.setText("Not running")
            self.obs_status_icon.setText("🔴")
            self.obs_status_icon.setStyleSheet("color: #dc3545;")
        
        # Check video status
        videos = self.config_data.get('videos', [])
        if videos:
            valid_videos = [v for v in videos if Path(v).exists()]
            if len(valid_videos) == len(videos):
                self.video_status_label.setText(f"{len(videos)} videos ready")
                self.video_status_icon.setText("🟢")
                self.video_status_icon.setStyleSheet("color: #28a745;")
            else:
                self.video_status_label.setText(f"{len(valid_videos)}/{len(videos)} videos available")
                self.video_status_icon.setText("🟡")
                self.video_status_icon.setStyleSheet("color: #ffc107;")
        else:
            self.video_status_label.setText("No videos")
            self.video_status_icon.setText("🔴")
            self.video_status_icon.setStyleSheet("color: #dc3545;")
    
    def toggle_stream(self):
        """Toggle streaming on/off"""
        if self.stream_worker and self.stream_worker.isRunning():
            self.stop_stream()
        else:
            self.start_stream()
    
    def start_stream(self):
        """Start streaming with enhanced error handling"""
        try:
            # Validate configuration
            if not self.validate_stream_config():
                return
            
            # Update config from UI
            self.update_config_from_ui()
            
            # Auto-launch OBS if needed
            if self.config_data.get('auto_start_obs', True) and not SystemDetector.is_obs_running():
                self.launch_obs()
                time.sleep(3)  # Wait for OBS to start
            
            # Start streaming worker
            self.stream_worker = ModernStreamWorker(self.config_data)
            self.stream_worker.log_signal.connect(self.add_log)
            self.stream_worker.progress_signal.connect(self.update_progress)
            self.stream_worker.status_signal.connect(self.update_stream_status)
            self.stream_worker.finished.connect(self.on_stream_finished)
            self.stream_worker.start()
            
            # Update UI
            self.stream_btn.setText("⏹️ Stop Stream")
            self.stream_btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 15px 30px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #28a745, stop:1 #20c997);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #218838, stop:1 #1e9687);
                }
            """)
            
            if self.config_data.get('duration_minutes', 0) > 0:
                self.stream_progress.setVisible(True)
                self.stream_progress.setValue(0)
            
            self.add_log("🔴 Stream started successfully!")
            
        except Exception as e:
            self.add_log(f"❌ Failed to start stream: {e}")
            QMessageBox.critical(self, "Stream Error", f"Failed to start stream:\n{e}")
    
    def stop_stream(self):
        """Stop active stream"""
        if self.stream_worker:
            self.stream_worker.stop()
            self.add_log("⏹️ Stopping stream...")
    
    def on_stream_finished(self):
        """Handle stream completion"""
        self.stream_btn.setText("🔴 Go Live")
        self.stream_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 15px 30px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a52);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5252, stop:1 #e53935);
            }
        """)
        
        self.stream_progress.setVisible(False)
        self.stream_status_label.setText("Stream ended")
        self.stream_status_icon.setText("⚪")
        self.stream_worker = None
    
    def validate_stream_config(self):
        """Validate streaming configuration"""
        if not self.config_data.get('obs_path'):
            QMessageBox.warning(self, "Configuration Error", 
                              "OBS Studio path not configured. Please run setup or configure manually.")
            return False
        
        if not Path(self.config_data['obs_path']).exists():
            QMessageBox.warning(self, "Configuration Error", 
                              "OBS Studio executable not found. Please check your installation.")
            return False
        
        if not self.config_data.get('videos'):
            reply = QMessageBox.question(self, "No Videos", 
                                       "No videos are configured. Continue with empty stream?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return False
        
        return True
    
    def update_config_from_ui(self):
        """Update configuration from UI elements"""
        self.config_data.update({
            'scene_name': self.scene_input.text(),
            'media_source_name': self.media_source_input.text(),
            'duration_minutes': self.duration_input.value(),
            'randomize': self.randomize_cb.isChecked(),
            'scheduler_enabled': self.scheduler_enabled_cb.isChecked()
        })
        
        # Update schedule
        schedule = {}
        for day, controls in self.schedule_controls.items():
            if controls['enabled'].isChecked():
                schedule[day] = {
                    'time': controls['time'].time().toString("HH:mm"),
                    'duration': controls['duration'].value()
                }
        self.config_data['schedule'] = schedule
        
        self.save_config()
    
    def update_progress(self, progress):
        """Update stream progress"""
        self.stream_progress.setValue(progress)
    
    def update_stream_status(self, status):
        """Update stream status"""
        self.stream_status_label.setText(status)
        if "live" in status.lower():
            self.stream_status_icon.setText("🔴")
            self.stream_status_icon.setStyleSheet("color: #dc3545;")
        elif "connecting" in status.lower() or "starting" in status.lower():
            self.stream_status_icon.setText("🟡")
            self.stream_status_icon.setStyleSheet("color: #ffc107;")
    
    def launch_obs(self):
        """Launch OBS Studio"""
        obs_path = self.config_data.get('obs_path')
        if obs_path and Path(obs_path).exists():
            try:
                self.obs_process = subprocess.Popen([obs_path])
                self.add_log("📺 Launching OBS Studio...")
            except Exception as e:
                self.add_log(f"❌ Failed to launch OBS: {e}")
                QMessageBox.critical(self, "Launch Error", f"Failed to launch OBS:\n{e}")
        else:
            QMessageBox.warning(self, "Configuration Error", "OBS Studio path not configured.")
    
    def select_video_files(self):
        """Select individual video files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", 
            str(Path.home() / "Videos"),
            "Video Files (*.mp4 *.mov *.mkv *.avi *.wmv *.flv *.webm *.m4v)"
        )
        if files:
            self.config_data['videos'] = files
            self.update_video_info()
            self.save_config()
            self.add_log(f"📹 Selected {len(files)} video files")
    
    def select_video_folder(self):
        """Select video folder"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Video Folder",
            str(Path.home() / "Videos")
        )
        if folder:
            videos = []
            video_extensions = {'.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv', '.webm', '.m4v'}
            for file_path in Path(folder).rglob('*'):
                if file_path.suffix.lower() in video_extensions:
                    videos.append(str(file_path))
            
            self.config_data['videos'] = videos
            self.config_data['video_folder'] = folder
            self.update_video_info()
            self.save_config()
            self.add_log(f"📁 Selected folder with {len(videos)} videos")
    
    def auto_discover_videos(self):
        """Auto-discover video files"""
        self.add_log("🔍 Auto-discovering videos...")
        videos = SystemDetector.find_video_files()
        
        if videos:
            self.config_data['videos'] = [str(v) for v in videos]
            self.update_video_info()
            self.save_config()
            self.add_log(f"✨ Auto-discovered {len(videos)} videos")
        else:
            self.add_log("❌ No videos found during auto-discovery")
            QMessageBox.information(self, "No Videos Found", 
                                  "No video files were found in common locations.\n\n"
                                  "Try using 'Select Videos' or 'Select Folder' to manually choose your videos.")
    
    def show_quick_setup(self):
        """Show quick setup dialog"""
        self.show_setup_wizard()
    
    def show_advanced_settings(self):
        """Show advanced settings dialog"""
        dialog = AdvancedSettingsDialog(self.config_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config_data.update(dialog.get_settings())
            self.save_config()
    
    def toggle_scheduler(self, enabled):
        """Toggle scheduler functionality"""
        self.schedule_frame.setEnabled(enabled)
        if enabled:
            self.add_log("⏰ Scheduler enabled")
            # Start scheduler timer
            if not hasattr(self, 'scheduler_timer'):
                self.scheduler_timer = QTimer()
                self.scheduler_timer.timeout.connect(self.check_schedule)
            self.scheduler_timer.start(60000)  # Check every minute
        else:
            self.add_log("⏰ Scheduler disabled")
            if hasattr(self, 'scheduler_timer'):
                self.scheduler_timer.stop()
    
    def check_schedule(self):
        """Check if scheduled stream should start"""
        if not self.scheduler_enabled_cb.isChecked():
            return
        
        if self.stream_worker and self.stream_worker.isRunning():
            return  # Already streaming
        
        now = datetime.now()
        current_day = now.strftime("%A")
        
        schedule = self.config_data.get('schedule', {})
        if current_day in schedule:
            scheduled_time = datetime.strptime(schedule[current_day]['time'], "%H:%M").time()
            if now.hour == scheduled_time.hour and now.minute == scheduled_time.minute:
                duration = schedule[current_day].get('duration', 60)
                self.config_data['duration_minutes'] = duration
                self.add_log(f"⏰ Scheduled stream starting: {current_day} at {scheduled_time}")
                self.start_stream()
    
    def add_log(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_display.appendPlainText(formatted_message)
        logging.info(message)
    
    def clear_log(self):
        """Clear log display"""
        self.log_display.clear()
        self.add_log("📋 Log cleared")
    
    def save_log(self):
        """Save log to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Log File", f"autostream_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_display.toPlainText())
                self.add_log(f"💾 Log saved to {filename}")
            except Exception as e:
                self.add_log(f"❌ Failed to save log: {e}")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.config_data.get('minimize_to_tray', True) and self.system_tray:
            event.ignore()
            self.hide()
            if self.system_tray:
                self.system_tray.showMessage(
                    "AutoStream Pro",
                    "Application minimized to tray",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        else:
            self.quit_application()
    
    def quit_application(self):
        """Properly quit the application"""
        if self.stream_worker and self.stream_worker.isRunning():
            self.stream_worker.stop()
            self.stream_worker.wait()
        
        self.save_config()
        QApplication.instance().quit()

class AdvancedSettingsDialog(QDialog):
    """Advanced settings dialog"""
    
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.config_data = config_data.copy()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Advanced Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # WebSocket settings
        ws_group = QGroupBox("OBS WebSocket Settings")
        ws_layout = QGridLayout(ws_group)
        
        ws_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.ip_input = QLineEdit(self.config_data.get('obs_websocket_ip', '127.0.0.1'))
        ws_layout.addWidget(self.ip_input, 0, 1)
        
        ws_layout.addWidget(QLabel("Port:"), 1, 0)
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(self.config_data.get('obs_websocket_port', 4455))
        ws_layout.addWidget(self.port_input, 1, 1)
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QVBoxLayout(app_group)
        
        self.auto_start_obs_cb = QCheckBox("Auto-start OBS Studio")
        self.auto_start_obs_cb.setChecked(self.config_data.get('auto_start_obs', True))
        
        self.minimize_to_tray_cb = QCheckBox("Minimize to system tray")
        self.minimize_to_tray_cb.setChecked(self.config_data.get('minimize_to_tray', True))
        
        self.start_with_windows_cb = QCheckBox("Start with Windows")
        self.start_with_windows_cb.setChecked(self.config_data.get('start_with_windows', False))
        
        app_layout.addWidget(self.auto_start_obs_cb)
        app_layout.addWidget(self.minimize_to_tray_cb)
        app_layout.addWidget(self.start_with_windows_cb)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(ws_group)
        layout.addWidget(app_group)
        layout.addLayout(button_layout)
    
    def get_settings(self):
        """Get settings from dialog"""
        return {
            'obs_websocket_ip': self.ip_input.text(),
            'obs_websocket_port': self.port_input.value(),
            'auto_start_obs': self.auto_start_obs_cb.isChecked(),
            'minimize_to_tray': self.minimize_to_tray_cb.isChecked(),
            'start_with_windows': self.start_with_windows_cb.isChecked()
        }

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    app.setApplicationVersion(config.version)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray
    
    # Create and show splash screen
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(QColor("#667eea"))
    
    painter = QPainter(splash_pixmap)
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
    painter.drawText(splash_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, config.app_name)
    painter.end()
    
    splash = QSplashScreen(splash_pixmap)
    splash.show()
    
    # Initialize application
    QTimer.singleShot(2000, splash.close)  # Show splash for 2 seconds
    
    window = AutoStreamProApp()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()