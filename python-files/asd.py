import os
if os.name != "nt":
    exit()
import subprocess
import sys
import time
import tempfile
from colorama import init, Fore, Style
init()
import random
import string
import winreg
import ctypes
import psutil
import shutil
import glob
import threading

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def typewriter_animation(text, delay=0.05):
    current_text = ""
    for char in text:
        current_text += char
        set_console_title(current_text)
        time.sleep(delay)

def erase_animation(text, delay=0.03):
    for i in range(len(text), -1, -1):
        current_text = text[:i]
        set_console_title(current_text)
        time.sleep(delay)

def animated_title():
    title_text = "Created & Developed By 1662realalex & XyZ"
    
    while True:
        typewriter_animation(title_text, 0.05)
        time.sleep(1)
        erase_animation(title_text, 0.03)
        time.sleep(0.5)

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return False
        except:
            return False

def animate_checking():
    for i in range(6):
        dots = "." * (i % 4)
        print(Fore.WHITE + f"\r[~] Checking License{dots}", end="")
        time.sleep(0.5)
    print()

def license_check():
    os.system("cls")
    print(Fore.WHITE + "\n")
    print("[~] Please enter your license key:")
    license_key = input("> ")
    
    animate_checking()
    
    if license_key == "alexbroo":
        print(Fore.GREEN + "[+] License verified successfully!")
        time.sleep(1.5)
        return True
    else:
        print(Fore.RED + "[-] Invalid license! Closing...")
        time.sleep(2)
        return False

def get_dll_name():
    print(Fore.WHITE + "\n")
    print("[~] Enter DLL file name (e.g., example.dll):")
    dll_name = input("> ")
    return dll_name

def find_dll(dll_name):
    current_dir = os.getcwd()
    dll_pattern = os.path.join(current_dir, dll_name)
    
    if os.path.exists(dll_pattern):
        return dll_pattern
    
    for root, dirs, files in os.walk(current_dir):
        if dll_name in files:
            return os.path.join(root, dll_name)
    
    return None

def get_mta_path():
    try:
        registry_paths = [
            r"SOFTWARE\WOW6432Node\Multi Theft Auto: San Andreas All\1.6",
            r"SOFTWARE\Multi Theft Auto: San Andreas All\1.6"
        ]
        
        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                value, _ = winreg.QueryValueEx(key, "Last Run Path")
                winreg.CloseKey(key)
                if os.path.exists(value):
                    return value
            except:
                continue
        
        common_paths = [
            r"C:\Program Files (x86)\MTA San Andreas 1.6\MTA.exe",
            r"C:\Program Files\MTA San Andreas 1.6\MTA.exe",
            os.path.expanduser(r"~\Desktop\MTA San Andreas 1.6\MTA.exe")
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
                
        return None
    except Exception as e:
        print(f"Error getting MTA path: {e}")
        return None

def get_original_autodialdll():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Services\WinSock2\Parameters")
        value, _ = winreg.QueryValueEx(key, "AutodialDLL")
        winreg.CloseKey(key)
        return value
    except:
        return None

def restore_autodialdll(original_value):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Services\WinSock2\Parameters", 0, winreg.KEY_SET_VALUE)
        
        if original_value:
            winreg.SetValueEx(key, "AutodialDLL", 0, winreg.REG_SZ, original_value)
        else:
            try:
                winreg.DeleteValue(key, "AutodialDLL")
            except:
                pass
            
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error restoring autodial: {e}")
        return False

def cleanup_temp_files():
    try:
        temp_dll = r"C:\Windows\rasadhlp.dll"
        if os.path.exists(temp_dll):
            os.remove(temp_dll)
    except Exception as e:
        print(f"Error cleaning temp files: {e}")

def set_autodialdll(dll_path):
    try:
        alternative_path = r"C:\Windows\rasadhlp.dll"
        
        if os.path.exists(dll_path):
            shutil.copy2(dll_path, alternative_path)
            
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Services\WinSock2\Parameters", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AutodialDLL", 0, winreg.REG_SZ, alternative_path)
            winreg.CloseKey(key)
            return True
    except Exception as e:
        print(f"Error setting autodial: {e}")
        return False

def wait_and_set_autodialdll(target_process="gta_sa.exe", dll_path=r"C:\Windows\rasadhlp.dll"):
    max_wait_time = 30  
    start_time = time.time()
    
    while True:
        if time.time() - start_time > max_wait_time:
            return False
            

        running = any(p.name().lower() == target_process.lower() for p in psutil.process_iter())
        if running:
            break
        time.sleep(0.5)

    time.sleep(2)

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Services\WinSock2\Parameters", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "AutodialDLL", 0, winreg.REG_SZ, dll_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error in wait_and_set: {e}")
        return False

def monitor_mta_and_cleanup(original_value):
    print("[+] Monitoring MTA process...")
    try:
        while True:
            mta_running = any(p.name().lower() == "gta_sa.exe" for p in psutil.process_iter())
            
            if not mta_running:
                print("[+] MTA closed, cleaning up...")
                restore_autodialdll(original_value)
                cleanup_temp_files()
                break
                
            time.sleep(2)
    except KeyboardInterrupt:
        print("[+] Manual interrupt, cleaning up...")
        restore_autodialdll(original_value)
        cleanup_temp_files()

def print_with_delay(message, delay=1.0):
    print(Fore.WHITE + message)
    time.sleep(delay)

if __name__ == "__main__":
    title_thread = threading.Thread(target=animated_title, daemon=True)
    title_thread.start()
    
    if not run_as_admin():
        print(Fore.RED + "[-] Administrator privileges required!")
        print(Fore.WHITE + "[+] Please run as administrator")
        time.sleep(5)
        sys.exit(0)
    
    if not license_check():
        sys.exit(0)
    
    dll_name = get_dll_name()
    
    original_autodial = get_original_autodialdll()
    
    local_dll_path = find_dll(dll_name)
    
    if not local_dll_path:
        print_with_delay(f"[-] {dll_name} not found!", 3)
        sys.exit(0)
    
    print_with_delay(f"[+] {dll_name} was successfully found.", 1.5)
    
    mta_path = get_mta_path()
    if not mta_path:
        print_with_delay("[-] MTA path not found!", 3)
        sys.exit(0)
    
    print_with_delay(f"[+] MTA found at: {mta_path}", 1.5)
    
    if set_autodialdll(local_dll_path):
        print_with_delay("[+] Opening MTA:SA...", 1.5)
        try:
            subprocess.Popen([mta_path])
            print_with_delay("[+] Waiting for game to start...", 1.5)
            
            if wait_and_set_autodialdll():
                print_with_delay("[+] Injection completed successfully!", 1.5)
                
                monitor_mta_and_cleanup(original_autodial)
                print_with_delay("[+] Cleanup completed successfully!", 1.5)
            else:
                print_with_delay("[-] Failed to set autodial during game runtime!", 1.5)
                restore_autodialdll(original_autodial)
                cleanup_temp_files()
                
            print_with_delay("[+] You can close this window now.", 5)
            
        except Exception as e:
            print(f"[-] Failed To Start MTA: {e}")
            restore_autodialdll(original_autodial)
            cleanup_temp_files()
            time.sleep(3)
            sys.exit(0)
    else:
        print_with_delay("[-] Injection failed!", 3)
        sys.exit(0)