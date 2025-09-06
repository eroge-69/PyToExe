Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import subprocess
... import pyautogui
... import os
... import time
... import win32com.client
... 
... def take_screenshot():
...     # Create folder next to the launcher for screenshots
...     output_folder = os.path.join(os.path.dirname(__file__), "screenshots")
...     os.makedirs(output_folder, exist_ok=True)
... 
...     # Minimize all windows (show desktop)
...     shell = win32com.client.Dispatch("WScript.Shell")
...     shell.SendKeys('^%{d}')
...     time.sleep(1)
... 
...     # Take screenshot
...     screenshot_path = os.path.join(output_folder, "desktop_only.png")
...     pyautogui.screenshot(screenshot_path)
... 
...     print(f"Screenshot saved at: {screenshot_path}")
... 
... def launch_game():
...     # Change this to the exact filename of your game exe
...     game_path = os.path.join(os.path.dirname(__file__), "DTTR - Test.exe")
...     subprocess.Popen([game_path])  # Run without waiting
...     # If you want the launcher to pause until the game exits, use:
...     # subprocess.run([game_path])
... 
... if __name__ == "__main__":
...     take_screenshot()
...     launch_game()
