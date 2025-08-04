# pip install psutil==6.1.1 pyautogui==0.9.54 pygetwindow==0.0.9

import psutil
import pyautogui
import pygetwindow as gw
import time
from datetime import datetime


def find_mspaint_instances():
    instances = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] and 'mspaint.exe' in proc.info['name'].lower():
            instances.append(proc.info['pid'])
    return instances


def bring_window_to_front(title):
    try:
        window = gw.getWindowsWithTitle(title)
        if window:
            window[0].activate()
            return True
    except Exception as e:
        print(f"Error bringing window to front: {e}")
    return False


def generate_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    return f"{timestamp}.png" 


def save_mspaint_file():
    time.sleep(1)  # Allow time for the window to activate
    pyautogui.hotkey("ctrl", "s")  
    time.sleep(2)  # Wait for the Save dialog to open because Windows can be fcking slow: https://superuser.com/q/1734042/116475

    filename = generate_filename()  
    pyautogui.write(filename) 
    time.sleep(1)

    pyautogui.press("enter")  
    time.sleep(2)  

    print(f"Saved as: {filename}")


def main():
    instances = find_mspaint_instances()

    if not instances:
        print("No running instances of MS Paint found.")
        return

    print(f"Found {len(instances)} instance(s) of MS Paint.")

    for window in gw.getWindowsWithTitle("Untitled - Paint") + gw.getWindowsWithTitle("Paint"):
        if bring_window_to_front(window.title):
            print(f"Saving: {window.title}")
            save_mspaint_file()


if __name__ == "__main__":
    main()
