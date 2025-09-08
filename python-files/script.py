from flask import Flask
import os
import webbrowser
import subprocess
import random
import time
import winsound
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>😈 Remote Prank Server</h1>
    <p>Waiting for remote commands...</p>
    """

@app.route('/chrome')
def open_chrome():
    webbrowser.open("https://www.google.com")
    return "Opened Chrome!"

@app.route('/spotify')
def open_spotify():
    subprocess.Popen(["spotify"])
    return "Opened Spotify!"

@app.route('/store')
def open_store():
    os.system("start ms-windows-store:")
    return "Opened Microsoft Store!"

@app.route('/explorer')
def open_explorer():
    os.system("explorer")
    return "Opened File Explorer!"

@app.route('/youtube')
def open_youtube():
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return "Opened YouTube!"

@app.route('/notepad')
def open_notepad():
    os.system("notepad")
    return "Opened Notepad!"

@app.route('/calc')
def open_calc():
    os.system("calc")
    return "Opened Calculator!"

@app.route('/paint')
def open_paint():
    os.system("mspaint")
    return "Opened Paint!"

@app.route('/sounds')
def play_random_sound():
    sound_files = [
        "C:\\Windows\\Media\\Windows Background.wav",
        "C:\\Windows\\Media\\Windows Error.wav",
        "C:\\Windows\\Media\\Windows Exclamation.wav",
        "C:\\Windows\\Media\\Windows Notify.wav",
        "C:\\Windows\\Media\\Windows Print complete.wav"
    ]
    sound = random.choice(sound_files)
    try:
        winsound.PlaySound(sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
        return f"Playing: {os.path.basename(sound)}"
    except Exception as e:
        return f"Error playing sound: {e}"

@app.route('/triple')
def open_three_explorers():
    for _ in range(3):
        os.system("explorer")
        time.sleep(0.3)
    return "Opened 3 File Explorer windows!"

@app.route('/hack')
def fake_hack():
    hack_cmd = (
        'start cmd /k "color 0a && title HACKING IN PROGRESS && '
        'echo Connecting to mainframe... && '
        'ping localhost -n 3 >nul && '
        'echo Downloading secrets... && '
        'ping localhost -n 3 >nul && '
        'echo Uploading virus... && '
        'ping localhost -n 3 >nul && '
        'echo HACK COMPLETE! && pause"'
    )
    os.system(hack_cmd)
    return "Opened Fake Hacking CMD!"

def get_local_ip():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if not ip.startswith("127."):
            return ip
    except:
        pass
    try:
        stream = os.popen("ipconfig")
        output = stream.read()
        for line in output.splitlines():
            if "IPv4 Address" in line:
                return line.split(":")[-1].strip()
    except:
        pass
    return "IP not found"

if __name__ == '__main__':
    ip = get_local_ip()
    print(f"Prank server running! Connect from another device at: http://{ip}:5000")
    app.run(host='0.0.0.0', port=5000)
