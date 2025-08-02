import os
import time
import winsound
from threading import Thread
from win10toast import ToastNotifier
from pathlib import Path

LOG_PATH = Path.home() / "AppData/Roaming/Microsoft/Teams/logs.txt"
SOUND_PATH = os.path.join(os.path.dirname(__file__), "teams_benachrichtigung.wav")
notifier = ToastNotifier()

def play_sound():
    winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME)

def monitor_logs():
    if not LOG_PATH.exists():
        notifier.show_toast("Teams-Sound", "Teams-Logdatei nicht gefunden", duration=5)
        return

    last_size = LOG_PATH.stat().st_size
    while True:
        time.sleep(2)
        try:
            current_size = LOG_PATH.stat().st_size
            if current_size > last_size:
                play_sound()
                last_size = current_size
        except:
            pass

if __name__ == "__main__":
    Thread(target=monitor_logs, daemon=True).start()
    while True:
        time.sleep(60)
