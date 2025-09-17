import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import threading
import time
import math
import pyttsx3
import speech_recognition as sr
import requests
import json

# === CONFIG ===
GROQ_API_KEY = "your_groq_api_key"
MODEL = "llama3-8b-8192"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# === TTS Engine ===
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        set_listening(True)
        update_terminal("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        update_terminal(f"🧑 You said: {command}")
        return command
    except sr.UnknownValueError:
        update_terminal("❌ Sorry, I didn't catch that.")
        speak("Sorry, I didn't catch that.")
        return None
    finally:
        set_listening(False)

def chat_with_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "⚠️ Error from Groq API."

def update_terminal(msg):
    terminal.config(state=tk.NORMAL)
    terminal.insert(tk.END, msg + "\n")
    terminal.yview(tk.END)
    terminal.config(state=tk.DISABLED)

def start_listening():
    threading.Thread(target=voice_thread).start()

def voice_thread():
    command = listen()
    if command:
        reply = chat_with_groq(command)
        update_terminal(f"🤖 {reply}")
        speak(reply)

def set_listening(active):
    global listening
    listening = active

def animate_waveform():
    phase = 0
    while True:
        canvas.delete("wave")
        if listening:
            for x in range(250, 550, 10):
                y = 180 + 25 * math.sin((x + phase) / 15)
                canvas.create_oval(x, y, x+6, y+6, fill="#00FFFF", outline="", tags="wave")
            phase += 6
        time.sleep(0.05)

# === GUI Setup ===
root = tk.Tk()
root.title("Alpha AI")
root.geometry("1080x700")
root.configure(bg="black")

# === Canvas with Background ===
bg_img = Image.open("bg.png")  # Use the image you uploaded, saved as 'bg.png'
bg_photo = ImageTk.PhotoImage(bg_img)
canvas = tk.Canvas(root, width=1080, height=500, highlightthickness=0)
canvas.pack()
canvas.create_image(0, 0, anchor="nw", image=bg_photo)

# === Voice Waveform Animation ===
listening = False
threading.Thread(target=animate_waveform, daemon=True).start()

# === Terminal Log ===
terminal = scrolledtext.ScrolledText(root, height=8, bg="black", fg="lime", font=("Courier", 12), state=tk.DISABLED)
terminal.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

# === Mic Button ===
mic_button = tk.Button(root, text="🎤 Speak", command=start_listening, font=("Arial", 14), bg="#111", fg="cyan")
mic_button.pack(pady=5)

# === Intro ===
update_terminal("🤖 Alpha AI initialized. Click 'Speak' to talk.")
speak("Hello, I am Alpha AI. Ready when you are.")

root.mainloop()
