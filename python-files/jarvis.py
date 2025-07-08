
import pyttsx3
import speech_recognition as sr
import os
import datetime
import time
import webbrowser
import openai
import json

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Log file
log_file = "jarvis_log.txt"

# Speak Function
def speak(text):
    with open(log_file, "a") as log:
        log.write(f"JARVIS: {text}\n")
    engine.say(text)
    engine.runAndWait()

# Listen Function
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for 'Hey Jarvis'...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            with open(log_file, "a") as log:
                log.write(f"User: {command}\n")
            return command
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

# OpenAI setup
def get_openai_answer(question):
    try:
        openai.api_key = "YOUR_OPENAI_API_KEY"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return response['choices'][0]['message']['content'].strip()
    except:
        return "Sorry, I couldn't connect to OpenAI."

# Main logic
def run_jarvis():
    while True:
        command = listen_command()
        if "hey jarvis" in command:
            speak("Yes, I'm here. How can I help you?")
            command = listen_command()

            if "shutdown" in command:
                speak("Shutting down the system.")
                os.system("shutdown /s /t 1")

            elif "restart" in command:
                speak("Restarting the system.")
                os.system("shutdown /r /t 1")

            elif "what time" in command:
                time_now = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {time_now}")

            elif "what date" in command:
                date_now = datetime.datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today is {date_now}")

            elif "search" in command or "what is" in command or "who is" in command:
                answer = get_openai_answer(command)
                speak(answer)

            elif "exit" in command or "stop" in command:
                speak("Goodbye!")
                break

            else:
                speak("I'm not sure how to help with that.")
