import speech_recognition as sr
import webbrowser
from gtts import gTTS
import requests
import time
import os
from playsound import playsound
import google.generativeai as genai

recognizer = sr.Recognizer()
newsapi = "bcf1569036b047ea86ac4e79ba435577"

def speak(text):
    print("Speaking:", text)
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound("response.mp3")
    os.remove("response.mp3")

def aiprocess(command):
    genai.configure(api_key="AIzaSyDG30-XVrbqq_K-SJTVNGOfcMf-Z-Pggww")
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(command)
    return response.text

def processcommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com")
    elif "instagram" in c.lower():
        webbrowser.open("https://www.instagram.com")
    elif "open spotify playlist" in c.lower():
        webbrowser.open("https://open.spotify.com/playlist/7vQB0bLNGv7hU7vkxoIAtv")
    elif "today" in c.lower() and "news" in c.lower(): 
        speak("Getting news...")
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        if r.status_code == 200:
            articles = r.json().get('articles', [])
            for item in articles[:5]:
                print("Title:", item['title'])
                speak(item['title'])
    else:
        speak("finding your answer..., 5 second please...")
        output = aiprocess(c)     
        speak(output)

if __name__ == "__main__":
    speak("Initializing bravo....")
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)
                word = recognizer.recognize_google(audio)
                print("Heard:", word)

            if word.lower() == "bravo":
                speak("yes...")
                print("Bravo active")
                time.sleep(0.5)

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("Listening for command...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)

                print("You said:", command)
                processcommand(command)

        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        
    