import pyautogui
import time
import os
import pygetwindow as gw
from datetime import datetime

TAB_COUNT = 5  # ����� �ȝ�� �� ����� ����� ��

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
base_dir = os.path.join(desktop, "Chrome_Tab_Screenshots")
os.makedirs(base_dir, exist_ok=True)

def capture_tabs():
    windows = gw.getWindowsWithTitle('Chrome')
    if not windows:
        print("? Chrome is not open.")
        return

    chrome = next((w for w in windows if "Google Chrome" in w.title), None)
    if chrome is None:
        print("? No Chrome window found.")
        return

    chrome.activate()
    time.sleep(1)

    # ���� ���� �� ���� ����
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = os.path.join(base_dir, timestamp)
    os.makedirs(folder, exist_ok=True)

    for i in range(TAB_COUNT):
        screenshot = pyautogui.screenshot()
        screenshot.save(os.path.join(folder, f"tab_{i+1}.png"))
        print(f"? {timestamp} - Tab {i+1} saved.")
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(1)

# ����� �� 1 ����
while True:
    print("?? Running screenshot cycle...")
    capture_tabs()
    print("?? Waiting 1 hour...")
    time.sleep(3600)
