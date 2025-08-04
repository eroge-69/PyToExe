import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests

# Text to Speech Engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Default voice
engine.setProperty('rate', 150)

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def greet():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("सुप्रभात साहिल।")
    elif 12 <= hour < 18:
        speak("नमस्कार साहिल।")
    else:
        speak("शुभ संध्या साहिल।")
    speak("मैं हमेशा आपकी सेवा में हूं। कृपया आदेश दें।")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ सुन रहा हूँ...")
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=5)
    try:
        print("🔎 पहचान रहा हूँ...")
        query = r.recognize_google(audio, language='hi-IN')
        print(f"आपने कहा: {query}")
    except Exception as e:
        print("⚠️ फिर से बोलिए...")
        return ""
    return query.lower()

def execute_command(query):
    if 'गाना' in query or 'song' in query:
        speak("आपका पसंदीदा गाना चला रहा हूं।")
        webbrowser.open("https://www.youtube.com")

    elif 'समय' in query or 'time' in query:
        time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"साहिल, अभी समय है {time}")

    elif 'गूगल' in query or 'open google' in query:
        speak("गूगल खोल रहा हूं।")
        webbrowser.open("https://www.google.com")

    elif 'मौसम' in query or 'weather' in query:
        speak("मौसम की जानकारी ला रहा हूं।")
        webbrowser.open("https://www.google.com/search?q=weather+in+bilaspur")

    elif 'बंद' in query or 'exit' in query or 'close' in query:
        speak("ठीक है साहिल, मैं बंद हो रहा हूं।")
        exit()

    else:
        speak("माफ कीजिए, ये आदेश मेरी समझ में नहीं आया।")

# 🔽 Start
if __name__ == "__main__":
    greet()
    while True:
        query = take_command()
        if query:
            execute_command(query)
