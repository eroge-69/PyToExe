import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import requests
import threading
import time

# Config
API_KEY = "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"
MODEL = "mistralai/devstral-small:free"

# Voice Engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# Speak Function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# AI API Request
def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=15)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Listening Loop in Background
def continuous_listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.energy_threshold = 400
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.5

    while True:
        try:
            with mic as source:
                user_label.configure(text="🎧 Listening for voice...", text_color="#cccccc")
                audio = recognizer.listen(source, phrase_time_limit=8)

            query = recognizer.recognize_google(audio, language='en-US')
            user_label.configure(text=f"You said: {query}", text_color="#00ffff")

            response = ask_openrouter(query)
            ai_label.configure(text=f"AI: {response}", text_color="#ffdd88")
            speak(response)

        except sr.UnknownValueError:
            user_label.configure(text="Sorry, couldn't understand. Trying again...", text_color="red")
        except sr.RequestError:
            user_label.configure(text="Speech recognition service down.", text_color="red")
        except Exception as e:
            user_label.configure(text=f"Error: {str(e)}", text_color="red")
        time.sleep(1)

# UI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Auto Listening AI Assistant")
app.geometry("360x400")
app.resizable(False, False)

frame = ctk.CTkFrame(master=app, width=320, height=320, corner_radius=160, fg_color="#1e1e1e")
frame.pack(pady=20)

user_label = ctk.CTkLabel(master=frame, text="", wraplength=260, font=("Arial", 14), text_color="#ffffff")
user_label.place(relx=0.5, rely=0.3, anchor="center")

ai_label = ctk.CTkLabel(master=frame, text="", wraplength=260, font=("Arial", 13, "italic"), text_color="#00ff99")
ai_label.place(relx=0.5, rely=0.55, anchor="center")

# Background Thread Start
threading.Thread(target=continuous_listen, daemon=True).start()

# Run GUI
app.mainloop()
