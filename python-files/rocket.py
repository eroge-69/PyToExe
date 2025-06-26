import speech_recognition as sr
import pyttsx3
import os
import datetime
import webbrowser
import requests
import subprocess
import threading

# === CONFIG ===
API_KEY = "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"
MODEL = "deepseek/deepseek-chat-v3-0324"

# === SPEECH ENGINE ===
engine = pyttsx3.init()
engine.setProperty('rate', 160)
voices = engine.getProperty('voices')
for v in voices:
    if "Zira" in v.name or "David" in v.name:
        engine.setProperty('voice', v.id)
        break

speaking_thread = None
stop_speaking = threading.Event()

def speak(text):
    global speaking_thread
    stop_speaking.clear()

    def _speak():
        engine.say(text)
        engine.runAndWait()

    def _run():
        try:
            _speak()
        except RuntimeError:
            pass

    if speaking_thread and speaking_thread.is_alive():
        stop_speaking.set()
        engine.stop()

    speaking_thread = threading.Thread(target=_run)
    speaking_thread.start()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\U0001F3A7 Rocket is listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            query = recognizer.recognize_google(audio, language='en-IN')
            print("You said:", query)
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry boss, I didn't get that.")
            return listen()
        except sr.RequestError:
            speak("Mic error boss.")
            return ""

def ai_response(message, detailed=False):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"You are Rocket, a smart assistant. The user may speak in English or Hinglish. "
        f"Always reply in fluent English. Be brief unless the user asks for full detail. "
        f"Question: {message}"
    )

    if detailed:
        prompt = (
            f"You are Rocket, a smart assistant. The user may speak in English or Hinglish. "
            f"Reply in fluent English with a full explanation. "
            f"Question: {message}"
        )

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "Rocket AI is offline, please check your internet."

def scan_installed_apps():
    speak("Scanning all installed apps boss. Please wait.")
    search_dirs = [
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        os.path.expanduser("~\\AppData\\Local"),
        os.path.expanduser("~\\AppData\\Roaming"),
        os.path.expanduser("~\\Desktop"),
        "C:\\Users\\Public\\Desktop"
    ]

    app_map = {}
    for folder in search_dirs:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".exe"):
                    name = file.lower().replace(".exe", "").strip()
                    full_path = os.path.join(root, file)
                    if name not in app_map:
                        app_map[name] = full_path

    speak(f"Found {len(app_map)} apps. Tell me what to do boss.")
    return app_map

def open_app_smart(spoken_text):
    for name in installed_apps:
        if name in spoken_text:
            try:
                speak(f"Opening {name}")
                os.startfile(installed_apps[name])
                return True
            except:
                speak(f"Tried to open {name} but failed.")
                return False
    return False

def stop_on_interrupt(recognizer, audio):
    global speaking_thread
    if speaking_thread and speaking_thread.is_alive():
        print("\U0001F6D1 Interrupted by user.")
        stop_speaking.set()
        engine.stop()

def process_command(cmd):
    local_handled = False

    if "time" in cmd:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
        local_handled = True
    elif "date" in cmd:
        today = datetime.date.today().strftime("%d %B %Y")
        speak(f"Today's date is {today}")
        local_handled = True
    elif "shutdown" in cmd or "band karo" in cmd:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 5")
        local_handled = True
    elif "youtube" in cmd:
        speak("Opening YouTube.")
        webbrowser.open("https://youtube.com")
        local_handled = True
    elif "search" in cmd:
        term = cmd.replace("search", "").strip()
        speak(f"Searching {term}")
        webbrowser.open(f"https://www.google.com/search?q={term}")
        local_handled = True
    elif "exit" in cmd:
        speak("Rocket shutting down. Goodbye boss.")
        exit()
        local_handled = True
    elif "open" in cmd or "kholo" in cmd:
        if open_app_smart(cmd):
            return
        else:
            speak("Sorry boss, I couldn’t find that app.")
            return

    if not local_handled:
        detailed = "detail" in cmd or "explain" in cmd
        response = ai_response(cmd, detailed=detailed)
        speak(response)

def start_rocket():
    global installed_apps
    installed_apps = scan_installed_apps()

    speak("Say 'Rocket' to wake me boss.")

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    recognizer.listen_in_background(mic, stop_on_interrupt)

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("\U0001F3A7 Waiting for 'Rocket'...")

            try:
                audio = recognizer.listen(source, timeout=5)
                wake_cmd = recognizer.recognize_google(audio, language='en-IN').lower()
                if "rocket" in wake_cmd:
                    speak("Yes boss?")
                    command = listen()
                    if command:
                        process_command(command)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                speak("Mic error boss.")

if __name__ == "__main__":
    start_rocket()
