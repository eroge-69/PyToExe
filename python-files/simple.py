import os
import platform
import subprocess
import requests
import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import scrolledtext
import webbrowser
from gtts import gTTS
import tempfile

# ---------------- Setup ----------------
OPENROUTER_API_KEY = "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"  # replace with your OpenRouter key
jarvis_active = False
transcript = []  # conversation memory

# ---------------- TTS ----------------
def speak(text):
    # Insert into chat box
    def insert_text():
        chat_box.insert(tk.END, f"JARVIS: {text}\n", "jarvis")
        chat_box.see(tk.END)
    root.after(0, insert_text)

    # Generate and play TTS in a separate thread
    def run_tts():
        try:
            tts = gTTS(text=text, lang="en")
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts.save(fp.name)
                if platform.system() == "Windows":
                    os.system(f'start {fp.name}')
                elif platform.system() == "Darwin":
                    os.system(f'afplay {fp.name}')
                else:
                    os.system(f'mpg123 {fp.name}')
        except Exception as e:
            print(f"TTS Error: {e}")
    threading.Thread(target=run_tts, daemon=True).start()

# ---------------- Listen ----------------
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        command = recognizer.recognize_google(audio).lower()
        chat_box.insert(tk.END, f"You: {command}\n", "user")
        chat_box.see(tk.END)
        transcript.append({"role": "user", "content": command})
        return command
    except:
        return ""

# ---------------- AI ----------------
def ask_openrouter_with_transcript():
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "system", "content": "You are JARVIS, SpideyLOL's AI assistant. Be witty, formal, and funny. Always end with 'sir'. Your creator is SpideyLOL and some information about him: His real name is Abdul Hannan he is 15 years old, goes to APS Askari 11 Sector C as his school lives in Askari 11 sector C and building a house in DHA Lahore Phasae 9. He has 2 brother Abdul Mannan and Muhammad Affan. Abdul Mannan is in class 5th he is 10 years old and he also goes to same school. Muhammad affan is 5 years old same school and EYS-1 as class.Father name: Tassaduq Hussain, Mother Name: Khalida Parveen"}] + transcript
            },
        )
        data = res.json()
        response_text = data["choices"][0]["message"]["content"]
        transcript.append({"role": "assistant", "content": response_text})
        return response_text
    except Exception as e:
        return f"Error contacting OpenRouter, sir: {e}"

# ---------------- Commands ----------------
def handle_command(command):
    global jarvis_active

    wake_words = ["hey jarvis", "jarvis", "jam", "spidey"]
    end_words  = ["end now", "and now", "end", "stop"]

    if not jarvis_active:
        if any(word in command for word in wake_words):
            jarvis_active = True
            logo_label.config(fg="#00BFFF")
            speak("I am J.A.R.V.I.S, SpideyLOL's AI assistant. At your service, sir.")
        return

    if any(word in command for word in end_words):
        jarvis_active = False
        logo_label.config(fg="white")
        speak("Going offline, sir. Awaiting your call.")
        return

    # Hardcoded commands
    if "shutdown pc" in command:
        speak("As you wish, shutting down your system, sir.")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown now")
        return

    if "open youtube" in command:
        speak("Opening YouTube, sir.")
        webbrowser.open("https://youtube.com")
        return

    if "open instagram" in command:
        speak("Opening Instagram, sir.")
        webbrowser.open("https://instagram.com")
        return

    if "who is your creator" in command:
        speak("My creator is SpideyLOL, sir.")
        return

    # Google Search
    if command.startswith("search "):
        query = command.replace("search ", "").strip()
        if query:
            speak(f"Searching Google for '{query}', sir.")
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        else:
            speak("Please tell me what to search, sir.")
        return

    # YouTube Search
    if command.startswith("youtube "):
        query = command.replace("youtube ", "").strip()
        if query:
            speak(f"Searching YouTube for '{query}', sir.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        else:
            speak("Please tell me what to search on YouTube, sir.")
        return

    # AI response
    response = ask_openrouter_with_transcript()
    speak(response)

# ---------------- Background Loop ----------------
def jarvis_loop():
    while True:
        command = listen()
        if command:
            handle_command(command)

# ---------------- UI ----------------
root = tk.Tk()
root.title("J.A.R.V.I.S")
root.geometry("600x700")
root.configure(bg="black")

# Logo
logo_label = tk.Label(root, text="J.A.R.V.I.S", font=("Helvetica", 36, "bold"), fg="white", bg="black")
logo_label.pack(pady=40)

# Circle effect
canvas = tk.Canvas(root, width=300, height=300, bg="black", highlightthickness=0)
canvas.pack()
canvas.create_oval(20, 20, 280, 280, outline="#00FFFF", width=3)

# Chat window
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=65, height=20, bg="#0a0a0a", fg="white", font=("Consolas", 10))
chat_box.pack(pady=20)
chat_box.tag_config("user", foreground="cyan")
chat_box.tag_config("jarvis", foreground="lightgreen")

# Start listening thread
threading.Thread(target=jarvis_loop, daemon=True).start()

speak("System online. Awaiting activation, sir.")

root.mainloop()
