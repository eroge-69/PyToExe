import sys
import os
import winreg
import logging
import subprocess
import ctypes
import json
import psutil
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QComboBox, QGroupBox,
    QFormLayout, QDialogButtonBox, QDialog,
    QAbstractItemView, QHeaderView, QTextEdit, QCheckBox,
    QProgressBar, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSettings
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette, QAction, QPixmap, QPainter, QPen, QBrush

# Constants
APP_NAME = "SegmentHeapManager"
APP_VERSION = "4.0"
COMPANY_NAME = "xAI"
TEMP_DIR = os.path.join(os.environ['TEMP'], APP_NAME)
CONFIG_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)

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
    "spotify.exe", "vlc.exe"
]

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    """Restart the script with admin privileges."""
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    
    # Use ShellExecuteW to restart with admin rights
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    sys.exit(0)

def setup_logging() -> str:
    """Configure logging to file and console."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    log_file = os.path.join(TEMP_DIR, f"{APP_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return log_file

class HeapModel:
    """Data model for heap settings and status."""
    def __init__(self):
        self.params: Dict[str, Optional[int]] = {}
        self.status: Dict[str, Any] = {'status': 'Unknown', 'detail': 'Not loaded', 'color': QColor(128, 128, 128)}
        self.excluded_apps: List[str] = []
        self.last_backup: Optional[str] = None
        self.backup_history: List[str] = []
        self.performance_stats: Dict[str, Any] = {}

    def update_params(self, result: Dict[str, Any]) -> None:
        self.params = result.get('params', {})

    def update_status(self, result: Dict[str, Any]) -> None:
        self.status = result

    def update_excluded_apps(self, result: Dict[str, Any]) -> None:
        self.excluded_apps = result.get('apps', [])

    def update_performance_stats(self, stats: Dict[str, Any]) -> None:
        self.performance_stats = stats

    def set_last_backup(self, path: str) -> None:
        self.last_backup = path
        if path and path not in self.backup_history:
            self.backup_history.append(path)
            # Keep only the last 10 backups in history
            if len(self.backup_history) > 10:
                self.backup_history.pop(0)

class ConfigManager:
    """Manages application configuration."""
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.config_file = os.path.join(CONFIG_DIR, "config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "auto_enable": False,
                "last_check": None,
                "theme": "dark",
                "monitor_enabled": False
            }
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            # Write to temp file first
            with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=CONFIG_DIR) as tmp:
                json.dump(self.config, tmp)
                tmp_path = tmp.name
            
            # Atomic replace
            os.replace(tmp_path, self.config_file)
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value."""
        self.config[key] = value
        return self.save_config()

class ThreadManager:
    """Manages worker threads to prevent resource leaks."""
    def __init__(self):
        self.workers: List[QThread] = []
        self._cleanup_lock = False
    
    def add_worker(self, worker: QThread) -> None:
        """Add a worker thread to manage."""
        self.workers.append(worker)
    
    def cleanup(self) -> None:
        """Clean up all worker threads."""
        if self._cleanup_lock:
            return
        
        self._cleanup_lock = True
        workers_to_clean = self.workers.copy()
        self.workers.clear()
        
        for worker in workers_to_clean:
            if worker.isRunning():
                try:
                    worker.stop()
                    worker.wait(2000)  # Wait up to 2 seconds
                except:
                    worker.terminate()
                    worker.wait(1000)  # Wait up to 1 second after terminate
        
        self._cleanup_lock = False

class RegistryWorker(QThread):
    """Worker thread for registry operations with improved error handling."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, operation: str, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self._is_running = True
    
    def run(self):
        try:
            if not self._is_running:
                return
                
            operations = {
                'get_status': self.get_segment_heap_status,
                'set_status': lambda: {'backup_path': self.set_segment_heap_status(*self.args)},
                'get_excluded_apps': lambda: {'apps': self.get_excluded_apps()},
                'add_excluded_app': lambda: {'backup_path': self.add_excluded_app(*self.args)},
                'remove_excluded_app': lambda: {'backup_path': self.remove_excluded_app(*self.args)},
                'get_heap_params': lambda: {'params': self.get_heap_params()},
                'set_heap_params': lambda: {'backup_path': self.set_heap_params(*self.args)},
                'copy_params_to_segment_heap': lambda: {'backup_path': self.copy_params_to_segment_heap()},
                'export_backup': lambda: {'backup_path': self.export_registry_backup()},
                'import_backup': lambda: {'success': self.import_registry_backup(*self.args)},
                'batch_remove_apps': lambda: {'removed_count': self.batch_remove_apps(*self.args)},
                'get_performance_stats': lambda: {'stats': self.get_performance_stats()},
                'check_windows_updates': lambda: {'updates': self.check_windows_updates()}
            }
            
            if self.operation not in operations:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            result = operations[self.operation]()
            
            if self._is_running:
                self.finished.emit(result)
        except PermissionError as e:
            logging.error(f"Permission denied in registry operation '{self.operation}': {str(e)}")
            if self._is_running:
                self.error.emit(f"Permission denied: {str(e)}")
        except winreg.WindowsError as e:
            logging.error(f"Windows registry error in '{self.operation}': {str(e)}")
            if self._is_running:
                self.error.emit(f"Registry error: {str(e)}")
        except Exception as e:
            logging.error(f"Registry operation '{self.operation}' failed: {str(e)}", exc_info=True)
            if self._is_running:
                self.error.emit(f"Operation failed: {str(e)}")
    
    def stop(self):
        """Stop the worker thread."""
        self._is_running = False
        self.quit()
        self.wait(1000)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get system performance statistics with validation."""
        try:
            mem = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Validate values
            if not (0 <= mem.percent <= 100):
                raise ValueError(f"Invalid memory percent: {mem.percent}")
            if not (0 <= cpu_percent <= 100):
                raise ValueError(f"Invalid CPU percent: {cpu_percent}")
            if not (0 <= disk.percent <= 100):
                raise ValueError(f"Invalid disk percent: {disk.percent}")
            
            return {
                'memory_percent': mem.percent,
                'cpu_percent': cpu_percent,
                'disk_percent': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to get performance stats: {str(e)}")
            return {}
    
    def check_windows_updates(self) -> bool:
        """Check if Windows updates were installed recently."""
        try:
            # Get system uptime
            uptime = ctypes.windll.kernel32.GetTickCount() / 1000  # Convert to seconds
            
            # If system was restarted in the last 24 hours, consider it a potential update
            return uptime < 86400  # 24 hours in seconds
        except Exception as e:
            logging.error(f"Error checking system uptime: {e}")
            return False
    
    def batch_remove_apps(self, apps: List[str]) -> int:
        """Remove multiple apps efficiently."""
        removed_count = 0
        total = len(apps)
        
        for i, app in enumerate(apps):
            if not self._is_running:
                break
                
            try:
                self.remove_excluded_app(app)
                removed_count += 1
                self.progress.emit(int((i + 1) / total * 100))
            except Exception as e:
                logging.error(f"Failed to remove {app}: {str(e)}")
        
        return removed_count
    
    def get_segment_heap_status(self) -> Dict[str, Any]:
        """Get the current status of Segment Heap with improved error handling."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SEGMENT_HEAP_KEY, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Enabled")
                status = "Enabled" if value == 1 else "Disabled"
                detail = "System will use Segment Heap after restart" if value == 1 else "System will use default LFH after restart"
                color = QColor(76, 175, 80) if value == 1 else QColor(244, 67, 54)
                return {'status': status, 'detail': detail, 'color': color}
        except FileNotFoundError:
            return {'status': 'Disabled', 'detail': 'No registry key found', 'color': QColor(244, 67, 54)}
        except PermissionError:
            raise PermissionError("Access denied. Run as administrator.")
        except winreg.WindowsError as e:
            logging.error(f"Registry error: {e}")
            raise Exception(f"Registry error: {e}")
    
    def set_segment_heap_status(self, enable: bool) -> str:
        """Enable or disable Segment Heap with proper backup verification."""
        backup_path = self.export_registry_backup()
        
        # Verify backup was created
        if not backup_path or not os.path.exists(backup_path):
            raise Exception("Failed to create backup")
        
        try:
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, SEGMENT_HEAP_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 1 if enable else 0)
                logging.info(f"Segment Heap {'enabled' if enable else 'disabled'}")
            return backup_path
        except Exception as e:
            # Try to restore from backup if we failed
            try:
                self.import_registry_backup(backup_path)
            except:
                logging.error("Failed to restore from backup after error")
            raise e
    
    def get_excluded_apps(self) -> List[str]:
        """Get list of applications excluded from Segment Heap."""
        apps: Set[str] = set()
        
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
                        except OSError as e:
                            if e.errno == 259:  # No more data
                                break
                            raise
            except PermissionError:
                logging.warning(f"Access denied to registry key with WOW flag {wow_flag}")
            except Exception as e:
                logging.debug(f"Error opening registry key {IMAGE_FILE_EXECUTION_KEY} with WOW flag {wow_flag}: {e}")
        
        return sorted(apps)
    
    def add_excluded_app(self, app_name: str) -> str:
        """Add an application to the exclusion list with validation."""
        if not app_name.lower().endswith('.exe') or len(app_name) > 260:
            raise ValueError("Invalid executable name: must end with .exe and be <= 260 characters")
        
        backup_path = self.export_registry_backup()
        
        # Verify backup was created
        if not backup_path or not os.path.exists(backup_path):
            raise Exception("Failed to create backup")
        
        success = False
        try:
            for wow_flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, IMAGE_FILE_EXECUTION_KEY, 0, winreg.KEY_SET_VALUE | wow_flag) as key:
                        with winreg.CreateKeyEx(key, app_name, 0, winreg.KEY_SET_VALUE) as subkey:
                            winreg.SetValueEx(subkey, "FrontEndHeapDebugOptions", 0, winreg.REG_DWORD, 4)
                    success = True
                except PermissionError:
                    logging.warning(f"Access denied for WOW flag {wow_flag}")
                except Exception as e:
                    logging.error(f"Failed to add excluded app to {IMAGE_FILE_EXECUTION_KEY} with WOW flag {wow_flag}: {str(e)}")
                    if success:
                        # If we succeeded for one architecture but failed the other, try to rollback
                        try:
                            self.remove_excluded_app(app_name)
                        except:
                            pass
                    raise
            
            if not success:
                raise Exception("Failed to add excluded app for any architecture")
            
            logging.info(f"Added excluded application: {app_name}")
            return backup_path
        except Exception as e:
            # Try to restore from backup if we failed
            try:
                self.import_registry_backup(backup_path)
            except:
                logging.error("Failed to restore from backup after error")
            raise e
    
    def remove_excluded_app(self, app_name: str) -> str:
        """Remove an application from the exclusion list."""
        backup_path = self.export_registry_backup()
        
        # Verify backup was created
        if not backup_path or not os.path.exists(backup_path):
            raise Exception("Failed to create backup")
        
        try:
            for wow_flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, IMAGE_FILE_EXECUTION_KEY, 0, winreg.KEY_SET_VALUE | wow_flag) as key:
                        try:
                            with winreg.OpenKey(key, app_name, 0, winreg.KEY_SET_VALUE | wow_flag) as subkey:
                                try:
                                    winreg.DeleteValue(subkey, "FrontEndHeapDebugOptions")
                                except FileNotFoundError:
                                    pass
                                
                                # Check if subkey is empty
                                num_values = winreg.QueryInfoKey(subkey)[1]
                                if num_values == 0:
                                    winreg.DeleteKey(key, app_name)
                        except FileNotFoundError:
                            pass
                except PermissionError:
                    logging.warning(f"Access denied for WOW flag {wow_flag}")
                except Exception as e:
                    logging.error(f"Failed to remove excluded app from {IMAGE_FILE_EXECUTION_KEY} with WOW flag {wow_flag}: {str(e)}")
            
            logging.info(f"Removed excluded application: {app_name}")
            return backup_path
        except Exception as e:
            # Try to restore from backup if we failed
            try:
                self.import_registry_backup(backup_path)
            except:
                logging.error("Failed to restore from backup after error")
            raise e
    
    def get_heap_params(self) -> Dict[str, Optional[int]]:
        """Get current heap parameters."""
        params: Dict[str, Optional[int]] = {}
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
        except PermissionError:
            raise PermissionError("Access denied. Run as administrator.")
        
        return params
    
    def set_heap_params(self, params_dict: Dict[str, Optional[int]]) -> str:
        """Set heap parameters with backup verification."""
        backup_path = self.export_registry_backup()
        
        # Verify backup was created
        if not backup_path or not os.path.exists(backup_path):
            raise Exception("Failed to create backup")
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SESSION_MANAGER_KEY, 0, winreg.KEY_SET_VALUE) as key:
                for param, value in params_dict.items():
                    if value is None:
                        try:
                            winreg.DeleteValue(key, param)
                        except FileNotFoundError:
                            pass
                    else:
                        winreg.SetValueEx(key, param, 0, winreg.REG_DWORD, value)
            
            logging.info("Heap parameters updated")
            return backup_path
        except Exception as e:
            # Try to restore from backup if we failed
            try:
                self.import_registry_backup(backup_path)
            except:
                logging.error("Failed to restore from backup after error")
            raise e
    
    def copy_params_to_segment_heap(self) -> str:
        """Copy heap parameters to Segment Heap key."""
        backup_path = self.export_registry_backup()
        
        # Verify backup was created
        if not backup_path or not os.path.exists(backup_path):
            raise Exception("Failed to create backup")
        
        try:
            params = self.get_heap_params()
            
            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, SEGMENT_HEAP_KEY, 0, winreg.KEY_SET_VALUE) as key:
                for param, value in params.items():
                    if value is not None:
                        winreg.SetValueEx(key, param, 0, winreg.REG_DWORD, value)
                        logging.info(f"Copied {param} = 0x{value:08x} to Segment Heap key")
                    else:
                        try:
                            winreg.DeleteValue(key, param)
                            logging.info(f"Removed {param} from Segment Heap key (using default)")
                        except FileNotFoundError:
                            pass
            
            logging.info("Heap parameters copied to Segment Heap key")
            return backup_path
        except Exception as e:
            # Try to restore from backup if we failed
            try:
                self.import_registry_backup(backup_path)
            except:
                logging.error("Failed to restore from backup after error")
            raise e
    
    def export_registry_backup(self) -> str:
        """Export registry settings to a backup file with verification."""
        os.makedirs(TEMP_DIR, exist_ok=True)
        backup_path = os.path.join(TEMP_DIR, f"SegmentHeapBackup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg")
        
        try:
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
                except FileNotFoundError:
                    pass
                except PermissionError:
                    logging.warning("Access denied to Segment Heap key")
                
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
                except FileNotFoundError:
                    pass
                except PermissionError:
                    logging.warning("Access denied to Session Manager key")
                
                # Backup Image File Execution Options for excluded apps
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
                            except OSError as e:
                                if e.errno == 259:  # No more data
                                    break
                                raise
                except FileNotFoundError:
                    pass
                except PermissionError:
                    logging.warning("Access denied to Image File Execution Options key")
            
            # Verify backup file was created and is not empty
            if not os.path.exists(backup_path) or os.path.getsize(backup_path) < 50:
                raise Exception("Backup file is invalid or empty")
            
            logging.info(f"Registry backup created: {backup_path}")
            return backup_path
        except Exception as e:
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except:
                    pass
            raise e
    
    def import_registry_backup(self, backup_path: str) -> bool:
        """Import registry settings from a backup file with verification."""
        if not os.path.exists(backup_path):
            raise Exception(f"Backup file not found: {backup_path}")
        
        try:
            # Create a backup before importing
            pre_import_backup = self.export_registry_backup()
            
            # Import the backup
            result = subprocess.run(['regedit.exe', '/s', backup_path], check=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Restore the pre-import backup if import failed
                try:
                    subprocess.run(['regedit.exe', '/s', pre_import_backup], check=True)
                except:
                    logging.error("Failed to restore pre-import backup")
                raise Exception(f"Registry import failed with error code: {result.returncode}")
            
            # Verify the import was successful by checking if we can read the keys
            try:
                self.get_segment_heap_status()
            except Exception as e:
                # Try to restore the pre-import backup
                try:
                    subprocess.run(['regedit.exe', '/s', pre_import_backup], check=True)
                except:
                    logging.error("Failed to restore pre-import backup after verification failure")
                raise Exception(f"Registry import verification failed: {str(e)}")
            
            logging.info(f"Registry restored from: {backup_path}")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to restore registry: {e.stderr}"
            logging.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to restore registry: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

class ParameterEditDialog(QDialog):
    """Dialog for editing heap parameters."""
    def __init__(self, current_params: Dict[str, Optional[int]], parent=None):
        super().__init__(parent)
        self.current_params = current_params
        self.param_widgets: Dict[str, Dict[str, Any]] = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Edit Heap Parameters")
        self.setMinimumWidth(600)
        
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
            
            reset_btn = QPushButton("Reset to Default")
            reset_btn.clicked.connect(lambda _, p=param, w=input_widget, u=unit_combo: self.reset_to_default(p, w, u))
            param_layout.addWidget(reset_btn)
            
            self.param_widgets[param] = {
                'input': input_widget,
                'unit': unit_combo,
                'default': info['default']
            }
            
            form_layout.addRow(param_group)
            
            desc_label = QLabel(info['description'])
            desc_label.setStyleSheet("color: gray; font-size: 9pt;")
            form_layout.addRow("", desc_label)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def reset_to_default(self, param: str, input_widget: QLineEdit, unit_combo: QComboBox) -> None:
        """Reset a parameter to its default value."""
        default_value = self.param_widgets[param]['default']
        
        if default_value >= 0x100000:
            input_widget.setText(str(default_value // 0x100000))
            unit_combo.setCurrentIndex(2)
        elif default_value >= 0x400:
            input_widget.setText(str(default_value // 0x400))
            unit_combo.setCurrentIndex(1)
        else:
            input_widget.setText(str(default_value))
            unit_combo.setCurrentIndex(0)
    
    def format_byte_size(self, bytes_value: int) -> str:
        """Format byte size in human-readable format."""
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
    """Base class for tabs with common functionality."""
    def __init__(self, parent=None, model=None, config_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.model = model
        self.config_manager = config_manager
        self.thread_manager = ThreadManager()
    
    def show_error(self, message):
        """Show an error message box."""
        QMessageBox.critical(self, "Error", message)
    
    def show_success(self, message):
        """Show a success message box."""
        QMessageBox.information(self, "Success", message)
    
    def prompt_restart(self):
        """Prompt the user to restart the system."""
        reply = QMessageBox.question(
            self, "Restart Required",
            "Changes have been saved successfully!\n\nA system restart is required for changes to take effect.\n\nWould you like to restart now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.restart_system()
    
    def restart_system(self):
        """Restart the system."""
        reply = QMessageBox.question(
            self, "Confirm Restart",
            "Are you sure you want to restart the system now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                subprocess.run(["shutdown", "/r", "/t", "0"], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                self.show_error(f"Failed to restart system: {str(e)}")

class StatusTab(BaseTab):
    """Tab for managing Segment Heap status."""
    def __init__(self, parent=None, model=None, config_manager=None):
        super().__init__(parent, model, config_manager)
        self.init_ui()
        self.setup_performance_monitoring()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Status card
        status_card = QGroupBox("Segment Heap Status")
        status_layout = QHBoxLayout(status_card)
        
        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(24, 24)
        status_layout.addWidget(self.status_indicator)
        
        # Status text
        status_text_layout = QVBoxLayout()
        self.status_label = QLabel("Checking status...")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        status_text_layout.addWidget(self.status_label)
        
        self.detail_label = QLabel("Please wait...")
        self.detail_label.setFont(QFont("Segoe UI", 10))
        status_text_layout.addWidget(self.detail_label)
        
        status_layout.addLayout(status_text_layout)
        status_layout.addStretch()
        
        layout.addWidget(status_card)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.enable_btn = QPushButton("Enable Segment Heap")
        self.enable_btn.clicked.connect(self.enable_segment_heap)
        button_layout.addWidget(self.enable_btn)
        
        self.disable_btn = QPushButton("Disable Segment Heap")
        self.disable_btn.clicked.connect(self.disable_segment_heap)
        button_layout.addWidget(self.disable_btn)
        
        self.restart_btn = QPushButton("Restart Now")
        self.restart_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.restart_btn.clicked.connect(self.restart_system)
        button_layout.addWidget(self.restart_btn)
        
        self.refresh_btn = QPushButton("Refresh Status")
        self.refresh_btn.clicked.connect(self.update_status)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Auto-enable section
        auto_enable_card = QGroupBox("Automatic Re-enabling")
        auto_enable_layout = QVBoxLayout(auto_enable_card)
        
        info_text = QLabel(
            "Windows updates sometimes disable Segment Heap. Enable this option to automatically re-enable it after updates."
        )
        info_text.setWordWrap(True)
        auto_enable_layout.addWidget(info_text)
        
        auto_enable_control_layout = QHBoxLayout()
        
        self.auto_enable_checkbox = QCheckBox("Automatically re-enable Segment Heap after Windows updates")
        self.auto_enable_checkbox.setChecked(self.config_manager.get("auto_enable", False))
        self.auto_enable_checkbox.stateChanged.connect(self.toggle_auto_enable)
        auto_enable_control_layout.addWidget(self.auto_enable_checkbox)
        
        auto_enable_control_layout.addStretch()
        
        self.monitor_status_label = QLabel("Monitor: Not installed")
        auto_enable_control_layout.addWidget(self.monitor_status_label)
        
        self.install_monitor_btn = QPushButton("Install Monitor")
        self.install_monitor_btn.clicked.connect(self.install_monitor)
        auto_enable_control_layout.addWidget(self.install_monitor_btn)
        
        auto_enable_layout.addLayout(auto_enable_control_layout)
        layout.addWidget(auto_enable_card)
        
        # Performance stats
        perf_card = QGroupBox("System Performance")
        perf_layout = QVBoxLayout(perf_card)
        
        self.perf_table = QTableWidget(3, 2)
        self.perf_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.perf_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.perf_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.perf_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.perf_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        perf_layout.addWidget(self.perf_table)
        
        self.update_perf_btn = QPushButton("Refresh Performance Data")
        self.update_perf_btn.clicked.connect(self.update_performance_stats)
        perf_layout.addWidget(self.update_perf_btn)
        
        layout.addWidget(perf_card)
        
        # Backup history
        backup_card = QGroupBox("Backup History")
        backup_layout = QVBoxLayout(backup_card)
        
        self.backup_list = QListWidget()
        self.backup_list.itemDoubleClicked.connect(self.restore_from_backup)
        backup_layout.addWidget(self.backup_list)
        
        self.update_backup_list_btn = QPushButton("Refresh Backup List")
        self.update_backup_list_btn.clicked.connect(self.update_backup_list)
        backup_layout.addWidget(self.update_backup_list_btn)
        
        layout.addWidget(backup_card)
        
        layout.addStretch()
        
        # Initial updates
        self.update_backup_list()
        self.update_status()
        self.update_performance_stats()
        self.check_monitor_status()
    
    def setup_performance_monitoring(self):
        """Set up automatic performance monitoring."""
        self.perf_timer = QTimer(self)
        self.perf_timer.timeout.connect(self.update_performance_stats)
        self.perf_timer.start(30000)  # Update every 30 seconds
    
    def check_monitor_status(self):
        """Check if the monitor is installed."""
        try:
            # Check if the scheduled task exists
            result = subprocess.run(
                ['schtasks', '/query', '/tn', 'SegmentHeapMonitor'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.monitor_status_label.setText("Monitor: Installed")
                self.install_monitor_btn.setText("Uninstall Monitor")
            else:
                self.monitor_status_label.setText("Monitor: Not installed")
                self.install_monitor_btn.setText("Install Monitor")
        except Exception as e:
            logging.error(f"Error checking monitor status: {e}")
            self.monitor_status_label.setText("Monitor: Status unknown")
    
    def install_monitor(self):
        """Install or uninstall the monitor."""
        try:
            # Check if the task exists
            result = subprocess.run(
                ['schtasks', '/query', '/tn', 'SegmentHeapMonitor'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Task exists, uninstall it
                subprocess.run(
                    ['schtasks', '/delete', '/tn', 'SegmentHeapMonitor', '/f'],
                    check=True, capture_output=True
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
import logging
import json
import subprocess
import ctypes
from datetime import datetime

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
LOG_FILE = os.path.join(os.environ['TEMP'], "SegmentHeapManager", "monitor.log")

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    except Exception as e:
        logging.error(f"Failed to save config: {e}")

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
        logging.info(f"Segment Heap {'enabled' if enable else 'disabled'}")
        return True
    except Exception as e:
        logging.error(f"Failed to set Segment Heap status: {e}")
        return False

def check_windows_updates():
    try:
        # Get system uptime
        uptime = ctypes.windll.kernel32.GetTickCount() / 1000
        
        # If system was restarted in the last 24 hours, consider it a potential update
        return uptime < 86400  # 24 hours in seconds
    except Exception as e:
        logging.error(f"Error checking system uptime: {e}")
        return False

def main():
    if not is_admin():
        logging.error("Monitor must be run as administrator")
        return
    
    logging.info("Segment Heap Monitor started")
    
    # Load configuration
    config = load_config()
    
    # Check if auto-enable is enabled
    if not config.get("auto_enable", False):
        logging.info("Auto-enable is disabled in configuration")
        return
    
    # Check last check time
    last_check = config.get("last_check")
    now = datetime.now().isoformat()
    
    # Skip if we checked in the last 6 hours
    if last_check:
        last_check_time = datetime.fromisoformat(last_check)
        if (datetime.now() - last_check_time).total_seconds() < 21600:  # 6 hours
            logging.info("Skipping check - last check was recent")
            return
    
    # Update last check time
    config["last_check"] = now
    save_config(config)
    
    # Get current status
    current_status = get_segment_heap_status()
    logging.info(f"Current Segment Heap status: {'Enabled' if current_status else 'Disabled'}")
    
    # Check if Windows updates were installed
    updates_installed = check_windows_updates()
    
    # If Segment Heap is disabled and updates were installed, re-enable it
    if not current_status and updates_installed:
        logging.info("Windows updates detected - re-enabling Segment Heap")
        if set_segment_heap_status(True):
            logging.info("Segment Heap successfully re-enabled")
        else:
            logging.error("Failed to re-enable Segment Heap")
    else:
        logging.info("No action needed")

if __name__ == "__main__":
    main()
''')
                
                # Create the scheduled task
                subprocess.run([
                    'schtasks', '/create', '/tn', 'SegmentHeapMonitor',
                    '/tr', f'python "{monitor_script_path}"',
                    '/sc', 'onlogon', '/rl', 'highest', '/f'
                ], check=True, capture_output=True)
                
                self.show_success("Monitor installed successfully")
                self.config_manager.set("monitor_enabled", True)
            
            self.check_monitor_status()
        except subprocess.CalledProcessError as e:
            self.show_error(f"Failed to install/uninstall monitor: {e.stderr}")
        except Exception as e:
            self.show_error(f"Failed to install/uninstall monitor: {str(e)}")
    
    def toggle_auto_enable(self, state):
        """Toggle the auto-enable setting."""
        self.config_manager.set("auto_enable", state == Qt.CheckState.Checked.value)
        
        if state == Qt.CheckState.Checked.value:
            if not self.config_manager.get("monitor_enabled", False):
                reply = QMessageBox.question(
                    self, "Install Monitor",
                    "To automatically re-enable Segment Heap, you need to install the monitor.\n\nWould you like to install it now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.install_monitor()
    
    def update_performance_stats(self):
        """Update the performance statistics display."""
        worker = RegistryWorker('get_performance_stats')
        self.thread_manager.add_worker(worker)
        worker.finished.connect(self.populate_perf_table)
        worker.error.connect(self.show_error)
        worker.start()
    
    def populate_perf_table(self, result):
        """Populate the performance table with new data."""
        stats = result.get('stats', {})
        self.model.update_performance_stats(stats)
        
        metrics = [
            ("Memory Usage", f"{stats.get('memory_percent', 0):.1f}%"),
            ("CPU Usage", f"{stats.get('cpu_percent', 0):.1f}%"),
            ("Disk Usage", f"{stats.get('disk_percent', 0):.1f}%")
        ]
        
        self.perf_table.setRowCount(len(metrics))
        
        for i, (metric, value) in enumerate(metrics):
            metric_item = QTableWidgetItem(metric)
            self.perf_table.setItem(i, 0, metric_item)
            
            value_item = QTableWidgetItem(value)
            self.perf_table.setItem(i, 1, value_item)
    
    def update_backup_list(self):
        """Update the backup history list."""
        self.backup_list.clear()
        
        if os.path.exists(TEMP_DIR):
            backups = []
            for file in os.listdir(TEMP_DIR):
                if file.startswith("SegmentHeapBackup_") and file.endswith(".reg"):
                    backups.append(os.path.join(TEMP_DIR, file))
            
            # Sort by modification time, newest first
            backups.sort(key=os.path.getmtime, reverse=True)
            
            for backup in backups:
                timestamp = os.path.getmtime(backup)
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                self.backup_list.addItem(f"{date_str} - {os.path.basename(backup)}")
                self.backup_list.item(self.backup_list.count()-1).setData(Qt.ItemDataRole.UserRole, backup)
    
    def restore_from_backup(self, item):
        """Restore from a selected backup."""
        backup_path = item.data(Qt.ItemDataRole.UserRole)
        if backup_path and os.path.exists(backup_path):
            reply = QMessageBox.question(
                self, "Confirm Restore",
                f"Restore from {os.path.basename(backup_path)}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                worker = RegistryWorker('import_backup', backup_path)
                self.thread_manager.add_worker(worker)
                worker.finished.connect(self.on_restore_complete)
                worker.error.connect(self.show_error)
                worker.start()
    
    def on_restore_complete(self, result):
        """Handle backup restoration completion."""
        if result.get('success', False):
            self.show_success("Registry restored successfully. Restart to apply changes.")
            self.update_status()
        else:
            self.show_error("Failed to restore registry.")
    
    def update_status(self):
        """Update the Segment Heap status display."""
        self.status_label.setText("Checking status...")
        self.detail_label.setText("Please wait...")
        self.update_status_indicator("unknown")
        
        worker = RegistryWorker('get_status')
        self.thread_manager.add_worker(worker)
        worker.finished.connect(self.update_status_display)
        worker.error.connect(self.show_error)
        worker.start()
    
    def update_status_indicator(self, status):
        """Update the status indicator."""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine color based on status
        if status == "enabled":
            color = QColor(76, 175, 80)  # Green
        elif status == "disabled":
            color = QColor(244, 67, 54)  # Red
        else:
            color = QColor(158, 158, 158)  # Gray
        
        # Draw circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(2, 2, 20, 20)
        
        painter.end()
        self.status_indicator.setPixmap(pixmap)
    
    def update_status_display(self, result):
        """Update the status display with new information."""
        try:
            self.model.update_status(result)
            status = self.model.status['status']
            detail = self.model.status['detail']
            color = self.model.status['color']
            
            self.status_label.setText(f"Segment Heap: {status}")
            self.status_label.setStyleSheet(f"color: {color.name()};")
            self.detail_label.setText(detail)
            
            if status == "Enabled":
                self.update_status_indicator("enabled")
            elif status == "Disabled":
                self.update_status_indicator("disabled")
            else:
                self.update_status_indicator("unknown")
            
            # Update system tray icon
            if hasattr(self.parent, 'update_tray_icon'):
                self.parent.update_tray_icon(status)
        except Exception as e:
            logging.error(f"Error updating status display: {e}")
            self.show_error(f"Error updating status: {str(e)}")
    
    def enable_segment_heap(self):
        """Enable Segment Heap."""
        reply = QMessageBox.question(
            self, "Confirm Enable",
            "Are you sure you want to enable Segment Heap? This will change how memory is managed system-wide.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            worker = RegistryWorker('set_status', True)
            self.thread_manager.add_worker(worker)
            worker.finished.connect(self.on_status_changed)
            worker.error.connect(self.show_error)
            worker.start()
    
    def disable_segment_heap(self):
        """Disable Segment Heap."""
        reply = QMessageBox.question(
            self, "Confirm Disable",
            "Are you sure you want to disable Segment Heap? This will revert to the default memory manager.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            worker = RegistryWorker('set_status', False)
            self.thread_manager.add_worker(worker)
            worker.finished.connect(self.on_status_changed)
            worker.error.connect(self.show_error)
            worker.start()
    
    def on_status_changed(self, result):
        """Handle status change completion."""
        try:
            backup_path = result['backup_path']
            self.model.set_last_backup(backup_path)
            self.show_success(
                f"Segment Heap status changed successfully!\n\nBackup created: {backup_path}"
            )
            self.update_status()
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling status change: {e}")
            self.show_error(f"Error: {str(e)}")

class ExcludedAppsTab(BaseTab):
    """Tab for managing applications excluded from Segment Heap."""
    def __init__(self, parent=None, model=None, config_manager=None):
        super().__init__(parent, model, config_manager)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Applications listed below will continue using the default Low Fragmentation Heap (LFH) "
            "instead of Segment Heap:"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Progress bar for batch operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search excluded apps...")
        self.search_edit.textChanged.connect(self.filter_list)
        search_layout.addWidget(self.search_edit)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "System", "User"])
        self.filter_combo.currentTextChanged.connect(self.filter_list)
        search_layout.addWidget(self.filter_combo)
        
        layout.addLayout(search_layout)
        
        # Content area
        content_layout = QHBoxLayout()
        
        # Left side - apps list
        left_layout = QVBoxLayout()
        self.apps_list = QListWidget()
        self.apps_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(QLabel("Excluded Applications:"))
        left_layout.addWidget(self.apps_list)
        content_layout.addLayout(left_layout, 2)
        
        # Right side - controls
        right_layout = QVBoxLayout()
        
        # Add application section
        add_group = QGroupBox("Add New Excluded Application")
        add_layout = QFormLayout(add_group)
        
        self.app_name_edit = QLineEdit()
        self.app_name_edit.setPlaceholderText("e.g., notepad.exe")
        add_layout.addRow("Executable Name:", self.app_name_edit)
        
        self.common_apps = QComboBox()
        self.common_apps.addItems(["Select an application..."] + COMMON_APPS)
        self.common_apps.currentIndexChanged.connect(self.on_common_app_selected)
        add_layout.addRow("Common Applications:", self.common_apps)
        
        self.add_btn = QPushButton("Add Application")
        self.add_btn.clicked.connect(self.add_app)
        add_layout.addRow(self.add_btn)
        
        right_layout.addWidget(add_group)
        
        # Remove application section
        remove_group = QGroupBox("Remove Application")
        remove_layout = QVBoxLayout(remove_group)
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_app)
        self.remove_btn.setStyleSheet("background-color: #f44336; color: white;")
        remove_layout.addWidget(self.remove_btn)
        
        right_layout.addWidget(remove_group)
        
        # Bulk operations section
        bulk_group = QGroupBox("Bulk Operations")
        bulk_layout = QVBoxLayout(bulk_group)
        
        self.import_btn = QPushButton("Import from File")
        self.import_btn.clicked.connect(self.import_list)
        bulk_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export List")
        self.export_btn.clicked.connect(self.export_list)
        bulk_layout.addWidget(self.export_btn)
        
        self.clear_all_btn = QPushButton("Clear All Exclusions")
        self.clear_all_btn.clicked.connect(self.clear_all)
        self.clear_all_btn.setStyleSheet("background-color: #f44336; color: white;")
        bulk_layout.addWidget(self.clear_all_btn)
        
        right_layout.addWidget(bulk_group)
        
        # Help section
        help_group = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFont(QFont("Segoe UI", 9))
        help_text.setMaximumHeight(180)
        help_text.setText("""\
EXCLUSION LIST HELP:

Applications in the exclusion list will continue to use the default Low Fragmentation Heap (LFH) instead of Segment Heap.

WHEN TO EXCLUDE APPLICATIONS:
• Legacy applications that have compatibility issues with Segment Heap
• Applications that perform better with LFH
• Critical system applications that you don't want to modify

Changes require a system restart to take effect.
        """)
        
        help_layout.addWidget(help_text)
        right_layout.addWidget(help_group)
        
        right_layout.addStretch()
        content_layout.addLayout(right_layout, 1)
        layout.addLayout(content_layout)
        
        self.update_list()
    
    def filter_list(self):
        """Filter the list based on search text and filter type."""
        search_text = self.search_edit.text().lower()
        filter_type = self.filter_combo.currentText()
        
        for i in range(self.apps_list.count()):
            item = self.apps_list.item(i)
            app_name = item.text().lower()
            
            # Show all items initially
            item.setHidden(False)
            
            # Apply search filter
            if search_text and search_text not in app_name:
                item.setHidden(True)
                continue
            
            # Apply type filter
            if filter_type == "System" and not self.is_system_app(app_name):
                item.setHidden(True)
            elif filter_type == "User" and self.is_system_app(app_name):
                item.setHidden(True)
    
    def is_system_app(self, app_name: str) -> bool:
        """Check if an app is likely a system application."""
        return app_name in SYSTEM_APPS
    
    def import_list(self):
        """Import excluded apps from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excluded Applications List",
            "", "Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    apps_to_add = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line.endswith('.exe'):
                            apps_to_add.append(line)
                
                if apps_to_add:
                    reply = QMessageBox.question(
                        self, "Confirm Import",
                        f"Add {len(apps_to_add)} applications to exclusion list?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        self.batch_add_apps(apps_to_add)
                else:
                    QMessageBox.information(self, "Information", "No valid applications found in the file.")
            except Exception as e:
                self.show_error(f"Failed to import exclusion list: {str(e)}")
    
    def batch_add_apps(self, apps: List[str]):
        """Add multiple apps to the exclusion list."""
        success_count = 0
        for app in apps:
            try:
                worker = RegistryWorker('add_excluded_app', app)
                worker.run()  # Run synchronously for simplicity
                success_count += 1
            except Exception as e:
                logging.error(f"Failed to add {app}: {str(e)}")
        
        QMessageBox.information(
            self, "Import Complete",
            f"Successfully added {success_count} of {len(apps)} applications to the exclusion list."
        )
        self.update_list()
    
    def export_list(self):
        """Export the exclusion list to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Excluded Applications List",
            "", "Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("# Segment Heap Exclusion List\n")
                    f.write("# Applications listed here will use LFH instead of Segment Heap\n\n")
                    for app in self.model.excluded_apps:
                        f.write(f"{app}\n")
                
                self.show_success(f"Exclusion list exported to {file_path}")
            except Exception as e:
                self.show_error(f"Failed to export exclusion list: {str(e)}")
    
    def clear_all(self):
        """Clear all exclusions."""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to remove all exclusions? This will allow all applications to use Segment Heap.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.progress_bar.setVisible(True)
            worker = RegistryWorker('batch_remove_apps', self.model.excluded_apps)
            self.thread_manager.add_worker(worker)
            worker.finished.connect(self.on_clear_complete)
            worker.error.connect(self.show_error)
            worker.progress.connect(self.progress_bar.setValue)
            worker.start()
    
    def on_clear_complete(self, result):
        """Handle clear operation completion."""
        try:
            removed_count = result.get('removed_count', 0)
            self.progress_bar.setVisible(False)
            QMessageBox.information(
                self, "Clear Complete",
                f"Removed {removed_count} applications from the exclusion list."
            )
            self.update_list()
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling clear completion: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def update_list(self):
        """Update the list of excluded applications."""
        self.apps_list.clear()
        
        worker = RegistryWorker('get_excluded_apps')
        self.thread_manager.add_worker(worker)
        worker.finished.connect(self.populate_list)
        worker.error.connect(self.show_error)
        worker.start()
    
    def populate_list(self, result):
        """Populate the list with excluded applications."""
        try:
            self.model.update_excluded_apps(result)
            apps = self.model.excluded_apps
            logging.info(f"Populating excluded apps list with {len(apps)} items: {apps}")
            self.apps_list.addItems(apps)
            
            if not apps:
                logging.warning("No excluded apps found in registry")
        except Exception as e:
            logging.error(f"Error populating excluded apps list: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def on_common_app_selected(self, index):
        """Handle selection from common apps dropdown."""
        if index > 0:
            self.app_name_edit.setText(self.common_apps.currentText())
    
    def add_app(self):
        """Add an application to the exclusion list."""
        app_name = self.app_name_edit.text().strip()
        
        if not app_name:
            self.show_error("Please enter an executable name (e.g., notepad.exe)")
            return
        
        if not app_name.lower().endswith('.exe'):
            self.show_error("Executable name must end with .exe")
            return
        
        if len(app_name) > 260:
            self.show_error("Executable name is too long (max: 260 characters)")
            return
        
        worker = RegistryWorker('add_excluded_app', app_name)
        self.thread_manager.add_worker(worker)
        worker.finished.connect(self.on_app_added)
        worker.error.connect(self.show_error)
        worker.start()
    
    def on_app_added(self, result):
        """Handle app addition completion."""
        try:
            backup_path = result['backup_path']
            self.model.set_last_backup(backup_path)
            self.show_success(
                f"Application added to exclusion list successfully!\n\nBackup created: {backup_path}"
            )
            self.app_name_edit.clear()
            self.common_apps.setCurrentIndex(0)
            self.update_list()
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling app addition: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def remove_app(self):
        """Remove selected applications from the exclusion list."""
        selected_items = self.apps_list.selectedItems()
        if not selected_items:
            self.show_error("Please select an application to remove")
            return
        
        app_names = [item.text() for item in selected_items]
        
        if len(app_names) > 1:
            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Are you sure you want to remove {len(app_names)} applications from the exclusion list?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Are you sure you want to remove '{app_names[0]}' from the exclusion list?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
        if reply == QMessageBox.StandardButton.Yes:
            if len(app_names) > 1:
                # Use batch operation for multiple apps
                self.progress_bar.setVisible(True)
                worker = RegistryWorker('batch_remove_apps', app_names)
                self.thread_manager.add_worker(worker)
                worker.finished.connect(self.on_batch_remove_complete)
                worker.error.connect(self.show_error)
                worker.progress.connect(self.progress_bar.setValue)
                worker.start()
            else:
                # Single app removal
                worker = RegistryWorker('remove_excluded_app', app_names[0])
                self.thread_manager.add_worker(worker)
                worker.finished.connect(self.on_app_removed)
                worker.error.connect(self.show_error)
                worker.start()
    
    def on_app_removed(self, result):
        """Handle single app removal completion."""
        try:
            backup_path = result['backup_path']
            self.model.set_last_backup(backup_path)
            self.show_success(
                f"Application removed from exclusion list successfully!\n\nBackup created: {backup_path}"
            )
            self.update_list()
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling app removal: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def on_batch_remove_complete(self, result):
        """Handle batch removal completion."""
        try:
            removed_count = result.get('removed_count', 0)
            self.progress_bar.setVisible(False)
            QMessageBox.information(
                self, "Removal Complete",
                f"Successfully removed {removed_count} applications from the exclusion list."
            )
            self.update_list()
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling batch removal completion: {e}")
            self.show_error(f"Error: {str(e)}")

class HeapParamsTab(BaseTab):
    """Tab for managing heap parameters."""
    def __init__(self, parent=None, model=None, config_manager=None):
        super().__init__(parent, model, config_manager)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Configure heap parameters to optimize memory management. "
            "Changes will apply to the entire system after restart."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Current parameters display
        params_group = QGroupBox("Current Heap Parameters")
        params_layout = QVBoxLayout(params_group)
        
        self.params_table = QTableWidget(4, 3)
        self.params_table.setHorizontalHeaderLabels(["Parameter", "Current Value", "Description"])
        self.params_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.params_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.params_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.params_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.params_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        params_layout.addWidget(self.params_table)
        
        layout.addWidget(params_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Parameters")
        self.edit_btn.clicked.connect(self.edit_parameters)
        button_layout.addWidget(self.edit_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        self.copy_btn = QPushButton("Copy to Segment Heap")
        self.copy_btn.clicked.connect(self.copy_to_segment_heap)
        button_layout.addWidget(self.copy_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.update_params)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Help section
        help_group = QGroupBox("Help")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFont(QFont("Segoe UI", 9))
        help_text.setMaximumHeight(180)
        help_text.setText("""\
HEAP PARAMETERS HELP:

These parameters control how Windows manages memory allocation. Adjusting them can improve performance for specific workloads.

PARAMETER DESCRIPTIONS:
• HeapSegmentReserve: Virtual memory reserved per heap segment
• HeapSegmentCommit: Physical memory committed upfront per segment
• HeapDeCommitTotalFreeThreshold: Total free memory threshold for decommit
• HeapDeCommitFreeBlockThreshold: Free block size threshold for decommit

NOTE: Changes require a system restart to take effect.
        """)
        
        help_layout.addWidget(help_text)
        layout.addWidget(help_group)
        
        layout.addStretch()
        
        # Initial update
        self.update_params()
    
    def update_params(self):
        """Update the parameters display."""
        worker = RegistryWorker('get_heap_params')
        self.thread_manager.add_worker(worker)
        worker.finished.connect(self.populate_params_table)
        worker.error.connect(self.show_error)
        worker.start()
    
    def populate_params_table(self, result):
        """Populate the parameters table with current values."""
        try:
            self.model.update_params(result)
            params = self.model.params
            
            param_info = {
                'HeapSegmentReserve': {
                    'description': 'Virtual memory reserved per heap segment'
                },
                'HeapSegmentCommit': {
                    'description': 'Physical memory committed upfront per segment'
                },
                'HeapDeCommitTotalFreeThreshold': {
                    'description': 'Total free memory threshold for decommit'
                },
                'HeapDeCommitFreeBlockThreshold': {
                    'description': 'Free block size threshold for decommit'
                }
            }
            
            self.params_table.setRowCount(4)
            
            for i, (param, info) in enumerate(param_info.items()):
                # Parameter name
                param_item = QTableWidgetItem(param)
                self.params_table.setItem(i, 0, param_item)
                
                # Current value
                value = params.get(param)
                if value is not None:
                    value_text = f"0x{value:08x} ({self.format_byte_size(value)})"
                else:
                    value_text = "Using Windows default"
                value_item = QTableWidgetItem(value_text)
                self.params_table.setItem(i, 1, value_item)
                
                # Description
                desc_item = QTableWidgetItem(info['description'])
                self.params_table.setItem(i, 2, desc_item)
        except Exception as e:
            logging.error(f"Error populating parameters table: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def format_byte_size(self, bytes_value: int) -> str:
        """Format byte size in human-readable format."""
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
            new_params = dialog.get_parameters()
            if new_params:
                worker = RegistryWorker('set_heap_params', new_params)
                self.thread_manager.add_worker(worker)
                worker.finished.connect(self.on_params_changed)
                worker.error.connect(self.show_error)
                worker.start()
    
    def on_params_changed(self, result):
        """Handle parameter change completion."""
        try:
            backup_path = result['backup_path']
            self.model.set_last_backup(backup_path)
            self.show_success(
                f"Heap parameters updated successfully!\n\nBackup created: {backup_path}"
            )
            self.update_params()
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling parameter change: {e}")
            self.show_error(f"Error: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all parameters to Windows defaults."""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all heap parameters to Windows defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Set all parameters to None (use defaults)
            default_params = {param: None for param in DEFAULT_HEAP_PARAMS}
            
            worker = RegistryWorker('set_heap_params', default_params)
            self.thread_manager.add_worker(worker)
            worker.finished.connect(self.on_params_changed)
            worker.error.connect(self.show_error)
            worker.start()
    
    def copy_to_segment_heap(self):
        """Copy current heap parameters to Segment Heap key."""
        reply = QMessageBox.question(
            self, "Confirm Copy",
            "Are you sure you want to copy current heap parameters to Segment Heap key?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            worker = RegistryWorker('copy_params_to_segment_heap')
            self.thread_manager.add_worker(worker)
            worker.finished.connect(self.on_copy_complete)
            worker.error.connect(self.show_error)
            worker.start()
    
    def on_copy_complete(self, result):
        """Handle copy operation completion."""
        try:
            backup_path = result['backup_path']
            self.model.set_last_backup(backup_path)
            self.show_success(
                f"Heap parameters copied to Segment Heap key successfully!\n\nBackup created: {backup_path}"
            )
            self.prompt_restart()
        except Exception as e:
            logging.error(f"Error handling copy completion: {e}")
            self.show_error(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.model = HeapModel()
        self.tray_icon = None
        self.init_ui()
        self.setup_tray_icon()
        self.apply_theme()
    
    def init_ui(self):
        self.setWindowTitle(f"Enhanced Segment Heap Manager v{APP_VERSION}")
        self.setMinimumSize(900, 700)
        
        # Set window icon
        self.setWindowIcon(QIcon(self.create_icon()))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header_layout = QHBoxLayout()
        
        # App logo and title
        title_layout = QVBoxLayout()
        app_title = QLabel(f"Segment Heap Manager v{APP_VERSION}")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_layout.addWidget(app_title)
        
        app_subtitle = QLabel("Advanced Windows Memory Management Tool")
        app_subtitle.setFont(QFont("Segoe UI", 10))
        app_subtitle.setStyleSheet("color: gray;")
        title_layout.addWidget(app_subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "High Contrast"])
        current_theme = self.config_manager.get("theme", "dark")
        self.theme_combo.setCurrentText(current_theme.capitalize())
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        header_layout.addLayout(theme_layout)
        layout.addLayout(header_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self.status_tab = StatusTab(self, self.model, self.config_manager)
        self.tabs.addTab(self.status_tab, "Status")
        
        self.excluded_apps_tab = ExcludedAppsTab(self, self.model, self.config_manager)
        self.tabs.addTab(self.excluded_apps_tab, "Excluded Apps")
        
        self.heap_params_tab = HeapParamsTab(self, self.model, self.config_manager)
        self.tabs.addTab(self.heap_params_tab, "Heap Parameters")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set up timer for periodic status checks
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_status_periodically)
        self.status_timer.start(60000)  # Check every minute
    
    def create_icon(self):
        """Create a simple icon for the application."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a simple memory chip icon
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setBrush(QBrush(QColor(76, 175, 80)))
        painter.drawRect(16, 16, 32, 32)
        
        # Draw details
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        for i in range(3):
            painter.drawLine(20, 24 + i*8, 44, 24 + i*8)
        
        painter.end()
        return QIcon(pixmap)
    
    def setup_tray_icon(self):
        """Set up system tray icon."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip(f"Segment Heap Manager v{APP_VERSION}")
        self.tray_icon.setIcon(self.create_icon())
        
        # Create context menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        self.enable_action = QAction("Enable Segment Heap", self)
        self.enable_action.triggered.connect(self.status_tab.enable_segment_heap)
        tray_menu.addAction(self.enable_action)
        
        self.disable_action = QAction("Disable Segment Heap", self)
        self.disable_action.triggered.connect(self.status_tab.disable_segment_heap)
        tray_menu.addAction(self.disable_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def update_tray_icon(self, status):
        """Update the tray icon based on Segment Heap status."""
        if not self.tray_icon:
            return
        
        if status == "Enabled":
            self.tray_icon.setToolTip(f"Segment Heap Manager - Status: Enabled")
            self.enable_action.setEnabled(False)
            self.disable_action.setEnabled(True)
        elif status == "Disabled":
            self.tray_icon.setToolTip(f"Segment Heap Manager - Status: Disabled")
            self.enable_action.setEnabled(True)
            self.disable_action.setEnabled(False)
        else:
            self.tray_icon.setToolTip(f"Segment Heap Manager - Status: Unknown")
            self.enable_action.setEnabled(True)
            self.disable_action.setEnabled(True)
    
    def check_status_periodically(self):
        """Periodically check the Segment Heap status."""
        if not self.isVisible():
            # Only check if window is not visible to avoid conflicts
            worker = RegistryWorker('get_status')
            worker.finished.connect(lambda result: self.update_tray_icon(result['status']))
            worker.start()
    
    def apply_theme(self):
        """Apply the selected theme."""
        theme = self.config_manager.get("theme", "dark")
        
        if theme == "light":
            self.apply_light_theme()
        elif theme == "high_contrast":
            self.apply_high_contrast_theme()
        else:
            self.apply_dark_theme()
    
    def apply_dark_theme(self):
        """Apply dark theme."""
        app = QApplication.instance()
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        app.setPalette(palette)
    
    def apply_light_theme(self):
        """Apply light theme."""
        app = QApplication.instance()
        app.setPalette(app.style().standardPalette())
    
    def apply_high_contrast_theme(self):
        """Apply high contrast theme."""
        app = QApplication.instance()
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        app.setPalette(palette)
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        theme = theme_name.lower()
        self.config_manager.set("theme", theme)
        self.apply_theme()
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Clean up threads
        self.status_tab.thread_manager.cleanup()
        self.excluded_apps_tab.thread_manager.cleanup()
        self.heap_params_tab.thread_manager.cleanup()
        
        # Hide to tray instead of closing
        if self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.show_tray_message("Application minimized to tray", "Double-click the tray icon to show the window again.")
        else:
            event.accept()
    
    def show_tray_message(self, title, message):
        """Show a message in the system tray."""
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

def main():
    """Main entry point for the application."""
    # Create QApplication first
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(COMPANY_NAME)
    
    # Check for administrator privileges and request elevation if needed
    if not is_admin():
        reply = QMessageBox.question(
            None, "Administrator Privileges Required",
            "This application requires administrator privileges to modify system settings.\n\n"
            "Would you like to restart with administrator privileges?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            restart_as_admin()
        else:
            QMessageBox.critical(
                None, "Insufficient Privileges",
                "This application cannot function properly without administrator privileges."
            )
            sys.exit(1)
    
    # Set up logging
    log_file = setup_logging()
    logging.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logging.info(f"Log file: {log_file}")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()