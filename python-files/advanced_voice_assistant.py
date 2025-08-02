import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import pyautogui
import os
import webbrowser
import requests

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""

def run_command(command):
    if 'play' in command:
        song = command.replace('play', '')
        speak(f'Playing {song}')
        pywhatkit.playonyt(song)
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        speak(f'Current time is {time}')
    elif 'who is' in command:
        person = command.replace('who is', '')
        info = wikipedia.summary(person, sentences=2)
        speak(info)
    elif 'joke' in command:
        speak(pyjokes.get_joke())
    elif 'screenshot' in command:
        pyautogui.screenshot('screenshot.png')
        speak('Screenshot taken.')
    elif 'open notepad' in command:
        os.system('notepad.exe')
    elif 'open browser' in command:
        webbrowser.open('https://www.google.com')
    elif 'shutdown' in command:
        speak('Shutting down the system.')
        os.system('shutdown /s /t 1')
    elif 'restart' in command:
        speak('Restarting the system.')
        os.system('shutdown /r /t 1')
    elif 'weather' in command:
        speak('Please tell me the city name.')
        city = listen()
        if city:
            api_key = '7c584d5564a406318f906eca5b11f69e'  # Replace with your API key
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
            response = requests.get(url)
            data = response.json()
            if data['cod'] == 200:
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                speak(f'The temperature in {city} is {temp}°C with {desc}.')
            else:
                speak('City not found.')
    elif 'exit' in command or 'quit' in command:
        speak('Goodbye!')
        exit()
    else:
        speak('Sorry, I cannot do that yet.')

def main():
    speak('Hello! I am your assistant. How can I help you?')
    while True:
        command = listen()
        if command:
            run_command(command)

if __name__ == '__main__':
    main()
