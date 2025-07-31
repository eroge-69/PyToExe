import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import pywhatkit
import pyjokes

engine = pyttsx3.init()
recognizer = sr.Recognizer()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except:
            speak("Sorry, I did not get that.")
            return ""


def wish_me():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I am Jarvis. How can I help you?")


wish_me()

while True:
    query = listen()

    if 'hello jarvis' in query:
        speak("Hello! How can I assist you?")

    elif 'time' in query:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {now}")

    elif 'wikipedia' in query:
        speak("What should I search on Wikipedia?")
        search_query = listen()
        if search_query:
            try:
                result = wikipedia.summary(search_query, sentences=2)
                speak(f"According to Wikipedia, {result}")
            except Exception:
                speak("Sorry, I couldn't find anything on Wikipedia.")

    elif 'open' in query:
        website = query.replace('open ', '').strip()
        if website == 'notepad':
            speak("Opening Notepad")
            os.system('notepad.exe')
        elif website == 'calculator':
            speak("Opening Calculator")
            os.system('calc.exe')
        else:
            speak(f"Opening {website}")
            webbrowser.open(f"https://{website}")

    elif 'play' in query:
        song = query.replace('play ', '').strip()
        speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)

    elif 'joke' in query:
        joke = pyjokes.get_joke()
        speak(joke)

    elif 'stop' in query or 'exit' in query or 'bye' in query:
        speak("Goodbye!")
        break
