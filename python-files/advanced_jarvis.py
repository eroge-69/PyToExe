# advanced_jarvis.py
# Complete voice-enabled Jarvis with LLM chat, memory, and system control.
# WARNING: API key is embedded for one-click use. Keep this file private.

import os
import sys
import time
import json
import threading
import subprocess
import webbrowser
import datetime
import requests
import platform
import logging

import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import pyjokes
import pyautogui
import keyboard

# ---------------------------
# CONFIG
# ---------------------------
API_KEY = "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"
OPENAI_COMPATIBLE = True
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
LLM_MODEL = "gpt-4o-mini"
WAKE_WORD = "jarvis"
LISTEN_HOTKEY = "f8"
LISTEN = True

DATA_DIR = os.path.join(os.path.expanduser("~"), ".advanced_jarvis")
os.makedirs(DATA_DIR, exist_ok=True)
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
LOG_FILE = os.path.join(DATA_DIR, "jarvis.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

# ---------------------------
# TTS
# ---------------------------
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)
engine.setProperty("rate", 165)

def talk(text, block=True):
    logging.info("SPEAK: %s", text)
    engine.say(str(text))
    if block:
        engine.runAndWait()
    else:
        threading.Thread(target=engine.runAndWait, daemon=True).start()

# ---------------------------
# Memory
# ---------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logging.exception("Failed to load memory, starting fresh.")
    return {"notes": [], "reminders": [], "facts": {}, "chat_history": []}

def save_memory(mem):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)
    except Exception:
        logging.exception("Failed to save memory.")

memory = load_memory()

# ---------------------------
# LLM integration (OpenAI-compatible)
# ---------------------------
def deepseek_chat(user_message, max_tokens=512):
    if not API_KEY:
        return "LLM API key not configured."

    # Build conversational history from memory.chat_history (last 6 exchanges)
    system_prompt = "You are Jarvis, a helpful assistant for a student. Be concise, friendly, and safe."
    messages = [{"role": "system", "content": system_prompt}]
    # include last few conversation turns for context
    for turn in memory.get("chat_history", [])[-6:]:
        # each turn stored as {"role":"user"/"assistant", "content": "..."}
        messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
    # append current user message
    messages.append({"role": "user", "content": user_message})

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.6,
    }
    try:
        resp = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=25)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"].strip()
            # store in memory chat history
            memory.setdefault("chat_history", []).append({"role": "user", "content": user_message})
            memory.setdefault("chat_history", []).append({"role": "assistant", "content": reply})
            # keep history reasonable
            if len(memory["chat_history"]) > 40:
                memory["chat_history"] = memory["chat_history"][-40:]
            save_memory(memory)
            return reply
        return "LLM returned an unexpected response."
    except Exception as e:
        logging.exception("LLM request failed")
        return f"LLM request failed: {e}"

# ---------------------------
# STT
# ---------------------------
listener = sr.Recognizer()
MIC_INDEX = None

def listen_for_command(timeout=6, phrase_time_limit=8):
    try:
        with sr.Microphone(device_index=MIC_INDEX) as source:
            listener.adjust_for_ambient_noise(source, duration=0.6)
            audio = listener.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = listener.recognize_google(audio)
            logging.info("Heard: %s", text)
            return text.lower()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except Exception:
        logging.exception("STT error")
        return ""

# ---------------------------
# Helpers / commands
# ---------------------------
def safe_confirm(action_text):
    talk(action_text + ". Say yes to confirm, no to cancel.")
    ans = listen_for_command(timeout=5, phrase_time_limit=4)
    if "yes" in ans or "yeah" in ans or "confirm" in ans:
        return True
    return False

def open_app(app_name):
    talk(f"Opening {app_name}")
    try:
        if platform.system() == "Windows":
            mapping = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                "chrome": "chrome",
                "vlc": "vlc",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe",
                "file explorer": "explorer.exe"
            }
            exe = mapping.get(app_name.lower(), app_name)
            os.startfile(exe)
        else:
            subprocess.Popen([app_name])
    except Exception as e:
        logging.exception("open_app")
        talk(f"Couldn't open {app_name}: {e}")

def play_youtube(query):
    talk(f"Playing {query} on YouTube")
    pywhatkit.playonyt(query)

def tell_time():
    now = datetime.datetime.now()
    s = now.strftime("%I:%M %p")
    talk("Current time is " + s)

def search_web(query):
    talk("Searching the web for " + query)
    webbrowser.open(f"https://www.google.com/search?q={requests.utils.requote_uri(query)}")

def take_note(text):
    entry = {"time": datetime.datetime.now().isoformat(), "text": text}
    memory.setdefault("notes", []).append(entry)
    save_memory(memory)
    talk("Saved the note.")

def add_reminder(reminder_text, when_dt):
    memory.setdefault("reminders", []).append({"time": when_dt.isoformat(), "text": reminder_text})
    save_memory(memory)
    talk("Reminder added.")

def list_notes():
    notes = memory.get("notes", [])
    if not notes:
        talk("You have no saved notes.")
        return
    talk(f"You have {len(notes)} notes. Reading top five.")
    for n in notes[-5:]:
        talk(n["text"], block=True)

# ---------------------------
# Reminder loop
# ---------------------------
def reminder_loop():
    while True:
        now = datetime.datetime.now()
        to_keep = []
        for r in memory.get("reminders", []):
            try:
                t = datetime.datetime.fromisoformat(r["time"])
                if now >= t:
                    talk("Reminder: " + r["text"])
                else:
                    to_keep.append(r)
            except Exception:
                to_keep.append(r)
        if len(to_keep) != len(memory.get("reminders", [])):
            memory["reminders"] = to_keep
            save_memory(memory)
        time.sleep(30)

threading.Thread(target=reminder_loop, daemon=True).start()

# ---------------------------
# Process command
# ---------------------------
def process_command(command):
    command = command.lower().strip()
    if not command:
        return

    if "play" in command and "youtube" in command:
        q = command.replace("play", "").replace("on youtube", "").strip()
        play_youtube(q or "top hits")
    elif command.startswith("play "):
        q = command.replace("play", "").strip()
        play_youtube(q)
    elif "time" in command and ("what" in command or "current" in command or command == "time"):
        tell_time()
    elif command.startswith("open "):
        app = command.replace("open", "").strip()
        open_app(app)
    elif "search" in command and ("web" in command or "google" in command):
        q = command.replace("search", "").replace("on web", "").replace("google", "").strip()
        search_web(q)
    elif "wikipedia" in command or command.startswith("who is") or command.startswith("what is"):
        subject = command.replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
        if not subject:
            talk("What should I search on Wikipedia?")
            subject = listen_for_command()
        try:
            summary = wikipedia.summary(subject, sentences=2)
            talk(summary)
        except Exception:
            talk("I couldn't find a good Wikipedia summary.")
    elif "joke" in command:
        talk(pyjokes.get_joke())
    elif "note" in command or "remember" in command:
        talk("What should I note?")
        note = listen_for_command()
        if note:
            take_note(note)
        else:
            talk("Note cancelled.")
    elif "add reminder" in command or "remind me" in command:
        talk("Tell me the reminder text.")
        text = listen_for_command(timeout=8, phrase_time_limit=6)
        talk("Tell me the time and date for the reminder, like 'tomorrow 6 pm' or 'in 10 minutes'.")
        timephrase = listen_for_command(timeout=8, phrase_time_limit=6)
        when = parse_time_phrase(timephrase)
        if when:
            add_reminder(text, when)
        else:
            talk("Couldn't parse the time. Reminder not added.")
    elif "shutdown" in command or "shut down" in command:
        if safe_confirm("I will shut down the system"):
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            else:
                os.system("shutdown now")
    elif "restart" in command:
        if safe_confirm("I will restart the system"):
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            else:
                os.system("reboot")
    elif "screenshot" in command or "take screenshot" in command:
        path = os.path.join(DATA_DIR, f"screenshot_{int(time.time())}.png")
        img = pyautogui.screenshot()
        img.save(path)
        talk(f"Screenshot saved to {path}")
    elif "ask" in command or "chat" in command or "explain" in command or command.startswith("explain"):
        prompt = command
        talk("Let me think...")
        resp = deepseek_chat(prompt)
        talk(resp)
    elif "remember that" in command or "note that" in command:
        fact = command.replace("remember that", "").replace("note that", "").strip()
        if fact:
            key = f"fact_{len(memory.get('facts', {})) + 1}"
            memory.setdefault("facts", {})[key] = fact
            save_memory(memory)
            talk("Okay, I will remember that.")
    elif "list notes" in command or "show notes" in command:
        list_notes()
    elif "stop listening" in command:
        global LISTEN
        LISTEN = False
        talk("Listening disabled. Press F8 to re-enable.")
    else:
        talk("I will try to answer that.")
        resp = deepseek_chat(command)
        talk(resp)

# ---------------------------
# Simple time parser
# ---------------------------
def parse_time_phrase(phrase):
    if not phrase:
        return None
    phrase = phrase.lower()
    now = datetime.datetime.now()
    try:
        if "in " in phrase and "minute" in phrase:
            num = int(''.join(ch for ch in phrase if ch.isdigit()))
            return now + datetime.timedelta(minutes=num)
        if "in " in phrase and "hour" in phrase:
            num = int(''.join(ch for ch in phrase if ch.isdigit()))
            return now + datetime.timedelta(hours=num)
        parts = phrase.split()
        if "tomorrow" in parts:
            for i, p in enumerate(parts):
                if p.isdigit():
                    hour = int(p)
                    minute = 0
                    if i+1 < len(parts) and parts[i+1] in ("pm","am"):
                        if parts[i+1] == "pm" and hour != 12:
                            hour += 12
                        if parts[i+1] == "am" and hour == 12:
                            hour = 0
                    t = now + datetime.timedelta(days=1)
                    return t.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if "at" in parts:
            idx = parts.index("at")
            if idx+1 < len(parts) and parts[idx+1].isdigit():
                hour = int(parts[idx+1])
                minute = 0
                if idx+2 < len(parts) and parts[idx+2] in ("pm","am"):
                    if parts[idx+2] == "pm" and hour != 12:
                        hour += 12
                    if parts[idx+2] == "am" and hour == 12:
                        hour = 0
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except Exception:
        return None
    return None

# ---------------------------
# Listening loop
# ---------------------------
def listen_loop():
    global LISTEN
    talk("Jarvis is online. Say 'Jarvis' followed by a command, or press F8 to toggle listening.")
    while True:
        if not LISTEN:
            time.sleep(0.5)
            continue
        text = listen_for_command(timeout=6, phrase_time_limit=6)
        if not text:
            continue
        if WAKE_WORD in text:
            cmd = text.replace(WAKE_WORD, "").strip()
            if not cmd:
                talk("Yes?")
                cmd = listen_for_command()
            logging.info("Command after wake: %s", cmd)
            process_command(cmd)
        else:
            import ctypes
            # if hotkey is pressed treat as command
            try:
                if keyboard.is_pressed(LISTEN_HOTKEY):
                    process_command(text)
                else:
                    reserved = ["open", "play", "search", "shutdown", "restart", "note", "remind", "screenshot"]
                    if any(word in text for word in reserved):
                        process_command(text)
                    else:
                        logging.info("Ignored ambient speech: %s", text)
            except Exception:
                logging.exception("hotkey check failed")

def hotkey_toggle():
    global LISTEN
    while True:
        keyboard.wait(LISTEN_HOTKEY)
        LISTEN = not LISTEN
        talk("Listening enabled." if LISTEN else "Listening disabled.")
        time.sleep(0.3)

threading.Thread(target=hotkey_toggle, daemon=True).start()

if __name__ == "__main__":
    try:
        listen_loop()
    except KeyboardInterrupt:
        talk("Shutting down. Bye.")
        save_memory(memory)
        sys.exit(0)
