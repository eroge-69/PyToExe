import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
from googletrans import Translator

recognizer = sr.Recognizer()
translator = Translator()
running = False  # Control flag for listening loop

# GUI setup
root = tk.Tk()
root.title("Live Translator")
root.geometry("400x250")
root.resizable(False, False)
root.attributes("-topmost", True)

# Language selector
tk.Label(root, text="Target Language (e.g., fr, de, ja):").pack(pady=5)
target_lang = tk.StringVar(value='fr')
tk.Entry(root, textvariable=target_lang).pack()

# Output display
output_var = tk.StringVar()
tk.Label(root, textvariable=output_var, fg="black", wraplength=380).pack(pady=10)

# Status bar
status_var = tk.StringVar(value="🟢 Ready")
tk.Label(root, textvariable=status_var, fg="blue", anchor="w").pack(fill=tk.X, padx=10, pady=5)

# Listening & Translation loop
def translate_loop():
    global running
    try:
        with sr.Microphone() as source:
            while running:
                try:
                    root.after(0, status_var.set, "🎙️ Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    root.after(0, status_var.set, "🧠 Recognizing...")
                    text = recognizer.recognize_google(audio)

                    root.after(0, status_var.set, "🌐 Translating...")
                    translated = translator.translate(text, dest=target_lang.get()).text

                    result = f"You said: {text}\nTranslated: {translated}"
                    root.after(0, output_var.set, result)
                    root.after(0, status_var.set, "✅ Ready - Waiting for next input")

                except Exception as e:
                    root.after(0, status_var.set, f"⚠️ Error: {e}")
                    root.after(0, output_var.set, "")
    except Exception as mic_error:
        root.after(0, status_var.set, f"🎙️ Microphone Error: {mic_error}")

# Control buttons
def start_translation():
    global running
    if not running:
        running = True
        threading.Thread(target=translate_loop, daemon=True).start()
        status_var.set("🔄 Translation started")

def stop_translation():
    global running
    running = False
    status_var.set("🔴 Translation stopped")

# Buttons
tk.Button(root, text="Start", bg="green", fg="white", command=start_translation).pack(pady=5, fill=tk.X, padx=20)
tk.Button(root, text="Stop", bg="red", fg="white", command=stop_translation).pack(pady=5, fill=tk.X, padx=20)

root.mainloop()
