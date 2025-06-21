
import os
import time
import random
import webbrowser
import subprocess
import platform
import speech_recognition as sr
import pyttsx3

try:
    from transformers import pipeline
    smart_mode = "online"
except ImportError:
    smart_mode = "offline"

# ========== VOICE SETUP ==========
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for v in voices:
    if "female" in v.name.lower():
        engine.setProperty('voice', v.id)
        break
engine.setProperty('rate', 170)

def speak(text):
    print(f"BEM: {text}")
    engine.say(text)
    engine.runAndWait()

# ========== SMART BRAIN SETUP ==========
if smart_mode == "online":
    try:
        generator = pipeline("text-generation", model="gpt2")
    except:
        smart_mode = "offline"

def ask_smart_ai(question):
    if smart_mode == "online":
        result = generator(question, max_length=100, num_return_sequences=1)
        return result[0]['generated_text']
    else:
        return random.choice([
            "I'm thinking... maybe try again later.",
            "You're doing great, Mahesh!",
            "Even without internet, you're still smart!"
        ])

# ========== MICROPHONE INPUT ==========
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-IN')
        print(f"You said: {query}")
    except:
        return "None"
    return query.lower()

# ========== MOTIVATION ==========
def motivate_me():
    quotes = [
        "You are stronger than you think, Mahesh.",
        "Success is the sum of small efforts repeated daily.",
        "Never give up on your dreams!",
        "Keep going, your future self will thank you."
    ]
    speak(random.choice(quotes))

# ========== COMMANDS ==========
def run_bem():
    speak("Hello Mahesh, I am BEM. What do you need today?")

    while True:
        query = take_command()

        if "youtube" in query:
            speak("Opening YouTube")
            webbrowser.open("https://youtube.com")

        elif "time" in query:
            strTime = time.strftime("%I:%M %p")
            speak(f"The time is {strTime}")

        elif "music" in query or "play song" in query:
            music_path = os.path.expanduser("~/Music")
            if os.path.exists(music_path):
                speak("Playing music")
                os.startfile(music_path)
            else:
                speak("Music folder not found")

        elif "motivate" in query:
            motivate_me()

        elif "open notepad" in query:
            speak("Opening Notepad")
            os.system("notepad")

        elif "open chrome" in query:
            speak("Opening Chrome")
            os.system("start chrome")

        elif "smart mode" in query or "question" in query:
            speak("Okay, ask me anything")
            question = take_command()
            answer = ask_smart_ai(question)
            speak(answer)

        elif "shutdown" in query:
            speak("Shutting down the system. Goodbye Mahesh!")
            os.system("shutdown /s /t 1")

        elif "stop" in query or "exit" in query:
            speak("Goodbye Mahesh")
            break

        elif query != "none":
            speak("Sorry, I didn't understand. Try again or say smart mode.")

if __name__ == "__main__":
    run_bem()
