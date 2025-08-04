# for this file a .py is needed because of pttsx3 usage
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import pyjokes
import pyttsx3
import threading
import tkinter as tk

# Initialize recognizer
listener = sr.Recognizer()

# Function to speak text
def talk(response):
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(response)
    engine.runAndWait()
    engine.stop()

# Function to listen and return command
def take_command():
    try:
        with sr.Microphone() as source:
            status_label.config(text="Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'zeus' in command:
                command = command.replace('zeus', '').strip()
                return command
    except Exception as e:
        status_label.config(text=f"Error: {e}")
    return ""

# Main logic for processing command
def run_alexa():
    command = take_command()
    response = ""

    if command:
        command_label.config(text=f"You said: {command}")
        
        if any(stop_word in command for stop_word in ['stop', 'exit', 'quit']):
            response = "Goodbye!"
            talk(response)
            response_label.config(text=response)
            root.after(2000, root.destroy)
            return

        elif 'play' in command:
            song = command.replace('play', '').strip()
            response = f"Playing {song}"
            pywhatkit.playonyt(song)

        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            response = f"The current time is {time}"

        elif 'who is' in command:
            person = command.replace('who is', '').strip()
            try:
                info = wikipedia.summary(person, 1)
                response = info
            except:
                response = f"I couldn't find information about {person}"

        elif 'what is' in command:
            topic = command.replace('what is', '').strip()
            try:
                info = wikipedia.summary(topic, 1)
                response = info
            except:
                response = f"Sorry, I couldn't find details about {topic}"

        elif 'joke' in command:
            response = pyjokes.get_joke()

        else:
            response = "Please say the command again."

        response_label.config(text=response)
        talk(response)
    else:
        command_label.config(text="Didn't catch that.")
        response_label.config(text="")

# To run the assistant
def threaded_run():
    threading.Thread(target=run_alexa).start()

# Setup GUI
root = tk.Tk()
root.title("Zeus Voice Assistant")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

status_label = tk.Label(root, text="Press 'Start Listening' to begin.", font=("Arial", 18), bg="#f0f0f0")
status_label.pack(pady=10)

command_label = tk.Label(root, text="", font=("Times", 14), fg="blue", wraplength=480, bg="#f0f0f0")
command_label.pack(pady=10)

response_label = tk.Label(root, text="", font=("Times", 14), wraplength=480, bg="#f0f0f0")
response_label.pack(pady=10)

start_button = tk.Button(root, text="🎙 Start Listening", font=("Times", 12), command=threaded_run)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="❌ Exit", font=("Times", 12), command=root.destroy)
stop_button.pack(pady=5)

root.mainloop()