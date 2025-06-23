import pyttsx3
import speech_recognition as sr
import webview  # PyWebView to show GUI

engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

def main():
    speak("RaOne is now active.")
    webview.create_window("RaOne Interface", "raone_gui/index.html")
    webview.start()

if __name__ == "__main__":
    main()