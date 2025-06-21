import os
import random
import string
import subprocess
import ctypes
import sys
import time
import urllib.request
import uuid
import hashlib
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLineEdit, QLabel, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon
from ctypes import windll, byref, c_ulong

# Admin elevation functions
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        script = os.path.abspath(sys.argv[0])
        python_exe = sys.executable  # Get the full path to the Python executable
        params = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
        batch_file = os.path.join(os.environ['TEMP'], 'run_as_admin.bat')
        
        with open(batch_file, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Requesting administrative privileges...\n')
            f.write(f'powershell -Command "Start-Process \"{python_exe}\" -ArgumentList \"{script} {params}\" -Verb RunAs"\n')
            f.write('del "%~f0"\n')
        
        subprocess.Popen(batch_file, shell=True)
        sys.exit(0)

# Constants
BRANDING = "Hyfty"
PRINTCLR = "#2563EB"  # Blue color for GUI
AUTHENTICATED = False
STD_OUTPUT_HANDLE = -11
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
TEMP_DIR_PATH = r"C:\Windows\System32"  # Changed to System32
AMI_EXE_URL = "https://raw.githubusercontent.com/creed3900/viywiwyeviweyv/main/AMIDEWINx64.EXE"
AMIFLDRV_URL = "https://raw.githubusercontent.com/creed3900/viywiwyeviweyv/main/amifldrv64.sys"
AMIGENDRV_URL = "https://raw.githubusercontent.com/creed3900/viywiwyeviweyv/main/amigendrv64.sys"
BATCH_FILE_PATH = os.path.join(TEMP_DIR_PATH, f"{BRANDING}_bat.bat")
TASK_NAME = f"{BRANDING}"
ASCII = r"""
                      
     __  __      ______       
   / / / /_  __/ __/ /___  __
  / /_/ / / / / /_/ __/ / / /
 / __  / /_/ / __/ /_/ /_/ / 
/_/ /_/\__, /_/  \__/\__, /  
      /____/        /____/                                                  
"""

# KeyAuthAPI class
class KeyAuthAPI:
    def __init__(self, name, ownerid, version, hash_to_check):
        if len(ownerid) != 10:
            print("Invalid ownerid length. Get your correct KeyAuth credentials.")
            sys.exit(1)
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.sessionid = ""
        self.initialized = False
        self.init()

    def init(self):
        if self.sessionid != "":
            print("Already initialized.")
            sys.exit(1)
        post_data = {
            "type": "init",
            "ver": self.version,
            "hash": self.hash_to_check,
            "name": self.name,
            "ownerid": self.ownerid
        }
        response = self.__do_request(post_data)
        if response == "KeyAuth_Invalid":
            print("Application doesn't exist.")
            sys.exit(1)
        json_resp = json.loads(response)
        if json_resp["message"] == "invalidver":
            if json_resp.get("download"):
                print("New version available, opening download link...")
                os.system(f"start {json_resp['download']}")
                sys.exit(1)
            else:
                print("Invalid version, contact owner.")
                sys.exit(1)
        if not json_resp["success"]:
            print(json_resp["message"])
            sys.exit(1)
        self.sessionid = json_resp["sessionid"]
        self.initialized = True

    def license(self, key, hwid=None):
        self.__check_init()
        if hwid is None:
            hwid = self.get_hwid()
        post_data = {
            "type": "license",
            "key": key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }
        response = self.__do_request(post_data)
        json_resp = json.loads(response)
        return json_resp["success"]

    def __do_request(self, post_data):
        try:
            response = requests.post("https://keyauth.win/api/1.3/", data=post_data, timeout=10)
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            sys.exit(1)

    def __check_init(self):
        if not self.initialized:
            print("Call init() before using this function.")
            sys.exit(1)

    @staticmethod
    def get_hwid():
        import platform
        return platform.node()

# Utility functions
def getchecksum():
    file_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return None

def enable_vt_mode():
    hOut = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    mode = c_ulong()
    windll.kernel32.GetConsoleMode(hOut, byref(mode))
    mode = c_ulong(mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    windll.kernel32.SetConsoleMode(hOut, mode)

def set_window_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def generate_random_string(length=15, lowercase=False):
    chars = string.ascii_uppercase + string.digits
    if lowercase:
        chars += string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(length))

def generate_random_uuid():
    return str(uuid.uuid4()).replace('-', '').upper()

def wmic_read_serial(name):
    try:
        if name == "BIOS Serial":
            cmd = ["wmic", "bios", "get", "serialnumber"]
        elif name == "BaseBoard Serial":
            cmd = ["wmic", "baseboard", "get", "serialnumber"]
        elif name == "Chassis Serial":
            cmd = ["wmic", "chassis", "get", "serialnumber"]
        elif name == "Processor Serial":
            cmd = ["wmic", "cpu", "get", "ProcessorId"]
        elif name == "System Serial":
            cmd = ["wmic", "computersystem", "get", "serialnumber"]
        else:
            return "UNKNOWN"
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        lines = output.strip().splitlines()
        return lines[1].strip() if len(lines) >= 2 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def generate_intel():
    base_prefix = "BX"
    cpu_ids = ["80715", "80716", "80717", "80718", "80719", "80684", "80693", "80695", "80697", "80808"]
    models = ["12400F", "12600K", "12700K", "12900KF", "13400F", "13600K", "13700K", "13900KS", "14400F", "14600K", "14700KF", "14900K"]
    return f"{base_prefix}{random.choice(cpu_ids)}{random.choice(models)}"

def task_exists(task_name):
    cmd = ['schtasks', '/Query', '/TN', task_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def create_scheduled_task(task_name, batch_path):
    cmd = ["schtasks", "/Create", "/SC", "ONSTART", "/RL", "HIGHEST", "/TN", task_name, "/TR", f'"{batch_path}"', "/F"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def download_file(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        # Verify the file is executable
        if os.path.exists(dest) and os.access(dest, os.X_OK):
            return True, ""
        else:
            os.chmod(dest, 0o755)  # Attempt to make it executable
            return os.path.exists(dest) and os.access(dest, os.X_OK), "File downloaded but not executable. Permissions may need adjustment."
    except Exception as e:
        return False, str(e)

def create_batch_file(uuid_val, SS, CS, BS, PSN, PAT, PPN):
    lines = [
        "@echo off", "setlocal EnableDelayedExpansion", "pushd %~dp0",
        f"title {BRANDING} Processing...", f'AMIDEWINx64.EXE /SU {uuid_val} >nul 2>&1',
        f'AMIDEWINx64.EXE /SS {SS} >nul 2>&1', f'AMIDEWINx64.EXE /CS {CS} >nul 2>&1',
        f'AMIDEWINx64.EXE /BS {BS} >nul 2>&1', f'AMIDEWINx64.EXE /PSN {PSN} >nul 2>&1',
        f'AMIDEWINx64.EXE /PAT {PAT} >nul 2>&1', f'AMIDEWINx64.EXE /PPN {PPN} >nul 2>&1',
        'AMIDEWINx64.EXE /CSK "Default string" >nul 2>&1', 'AMIDEWINx64.EXE /CM "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /SK "Default string" >nul 2>&1', 'AMIDEWINx64.EXE /SF "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /BT "Default string" >nul 2>&1', 'AMIDEWINx64.EXE /BLC "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /CA "Default string" >nul 2>&1', "exit"
    ]
    os.makedirs(TEMP_DIR_PATH, exist_ok=True)
    with open(BATCH_FILE_PATH, "w") as f:
        f.write("\r\n".join(lines))
    return True

def spoof_random_serials(asus_mode=False, parent=None):
    if not is_admin():
        QMessageBox.critical(parent, f"{BRANDING} Error", "Administrator privileges required for spoofing.")
        return False, "Administrator privileges required."

    serial_names = ["BIOS Serial", "BaseBoard Serial", "Chassis Serial", "Processor Serial", "System Serial"]
    old_serials = {name: wmic_read_serial(name) for name in serial_names}
    new_serials = {name: generate_random_string(15) for name in serial_names}

    # Prepare serials
    uuid_val = new_serials["BIOS Serial"]
    BS = new_serials["BaseBoard Serial"]
    SS = new_serials["System Serial"]
    CS = new_serials["Chassis Serial"]
    PSN = new_serials["Processor Serial"]
    PAT = "CPU-INTEL-WINTERZ"
    PPN = generate_intel()

    # Download files if not present and verify
    ami_exe_path = os.path.join(TEMP_DIR_PATH, "AMIDEWINx64.EXE")
    if not os.path.exists(ami_exe_path):
        success, error = download_file(AMI_EXE_URL, ami_exe_path)
        if not success:
            QMessageBox.critical(parent, f"{BRANDING} Error", f"Failed to download AMIDEWINx64.EXE: {error}")
            return False, f"Download failed: {error}"
    for url, dest in [
        (AMIFLDRV_URL, os.path.join(TEMP_DIR_PATH, "amifldrv64.sys")),
        (AMIGENDRV_URL, os.path.join(TEMP_DIR_PATH, "amigendrv64.sys"))
    ]:
        if not os.path.exists(dest):
            success, error = download_file(url, dest)
            if not success:
                QMessageBox.critical(parent, f"{BRANDING} Error", f"Failed to download {os.path.basename(dest)}: {error}")
                return False, f"Download failed: {error}"

    if not os.path.exists(ami_exe_path) or not os.access(ami_exe_path, os.X_OK):
        QMessageBox.critical(parent, f"{BRANDING} Error", "AMIDEWINx64.EXE not found or not executable. Please ensure the file is downloaded and has proper permissions.")
        return False, "AMIDEWINx64.EXE not executable"

    if not asus_mode:
        commands = [
            f'AMIDEWINx64.EXE /SU {uuid_val}',
            f'AMIDEWINx64.EXE /SS {SS}',
            f'AMIDEWINx64.EXE /CS {CS}',
            f'AMIDEWINx64.EXE /BS {BS}',
            f'AMIDEWINx64.EXE /PSN {PSN}',
            f'AMIDEWINx64.EXE /PAT {PAT}',
            f'AMIDEWINx64.EXE /PPN {PPN}',
            'AMIDEWINx64.EXE /CSK "Default string"',
            'AMIDEWINx64.EXE /CM "Default string"',
            'AMIDEWINx64.EXE /SK "Default string"',
            'AMIDEWINx64.EXE /SF "Default string"',
            'AMIDEWINx64.EXE /BT "Default string"',
            'AMIDEWINx64.EXE /BLC "Default string"',
            'AMIDEWINx64.EXE /CA "Default string"'
        ]
        for cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    QMessageBox.critical(parent, f"{BRANDING} Error", f"Failed to execute spoofing command: {cmd}\nError: {result.stderr}")
                    return False, f"Command failed: {cmd}\nError: {result.stderr}"
            except Exception as e:
                QMessageBox.critical(parent, f"{BRANDING} Error", f"Exception executing command: {cmd}\nError: {str(e)}")
                return False, f"Exception: {str(e)}"
        # Verify spoofing by re-reading serials
        new_serials_verified = {name: wmic_read_serial(name) for name in serial_names}
        if any(old_serials[name] == new_serials_verified[name] for name in serial_names):
            QMessageBox.warning(parent, f"{BRANDING} Warning", "Spoofing may not have applied. Please restart your system or check admin privileges.")
        return True, {"message": "Successfully executed spoofing command: All serials spoofed.", "serials": new_serials}
    else:
        success = create_batch_file(uuid_val, SS, CS, BS, PSN, PAT, PPN)
        if not success:
            QMessageBox.critical(parent, f"{BRANDING} Error", "Failed to create batch file.")
            return False, "Batch file creation failed."
        if task_exists(TASK_NAME):
            reply = QMessageBox.question(parent, f"{BRANDING} Confirm", 
                                        "ASUS spoof task already exists. Overwrite?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return True, {"message": "ASUS spoof task already exists. Please contact support if serials aren't changing!", "serials": new_serials}
        success, error = create_scheduled_task(TASK_NAME, BATCH_FILE_PATH)
        if not success:
            QMessageBox.critical(parent, f"{BRANDING} Error", f"Failed to create scheduled task: {error}")
            return False, error
        return True, {"message": "ASUS Spoof setup complete. Please restart your PC and verify serials.", "serials": new_serials}

# GUI Classes
class LoginWindow(QWidget):
    def __init__(self, keyauth):
        super().__init__()
        self.keyauth = keyauth
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"{BRANDING} Spoofer")
        self.setFixedSize(400, 500)
        layout = QVBoxLayout()

        # Set dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(PRINTCLR))
        palette.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(palette)

        # ASCII logo
        ascii_label = QLabel(ASCII)
        ascii_label.setFont(QFont("Courier", 8))
        ascii_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(ascii_label)

        # Welcome text
        welcome_label = QLabel(f"Welcome to {BRANDING} Spoofer")
        welcome_label.setFont(QFont("Arial", 14, QFont.Bold))
        welcome_label.setStyleSheet(f"color: {PRINTCLR};")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        # Horizontal layout for Discord button
        discord_layout = QHBoxLayout()
        
        # Fancy Discord Button
        discord_path = os.path.join(TEMP_DIR_PATH, "discord_icon.png")
        if not os.path.exists(discord_path):
            download_file("https://cdn.discordapp.com/attachments/123456789/987654321/discord_icon.png", discord_path)  # Replace with valid URL
        discord_button = QPushButton("Join Discord")
        discord_pixmap = QPixmap(discord_path)
        if not discord_pixmap.isNull():  # Check if image loaded successfully
            discord_pixmap = discord_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            discord_button.setIcon(QIcon(discord_pixmap))
            discord_button.setIconSize(QSize(32, 32))
        discord_button.setStyleSheet("""
            QPushButton {
                background-color: #7289DA; /* Discord blue */
                color: white;
                padding: 12px 24px;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #5865F2;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #5865F2; /* Darker blue on hover */
                border: 2px solid #7289DA;
                transform: scale(1.05); /* Slight scale effect */
                transition: all 0.3s ease;
            }
            QPushButton:pressed {
                background-color: #4A5E9A; /* Even darker when pressed */
                transform: scale(0.98);
            }
            QPushButton:disabled {
                background-color: #A3BFFA;
                color: #D3D3D3;
                border: 2px solid #A3BFFA;
            }
        """)
        discord_button.clicked.connect(lambda: os.system(f"start https://discord.gg/nEHkzHZQ94"))
        discord_layout.addWidget(discord_button)
        discord_layout.addStretch()  # Push to the right
        layout.addLayout(discord_layout)

        # Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter License Key")
        self.key_input.setStyleSheet("padding: 10px; border-radius: 5px;")
        self.key_input.returnPressed.connect(self.authenticate)
        layout.addWidget(self.key_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet(f"background-color: {PRINTCLR}; padding: 10px; border-radius: 5px;")
        login_button.clicked.connect(self.authenticate)
        layout.addWidget(login_button)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        layout.addStretch()
        self.setLayout(layout)

    def authenticate(self):
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate progress
        QTimer.singleShot(1000, self.check_key)

    def check_key(self):
        key = self.key_input.text().strip()
        if self.keyauth.license(key):
            self.progress.setVisible(False)
            self.close()
            main_window = MainWindow()
            main_window.show()
        else:
            self.progress.setVisible(False)
            self.error_label.setText("Invalid license key")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"{BRANDING} Perm | Coded by 1337tuno")
        self.setFixedSize(400, 600)
        widget = QWidget()
        layout = QVBoxLayout()

        # Set dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(PRINTCLR))
        palette.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(palette)

        # ASCII logo
        ascii_label = QLabel(ASCII)
        ascii_label.setFont(QFont("Courier", 8))
        ascii_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(ascii_label)

        # Welcome text
        welcome_label = QLabel(f"Welcome to {BRANDING} Perm!")
        welcome_label.setFont(QFont("Arial", 14, QFont.Bold))
        welcome_label.setStyleSheet(f"color: {PRINTCLR};")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        # Horizontal layout for Discord button
        discord_layout = QHBoxLayout()
        
        # Fancy Discord Button
        discord_path = os.path.join(TEMP_DIR_PATH, "discord_icon.png")
        if not os.path.exists(discord_path):
            download_file("https://cdn.discordapp.com/attachments/123456789/987654321/discord_icon.png", discord_path)  # Replace with valid URL
        discord_button = QPushButton("Join Discord")
        discord_pixmap = QPixmap(discord_path)
        if not discord_pixmap.isNull():  # Check if image loaded successfully
            discord_pixmap = discord_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            discord_button.setIcon(QIcon(discord_pixmap))
            discord_button.setIconSize(QSize(32, 32))
        discord_button.setStyleSheet("""
            QPushButton {
                background-color: #7289DA; /* Discord blue */
                color: white;
                padding: 12px 24px;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #5865F2;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #5865F2; /* Darker blue on hover */
                border: 2px solid #7289DA;
                transform: scale(1.05); /* Slight scale effect */
                transition: all 0.3s ease;
            }
            QPushButton:pressed {
                background-color: #4A5E9A; /* Even darker when pressed */
                transform: scale(0.98);
            }
            QPushButton:disabled {
                background-color: #A3BFFA;
                color: #D3D3D3;
                border: 2px solid #A3BFFA;
            }
        """)
        discord_button.clicked.connect(lambda: os.system(f"start https://discord.gg/nEHkzHZQ94"))
        discord_layout.addWidget(discord_button)
        discord_layout.addStretch()  # Push to the right
        layout.addLayout(discord_layout)

        # Spoof buttons in vertical layout
        spoof_button = QPushButton("Spoof All Serials")
        spoof_button.setStyleSheet(f"background-color: {PRINTCLR}; padding: 10px; border-radius: 5px;")
        spoof_button.clicked.connect(lambda: self.spoof(False))
        layout.addWidget(spoof_button)

        asus_button = QPushButton("ASUS Spoof Mode")
        asus_button.setStyleSheet(f"background-color: {PRINTCLR}; padding: 10px; border-radius: 5px;")
        asus_button.clicked.connect(lambda: self.spoof(True))
        layout.addWidget(asus_button)

        # Exit button
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("background-color: #DC2626; padding: 10px; border-radius: 5px;")
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Result label
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: white;")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        layout.addStretch()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def spoof(self, asus_mode):
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        QTimer.singleShot(100, lambda: self.perform_spoof(asus_mode))

    def perform_spoof(self, asus_mode):
        success, result = spoof_random_serials(asus_mode, self)
        self.progress.setVisible(False)
        if success:
            message = result["message"]
            serials = result["serials"]
            serial_text = "\n".join([f"{name}: {value}" for name, value in serials.items()])
            self.result_label.setText(f"{message}\n\n{serial_text}")
            self.result_label.setStyleSheet("color: green;")
        else:
            self.result_label.setText(result)
            self.result_label.setStyleSheet("color: red;")

if __name__ == "__main__":
    run_as_admin()  # Ensure admin privileges
    enable_vt_mode()
    set_window_title(f"{BRANDING} Perm | Coded by 1337tuno -_- | {generate_random_string(15, True)}")
    WinterzAuth = KeyAuthAPI(
        name="ImHyfty's Application",
        ownerid="NUuHY0X3Li",
        version="1.0",
        hash_to_check=getchecksum()
    )
    app = QApplication(sys.argv)
    login_window = LoginWindow(WinterzAuth)
    login_window.show()
    sys.exit(app.exec_())
