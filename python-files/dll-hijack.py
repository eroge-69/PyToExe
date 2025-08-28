import os
import pefile
import winreg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# List of common trusted directories for system DLLs
trusted_dirs = [
    "C:\\Windows\\System32",
    "C:\\Windows\\SysWOW64",
    "C:\\Program Files",
    "C:\\Program Files (x86)"
]

def check_dll_path(dll_path):
    """
    Check if the DLL path is secure or potentially vulnerable.
    """
    for trusted_dir in trusted_dirs:
        if dll_path.lower().startswith(trusted_dir.lower()):
            return False
    return True

def check_dll(dll_file):
    """
    Check if a DLL is prone to hijacking based on its loading location.
    """
    if not os.path.isfile(dll_file):
        return

    # Check if it's a valid PE file (DLL)
    try:
        pe = pefile.PE(dll_file)
    except Exception as e:
        logging.warning(f"Skipping {dll_file} - not a valid PE file.")
        return

    # Check for non-secure load paths
    if check_dll_path(dll_file):
        logging.warning(f"Potential DLL Hijacking Risk: {dll_file}")

def scan_for_dlls():
    """
    Scan the system for potentially insecure DLLs by checking common application directories.
    """
    # Check program files
    program_dirs = [os.getenv('ProgramFiles'), os.getenv('ProgramFiles(x86)')]
    for dir_path in program_dirs:
        if dir_path and os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith('.dll'):
                        dll_path = os.path.join(root, file)
                        check_dll(dll_path)

    # Check the Windows system directories
    system_dirs = [r"C:\Windows\System32", r"C:\Windows\SysWOW64"]
    for system_dir in system_dirs:
        if os.path.exists(system_dir):
            for root, dirs, files in os.walk(system_dir):
                for file in files:
                    if file.lower().endswith('.dll'):
                        dll_path = os.path.join(root, file)
                        check_dll(dll_path)

    # Check the current working directory (typically risky for loading DLLs)
    cwd = os.getcwd()
    if os.path.exists(cwd):
        for file in os.listdir(cwd):
            if file.lower().endswith('.dll'):
                dll_path = os.path.join(cwd, file)
                check_dll(dll_path)

def check_registry_for_dlls():
    """
    Check registry for DLL loading patterns that could be insecure.
    """
    # Check registry for DLL paths that could be vulnerable to hijacking
    try:
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunServices"
        ]

        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[1]):
                            value_name, value, _ = winreg.EnumValue(key, i)
                            if isinstance(value, str) and '.dll' in value.lower():
                                logging.warning(f"Registry DLL Path Vulnerability: {value_name} -> {value}")
                except FileNotFoundError:
                    continue
    except Exception as e:
        logging.error(f"Error checking registry: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting DLL Hijacking Risk Scan...")
    
    # Scan common directories for DLLs
    scan_for_dlls()
    
    # Scan registry for insecure DLL loading
    check_registry_for_dlls()

    logging.info("Scan completed.")
