import time
import subprocess
import pyautogui
import os

def is_hotspot_on():
    try:
        result = subprocess.check_output("powershell Get-NetConnectionSharing", shell=True)
        return "SharingEnabled : True" in result.decode()
    except:
        return False

def toggle_mobile_hotspot():
    # Open the settings page
    subprocess.Popen(["start", "ms-settings:network-mobilehotspot"], shell=True)
    time.sleep(4)  # Wait for UI to open
    pyautogui.press('tab', presses=2)
    pyautogui.press('enter')
    time.sleep(2)

# Main loop
while True:
    if not is_hotspot_on():
        print("Hotspot OFF. Trying to restart.")
        toggle_mobile_hotspot()
    time.sleep(30)
