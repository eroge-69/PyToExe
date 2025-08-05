import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import pywhatkit
import os
import openai
from colorama import Fore, Style, init
from playsound import playsound
import threading

# Init
init(autoreset=True)
openai.api_key = 'YOUR_API_KEY_HERE'

# Text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 0 for male, 1 for female
engine.setProperty('rate', 170)

tasks = []

def speak(text):
    print(Fore.CYAN + "Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

def play_startup_sound():
    try:
        threading.Thread(target=playsound, args=('jarvis_startup.mp3',)).start()
    except:
        pass

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(Fore.YELLOW + "🎤 Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(Fore.GREEN + "You said:", command)
        return command.lower()
    except:
        speak("Sorry, I didn't catch that.")
        return ""

def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        return reply.strip()
    except:
        return "I had trouble connecting to ChatGPT."

def handle_tasks(command):
    if "add task" in command:
        task = command.replace("add task", "").strip()
        tasks.append(task)
        speak(f"Task added: {task}")
    elif "show tasks" in command:
        if tasks:
            speak("Here are your tasks:")
            for i, task in enumerate(tasks, 1):
                speak(f"{i}. {task}")
        else:
            speak("You have no tasks.")
    elif "clear tasks" in command:
        tasks.clear()
        speak("All tasks cleared.")

def greet():
    play_startup_sound()
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning, I am Jarvis. How can I assist you?")
    elif hour < 18:
        speak("Good afternoon, I am Jarvis. Ready for your commands.")
    else:
        speak("Good evening, I am Jarvis. How may I help you tonight?")

def run_jarvis():
    greet()
    while True:
        command = take_command()

        if not command:
            continue

        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            speak(f"The time is {time}")

        elif 'open youtube' in command:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")

        elif 'open google' in command:
            webbrowser.open("https://google.com")
            speak("Opening Google")

        elif 'search' in command:
            query = command.replace('search', '')
            pywhatkit.search(query)
            speak(f"Searching for {query}")

        elif 'who is' in command or 'what is' in command:
            try:
                person = command.replace('who is', '').replace('what is', '')
                info = wikipedia.summary(person, sentences=2)
                speak(info)
            except:
                speak("Sorry, I couldn't find that.")

        elif 'play' in command:
            song = command.replace('play', '')
            pywhatkit.playonyt(song)
            speak(f"Playing {song}")

        elif 'open notepad' in command:
            os.system('notepad.exe')
            speak("Notepad opened")

        elif 'add task' in command or 'show tasks' in command or 'clear tasks' in command:
            handle_tasks(command)

        elif 'exit' in command or 'bye' in command:
            speak("Goodbye, powering down.")
            break

        else:
            answer = chat_with_gpt(command)
            speak(answer)

if __name__ == "__main__":
    run_jarvis()
