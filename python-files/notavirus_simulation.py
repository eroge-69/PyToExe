
import os
import time
import ctypes
import webbrowser
import threading

# Optional: fake persistence via startup shortcut (Windows only)
def create_fake_persistence():
    path = os.getenv("APPDATA") + r"\Microsoft\Windows\Start Menu\Programs\Startup\notavirus.bat"
    with open(path, "w") as file:
        file.write(f'start "" "{os.path.abspath(__file__)}"')

# Popup message box (Windows only)
def popup_loop():
    while True:
        ctypes.windll.user32.MessageBoxW(0, "You've been mildly annoyed 🐛", "NotAVirus", 0x40)
        time.sleep(3)

# Open a funny website in browser
def open_web_loop():
    while True:
        webbrowser.open("https://www.pointerpointer.com/")
        time.sleep(10)

# CPU stress simulation
def cpu_waster():
    while True:
        _ = [x**2 for x in range(10000)]

if __name__ == "__main__":
    print("Simulated harmless 'virus' running...")

    # Uncomment this to simulate startup persistence
    # create_fake_persistence()

    # Start non-destructive threads
    threading.Thread(target=popup_loop, daemon=True).start()
    threading.Thread(target=open_web_loop, daemon=True).start()
    threading.Thread(target=cpu_waster, daemon=True).start()

    # Keep script alive
    while True:
        time.sleep(1)
