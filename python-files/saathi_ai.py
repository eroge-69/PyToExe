
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print("Saathi AI:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I could not understand.")
        except sr.RequestError:
            speak("Sorry, there seems to be a problem with the service.")
    return ""

def main():
    speak("Welcome Sadique Sir. Saathi AI is ready.")
    while True:
        command = listen()
        if "exit" in command or "bye" in command:
            speak("Goodbye!")
            break
        elif "hello" in command:
            speak("Hello, how can I assist you?")
        elif "your name" in command:
            speak("I am Saathi AI, your personal assistant.")
        else:
            speak("I am still learning. Please try another command.")

if __name__ == "__main__":
    main()
