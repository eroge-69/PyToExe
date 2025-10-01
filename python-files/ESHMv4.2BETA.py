import sys
import os
import winreg
import subprocess
import ctypes
import json
import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QGroupBox,
    QFormLayout, QDialogButtonBox, QDialog,
    QAbstractItemView, QHeaderView, QCheckBox,
    QSystemTrayIcon, QMenu, QProgressBar, QFrame,
    QSplitter, QScrollArea, QToolButton, QSizePolicy,
    QGridLayout, QSpinBox, QSlider, QToolTip, QStatusBar,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter, QPen, QBrush, QAction, QPalette, QLinearGradient, QCursor

# Constants
APP_NAME = "Segment Heap Manager"
APP_VERSION = "5.0"
TEMP_DIR = os.path.join(os.environ['TEMP'], APP_NAME)
CONFIG_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
LOG_DIR = os.path.join(CONFIG_DIR, "logs")

# Registry paths
SEGMENT_HEAP_KEY = r"SYSTEM\CurrentControlSet\Control\Session Manager\Segment Heap"
SESSION_MANAGER_KEY = r"SYSTEM\CurrentControlSet\Control\Session Manager"
IMAGE_FILE_EXECUTION_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"

# Default heap parameters
DEFAULT_HEAP_PARAMS = {
    'HeapSegmentReserve': 0x00100000,
    'HeapSegmentCommit': 0x00002000,
    'HeapDeCommitTotalFreeThreshold': 0x00010000,
    'HeapDeCommitFreeBlockThreshold': 0x00001000
}

# System applications
SYSTEM_APPS = {
    "svchost.exe", "explorer.exe", "wininit.exe", "services.exe",
    "lsass.exe", "winlogon.exe", "csrss.exe", "smss.exe",
    "dwm.exe", "taskhost.exe", "rundll32.exe", "spoolsv.exe"
}

# Common applications
COMMON_APPS = [
    "chrome.exe", "firefox.exe", "msedge.exe", "explorer.exe",
    "winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe",
    "devenv.exe", "code.exe", "discord.exe", "steam.exe",
    "spotify.exe", "vlc.exe", "teams.exe", "node.exe"
]

# Dark theme colors
BG_COLOR = QColor(25, 25, 35)
CARD_COLOR = QColor(35, 35, 50)
ACCENT_COLOR = QColor(64, 156, 255)
TEXT_COLOR = QColor(220, 220, 220)
SUBTEXT_COLOR = QColor(160, 160, 170)
SUCCESS_COLOR = QColor(76, 175, 80)
WARNING_COLOR = QColor(255, 152, 0)
ERROR_COLOR = QColor(244, 67, 54)

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    """Restart the script with admin privileges."""
    script = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, script, None, 1
    )
    sys.exit(0)

def force_admin():
    """Force the application to run as administrator."""
    if not is_admin():
        restart_as_admin()

class HeapModel:
    """Enhanced data model for heap settings."""
    def __init__(self):
        self.params: Dict[str, Optional[int]] = {}
        self.status: Dict[str, Any] = {'status': 'Unknown', 'detail': 'Not loaded', 'color': QColor(128, 128, 128)}
        self.excluded_apps: List[str] = []
        self.last_backup: Optional[str] = None
        self.performance_metrics: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
    
    def update_status(self, result):
        """Update status from result."""
        self.status = result
        self.add_to_history("status_change", result)
    
    def update_excluded_apps(self, result):
        """Update excluded apps from result."""
        self.excluded_apps = result.get('apps', [])
        self.add_to_history("exclusion_change", result)
    
    def update_params(self, result):
        """Update parameters from result."""
        self.params = result.get('params', {})
        self.add_to_history("param_change", result)
    
    def update_performance_metrics(self, result):
        """Update performance metrics."""
        self.performance_metrics = result
    
    def add_to_history(self, event_type, data):
        """Add event to history."""
        self.history.append({
            'timestamp': datetime.now(),
            'type': event_type,
            'data': data
        })
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]

class ConfigManager:
    """Enhanced configuration manager."""
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
        self.config_file = os.path.join(CONFIG_DIR, "config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "auto_enable": False, 
                "monitor_enabled": False,
                "performance_monitoring": True,
                "notifications": True,
                "backup_frequency": "weekly",
                "advanced_mode": False
            }
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value."""
        self.config[key] = value
        return self.save_config()
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.log")
        try:
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except:
            pass

class PerformanceMonitor(QThread):
    """Thread for monitoring system performance."""
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.interval = 5  # seconds
    
    def run(self):
        """Monitor system performance."""
        while self.running:
            try:
                # Get memory usage
                memory = psutil.virtual_memory()
                
                # Get process list
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory': proc.info['memory_info'].rss
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Sort by memory usage
                processes.sort(key=lambda x: x['memory'], reverse=True)
                
                metrics = {
                    'memory_total': memory.total,
                    'memory_used': memory.used,
                    'memory_percent': memory.percent,
                    'top_processes': processes[:10]
                }
                
                self.metrics_updated.emit(metrics)
                time.sleep(self.interval)
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(self.interval)
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False

class RegistryWorker(QThread):
    """Enhanced worker for registry operations."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, operation: str, *args):
        super().__init__()
        self.operation = operation
        self.args = args
    
    def run(self):
        try:
            if self.operation == 'get_status':
                result = self.get_segment_heap_status()
            elif self.operation == 'set_status':
                result = {'backup_path': self.set_segment_heap_status(self.args[0])}
            elif self.operation == 'get_excluded_apps':
                result = {'apps': self.get_excluded_apps()}
            elif self.operation == 'add_excluded_app':
                result = {'backup_path': self.add_excluded_app(self.args[0])}
            elif self.operation == 'remove_excluded_app':
                result = {'backup_path': self.remove_excluded_app(self.args[0])}
            elif self.operation == 'get_heap_params':
                result = {'params': self.get_heap_params()}
            elif self.operation == 'set_heap_params':
                result = {'backup_path': self.set_heap_params(self.args[0])}
            elif self.operation == 'export_backup':
                result = {'backup_path': self.export_registry_backup()}
            elif self.operation == 'import_backup':
                result = {'success': self.import_registry_backup(self.args[0])}
            elif self.operation == 'batch_remove_apps':
                result = {'removed_count': self.batch_remove_apps(self.args[0])}
            elif self.operation == 'analyze_performance':
                result = self.analyze_performance()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
    
    def get_segment_heap_status(self) -> Dict[str, Any]:
        """Get Segment Heap status."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SEGMENT_HEAP_KEY, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Enabled")
                status = "Enabled" if value == 1 else "Disabled"
                detail = "System will use Segment Heap after restart" if value == 1 else "System will use default LFH after restart"
                color = SUCCESS_COLOR if value == 1 else ERROR_COLOR
                return {'status': status, 'detail': detail, 'color': color}
        except FileNotFoundError:
            return {'status': 'Disabled', 'detail': 'No registry key found', 'color': ERROR_COLOR}
    
    def set_segment_heap_status(self, enable: bool) -> str:
        """Set Segment Heap status."""
        self.progress.emit(25)
        backup_path = self.export_registry_backup()
        self.progress.emit(50)
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, SEGMENT_HEAP_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 1 if enable else 0)
        self.progress.emit(75)
        return backup_path
    
    def get_excluded_apps(self) -> List[str]:
        """Get excluded applications."""
        apps = set()
        for wow_flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, IMAGE_FILE_EXECUTION_KEY, 0, winreg.KEY_READ | wow_flag) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ | wow_flag) as subkey:
                                try:
                                    value, _ = winreg.QueryValueEx(subkey, "FrontEndHeapDebugOptions")
                                    if value == 4:
                                        apps.add(subkey_name)
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except:
                pass
        return sorted(list(apps))
    
    def add_excluded_app(self, app_name: str) -> str:
        """Add application to exclusion list."""
        backup_path = self.export_registry_backup()
        for wow_flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, IMAGE_FILE_EXECUTION_KEY, 0, winreg.KEY_SET_VALUE | wow_flag) as key:
                    with winreg.CreateKeyEx(key, app_name, 0, winreg.KEY_SET_VALUE) as subkey:
                        winreg.SetValueEx(subkey, "FrontEndHeapDebugOptions", 0, winreg.REG_DWORD, 4)
            except:
                pass
        return backup_path
    
    def remove_excluded_app(self, app_name: str) -> str:
        """Remove application from exclusion list."""
        backup_path = self.export_registry_backup()
        for wow_flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, IMAGE_FILE_EXECUTION_KEY, 0, winreg.KEY_SET_VALUE | wow_flag) as key:
                    try:
                        with winreg.OpenKey(key, app_name, 0, winreg.KEY_SET_VALUE | wow_flag) as subkey:
                            try:
                                winreg.DeleteValue(subkey, "FrontEndHeapDebugOptions")
                            except FileNotFoundError:
                                pass
                            try:
                                if winreg.QueryInfoKey(subkey)[1] == 0:
                                    winreg.DeleteKey(key, app_name)
                            except:
                                pass
                    except FileNotFoundError:
                        pass
            except:
                pass
        return backup_path
    
    def get_heap_params(self) -> Dict[str, Optional[int]]:
        """Get heap parameters."""
        params = {}
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SESSION_MANAGER_KEY, 0, winreg.KEY_READ) as key:
                for param in DEFAULT_HEAP_PARAMS:
                    try:
                        value, _ = winreg.QueryValueEx(key, param)
                        params[param] = value
                    except FileNotFoundError:
                        params[param] = None
        except FileNotFoundError:
            for param in DEFAULT_HEAP_PARAMS:
                params[param] = None
        return params
    
    def set_heap_params(self, params_dict: Dict[str, Optional[int]]) -> str:
        """Set heap parameters."""
        backup_path = self.export_registry_backup()
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SESSION_MANAGER_KEY, 0, winreg.KEY_SET_VALUE) as key:
            for param, value in params_dict.items():
                if value is None:
                    try:
                        winreg.DeleteValue(key, param)
                    except FileNotFoundError:
                        pass
                else:
                    winreg.SetValueEx(key, param, 0, winreg.REG_DWORD, value)
        return backup_path
    
    def export_registry_backup(self) -> str:
        """Export registry backup."""
        os.makedirs(TEMP_DIR, exist_ok=True)
        backup_path = os.path.join(TEMP_DIR, f"SegmentHeapBackup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg")
        
        with open(backup_path, 'w', encoding='utf-16') as f:
            f.write("Windows Registry Editor Version 5.00\n\n")
            
            # Backup Segment Heap key
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SEGMENT_HEAP_KEY, 0, winreg.KEY_READ) as key:
                    f.write(f"[HKEY_LOCAL_MACHINE\\{SEGMENT_HEAP_KEY}]\n")
                    try:
                        value, _ = winreg.QueryValueEx(key, "Enabled")
                        f.write(f'"Enabled"=dword:{value:08x}\n')
                    except FileNotFoundError:
                        pass
                    f.write("\n")
            except:
                pass
            
            # Backup Session Manager parameters
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SESSION_MANAGER_KEY, 0, winreg.KEY_READ) as key:
                    f.write(f"[HKEY_LOCAL_MACHINE\\{SESSION_MANAGER_KEY}]\n")
                    for param in DEFAULT_HEAP_PARAMS:
                        try:
                            value, _ = winreg.QueryValueEx(key, param)
                            f.write(f'"{param}"=dword:{value:08x}\n')
                        except FileNotFoundError:
                            pass
                    f.write("\n")
            except:
                pass
            
            # Backup excluded apps
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, IMAGE_FILE_EXECUTION_KEY, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ) as subkey:
                                try:
                                    value, _ = winreg.QueryValueEx(subkey, "FrontEndHeapDebugOptions")
                                    if value == 4:
                                        f.write(f"[HKEY_LOCAL_MACHINE\\{IMAGE_FILE_EXECUTION_KEY}\\{subkey_name}]\n")
                                        f.write('"FrontEndHeapDebugOptions"=dword:00000004\n\n')
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except:
                pass
        
        return backup_path
    
    def import_registry_backup(self, backup_path: str) -> bool:
        """Import registry backup."""
        try:
            subprocess.run(['regedit.exe', '/s', backup_path], check=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            return False
    
    def batch_remove_apps(self, apps: List[str]) -> int:
        """Remove multiple apps."""
        removed_count = 0
        total = len(apps)
        for i, app in enumerate(apps):
            try:
                self.remove_excluded_app(app)
                removed_count += 1
                self.progress.emit(int((i + 1) / total * 100))
            except:
                pass
        return removed_count
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance with Segment Heap."""
        try:
            # Get system uptime
            uptime = ctypes.windll.kernel32.GetTickCount() / 1000
            
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get process list with memory usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory': proc.info['memory_info'].rss
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory'], reverse=True)
            
            return {
                'uptime': uptime,
                'memory_total': memory.total,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'cpu_percent': cpu_percent,
                'top_processes': processes[:10]
            }
        except Exception as e:
            return {'error': str(e)}

class ModernButton(QPushButton):
    """Modern styled button with hover effects and animations."""
    def __init__(self, text, color=None, parent=None):
        super().__init__(text, parent)
        self.default_color = color if color else ACCENT_COLOR
        self.hover_color = QColor(self.default_color.red() + 20, 
                                 self.default_color.green() + 20, 
                                 self.default_color.blue() + 20)
        self.pressed_color = QColor(self.default_color.red() - 20, 
                                   self.default_color.green() - 20, 
                                   self.default_color.blue() - 20)
        self._setup_style()
        self._setup_animation()
    
    def _setup_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({self.default_color.red()}, {self.default_color.green()}, {self.default_color.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgb({self.hover_color.red()}, {self.hover_color.green()}, {self.hover_color.blue()});
            }}
            QPushButton:pressed {{
                background-color: rgb({self.pressed_color.red()}, {self.pressed_color.green()}, {self.pressed_color.blue()});
            }}
        """)
    
    def _setup_animation(self):
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shadow.setColor(QColor(self.default_color.red(), self.default_color.green(), self.default_color.blue(), 120))
    
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.shadow.setColor(QColor(0, 0, 0, 80))

class ModernCard(QFrame):
    """Modern styled card widget with dark theme."""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({CARD_COLOR.red()}, {CARD_COLOR.green()}, {CARD_COLOR.blue()});
                border-radius: 10px;
                border: 1px solid rgb(50, 50, 65);
            }}
        """)
        
        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(5)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self.shadow)
        
        if title:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(16, 16, 16, 16)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            title_label.setStyleSheet(f"color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()}); margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            self.content_layout = QVBoxLayout()
            layout.addLayout(self.content_layout)
        else:
            self.content_layout = QVBoxLayout(self)
            self.content_layout.setContentsMargins(16, 16, 16, 16)

class ParameterEditDialog(QDialog):
    """Enhanced dialog for editing heap parameters with dark theme."""
    def __init__(self, current_params: Dict[str, Optional[int]], parent=None):
        super().__init__(parent)
        self.current_params = current_params
        self.param_widgets = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Edit Heap Parameters")
        self.setMinimumWidth(700)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid rgb(60, 60, 80);
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QLineEdit {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgb({ACCENT_COLOR.red() + 20}, {ACCENT_COLOR.green() + 20}, {ACCENT_COLOR.blue() + 20});
            }}
            QPushButton:pressed {{
                background-color: rgb({ACCENT_COLOR.red() - 20}, {ACCENT_COLOR.green() - 20}, {ACCENT_COLOR.blue() - 20});
            }}
        """)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        param_info = {
            'HeapSegmentReserve': {
                'label': 'Heap Segment Reserve',
                'description': 'Virtual memory to reserve per segment (default: 1 MB)',
                'default': DEFAULT_HEAP_PARAMS['HeapSegmentReserve']
            },
            'HeapSegmentCommit': {
                'label': 'Heap Segment Commit',
                'description': 'Physical memory to commit upfront (default: 8 KB)',
                'default': DEFAULT_HEAP_PARAMS['HeapSegmentCommit']
            },
            'HeapDeCommitTotalFreeThreshold': {
                'label': 'Heap DeCommit Total Free Threshold',
                'description': 'Total free memory threshold (default: 64 KB)',
                'default': DEFAULT_HEAP_PARAMS['HeapDeCommitTotalFreeThreshold']
            },
            'HeapDeCommitFreeBlockThreshold': {
                'label': 'Heap DeCommit Free Block Threshold',
                'description': 'Free block size threshold (default: 4 KB)',
                'default': DEFAULT_HEAP_PARAMS['HeapDeCommitFreeBlockThreshold']
            }
        }
        
        for param, info in param_info.items():
            param_group = QGroupBox(info['label'])
            param_layout = QHBoxLayout(param_group)
            
            current_value = self.current_params.get(param, None)
            current_text = f"0x{current_value:08x} ({self.format_byte_size(current_value)})" if current_value is not None else "Using Windows default"
            
            current_label = QLabel(f"Current: {current_text}")
            current_label.setMinimumWidth(200)
            param_layout.addWidget(current_label)
            
            input_widget = QLineEdit()
            input_widget.setPlaceholderText("Enter value")
            param_layout.addWidget(input_widget)
            
            unit_combo = QComboBox()
            unit_combo.addItems(["Bytes", "KB", "MB"])
            unit_combo.setCurrentIndex(1)
            param_layout.addWidget(unit_combo)
            
            # Create reset function with proper closure
            def make_reset_func(p, w, u, default_val):
                def reset_to_default():
                    if default_val >= 0x100000:
                        w.setText(str(default_val // 0x100000))
                        u.setCurrentIndex(2)
                    elif default_val >= 0x400:
                        w.setText(str(default_val // 0x400))
                        u.setCurrentIndex(1)
                    else:
                        w.setText(str(default_val))
                        u.setCurrentIndex(0)
                return reset_to_default
            
            reset_btn = ModernButton("Reset to Default", QColor(100, 100, 100))
            reset_btn.clicked.connect(make_reset_func(param, input_widget, unit_combo, info['default']))
            param_layout.addWidget(reset_btn)
            
            self.param_widgets[param] = {
                'input': input_widget,
                'unit': unit_combo,
                'default': info['default']
            }
            
            form_layout.addRow(param_group)
            
            desc_label = QLabel(info['description'])
            desc_label.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()}); font-size: 9pt; margin-left: 10px;")
            form_layout.addRow("", desc_label)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def format_byte_size(self, bytes_value: int) -> str:
        """Format byte size in human-readable format."""
        if bytes_value is None:
            return "N/A"
        if bytes_value == 0:
            return "0 B"
        sizes = ["B", "KB", "MB", "GB"]
        index = 0
        value = float(bytes_value)
        while value >= 1024 and index < len(sizes) - 1:
            value /= 1024
            index += 1
        return f"{value:.1f} {sizes[index]}"
    
    def get_parameters(self) -> Optional[Dict[str, Optional[int]]]:
        """Get the parameter values from the dialog."""
        params_dict = {}
        errors = []
        
        for param, widgets in self.param_widgets.items():
            input_text = widgets['input'].text().strip()
            unit = widgets['unit'].currentText()
            
            if not input_text:
                params_dict[param] = self.current_params.get(param)
                continue
            
            try:
                value = float(input_text)
                if unit == "KB":
                    value *= 1024
                elif unit == "MB":
                    value *= 1024 * 1024
                value = int(value)
                
                if value <= 0:
                    errors.append(f"{param}: Value must be greater than 0")
                elif value > 0xFFFFFFFF:
                    errors.append(f"{param}: Value too large (max: 4 GB)")
                else:
                    params_dict[param] = value
            except ValueError:
                errors.append(f"{param}: Invalid numeric value")
        
        if errors:
            QMessageBox.critical(
                self, "Validation Error",
                "Please fix the following errors:\n\n" + "\n".join(errors)
            )
            return None
        
        return params_dict

class BaseTab(QWidget):
    """Base class for tabs with enhanced functionality."""
    def __init__(self, model=None, config_manager=None):
        super().__init__()
        self.model = model
        self.config_manager = config_manager
        self.workers = []
        self.updating = False
        self.progress_dialog = None
    
    def show_error(self, message):
        """Show an error message box."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        msg.exec()
        self.config_manager.log(f"Error: {message}", "ERROR")
    
    def show_success(self, message):
        """Show a success message box."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Success")
        msg.setInformativeText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        msg.exec()
        self.config_manager.log(f"Success: {message}")
    
    def show_info(self, message):
        """Show an info message box."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Information")
        msg.setInformativeText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        msg.exec()
        self.config_manager.log(f"Info: {message}")
    
    def prompt_restart(self):
        """Prompt the user to restart the system."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Restart Required")
        msg.setInformativeText("Changes have been saved successfully!\n\nA system restart is required for changes to take effect.\n\nWould you like to restart now?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.restart_system()
    
    def restart_system(self):
        """Restart the system."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Confirm Restart")
        msg.setInformativeText("Are you sure you want to restart the system now?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                subprocess.run(["shutdown", "/r", "/t", "0"], check=True, 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                self.show_error("Failed to restart system")
    
    def create_worker(self, operation, *args, callback=None, error_callback=None, progress_callback=None):
        """Create and start a worker thread."""
        if self.updating:
            return None
            
        self.updating = True
        worker = RegistryWorker(operation, *args)
        if callback:
            worker.finished.connect(callback)
        if error_callback:
            worker.error.connect(error_callback)
        else:
            worker.error.connect(self.show_error)
        if progress_callback:
            worker.progress.connect(progress_callback)
        worker.finished.connect(lambda: setattr(self, 'updating', False))
        worker.error.connect(lambda: setattr(self, 'updating', False))
        self.workers.append(worker)
        worker.start()
        return worker

class StatusTab(BaseTab):
    """Enhanced tab for managing Segment Heap status with dark theme."""
    def __init__(self, model=None, config_manager=None):
        super().__init__(model, config_manager)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Status card
        status_card = ModernCard("Segment Heap Status")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(15)
        
        # Status indicator and text
        status_info_layout = QHBoxLayout()
        
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(32, 32)
        status_info_layout.addWidget(self.status_indicator)
        
        status_text_layout = QVBoxLayout()
        self.status_label = QLabel("Checking status...")
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});")
        status_text_layout.addWidget(self.status_label)
        
        self.detail_label = QLabel("Please wait...")
        self.detail_label.setFont(QFont("Segoe UI", 10))
        self.detail_label.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        status_text_layout.addWidget(self.detail_label)
        
        status_info_layout.addLayout(status_text_layout)
        status_info_layout.addStretch()
        
        status_layout.addLayout(status_info_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.enable_btn = ModernButton("Enable Segment Heap", SUCCESS_COLOR)
        self.enable_btn.clicked.connect(self.enable_segment_heap)
        button_layout.addWidget(self.enable_btn)
        
        self.disable_btn = ModernButton("Disable Segment Heap", ERROR_COLOR)
        self.disable_btn.clicked.connect(self.disable_segment_heap)
        button_layout.addWidget(self.disable_btn)
        
        self.restart_btn = ModernButton("Restart Now", ERROR_COLOR)
        self.restart_btn.clicked.connect(self.restart_system)
        button_layout.addWidget(self.restart_btn)
        
        self.refresh_btn = ModernButton("Refresh Status", ACCENT_COLOR)
        self.refresh_btn.clicked.connect(self.update_status)
        button_layout.addWidget(self.refresh_btn)
        
        status_layout.addLayout(button_layout)
        status_card.content_layout.addLayout(status_layout)
        main_layout.addWidget(status_card)
        
        # Auto-enable section
        auto_enable_card = ModernCard("Automatic Re-enabling")
        auto_enable_layout = QVBoxLayout()
        auto_enable_layout.setSpacing(10)
        
        info_text = QLabel(
            "Windows updates sometimes disable Segment Heap. Enable this option to automatically re-enable it after updates."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        auto_enable_layout.addWidget(info_text)
        
        auto_enable_control_layout = QHBoxLayout()
        
        self.auto_enable_checkbox = QCheckBox("Automatically re-enable Segment Heap after Windows updates")
        self.auto_enable_checkbox.setChecked(self.config_manager.get("auto_enable", False))
        self.auto_enable_checkbox.stateChanged.connect(self.toggle_auto_enable)
        self.auto_enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid rgb(70, 70, 90);
                background-color: rgb(50, 50, 65);
            }}
            QCheckBox::indicator:checked {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTggM0w0IDdMMiA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
        """)
        auto_enable_control_layout.addWidget(self.auto_enable_checkbox)
        
        auto_enable_control_layout.addStretch()
        
        self.monitor_status_label = QLabel("Monitor: Not installed")
        self.monitor_status_label.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        auto_enable_control_layout.addWidget(self.monitor_status_label)
        
        self.install_monitor_btn = ModernButton("Install Monitor", ACCENT_COLOR)
        self.install_monitor_btn.clicked.connect(self.install_monitor)
        auto_enable_control_layout.addWidget(self.install_monitor_btn)
        
        auto_enable_layout.addLayout(auto_enable_control_layout)
        auto_enable_card.content_layout.addLayout(auto_enable_layout)
        main_layout.addWidget(auto_enable_card)
        
        # Performance section
        performance_card = ModernCard("Performance Impact")
        performance_layout = QVBoxLayout()
        performance_layout.setSpacing(10)
        
        self.performance_label = QLabel("Analyzing performance impact...")
        self.performance_label.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        performance_layout.addWidget(self.performance_label)
        
        self.analyze_btn = ModernButton("Analyze Performance", ACCENT_COLOR)
        self.analyze_btn.clicked.connect(self.analyze_performance)
        performance_layout.addWidget(self.analyze_btn)
        
        performance_card.content_layout.addLayout(performance_layout)
        main_layout.addWidget(performance_card)
        
        # Backup history
        backup_card = ModernCard("Backup History")
        backup_layout = QVBoxLayout()
        backup_layout.setSpacing(10)
        
        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet(f"""
            QListWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
            }}
            QListWidget::item:hover {{
                background-color: rgb(60, 60, 80);
            }}
        """)
        self.backup_list.itemDoubleClicked.connect(self.restore_from_backup)
        backup_layout.addWidget(self.backup_list)
        
        self.update_backup_list_btn = ModernButton("Refresh Backup List", ACCENT_COLOR)
        self.update_backup_list_btn.clicked.connect(self.update_backup_list)
        backup_layout.addWidget(self.update_backup_list_btn)
        
        backup_card.content_layout.addLayout(backup_layout)
        main_layout.addWidget(backup_card)
        
        main_layout.addStretch()
        
        # Initial updates
        self.update_backup_list()
        self.update_status()
        self.check_monitor_status()
    
    def check_monitor_status(self):
        """Check if the monitor is installed."""
        try:
            # Check if the scheduled task exists
            result = subprocess.run(
                ['schtasks', '/query', '/tn', 'SegmentHeapMonitor'],
                capture_output=True, text=True, 
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                self.monitor_status_label.setText("Monitor: Installed")
                self.install_monitor_btn.setText("Uninstall Monitor")
            else:
                self.monitor_status_label.setText("Monitor: Not installed")
                self.install_monitor_btn.setText("Install Monitor")
        except Exception:
            self.monitor_status_label.setText("Monitor: Status unknown")
    
    def install_monitor(self):
        """Install or uninstall the monitor."""
        try:
            # Check if the task exists
            result = subprocess.run(
                ['schtasks', '/query', '/tn', 'SegmentHeapMonitor'],
                capture_output=True, text=True, 
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            
            if result.returncode == 0:
                # Task exists, uninstall it
                subprocess.run(
                    ['schtasks', '/delete', '/tn', 'SegmentHeapMonitor', '/f'],
                    check=True, capture_output=True, 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self.show_success("Monitor uninstalled successfully")
                self.config_manager.set("monitor_enabled", False)
            else:
                # Task doesn't exist, install it
                # Write the monitor script
                os.makedirs(CONFIG_DIR, exist_ok=True)
                monitor_script_path = os.path.join(CONFIG_DIR, "monitor.py")
                
                with open(monitor_script_path, 'w') as f:
                    f.write('''import os
import sys
import winreg
import json
import subprocess
import ctypes
from datetime import datetime

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"auto_enable": False, "last_check": None}

def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception:
        pass

def get_segment_heap_status():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                          r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Segment Heap", 
                          0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "Enabled")
            return value == 1
    except (FileNotFoundError, OSError):
        return False

def set_segment_heap_status(enable):
    try:
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Segment Heap", 
                               0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 1 if enable else 0)
        return True
    except Exception:
        return False

def check_windows_updates():
    try:
        # Get system uptime
        uptime = ctypes.windll.kernel32.GetTickCount() / 1000
        
        # If system was restarted in the last 24 hours, consider it a potential update
        return uptime < 86400  # 24 hours in seconds
    except Exception:
        return False

def main():
    if not is_admin():
        return
    
    # Load configuration
    config = load_config()
    
    # Check if auto-enable is enabled
    if not config.get("auto_enable", False):
        return
    
    # Check last check time
    last_check = config.get("last_check")
    now = datetime.now().isoformat()
    
    # Skip if we checked in the last 6 hours
    if last_check:
        last_check_time = datetime.fromisoformat(last_check)
        if (datetime.now() - last_check_time).total_seconds() < 21600:  # 6 hours
            return
    
    # Update last check time
    config["last_check"] = now
    save_config(config)
    
    # Get current status
    current_status = get_segment_heap_status()
    
    # Check if Windows updates were installed
    updates_installed = check_windows_updates()
    
    # If Segment Heap is disabled and updates were installed, re-enable it
    if not current_status and updates_installed:
        set_segment_heap_status(True)

if __name__ == "__main__":
    main()
''')
                
                # Create the scheduled task
                task_cmd = f'schtasks /create /tn "SegmentHeapMonitor" /tr "{sys.executable} \\"{monitor_script_path}\\"" /sc onlogon /rl highest /f'
                subprocess.run(task_cmd, check=True, shell=True, 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                self.show_success("Monitor installed successfully")
                self.config_manager.set("monitor_enabled", True)
            
            # Update UI
            self.check_monitor_status()
        except Exception as e:
            self.show_error(f"Failed to install/uninstall monitor: {str(e)}")
    
    def toggle_auto_enable(self, state):
        """Toggle the auto-enable option."""
        enabled = state == Qt.CheckState.Checked.value
        self.config_manager.set("auto_enable", enabled)
        
        if enabled and not self.config_manager.get("monitor_enabled", False):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setText("Install Monitor")
            msg.setInformativeText("To automatically re-enable Segment Heap after updates, you need to install the monitor.\n\nWould you like to install it now?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                    color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                }}
                QMessageBox QLabel {{
                    color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                }}
                QPushButton {{
                    background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
            """)
            
            if msg.exec() == QMessageBox.StandardButton.Yes:
                self.install_monitor()
    
    def update_status(self):
        """Update the Segment Heap status display."""
        self.create_worker('get_status', callback=self.on_status_updated)
    
    def on_status_updated(self, result):
        """Handle status update result."""
        self.model.update_status(result)
        
        # Update UI
        self.status_label.setText(result['status'])
        self.detail_label.setText(result['detail'])
        
        # Update status indicator
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(result['color']))
        painter.drawEllipse(2, 2, 28, 28)
        painter.end()
        
        self.status_indicator.setPixmap(pixmap)
        
        # Update button states
        self.enable_btn.setEnabled(result['status'] != 'Enabled')
        self.disable_btn.setEnabled(result['status'] != 'Disabled')
    
    def enable_segment_heap(self):
        """Enable Segment Heap."""
        self.create_worker('set_status', True, callback=self.on_status_set)
    
    def disable_segment_heap(self):
        """Disable Segment Heap."""
        self.create_worker('set_status', False, callback=self.on_status_set)
    
    def on_status_set(self, result):
        """Handle status set result."""
        backup_path = result.get('backup_path')
        if backup_path:
            self.model.last_backup = backup_path
            self.update_backup_list()
            self.show_success("Segment Heap status updated successfully")
            self.prompt_restart()
    
    def analyze_performance(self):
        """Analyze performance impact of Segment Heap."""
        self.performance_label.setText("Analyzing performance impact...")
        self.create_worker('analyze_performance', callback=self.on_performance_analyzed)
    
    def on_performance_analyzed(self, result):
        """Handle performance analysis result."""
        if 'error' in result:
            self.performance_label.setText(f"Error analyzing performance: {result['error']}")
            return
        
        self.model.update_performance_metrics(result)
        
        # Format the results
        uptime_hours = result.get('uptime', 0) / 3600
        memory_used_gb = result.get('memory_used', 0) / (1024**3)
        memory_total_gb = result.get('memory_total', 0) / (1024**3)
        cpu_percent = result.get('cpu_percent', 0)
        
        self.performance_label.setText(
            f"System Uptime: {uptime_hours:.1f} hours\n"
            f"Memory Usage: {memory_used_gb:.2f} GB / {memory_total_gb:.2f} GB\n"
            f"CPU Usage: {cpu_percent:.1f}%\n"
            f"Top Memory Consumers: {', '.join([p['name'] for p in result.get('top_processes', [])[:3]])}"
        )
    
    def update_backup_list(self):
        """Update the backup history list."""
        self.backup_list.clear()
        
        # Get all backup files
        backup_files = []
        try:
            for file in os.listdir(TEMP_DIR):
                if file.startswith("SegmentHeapBackup_") and file.endswith(".reg"):
                    path = os.path.join(TEMP_DIR, file)
                    backup_files.append((os.path.getmtime(path), path))
        except:
            pass
        
        # Sort by modification time (newest first)
        backup_files.sort(reverse=True)
        
        # Add to list
        for _, path in backup_files[:10]:  # Show only the last 10
            filename = os.path.basename(path)
            self.backup_list.addItem(filename)
    
    def restore_from_backup(self, item):
        """Restore settings from a backup file."""
        filename = item.text()
        backup_path = os.path.join(TEMP_DIR, filename)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Confirm Restore")
        msg.setInformativeText(f"Are you sure you want to restore settings from {filename}?\n\nThis will overwrite current settings.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.create_worker('import_backup', backup_path, callback=self.on_backup_restored)
    
    def on_backup_restored(self, result):
        """Handle backup restore result."""
        if result.get('success'):
            self.show_success("Settings restored successfully")
            self.update_status()
            self.prompt_restart()
        else:
            self.show_error("Failed to restore settings from backup")

class ExclusionTab(BaseTab):
    """Enhanced tab for managing application exclusions with dark theme."""
    def __init__(self, model=None, config_manager=None):
        super().__init__(model, config_manager)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Excluded apps list
        list_card = ModernCard("Excluded Applications")
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        
        self.excluded_list = QListWidget()
        self.excluded_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.excluded_list.setStyleSheet(f"""
            QListWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
            }}
            QListWidget::item:hover {{
                background-color: rgb(60, 60, 80);
            }}
        """)
        list_layout.addWidget(self.excluded_list)
        
        # List buttons
        list_btn_layout = QHBoxLayout()
        list_btn_layout.setSpacing(10)
        
        self.remove_btn = ModernButton("Remove Selected", ERROR_COLOR)
        self.remove_btn.clicked.connect(self.remove_selected_apps)
        list_btn_layout.addWidget(self.remove_btn)
        
        self.refresh_btn = ModernButton("Refresh List", ACCENT_COLOR)
        self.refresh_btn.clicked.connect(self.update_excluded_apps)
        list_btn_layout.addWidget(self.refresh_btn)
        
        list_layout.addLayout(list_btn_layout)
        list_card.content_layout.addLayout(list_layout)
        main_layout.addWidget(list_card)
        
        # Add new app section
        add_card = ModernCard("Add New Exclusion")
        add_layout = QFormLayout()
        add_layout.setSpacing(10)
        
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Enter executable name (e.g., chrome.exe)")
        self.app_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border-radius: 4px;
            }}
        """)
        add_layout.addRow("Application Name:", self.app_input)
        
        self.add_btn = ModernButton("Add Exclusion", SUCCESS_COLOR)
        self.add_btn.clicked.connect(self.add_exclusion)
        add_layout.addRow("", self.add_btn)
        
        add_card.content_layout.addLayout(add_layout)
        main_layout.addWidget(add_card)
        
        # Common apps section
        common_card = ModernCard("Common Applications")
        common_layout = QVBoxLayout()
        common_layout.setSpacing(10)
        
        self.common_apps_list = QListWidget()
        self.common_apps_list.addItems(COMMON_APPS)
        self.common_apps_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.common_apps_list.setStyleSheet(f"""
            QListWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
            }}
            QListWidget::item:hover {{
                background-color: rgb(60, 60, 80);
            }}
        """)
        common_layout.addWidget(self.common_apps_list)
        
        self.add_common_btn = ModernButton("Add Selected", SUCCESS_COLOR)
        self.add_common_btn.clicked.connect(self.add_common_apps)
        common_layout.addWidget(self.add_common_btn)
        
        common_card.content_layout.addLayout(common_layout)
        main_layout.addWidget(common_card)
        
        main_layout.addStretch()
        
        # Initial update
        self.update_excluded_apps()
    
    def update_excluded_apps(self):
        """Update the list of excluded applications."""
        self.create_worker('get_excluded_apps', callback=self.on_excluded_apps_updated)
    
    def on_excluded_apps_updated(self, result):
        """Handle excluded apps update."""
        self.model.update_excluded_apps(result)
        
        # Update UI
        self.excluded_list.clear()
        for app in self.model.excluded_apps:
            item = QListWidgetItem(app)
            if app in SYSTEM_APPS:
                item.setForeground(ERROR_COLOR)  # Red for system apps
            self.excluded_list.addItem(item)
    
    def add_exclusion(self):
        """Add a new application exclusion."""
        app_name = self.app_input.text().strip()
        
        if not app_name:
            self.show_error("Please enter an application name")
            return
        
        # Validate app name format
        if not app_name.endswith('.exe'):
            app_name += '.exe'
        
        self.create_worker('add_excluded_app', app_name, callback=self.on_exclusion_added)
    
    def on_exclusion_added(self, result):
        """Handle exclusion addition result."""
        backup_path = result.get('backup_path')
        if backup_path:
            self.model.last_backup = backup_path
            self.app_input.clear()
            self.update_excluded_apps()
            self.show_success("Application excluded successfully")
            self.prompt_restart()
    
    def add_common_apps(self):
        """Add selected common applications."""
        selected_items = self.common_apps_list.selectedItems()
        if not selected_items:
            self.show_error("Please select applications to add")
            return
        
        apps = [item.text() for item in selected_items]
        
        # Filter out system apps
        apps_to_add = [app for app in apps if app not in SYSTEM_APPS]
        
        if not apps_to_add:
            self.show_error("Cannot exclude system applications")
            return
        
        self.create_worker('batch_remove_apps', apps_to_add, callback=self.on_common_apps_added)
    
    def on_common_apps_added(self, result):
        """Handle common apps addition result."""
        removed_count = result.get('removed_count', 0)
        if removed_count > 0:
            self.update_excluded_apps()
            self.show_success(f"Successfully excluded {removed_count} application(s)")
            self.prompt_restart()
    
    def remove_selected_apps(self):
        """Remove selected applications from exclusion list."""
        selected_items = self.excluded_list.selectedItems()
        if not selected_items:
            self.show_error("Please select applications to remove")
            return
        
        apps = [item.text() for item in selected_items]
        
        # Check for system apps
        system_apps = [app for app in apps if app in SYSTEM_APPS]
        if system_apps:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("System Applications")
            msg.setInformativeText(f"The following are system applications: {', '.join(system_apps)}\n\nRemoving them may cause system instability.\n\nAre you sure you want to continue?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                    color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                }}
                QMessageBox QLabel {{
                    color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                }}
                QPushButton {{
                    background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
            """)
            
            if msg.exec() != QMessageBox.StandardButton.Yes:
                return
        
        self.create_worker('batch_remove_apps', apps, callback=self.on_apps_removed)
    
    def on_apps_removed(self, result):
        """Handle apps removal result."""
        removed_count = result.get('removed_count', 0)
        if removed_count > 0:
            self.update_excluded_apps()
            self.show_success(f"Successfully removed {removed_count} application(s) from exclusion list")
            self.prompt_restart()

class ParametersTab(BaseTab):
    """Enhanced tab for managing heap parameters with dark theme."""
    def __init__(self, model=None, config_manager=None):
        super().__init__(model, config_manager)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Current parameters
        params_card = ModernCard("Current Heap Parameters")
        params_layout = QVBoxLayout()
        params_layout.setSpacing(10)
        
        self.params_table = QTableWidget(4, 3)
        self.params_table.setHorizontalHeaderLabels(["Parameter", "Value", "Description"])
        self.params_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.params_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.params_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.params_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.params_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.params_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                gridline-color: rgb(70, 70, 90);
            }}
            QHeaderView::section {{
                background-color: rgb(40, 40, 55);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border: none;
                border-right: 1px solid rgb(70, 70, 90);
                border-bottom: 1px solid rgb(70, 70, 90);
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid rgb(70, 70, 90);
            }}
            QTableWidget::item:selected {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
            }}
        """)
        params_layout.addWidget(self.params_table)
        
        # Parameter buttons
        param_btn_layout = QHBoxLayout()
        param_btn_layout.setSpacing(10)
        
        self.edit_params_btn = ModernButton("Edit Parameters", ACCENT_COLOR)
        self.edit_params_btn.clicked.connect(self.edit_parameters)
        param_btn_layout.addWidget(self.edit_params_btn)
        
        self.reset_params_btn = ModernButton("Reset to Defaults", QColor(100, 100, 100))
        self.reset_params_btn.clicked.connect(self.reset_parameters)
        param_btn_layout.addWidget(self.reset_params_btn)
        
        params_layout.addLayout(param_btn_layout)
        params_card.content_layout.addLayout(params_layout)
        main_layout.addWidget(params_card)
        
        # Presets section
        presets_card = ModernCard("Parameter Presets")
        presets_layout = QVBoxLayout()
        presets_layout.setSpacing(10)
        
        presets_info = QLabel("Select a preset to quickly apply optimized parameters for different use cases:")
        presets_info.setWordWrap(True)
        presets_info.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        presets_layout.addWidget(presets_info)
        
        presets_grid = QGridLayout()
        presets_grid.setSpacing(10)
        
        # Gaming preset
        gaming_btn = ModernButton("Gaming", SUCCESS_COLOR)
        gaming_btn.clicked.connect(lambda: self.apply_preset("gaming"))
        presets_grid.addWidget(gaming_btn, 0, 0)
        
        # Productivity preset
        productivity_btn = ModernButton("Productivity", ACCENT_COLOR)
        productivity_btn.clicked.connect(lambda: self.apply_preset("productivity"))
        presets_grid.addWidget(productivity_btn, 0, 1)
        
        # Development preset
        development_btn = ModernButton("Development", QColor(156, 39, 176))
        development_btn.clicked.connect(lambda: self.apply_preset("development"))
        presets_grid.addWidget(development_btn, 0, 2)
        
        # Minimal preset
        minimal_btn = ModernButton("Minimal", QColor(100, 100, 100))
        minimal_btn.clicked.connect(lambda: self.apply_preset("minimal"))
        presets_grid.addWidget(minimal_btn, 1, 0)
        
        # Balanced preset
        balanced_btn = ModernButton("Balanced", WARNING_COLOR)
        balanced_btn.clicked.connect(lambda: self.apply_preset("balanced"))
        presets_grid.addWidget(balanced_btn, 1, 1)
        
        # Custom preset
        custom_btn = ModernButton("Custom", QColor(121, 85, 72))
        custom_btn.clicked.connect(lambda: self.apply_preset("custom"))
        presets_grid.addWidget(custom_btn, 1, 2)
        
        presets_layout.addLayout(presets_grid)
        presets_card.content_layout.addLayout(presets_layout)
        main_layout.addWidget(presets_card)
        
        main_layout.addStretch()
        
        # Initial updates
        self.update_parameters()
    
    def update_parameters(self):
        """Update the heap parameters display."""
        self.create_worker('get_heap_params', callback=self.on_parameters_updated)
    
    def on_parameters_updated(self, result):
        """Handle parameters update result."""
        self.model.update_params(result)
        
        # Update table
        param_info = {
            'HeapSegmentReserve': {
                'description': 'Virtual memory to reserve per segment',
                'default': DEFAULT_HEAP_PARAMS['HeapSegmentReserve']
            },
            'HeapSegmentCommit': {
                'description': 'Physical memory to commit upfront',
                'default': DEFAULT_HEAP_PARAMS['HeapSegmentCommit']
            },
            'HeapDeCommitTotalFreeThreshold': {
                'description': 'Total free memory threshold',
                'default': DEFAULT_HEAP_PARAMS['HeapDeCommitTotalFreeThreshold']
            },
            'HeapDeCommitFreeBlockThreshold': {
                'description': 'Free block size threshold',
                'default': DEFAULT_HEAP_PARAMS['HeapDeCommitFreeBlockThreshold']
            }
        }
        
        for i, (param, info) in enumerate(param_info.items()):
            value = self.model.params.get(param)
            
            # Parameter name
            self.params_table.setItem(i, 0, QTableWidgetItem(param))
            
            # Value
            if value is not None:
                value_text = f"0x{value:08x} ({self.format_byte_size(value)})"
            else:
                value_text = "Using Windows default"
            self.params_table.setItem(i, 1, QTableWidgetItem(value_text))
            
            # Description
            desc_text = f"{info['description']}\nDefault: 0x{info['default']:08x} ({self.format_byte_size(info['default'])})"
            self.params_table.setItem(i, 2, QTableWidgetItem(desc_text))
    
    def format_byte_size(self, bytes_value: int) -> str:
        """Format byte size in human-readable format."""
        if bytes_value is None:
            return "N/A"
        if bytes_value == 0:
            return "0 B"
        sizes = ["B", "KB", "MB", "GB"]
        index = 0
        value = float(bytes_value)
        while value >= 1024 and index < len(sizes) - 1:
            value /= 1024
            index += 1
        return f"{value:.1f} {sizes[index]}"
    
    def edit_parameters(self):
        """Open dialog to edit heap parameters."""
        dialog = ParameterEditDialog(self.model.params, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            params = dialog.get_parameters()
            if params:
                self.create_worker('set_heap_params', params, callback=self.on_parameters_set)
    
    def on_parameters_set(self, result):
        """Handle parameters set result."""
        backup_path = result.get('backup_path')
        if backup_path:
            self.model.last_backup = backup_path
            self.update_parameters()
            self.show_success("Heap parameters updated successfully")
            self.prompt_restart()
    
    def reset_parameters(self):
        """Reset parameters to defaults."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Confirm Reset")
        msg.setInformativeText("Are you sure you want to reset all heap parameters to their default values?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QMessageBox QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QPushButton {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.create_worker('set_heap_params', {}, callback=self.on_parameters_set)
    
    def apply_preset(self, preset_name):
        """Apply a parameter preset."""
        presets = {
            "gaming": {
                'HeapSegmentReserve': 0x00200000,  # 2 MB
                'HeapSegmentCommit': 0x00004000,   # 16 KB
                'HeapDeCommitTotalFreeThreshold': 0x00020000,  # 128 KB
                'HeapDeCommitFreeBlockThreshold': 0x00002000   # 8 KB
            },
            "productivity": {
                'HeapSegmentReserve': 0x00100000,  # 1 MB
                'HeapSegmentCommit': 0x00002000,   # 8 KB
                'HeapDeCommitTotalFreeThreshold': 0x00010000,  # 64 KB
                'HeapDeCommitFreeBlockThreshold': 0x00001000   # 4 KB
            },
            "development": {
                'HeapSegmentReserve': 0x00400000,  # 4 MB
                'HeapSegmentCommit': 0x00008000,   # 32 KB
                'HeapDeCommitTotalFreeThreshold': 0x00040000,  # 256 KB
                'HeapDeCommitFreeBlockThreshold': 0x00004000   # 16 KB
            },
            "minimal": {
                'HeapSegmentReserve': 0x00080000,  # 512 KB
                'HeapSegmentCommit': 0x00001000,   # 4 KB
                'HeapDeCommitTotalFreeThreshold': 0x00008000,  # 32 KB
                'HeapDeCommitFreeBlockThreshold': 0x00000800   # 2 KB
            },
            "balanced": {
                'HeapSegmentReserve': 0x00150000,  # 1.5 MB
                'HeapSegmentCommit': 0x00003000,   # 12 KB
                'HeapDeCommitTotalFreeThreshold': 0x00018000,  # 96 KB
                'HeapDeCommitFreeBlockThreshold': 0x00001800   # 6 KB
            },
            "custom": {}  # Will open the custom dialog
        }
        
        if preset_name == "custom":
            self.edit_parameters()
            return
        
        params = presets.get(preset_name, {})
        if params:
            self.create_worker('set_heap_params', params, callback=self.on_parameters_set)
            self.show_success(f"Applied {preset_name} preset successfully")

class PerformanceTab(BaseTab):
    """New tab for performance monitoring and analysis with dark theme."""
    def __init__(self, model=None, config_manager=None):
        super().__init__(model, config_manager)
        self.performance_monitor = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Performance metrics card
        metrics_card = ModernCard("System Performance Metrics")
        metrics_layout = QVBoxLayout()
        metrics_layout.setSpacing(15)
        
        # Memory usage
        memory_layout = QVBoxLayout()
        memory_label = QLabel("Memory Usage:")
        memory_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        memory_label.setStyleSheet(f"color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});")
        memory_layout.addWidget(memory_label)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setFormat("%v% of %p%")
        self.memory_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                text-align: center;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                background-color: rgb(50, 50, 65);
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()}), 
                    stop:1 rgb({ACCENT_COLOR.red() + 30}, {ACCENT_COLOR.green() + 30}, {ACCENT_COLOR.blue() + 30}));
                border-radius: 5px;
            }}
        """)
        memory_layout.addWidget(self.memory_progress)
        
        metrics_layout.addLayout(memory_layout)
        
        # CPU usage
        cpu_layout = QVBoxLayout()
        cpu_label = QLabel("CPU Usage:")
        cpu_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cpu_label.setStyleSheet(f"color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});")
        cpu_layout.addWidget(cpu_label)
        
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setFormat("%p%")
        self.cpu_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                text-align: center;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                background-color: rgb(50, 50, 65);
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb({SUCCESS_COLOR.red()}, {SUCCESS_COLOR.green()}, {SUCCESS_COLOR.blue()}), 
                    stop:1 rgb({SUCCESS_COLOR.red() + 30}, {SUCCESS_COLOR.green() + 30}, {SUCCESS_COLOR.blue() + 30}));
                border-radius: 5px;
            }}
        """)
        cpu_layout.addWidget(self.cpu_progress)
        
        metrics_layout.addLayout(cpu_layout)
        
        # Top processes
        processes_label = QLabel("Top Memory Consumers:")
        processes_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        processes_label.setStyleSheet(f"color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});")
        metrics_layout.addWidget(processes_label)
        
        self.processes_table = QTableWidget(0, 2)
        self.processes_table.setHorizontalHeaderLabels(["Process", "Memory Usage"])
        self.processes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.processes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.processes_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.processes_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                gridline-color: rgb(70, 70, 90);
            }}
            QHeaderView::section {{
                background-color: rgb(40, 40, 55);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border: none;
                border-right: 1px solid rgb(70, 70, 90);
                border-bottom: 1px solid rgb(70, 70, 90);
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid rgb(70, 70, 90);
            }}
            QTableWidget::item:selected {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
            }}
        """)
        metrics_layout.addWidget(self.processes_table)
        
        metrics_card.content_layout.addLayout(metrics_layout)
        main_layout.addWidget(metrics_card)
        
        # Performance history card
        history_card = ModernCard("Performance History")
        history_layout = QVBoxLayout()
        history_layout.setSpacing(10)
        
        self.history_label = QLabel("Performance history will be displayed here after monitoring is enabled.")
        self.history_label.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        history_layout.addWidget(self.history_label)
        
        history_card.content_layout.addLayout(history_layout)
        main_layout.addWidget(history_card)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.start_monitor_btn = ModernButton("Start Monitoring", SUCCESS_COLOR)
        self.start_monitor_btn.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_monitor_btn)
        
        self.stop_monitor_btn = ModernButton("Stop Monitoring", ERROR_COLOR)
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        self.stop_monitor_btn.setEnabled(False)
        control_layout.addWidget(self.stop_monitor_btn)
        
        self.analyze_btn = ModernButton("Analyze Performance", ACCENT_COLOR)
        self.analyze_btn.clicked.connect(self.analyze_performance)
        control_layout.addWidget(self.analyze_btn)
        
        main_layout.addLayout(control_layout)
        main_layout.addStretch()
    
    def start_monitoring(self):
        """Start performance monitoring."""
        if not self.performance_monitor:
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.metrics_updated.connect(self.update_metrics)
            self.performance_monitor.start()
            
            self.start_monitor_btn.setEnabled(False)
            self.stop_monitor_btn.setEnabled(True)
            self.show_info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if self.performance_monitor:
            self.performance_monitor.stop()
            self.performance_monitor.wait()
            self.performance_monitor = None
            
            self.start_monitor_btn.setEnabled(True)
            self.stop_monitor_btn.setEnabled(False)
            self.show_info("Performance monitoring stopped")
    
    def update_metrics(self, metrics):
        """Update performance metrics display."""
        # Update memory progress
        memory_percent = metrics.get('memory_percent', 0)
        self.memory_progress.setValue(int(memory_percent))
        self.memory_progress.setFormat(f"{memory_percent:.1f}%")
        
        # Update CPU progress
        cpu_percent = metrics.get('cpu_percent', 0)
        self.cpu_progress.setValue(int(cpu_percent))
        
        # Update processes table
        processes = metrics.get('top_processes', [])
        self.processes_table.setRowCount(len(processes))
        
        for i, process in enumerate(processes):
            name_item = QTableWidgetItem(process.get('name', 'Unknown'))
            memory_bytes = process.get('memory', 0)
            memory_mb = memory_bytes / (1024 * 1024)
            memory_item = QTableWidgetItem(f"{memory_mb:.1f} MB")
            
            self.processes_table.setItem(i, 0, name_item)
            self.processes_table.setItem(i, 1, memory_item)
    
    def analyze_performance(self):
        """Analyze system performance."""
        self.show_info("Analyzing system performance...")
        self.create_worker('analyze_performance', callback=self.on_performance_analyzed)
    
    def on_performance_analyzed(self, result):
        """Handle performance analysis result."""
        if 'error' in result:
            self.show_error(f"Error analyzing performance: {result['error']}")
            return
        
        # Format the results
        uptime_hours = result.get('uptime', 0) / 3600
        memory_used_gb = result.get('memory_used', 0) / (1024**3)
        memory_total_gb = result.get('memory_total', 0) / (1024**3)
        cpu_percent = result.get('cpu_percent', 0)
        
        analysis_text = (
            f"System Uptime: {uptime_hours:.1f} hours\n"
            f"Memory Usage: {memory_used_gb:.2f} GB / {memory_total_gb:.2f} GB\n"
            f"CPU Usage: {cpu_percent:.1f}%\n\n"
            f"Top Memory Consumers:\n"
        )
        
        for i, process in enumerate(result.get('top_processes', [])[:5]):
            memory_mb = process.get('memory', 0) / (1024 * 1024)
            analysis_text += f"{i+1}. {process.get('name', 'Unknown')}: {memory_mb:.1f} MB\n"
        
        self.history_label.setText(analysis_text)

class MainWindow(QMainWindow):
    """Main application window with dark, fancy, and minimalistic design."""
    def __init__(self):
        super().__init__()
        self.model = HeapModel()
        self.config_manager = ConfigManager()
        self.init_ui()
        self.apply_dark_theme()
    
    def init_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 900, 700)
        
        # Set application icon
        self.setWindowIcon(QIcon())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
            }}
            QTabBar::tab {{
                background-color: rgb(40, 40, 55);
                color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: rgb({CARD_COLOR.red()}, {CARD_COLOR.green()}, {CARD_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                border-bottom: 2px solid rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
            }}
            QTabBar::tab:hover:!selected {{
                background-color: rgb(50, 50, 65);
            }}
        """)
        
        # Create tabs
        self.status_tab = StatusTab(self.model, self.config_manager)
        self.tab_widget.addTab(self.status_tab, "Status")
        
        self.exclusion_tab = ExclusionTab(self.model, self.config_manager)
        self.tab_widget.addTab(self.exclusion_tab, "Exclusions")
        
        self.parameters_tab = ParametersTab(self.model, self.config_manager)
        self.tab_widget.addTab(self.parameters_tab, "Parameters")
        
        self.performance_tab = PerformanceTab(self.model, self.config_manager)
        self.tab_widget.addTab(self.performance_tab, "Performance")
        
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(f"""
            QStatusBar {{
                background-color: rgb(30, 30, 40);
                color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});
                border-top: 1px solid rgb(50, 50, 65);
            }}
        """)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create system tray icon
        self.create_tray_icon()
    
    def create_header(self):
        """Create the application header with gradient."""
        header = QFrame()
        header.setFixedHeight(70)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, header.height())
        gradient.setColorAt(0, QColor(30, 30, 45))
        gradient.setColorAt(1, QColor(40, 40, 60))
        
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgb(30, 30, 45), stop:1 rgb(40, 40, 60));
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # App title
        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Version label
        version = QLabel(f"v{APP_VERSION}")
        version.setFont(QFont("Segoe UI", 10))
        version.setStyleSheet(f"color: rgb({SUBTEXT_COLOR.red()}, {SUBTEXT_COLOR.green()}, {SUBTEXT_COLOR.blue()});")
        layout.addWidget(version)
        
        return header
    
    def create_tray_icon(self):
        """Create system tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create tray menu
            tray_menu = QMenu()
            tray_menu.setStyleSheet(f"""
                QMenu {{
                    background-color: rgb({CARD_COLOR.red()}, {CARD_COLOR.green()}, {CARD_COLOR.blue()});
                    color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                    border: 1px solid rgb(70, 70, 90);
                }}
                QMenu::item {{
                    padding: 8px 16px;
                }}
                QMenu::item:selected {{
                    background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                }}
            """)
            
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def apply_dark_theme(self):
        """Apply the dark theme to the entire application."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QWidget {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QLabel {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QLineEdit {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                border-radius: 6px;
            }}
            QTableWidget {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                gridline-color: rgb(70, 70, 90);
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background-color: rgb(40, 40, 55);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border: none;
            }}
            QComboBox {{
                background-color: rgb(50, 50, 65);
                border: 1px solid rgb(70, 70, 90);
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QCheckBox {{
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid rgb(70, 70, 90);
                background-color: rgb(50, 50, 65);
            }}
            QCheckBox::indicator:checked {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTggM0w0IDdMMiA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
            QProgressBar {{
                border: 1px solid rgb(70, 70, 90);
                border-radius: 6px;
                text-align: center;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
                background-color: rgb(50, 50, 65);
            }}
            QProgressBar::chunk {{
                background-color: rgb({ACCENT_COLOR.red()}, {ACCENT_COLOR.green()}, {ACCENT_COLOR.blue()});
                border-radius: 5px;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid rgb(60, 60, 80);
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                color: rgb({TEXT_COLOR.red()}, {TEXT_COLOR.green()}, {TEXT_COLOR.blue()});
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QScrollArea {{
                background-color: rgb({BG_COLOR.red()}, {BG_COLOR.green()}, {BG_COLOR.blue()});
                border: none;
            }}
        """)
    
    def closeEvent(self, event):
        """Handle application close event."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            event.ignore()
        else:
            event.accept()

def main():
    """Main entry point."""
    # Force admin privileges
    force_admin()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()