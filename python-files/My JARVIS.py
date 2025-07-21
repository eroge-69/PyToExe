import pyttsx3
import datetime
import wikipedia
import webbrowser
import pywhatkit
import pyjokes
import os

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# Set your name and voice preference
USER_NAME = "Boss"
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Use female voice; change to [0] for male

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def greet():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning " + USER_NAME)
    elif 12 <= hour < 18:
        speak("Good afternoon " + USER_NAME)
    else:
        speak("Good evening " + USER_NAME)
    speak("I am Jarvis. How can I assist you today?")

def take_command():
    command = input(f"{USER_NAME}: ").lower()
    return command

def run_jarvis():
    greet()
    while True:
        command = take_command()

        if "wikipedia" in command:
            topic = command.replace("wikipedia", "")
            speak("Searching Wikipedia...")
            try:
                result = wikipedia.summary(topic, sentences=2)
                speak(result)
            except Exception as e:
                speak("Sorry, I couldn't find any results.")

        elif "open youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://youtube.com")

        elif "open google" in command:
            speak("Opening Google")
            webbrowser.open("https://google.com")

        elif "play" in command:
            song = command.replace("play", "")
            speak(f"Playing {song} on YouTube")
            pywhatkit.playonyt(song)

        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {current_time}")

        elif "date" in command:
            today = datetime.date.today().strftime("%B %d, %Y")
            speak(f"Today's date is {today}")

        elif "joke" in command:
            joke = pyjokes.get_joke()
            speak(joke)

        elif "open notepad" in command:
            speak("Opening Notepad")
            os.system("notepad")

        elif "open command prompt" in command or "cmd" in command:
            speak("Opening Command Prompt")
            os.system("start cmd")

        elif "exit" in command or "bye" in command or "stop" in command:
            speak("Goodbye, have a great day!")
            break

        else:
            speak("Sorry, I did not understand that command.")

if __name__ == "__main__":
    run_jarvis()
