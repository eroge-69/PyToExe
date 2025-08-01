import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os

def speak(text, voice_id=None):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Set voice: voices[0] = male, voices[1] = female (may vary by system)
    if voice_id is not None:
        engine.setProperty('voice', voices[voice_id].id)
    else:
        engine.setProperty('voice', voices[0].id)  # Default to male
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        command = recognizer.recognize_google(audio)
        print("You:", command)
        return command.lower()
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I did not catch that.")
        return ""

def run_jarvis():
    # Change voice_id to 1 for female, 0 for male
    voice_id = 0  # 0 = male, 1 = female (may vary by system)
    speak("Hi, I am JARVIS, your next level personal assistant. How can I help you?", voice_id)
    while True:
        command = listen()
        if "time" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {now}", voice_id)
        elif "date" in command:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {today}", voice_id)
        elif "open google" in command:
            speak("Opening Google", voice_id)
            webbrowser.open("https://www.google.com")
        elif "open youtube" in command:
            speak("Opening YouTube", voice_id)
            webbrowser.open("https://www.youtube.com")
        elif "play music" in command:
            speak("Playing music", voice_id)
            # Change the path below to a folder with your music files
            music_folder = "C:\\Users\\Public\\Music"
            songs = os.listdir(music_folder)
            if songs:
                os.startfile(os.path.join(music_folder, songs[0]))
            else:
                speak("No music files found.", voice_id)
        elif "exit" in command or "quit" in command:
            speak("Goodbye!", voice_id)
            break
        elif command:
            speak("Sorry, I didn't understand that.", voice_id)

if __name__ == "__main__":
    run_jarvis()
    input("Press Enter to exit...")
    # List available voices
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for i, v in enumerate(voices):
        print(i, v.name)