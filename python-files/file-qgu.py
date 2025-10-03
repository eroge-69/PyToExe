import ctypes
import math
import time
import random

# Load required GDI functions
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Get desktop device context
hDC = user32.GetDC(0)
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

# Create a compatible DC and bitmap
hMemDC = gdi32.CreateCompatibleDC(hDC)
hBitmap = gdi32.CreateCompatibleBitmap(hDC, width, height)
gdi32.SelectObject(hMemDC, hBitmap)

# Main loop for wave distortion
try:
    t = 0
    while True:
        # Copy screen into memory DC
        gdi32.BitBlt(hMemDC, 0, 0, width, height, hDC, 0, 0, 0x00CC0020)

        # Apply wave effect line by line
        for y in range(0, height, 2):  
            offset = int(20 * math.sin((y / 50.0) + t))
            gdi32.BitBlt(hDC, offset, y, width, 2, hMemDC, 0, y, 0x00CC0020)

        t += 0.2
        time.sleep(0.02)

except KeyboardInterrupt:
    # Release resources when stopped
    user32.ReleaseDC(0, hDC)
    gdi32.DeleteDC(hMemDC)
    gdi32.DeleteObject(hBitmap)