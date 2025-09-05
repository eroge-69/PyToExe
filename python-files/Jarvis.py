import speech_recognition as sr
from gtts import gTTS
import os
import webbrowser
import datetime
import random
import sys
import playsound

# Speak Function using gTTS
def speak(text):
    print(f"JARVIS: {text}")
    tts = gTTS(text=text, lang="en", slow=False)
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=6)

    try:
        query = r.recognize_google(audio, language="en-in").lower()
        print(f"👉 You said: {query}")
        return query
    except:
        return ""

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning sir.")
    elif 12 <= hour < 18:
        speak("Good afternoon sir.")
    else:
        speak("Good evening sir.")
    speak("I am Jarvis, online and fully operational.")

def open_application(app):
    paths = {
        "notepad": "notepad.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "spotify": r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe"
    }
    path = paths.get(app)
    if path:
        os.startfile(path)
        speak(f"Opening {app}.")
    else:
        speak(f"Sorry, I don’t know how to open {app} yet.")

def execute_query(query):
    if "time" in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")

    elif "date" in query:
        today = datetime.date.today().strftime("%B %d, %Y")
        speak(f"Today's date is {today}")

    elif "open google" in query:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")

    elif "open youtube" in query:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")

    elif "open notepad" in query:
        open_application("notepad")

    elif "open chrome" in query:
        open_application("chrome")

    elif "open code" in query or "open vs code" in query:
        open_application("vscode")

    elif "play music" in query:
        music_dir = r"C:\Users\%USERNAME%\Music"
        try:
            songs = os.listdir(music_dir)
            if songs:
                song = random.choice(songs)
                os.startfile(os.path.join(music_dir, song))
                speak("Playing music.")
            else:
                speak("No music files found.")
        except:
            speak("I couldn't find your music directory.")

    elif "shutdown" in query:
        speak("Shutting down the system. Goodbye sir.")
        os.system("shutdown /s /t 1")

    elif "restart" in query:
        speak("Restarting the system.")
        os.system("shutdown /r /t 1")

    elif "exit" in query or "quit" in query:
        speak("Goodbye sir.")
        sys.exit()

    else:
        speak("I am not programmed for that yet.")

if __name__ == "__main__":
    wish_me()
    while True:
        command = listen()
        if command:
            execute_query(command)
