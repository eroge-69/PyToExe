import webbrowser
import time
import threading
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Set volume to 100%
def max_volume_loop():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    while True:
        volume.SetMasterVolumeLevelScalar(1.0, None)
        time.sleep(1)

# Reopen Rickroll if closed
def rickroll_loop():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    while True:
        webbrowser.open(url)
        time.sleep(5)

# Move mouse to mess with user
def distract_mouse():
    while True:
        pyautogui.moveTo(0, 0)
        time.sleep(1)

# Run all pranks simultaneously
if __name__ == "__main__":
    threading.Thread(target=max_volume_loop).start()
    threading.Thread(target=rickroll_loop).start()
    threading.Thread(target=distract_mouse).start()

    while True:
        time.sleep(1)
