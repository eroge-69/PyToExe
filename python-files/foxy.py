import tkinter as tk
from tkinter import scrolledtext
from gtts import gTTS
import os
import uuid
import pygame
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import pyjokes
import openai
from config import OPENAI_API_KEY

# === Init ===
openai.api_key = OPENAI_API_KEY
pygame.mixer.init()

# === Voice Function using gTTS + pygame ===
def speak(text):
    print(f"Foxy 🦊: {text}")
    chatbox.insert(tk.END, f"Foxy 🦊: {text}\n")
    chatbox.see(tk.END)

    tts = gTTS(text=text, lang='en')
    filename = f"temp_{uuid.uuid4()}.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until the sound finishes
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # wait with proper CPU usage

    pygame.mixer.music.unload()  # ⬅️ unload the file before deleting
    pygame.mixer.quit()
    os.remove(filename)


# === Listening ===
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("🎙️ Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5)
            query = r.recognize_google(audio, language='en-in')
            chatbox.insert(tk.END, f"🗣️ You: {query}\n")
            chatbox.see(tk.END)
            return query.lower()
        except sr.WaitTimeoutError:
            speak("No input detected.")
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand.")
        except sr.RequestError:
            speak("Speech service is down.")
    return ""

# === Assistant Logic ===
def greet_user():
    hour = datetime.datetime.now().hour
    greet = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
    speak(f"{greet}! I am Foxy, your assistant. How can I help?")

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {now}")

def tell_date():
    date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {date}")

def open_site(query):
    if "youtube" in query:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
    elif "google" in query:
        webbrowser.open("https://google.com")
        speak("Opening Google")
    elif "gmail" in query:
        webbrowser.open("https://mail.google.com")
        speak("Opening Gmail")
    else:
        speak("I can only open Google, YouTube, or Gmail.")

def wiki_search(query):
    topic = query.replace("wikipedia", "").strip()
    try:
        result = wikipedia.summary(topic, sentences=2)
        speak("According to Wikipedia...")
        speak(result)
    except:
        speak("Couldn't find info on Wikipedia.")

def run_chatbot(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        speak(reply)
    except Exception as e:
        speak("Chatbot is not available right now.")

def handle_query(query):
    if "time" in query:
        tell_time()
    elif "date" in query:
        tell_date()
    elif "open" in query:
        open_site(query)
    elif "wikipedia" in query:
        wiki_search(query)
    elif "joke" in query:
        speak(pyjokes.get_joke())
    elif "chat" in query or "talk to me" in query:
        speak("Chatbot mode activated. Say 'exit' to stop.")
        while True:
            user_input = listen()
            if "exit" in user_input:
                speak("Exiting chatbot.")
                break
            run_chatbot(user_input)
    elif "exit" in query or "bye" in query:
        speak("Goodbye, shutting down Foxy!")
        root.destroy()
    else:
        speak("I didn't understand that command.")

def run_foxy():
    query = listen()
    if query:
        handle_query(query)

# === GUI ===
root = tk.Tk()
root.title("🦊 Foxy Voice Assistant")
root.geometry("600x400")

chatbox = scrolledtext.ScrolledText(root, font=("Consolas", 12), bg="#1e1e1e", fg="white")
chatbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

btn = tk.Button(root, text="🎙️ Start Listening", font=("Arial", 14), bg="orange", fg="black", command=run_foxy)
btn.pack(pady=10)

greet_user()
root.mainloop()
