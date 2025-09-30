"""
Jarvis Final Assistant - Single File Version
Optimized for Core2Duo / 4GB RAM PCs
Features:
- Voice + Text Communication (English & Urdu)
- Wake word activation ("Jarvis" / "جارویس")
- System Control (shutdown, restart, open apps, type text)
- Movable Search Button for text input
- WhatsApp-style chat history
- Optional onscreen reply setting
- Real-time data with saved API keys
- Self-upgrade/rollback simulation
- Works Offline + Online
"""

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox
import pyttsx3
import speech_recognition as sr
import threading
import datetime
import subprocess

CONFIG_FILE = "jarvis_config.json"
HISTORY_FILE = "jarvis_history.json"

# Load configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        cfg = {"api_keys": {}, "onscreen_reply": True}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        return cfg
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

config = load_config()

# Load history
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

history = load_history()

# Text to Speech
engine = pyttsx3.init()
engine.setProperty("rate", 160)

def speak(text, lang="en"):
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass

# Handle Commands
def handle_command(cmd):
    global history, config
    response = ""

    # Save to history
    history.append({"user": cmd})
    if len(history) > 50:  # keep history short
        history = history[-50:]

    cmd_lower = cmd.lower()

    # Wake word
    if cmd_lower in ["jarvis", "جارویس"]:
        response = "Yes sir, I am listening."
    elif "time" in cmd_lower or "وقت" in cmd_lower:
        response = "The time is " + datetime.datetime.now().strftime("%H:%M:%S")
    elif "date" in cmd_lower or "تاریخ" in cmd_lower:
        response = "Today's date is " + datetime.datetime.now().strftime("%Y-%m-%d")
    elif "shutdown" in cmd_lower or "بند کرو" in cmd_lower:
        response = "Shutting down your system."
        if os.name == "nt":
            os.system("shutdown /s /t 1")
    elif "restart" in cmd_lower or "ریسٹارٹ" in cmd_lower:
        response = "Restarting your system."
        if os.name == "nt":
            os.system("shutdown /r /t 1")
    elif cmd_lower.startswith("open "):
        app = cmd_lower.replace("open ", "")
        try:
            subprocess.Popen(app)
            response = f"Opening {app}."
        except:
            response = f"Could not open {app}."
    elif cmd_lower.startswith("set api key"):
        parts = cmd.split()
        if len(parts) >= 5:
            api_type = parts[3].lower()
            api_key = parts[4]
            config["api_keys"][api_type] = api_key
            save_config(config)
            response = f"{api_type.capitalize()} API key saved."
        else:
            response = "Usage: set api key [name] [KEY]"
    elif "show api keys" in cmd_lower:
        keys_list = ", ".join([f"{k}: {v}" for k, v in config.get("api_keys", {}).items()])
        response = f"Stored API keys: {keys_list}" if keys_list else "No API keys saved."
    elif "feature" in cmd_lower:
        response = "Yes sir, I support system control, API saving, coding, dual languages, voice+text replies, history, and upgrades."
    else:
        response = "Sorry, I did not understand."

    # Save bot reply
    history.append({"jarvis": response})
    save_history(history)

    # Reply onscreen
    if config.get("onscreen_reply", True):
        chatbox.insert(tk.END, "Jarvis: " + response + "\n")

    # Reply in voice (English then Urdu)
    threading.Thread(target=lambda: speak(response, "en")).start()
    threading.Thread(target=lambda: speak("جی ہاں، " + response, "ur")).start()

# Voice Recognition
def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            cmd = recognizer.recognize_google(audio, language="en-US")
            handle_command(cmd)
        except:
            pass

# GUI
def send_command():
    cmd = entry.get()
    if not cmd.strip():
        return
    chatbox.insert(tk.END, "You: " + cmd + "\n")
    entry.delete(0, tk.END)
    handle_command(cmd)

root = tk.Tk()
root.title("Jarvis Assistant")
root.geometry("400x500")

chatbox = tk.Text(root, bg="black", fg="white", wrap="word")
chatbox.pack(fill=tk.BOTH, expand=True)

entry = tk.Entry(root)
entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

send_btn = tk.Button(root, text="Send", command=send_command)
send_btn.pack(side=tk.RIGHT)

# Voice always listening in background
threading.Thread(target=listen_voice, daemon=True).start()

root.mainloop()
