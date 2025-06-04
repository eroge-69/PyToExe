import random
import time
import ctypes
from ctypes import wintypes

# Windows API setup
user32 = ctypes.WinDLL('user32')
gdi32 = ctypes.WinDLL('gdi32')

# Constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
IDI_APPLICATION = 32512
IDI_INFORMATION = 32516
IDI_WARNING = 32515
IDI_ERROR = 32513
IDI_QUESTION = 32514

# Configure Windows API functions
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetDesktopWindow.restype = wintypes.HWND
user32.GetWindowDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.DrawIcon.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.HICON]

# Load icons
icons = [
    user32.LoadIconW(None, IDI_APPLICATION),
    user32.LoadIconW(None, IDI_INFORMATION),
    user32.LoadIconW(None, IDI_WARNING),
    user32.LoadIconW(None, IDI_ERROR),
    user32.LoadIconW(None, IDI_QUESTION)
]

def get_screen_size():
    return (
        user32.GetSystemMetrics(SM_CXSCREEN),
        user32.GetSystemMetrics(SM_CYSCREEN)
    )

def draw_chaos():
    width, height = get_screen_size()
    hwnd = user32.GetDesktopWindow()
    
    try:
        while True:
            hdc = user32.GetWindowDC(hwnd)
            
            # Draw 100 random icons each frame
            for _ in range(100):
                x = random.randint(0, width - 32)
                y = random.randint(0, height - 32)
                icon = random.choice(icons)
                user32.DrawIcon(hdc, x, y, icon)
            
            user32.ReleaseDC(hwnd, hdc)
            time.sleep(0.01)  # Small delay to prevent complete freeze
            
    except KeyboardInterrupt:
        print("Chaos stopped")

if __name__ == "__main__":
    print("Desktop Icon Chaos - Press Ctrl+C to stop")
    draw_chaos()
