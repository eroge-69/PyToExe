import os
import datetime
import webbrowser
import subprocess
import json
import http.client
import pyttsx3

# ====== CONFIGURATION ======
OPENROUTER_API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"
# ===========================

SPEAK_MODE = False
CALL_NAME = ""
VOICE_ID = None   # Will hold male/female voice


def speak(text):
    """Speak with pyttsx3 using the chosen gender voice."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 1.0)

        if VOICE_ID is not None:
            engine.setProperty('voice', VOICE_ID)

        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("[ERROR] TTS failed:", e)


def print_response(text):
    """Print and optionally speak."""
    global SPEAK_MODE, CALL_NAME
    print(f"{CALL_NAME}: {text}")
    if SPEAK_MODE:
        speak(text)


def ask_openrouter(prompt):
    """Call OpenRouter API for a response."""
    conn = http.client.HTTPSConnection("openrouter.ai")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    })

    try:
        conn.request("POST", "/api/v1/chat/completions", body, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        response_json = json.loads(data)
        return response_json["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API Error: {str(e)}"


def ask_gender():
    """Ask user for male/female and set correct voice."""
    global VOICE_ID
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    gender = input("🤖 Should my voice be male or female? ").strip().lower()

    if gender == "female":
        for v in voices:
            if "female" in v.name.lower() or "zira" in v.name.lower():
                VOICE_ID = v.id
                break
    elif gender == "male":
        for v in voices:
            if "male" in v.name.lower() or "david" in v.name.lower():
                VOICE_ID = v.id
                break

    if VOICE_ID is None and voices:
        VOICE_ID = voices[0].id  # fallback

    print(f"{CALL_NAME}: Okay, I will speak in a {gender} voice!")


def find_app(app_name, search_paths):
    """Search common directories for the app executable."""
    for root_dir in search_paths:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().startswith(app_name.lower()) and file.endswith(".exe"):
                    return os.path.join(root, file)
    return None


def execute_command(command):
    global SPEAK_MODE, CALL_NAME
    cmd = command.strip().lower()
    name = CALL_NAME.lower()

    # === Speak ON ===
    if cmd in [f"{name} speak", f"{name} speak up", f"{name} speak from now",
               f"speak {name}", f"speak up {name}"]:
        SPEAK_MODE = True
        print_response("Okay, I will speak from now on.")
        return

    # === Speak OFF ===
    if cmd in [f"{name} don't speak", f"{name} shut up",
               f"shut up {name}", f"don't speak {name}"]:
        SPEAK_MODE = False
        print_response("Okay, I will stay quiet and only print.")
        return

    # === Change Name ===
    if cmd == "i want to change your name":
        print(f"{CALL_NAME}: What name do you want to give me?")
        new_name = input("You: ").strip().lower()
        CALL_NAME = new_name
        print(f"{CALL_NAME}: oo I like the new name {CALL_NAME}!")
        ask_gender()   # <-- now ask gender again after renaming
        return

    # === Built-in Commands ===
    if "time" in cmd:
        time = datetime.datetime.now().strftime("%H:%M:%S")
        print_response(f"The time is {time}")

    elif "open youtube" in cmd:
        print_response("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")

    elif "open instagram" in cmd:
        print_response("Opening Instagram.")
        webbrowser.open("https://www.instagram.com")

    elif "open google" in cmd:
        print_response("Opening Google.")
        webbrowser.open("https://www.google.com")

    elif "shutdown" in cmd:
        print_response("Shutting down the system.")
        os.system("shutdown /s /t 1")

    elif "restart" in cmd:
        print_response("Restarting the system.")
        os.system("shutdown /r /t 1")

    elif "launch" in cmd:
        app = cmd.replace("launch", "").strip()
        search_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expanduser(r"~\AppData\Local")
        ]
        path = find_app(app, search_dirs)
        if path:
            subprocess.Popen(path)
            print_response(f"Launching {app}")
        else:
            print_response(f"Could not find {app}. Try exact app name or give full path.")

    else:
        # === Ask AI for everything else ===
        response = ask_openrouter(cmd)
        print_response(response)


def set_name_and_gender():
    global CALL_NAME
    CALL_NAME = input("🤖 What do you want to call me? ").strip().lower()
    print(f"{CALL_NAME}: oo I like the name {CALL_NAME}!")
    ask_gender()   # <-- always ask gender here


def main():
    set_name_and_gender()
    print(f"\n🧠 {CALL_NAME} is running. Type your command. Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() in ["exit", "quit", "bye", "stop"]:
            print_response("Goodbye!")
            break
        execute_command(query)


if __name__ == "__main__":
    main()
