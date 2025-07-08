import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import datetime
import time
import requests
import json

# Load DeepSeek API key
with open("config.txt", "r") as f:
    API_KEY = f.read().strip()

# Text-to-speech engine setup
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

# Wake word
WAKE_WORD = "hey jarvis"

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        command = r.recognize_google(audio).lower()
        print("You said:", command)
        return command
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Sorry, your internet connection is off.")
        return ""

def ask_deepseek(question):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        reply = response.json()['choices'][0]['message']['content']
        return reply
    except Exception as e:
        return "Sorry, I couldn't reach DeepSeek."

def perform_task(command):
    if "open notepad" in command:
        os.system("notepad")
        speak("Opening Notepad.")
    elif "open chrome" in command:
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        os.startfile(chrome_path)
        speak("Opening Chrome.")
    elif "play music" in command:
        music_folder = "C:\\Users\\Public\\Music"
        songs = os.listdir(music_folder)
        if songs:
            os.startfile(os.path.join(music_folder, songs[0]))
            speak("Playing music.")
        else:
            speak("No music found.")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}")
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif "shutdown" in command:
        speak("Shutting down the computer.")
        os.system("shutdown /s /t 5")
    elif "restart" in command:
        speak("Restarting the computer.")
        os.system("shutdown /r /t 5")
    elif "search google for" in command:
        search_query = command.replace("search google for", "").strip()
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(url)
        speak(f"Searching Google for {search_query}")
    elif "search youtube for" in command:
        search_query = command.replace("search youtube for", "").strip()
        url = f"https://www.youtube.com/results?search_query={search_query}"
        webbrowser.open(url)
        speak(f"Searching YouTube for {search_query}")
    elif "tell me a joke" in command:
        joke = ask_deepseek("Tell me a short funny joke.")
        speak(joke)
    else:
        reply = ask_deepseek(command)
        speak(reply)

# --- Main Loop ---
speak("JARVIS is now online.")
while True:
    text = listen()
    if WAKE_WORD in text:
        speak("Yes, boss.")
        time.sleep(1)
        command = listen()
        if command:
            perform_task(command)
