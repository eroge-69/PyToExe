import socket
import threading
import os
import time
import getpass
import subprocess
import sys
import logging
import platform
import urllib.request
import tempfile
import shutil
import importlib
from pathlib import Path

# Configuration
HOST = '0.0.0.0'
PORT = 5000
LOG_FILE = 'server.log'
RECV_DIR = 'received_files'
TASK_NAME = "PythonTCPServer"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit for received files
RECOMMENDED_PYTHON_VERSION = (3, 10, 0)  # Minimum recommended Python version
REQUIRED_PACKAGES = ['logging', 'socket', 'threading', 'pathlib', 'urllib', 'platform']  # Add all your dependencies here

# Create received files directory
os.makedirs(RECV_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log(message, level='info'):
    """Log messages to both file and console."""
    if level.lower() == 'info':
        logging.info(message)
    elif level.lower() == 'warning':
        logging.warning(message)
    elif level.lower() == 'error':
        logging.error(message)
    else:
        logging.info(message)

    try:
        print(message)
        sys.stdout.flush()
    except Exception as e:
        logging.error(f"Failed to print message: {e}")

def is_running_as_exe():
    """Check if the script is running as a compiled executable."""
    return getattr(sys, 'frozen', False)

def get_python_version():
    """Get current Python version as a tuple."""
    return sys.version_info[:3]

def install_python_windows(target_version=RECOMMENDED_PYTHON_VERSION):
    """Install Python on Windows if needed."""
    try:
        # Check if Python is already installed
        try:
            result = subprocess.run(
                ['python', '--version'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                installed_version = result.stderr or result.stdout
                log(f"Found Python version: {installed_version.strip()}")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Download Python installer
        python_version_str = f"{target_version[0]}.{target_version[1]}"
        arch = 'amd64' if platform.machine().endswith('64') else 'win32'
        url = f"https://www.python.org/ftp/python/{python_version_str}/python-{python_version_str}-{arch}.exe"
        
        log(f"Downloading Python installer from {url}")
        installer_path = os.path.join(tempfile.gettempdir(), f"python_{python_version_str}_installer.exe")
        
        try:
            urllib.request.urlretrieve(url, installer_path)
        except urllib.error.URLError as e:
            log(f"Failed to download Python installer: {e}", level='error')
            return False

        log("Download completed")

        # Install Python silently with pre-selected options
        install_cmd = [
            installer_path,
            '/quiet',
            'InstallAllUsers=1',
            'PrependPath=1',
            'Include_test=0',
            'Include_launcher=0',
            'SimpleInstall=1',
            'AssociateFiles=0',
            'CompileAll=1',
            'Shortcuts=0'
        ]

        log("Installing Python in background...")
        # Use START to run the installer in background without showing window
        subprocess.Popen(
            ['start', '/wait', installer_path] + install_cmd[1:],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        log("Python installation started in background")
        return True

    except Exception as e:
        log(f"Failed to install Python: {e}", level='error')
        return False

def install_required_packages():
    """Install all required Python packages."""
    try:
        log("Checking required packages...")
        
        # Get pip path
        pip_path = None
        possible_pip_paths = [
            os.path.join(os.path.dirname(sys.executable), 'pip'),
            os.path.join(os.path.dirname(sys.executable), 'Scripts', 'pip'),
            'pip'
        ]
        
        for path in possible_pip_paths:
            try:
                subprocess.run([path, '--version'], check=True, capture_output=True)
                pip_path = path
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not pip_path:
            log("Could not find pip executable", level='error')
            return False

        # Install each required package
        for package in REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
                log(f"Package {package} already installed")
            except ImportError:
                log(f"Installing package {package}...")
                try:
                    subprocess.run(
                        [pip_path, 'install', package, '--quiet', '--disable-pip-version-check'],
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    log(f"Successfully installed {package}")
                except subprocess.CalledProcessError as e:
                    log(f"Failed to install {package}: {e}", level='error')
                    continue
        
        return True

    except Exception as e:
        log(f"Error installing packages: {e}", level='error')
        return False

def check_and_install_requirements():
    """Check Python version and install if needed."""
    if not is_running_as_exe():
        return True  # Skip if running as script

    current_version = get_python_version()
    python_ok = current_version >= RECOMMENDED_PYTHON_VERSION
    
    if not python_ok:
        log(f"Current Python version {current_version} is below recommended {RECOMMENDED_PYTHON_VERSION}")
        
        if platform.system() == 'Windows':
            if install_python_windows():
                log("Python installed successfully. Please restart the application.")
                return False
            else:
                log("Continuing with current Python version despite installation issues", level='warning')
                python_ok = True  # Continue even if installation failed
        else:
            log("Automatic Python installation is only supported on Windows", level='warning')
            python_ok = True  # Continue with current Python

    # Install required packages
    if python_ok:
        if not install_required_packages():
            log("Some packages failed to install", level='warning')
    
    return True

# [Previous functions: recv_exact, handle_client, start_server, install_autostart, selftest_send_text]
# ... (keep all your existing functions exactly as they were) ...

if __name__ == "__main__":
    # Check and install requirements if running as executable
    if not check_and_install_requirements():
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "/install":
        install_autostart()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "/selftest":
        selftest_send_text()
        sys.exit(0)

    start_server()