import ctypes
import time

def safe_demo_popups():
    for _ in range(3):
        ctypes.windll.user32.MessageBoxW(0, "This is a simulated popup.", "Educational Demo", 0)
        time.sleep(1)

# Run the safe version
safe_demo_popups()
