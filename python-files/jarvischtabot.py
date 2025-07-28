import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import os
import webbrowser
import psutil

# Initialize voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('voice', engine.getProperty('voices')[1].id)

def speak(text):
    chat_area.insert(tk.END, f"AURA: {text}\n")
    engine.say(text)
    engine.runAndWait()

def perform_action(command):
    command = command.lower()
    if "open notepad" in command:
        os.system("notepad")
        speak("Opening Notepad.")
    elif "open chrome" in command:
        os.system("start chrome")
        speak("Launching Chrome.")
    elif "shutdown system" in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")
    elif "restart system" in command:
        speak("Rebooting system.")
        os.system("shutdown /r /t 1")
    elif "lock screen" in command:
        speak("Locking your system.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "battery status" in command:
        battery = psutil.sensors_battery()
        speak(f"Battery is at {battery.percent} percent.")
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("Launching YouTube.")
    elif "open google" in command:
        webbrowser.open("https://google.com")
        speak("Accessing Google.")
    else:
        speak("Command not recognized.")

def send_command():
    command = entry.get()
    if command.strip() == "":
        return
    chat_area.insert(tk.END, f"You: {command}\n")
    entry.delete(0, tk.END)
    if command.lower() == "shutdown":
        speak("Goodbye, Commander.")
        window.quit()
    else:
        perform_action(command)

# GUI setup
window = tk.Tk()
window.title("🛰️ AURA - Sci-Fi Assistant Dashboard")
window.geometry("600x500")
window.configure(bg="#0d0d0d")

title = tk.Label(window, text="AURA – Autonomous Unit for Response & Assistance", font=("Orbitron", 14), bg="#0d0d0d", fg="#00ffcc")
title.pack(pady=10)

chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=20, font=("Consolas", 10), bg="#1a1a1a", fg="#00ffcc")
chat_area.pack(padx=10, pady=5)
chat_area.insert(tk.END, "🛰️ AURA ONLINE. Type your command below.\n\n")

entry = tk.Entry(window, font=("Consolas", 12), width=50, bg="#262626", fg="#00ffcc", insertbackground="#00ffcc")
entry.pack(pady=10)
entry.bind("<Return>", lambda event: send_command())

send_btn = tk.Button(window, text="Execute", command=send_command, bg="#00ffcc", fg="#0d0d0d", font=("Consolas", 12))
send_btn.pack(pady=5)

window.mainloop()
