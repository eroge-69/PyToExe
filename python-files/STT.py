from gtts import gTTS
from playsound import playsound
import tempfile
import os
import speech_recognition as sr
from fuzzywuzzy import process
import time
import subprocess
import queue
import sounddevice as sd
import vosk
import json
import psutil  # for closing apps
import sys

# Get folder of the running script or exe
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller temporary folder
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

vosk_model_path = os.path.join(base_path, "vosk-model-small-en-us-0.15")
vosk_model = vosk.Model(vosk_model_path)


#System Tray
import pystray
from PIL import Image, ImageDraw
import threading

# Create a simple icon
def create_image():
    # 16x16 icon with a circle
    image = Image.new('RGB', (64, 64), "black")
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill="white")
    return image

# Quit function
def on_quit(icon, item):
    icon.stop()
    os._exit(0)  # force quit the program

# Run tray in another thread
def run_tray():
    icon = pystray.Icon("bob", create_image(), menu=pystray.Menu(
        pystray.MenuItem("Exit", on_quit)
    ))
    icon.run()

# Start tray in a background thread
threading.Thread(target=run_tray, daemon=True).start()


# ---------- TTS ----------
def speak(text):
    print(f"Bob: {text}")
    try:
        tts = gTTS(text)
        temp_file = os.path.join(tempfile.gettempdir(), "temp_bob.mp3")
        tts.save(temp_file)
        playsound(temp_file)
        os.remove(temp_file)
    except Exception as e:
        print(f"[TTS Error] {e}")

# ---------- Get Start Menu Apps ----------
def get_start_menu_apps():
    apps = {}
    start_menu_paths = [
        os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.environ['PROGRAMDATA'], r"Microsoft\Windows\Start Menu\Programs")
    ]
    for folder in start_menu_paths:
        for root_dir, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(".lnk"):
                    name = os.path.splitext(file)[0].lower()
                    path = os.path.join(root_dir, file)
                    apps[name] = path
    return apps

# ---------- Parse Intent ----------
def parse_intent(text):
    text = text.lower()
    # Open
    for keyword in ["open", "launch", "start"]:
        if keyword in text:
            target = text.split(keyword, 1)[1].strip()
            return "open_app", target
    # Close
    for keyword in ["close", "kill", "exit", "terminate"]:
        if keyword in text:
            target = text.split(keyword, 1)[1].strip()
            return "close_app", target
    return None, None

# ---------- Try launching MS Store apps ----------
def launch_store_app(app_name):
    uri_map = {
    # Communication & Social
    "whatsapp": "whatsapp://",
    "microsoft teams": "msteams://",
    "discord": "discord://",
    "telegram": "tg://",
    "skype": "skype:",
    "zoom": "zoommtg://",
    
    # Media & Entertainment
    "spotify": "spotify:",
    "netflix": "ms-windows-store://pdp/?productid=9wzdncrfj3tj",
    "disney plus": "ms-windows-store://pdp/?productid=9nxqxxlfst89",
    "amazon prime video": "ms-windows-store://pdp/?productid=9p6rc76msmmj",
    "vlc": "vlc://",
    "apple music": "ms-windows-store://pdp/?productid=9pfhdd62mxs1",
    
    # Productivity
    "microsoft office": "ms-word://", # or ms-excel://, ms-powerpoint://
    "notion": "notion://",
    "evernote": "evernote://",
    "onenote": "onenote:",
    "adobe creative cloud": "ms-windows-store://pdp/?productid=9nblggh4r5r6",
    
    # Mail & Calendar
    "mail": "mailto:",
    "calendar": "ms-calendar://",
    "outlook": "ms-outlook://",
    
    # Gaming
    "xbox": "ms-xbl-3d8b930f://",
    "steam": "steam://",
    "epic games": "com.epicgames.launcher://",
    
    # Utilities
    "calculator": "calculator://",
    "settings": "ms-settings:",
    "microsoft store": "ms-windows-store:",
    "camera": "microsoft.windows.camera:",
    "photos": "ms-photos:",
    "maps": "bingmaps:",
    "weather": "msnweather:",
    
    # Development
    "visual studio code": "vscode://",
    "github desktop": "x-github-client://",
    "windows terminal": "ms-terminal:",
    
    # Social & News
    "twitter": "twitter://",
    "facebook": "fb://",
    "instagram": "instagram://",
    "reddit": "ms-windows-store://pdp/?productid=9nblggh892k5",
    
    # File Management
    "dropbox": "dbx://",
    "onedrive": "ms-onedrive://",
    "google drive": "googledrive://",
    
    # Reading & Reference
    "kindle": "kindle://",
    "adobe acrobat": "ms-windows-store://pdp/?productid=9nblggh4tcx4"
}
    for key, uri in uri_map.items():
        if key in app_name.lower():
            try:
                subprocess.Popen(["start", uri], shell=True)
                return True
            except Exception as e:
                print(f"[URI Launch Error] {e}")
                return False
    return False

# ---------- Close App (Dynamic with confirmation) ----------
def close_app(target):
    # Ask for confirmation first
    speak(f"Are you sure you want to close '{target}'?")
    with mic as source:
        audio = recognizer.listen(source)
    try:
        answer = recognizer.recognize_google(audio).lower()
        if "yes" not in answer:
            speak("Okay, not closing anything.")
            return False
    except:
        speak("Sorry, I didn't catch that. Not closing anything.")
        return False

    killed = False

    # 1️⃣ Try fuzzy match with installed Start Menu apps
    candidates = list(installed_apps.keys())
    best_match, score = process.extractOne(target.lower(), candidates)

    if score > 60:
        exe_name = os.path.splitext(os.path.basename(installed_apps[best_match]))[0].lower()
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and exe_name in proc.info['name'].lower():
                try:
                    proc.kill()
                    killed = True
                except Exception as e:
                    print(f"[Error killing {proc.info['name']}]: {e}")

    # 2️⃣ Fallback: try killing any process containing the target string
    if not killed:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and target.lower() in proc.info['name'].lower():
                try:
                    proc.kill()
                    killed = True
                except Exception as e:
                    print(f"[Error killing {proc.info['name']}]: {e}")

    if killed:
        speak(f"Closed {target}.")
        return True
    else:
        speak(f"Could not find a running app named '{target}'.")
        return False

# ---------- Initialize ----------
recognizer = sr.Recognizer()
mic = sr.Microphone()
with mic as source:
    recognizer.adjust_for_ambient_noise(source)
installed_apps = get_start_menu_apps()
print(f"Loaded {len(installed_apps)} apps.")
speak("Hey, I'm ready. Say 'Hey Bob' to wake me up.")

# ---------- Vosk Setup ----------
vosk_model = vosk.Model("C:\\Users\\Dell\\Desktop\\Work Programs\\vosk-model-small-en-us-0.15")
q = queue.Queue()
def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

stream = sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback)
rec = vosk.KaldiRecognizer(vosk_model, 16000)

# ---------- Main Loop ----------
with stream:
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower()
            if text and "hey bob" in text:
                speak("Yes?")
                # Listen for command using Google STT
                with mic as source:
                    audio = recognizer.listen(source)
                try:
                    command = recognizer.recognize_google(audio)
                    print(f"Command: {command}")

                    # Exit
                    if any(word in command.lower() for word in ["exit", "stop", "end", "bye"]):
                        speak("Goodbye, have a great day!")
                        break

                    intent, target = parse_intent(command)
                    print("Intent:", intent, "| Target:", target)

                    if intent == "open_app" and target:
                        candidates = list(installed_apps.keys())
                        best_match, score = process.extractOne(target.lower(), candidates)

                        if score > 60:
                            app_path = installed_apps[best_match]
                            speak(f"Launching {best_match}...")
                            os.startfile(app_path)
                        else:
                            if launch_store_app(target):
                                speak(f"Launching {target}...")
                            else:
                                speak(f"App '{target}' not found (closest match: {best_match}).")

                    elif intent == "close_app" and target:
                        close_app(target)

                except sr.UnknownValueError:
                    speak("Sorry, I didn't catch that.")
                except sr.RequestError:
                    speak("Sorry, my speech service is down.")
