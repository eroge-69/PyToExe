Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import speech_recognition as sr
... import pyttsx3
... import webbrowser
... import os
... 
... # Initialize the voice engine
... engine = pyttsx3.init()
... engine.setProperty('rate', 150)  # Speed of speech
... engine.setProperty('volume', 1.0)  # Volume 0-1
... 
... # Speak function
... def speak(text):
...     engine.say(text)
...     engine.runAndWait()
... 
... # Listen for a command
... def take_command():
...     recognizer = sr.Recognizer()
...     with sr.Microphone() as source:
...         print("Listening...")
...         speak("I'm listening")
...         audio = recognizer.listen(source)
...     try:
...         print("Recognizing...")
...         command = recognizer.recognize_google(audio)
...         command = command.lower()
...         print(f"You said: {command}")
...     except sr.UnknownValueError:
...         speak("Sorry, I did not catch that.")
...         return ""
...     except sr.RequestError:
...         speak("Sorry, my speech service is down.")
...         return ""
...     return command
... 
... # Open apps or websites
... def run_jarvis():
...     while True:
...         command = take_command()
... 
...         if "open notepad" in command:
...             speak("Opening Notepad")
...             os.system("notepad")
... 
...         elif "open chrome" in command:
...             speak("Opening Google Chrome")
...             os.system("start chrome")
... 
        elif "open youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

        elif "open google" in command:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")

        elif "stop" in command or "exit" in command:
            speak("Goodbye!")
            break

        else:
            speak("I didn't understand that command.")

if __name__ == "__main__":
    speak("Hello, I am your assistant. How can I help you?")
    run_jarvis()
