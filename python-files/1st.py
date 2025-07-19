import speech_recognition as sr
import pyttsx3
import datetime
import pywhatkit

listener = sr.Recognizer()
alexa =pyttsx3.init()
voices =alexa.getProperty('voices')
alexa.setProperty('voice', voices[1].id)

def talk(text):
    alexa.say(text)
    alexa.runAndWait()


def take_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source)
            command =listener.recognize_google(voice)
            command = command.lower()
            if 'alexa' in command:
                command = command.replace('alexa','')

    except:
        pass
    return command

def run_alxa():
    command = take_command()
    if 'time' in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        print(time)
        talk('time is'+time)
    elif 'play' in command:
        song = command.replace('play','')
        talk('playing ' +song)
        pywhatkit.playonyt(song)

while True:
    run_alxa()