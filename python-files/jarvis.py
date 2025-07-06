import sys
import requests
import pytz
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import pyjokes
import pywhatkit

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# API Keys (replace with your own for production)
NEWS_API_KEY = "3c91eb92a3a54ea89417c1c203baea84"
WEATHER_API_KEY = "123abc456def789ghi"
POPULATION_API_KEY = "3c91eb92a3a54ea89417c1c203baea84"

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Data Fetch Functions ---

def get_world_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=3&apiKey={NEWS_API_KEY}"
    resp = requests.get(url).json().get("articles", [])
    return [a["title"] for a in resp]

def get_jk_news():
    url = f"https://newsapi.org/v2/everything?q=Jammu+and+Kashmir&pageSize=3&language=en&apiKey={NEWS_API_KEY}"
    resp = requests.get(url).json().get("articles", [])
    return [a["title"] for a in resp]

def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()
    if data.get("cod") != 200:
        return None, None
    weather_desc = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    return weather_desc, temp

def get_population(country: str):
    url = f"https://api.api-ninjas.com/v1/population?country={country}"
    headers = {"X-Api-Key": POPULATION_API_KEY}
    data = requests.get(url, headers=headers).json()
    return data.get("population")

def get_local_time(tz_name: str):
    try:
        tz = pytz.timezone(tz_name)
        return datetime.datetime.now(tz).strftime('%I:%M %p')
    except Exception:
        return None

def get_gk_summary(topic: str, sentences: int = 2):
    try:
        return wikipedia.summary(topic, sentences=sentences)
    except Exception:
        return None

# --- Voice Recognition Thread ---
class VoiceThread(QThread):
    recognized = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        rec = sr.Recognizer()
        with sr.Microphone() as src:
            self.recognized.emit("Listening...")
            rec.adjust_for_ambient_noise(src)
            audio = rec.listen(src)

        try:
            self.recognized.emit("Recognizing...")
            txt = rec.recognize_google(audio).lower()
            self.recognized.emit(txt)
        except sr.UnknownValueError:
            self.error.emit("Could not understand audio")
        except sr.RequestError:
            self.error.emit("Check your internet connection")

# --- Main GUI & Logic ---    
class JarvisGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.active = False
        self.initUI()
        self.voice_thread = VoiceThread()
        self.voice_thread.recognized.connect(self.process_command)
        self.voice_thread.error.connect(self.handle_error)

    def initUI(self):
        self.setWindowTitle("Jarvis – All-in-One Assistant")
        self.setGeometry(200, 200, 700, 500)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.WindowText, QColor(0, 255, 255))
        self.setPalette(palette)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Jarvis")
        title.setFont(QFont("Orbitron", 36))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 14))
        self.output.setStyleSheet("background-color: #111; color: #00ffff;")
        layout.addWidget(self.output)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setFont(QFont("Orbitron", 14))
        self.activate_btn.setStyleSheet("background-color: #00ffff; color: #000;")
        self.activate_btn.clicked.connect(self.activate_jarvis)
        btn_layout.addWidget(self.activate_btn)

        self.listen_btn = QPushButton("Listen")
        self.listen_btn.setFont(QFont("Orbitron", 14))
        self.listen_btn.setEnabled(False)
        self.listen_btn.setStyleSheet("background-color: #00ffff; color: #000;")
        self.listen_btn.clicked.connect(self.listen_command)
        btn_layout.addWidget(self.listen_btn)

    def write(self, text: str):
        self.output.append(text)

    def activate_jarvis(self):
        if not self.active:
            self.active = True
            msg = "Jarvis activated. How can I help you today?"
            self.write(msg); speak(msg)
            self.listen_btn.setEnabled(True)
            self.activate_btn.setEnabled(False)

    def listen_command(self):
        self.write("Listening for your command...")
        self.voice_thread.start()

    def handle_error(self, err: str):
        self.write(f"Error: {err}")
        speak(err)

    def process_command(self, cmd: str):
        if cmd in ("Listening...", "Recognizing..."):
            self.write(cmd); return

        self.write(f"User said: {cmd}")

        if not self.active:
            self.write("Please activate Jarvis first.")
            return

        # Command logic
        if 'wikipedia' in cmd:
            topic = cmd.replace('wikipedia', '').strip()
            self.search_wikipedia(topic)

        elif cmd.startswith(('what is', 'who is', 'tell me about', 'define')):
            topic = cmd.replace('what is', '').replace('who is','').replace('tell me about','').replace('define','').strip()
            self.answer_gk(topic)

        elif 'general knowledge' in cmd:
            topic = cmd.replace('general knowledge','').strip()
            self.answer_gk(topic)

        elif 'time in' in cmd:
            tz = cmd.replace('time in','').strip()
            self.answer_time_in(tz)

        elif 'time' in cmd:
            now = datetime.datetime.now().strftime('%I:%M %p')
            self.write(now); speak(f"The time is {now}")

        elif 'weather in' in cmd:
            city = cmd.replace('weather in','').strip()
            self.answer_weather(city)

        elif 'population of' in cmd:
            country = cmd.replace('population of','').strip()
            self.answer_population(country)

        elif 'news about jammu and kashmir' in cmd or 'jk news' in cmd:
            self.answer_jk_news()

        elif 'news' in cmd:
            self.answer_news()

        elif 'joke' in cmd:
            joke = pyjokes.get_joke()
            self.write(joke); speak(joke)

        elif 'open youtube' in cmd:
            self.write("Opening YouTube"); speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

        elif 'open google' in cmd:
            self.write("Opening Google"); speak("Opening Google")
            webbrowser.open("https://www.google.com")

        elif 'play' in cmd:
            song = cmd.replace('play','').strip()
            self.write(f"Playing {song}"); speak(f"Playing {song}")
            pywhatkit.playonyt(song)

        elif cmd in ('exit','stop','goodbye','deactivate'):
            self.write("Goodbye!"); speak("Goodbye!"); self.close()

        else:
            self.write("Command not recognized.")
            speak("I didn't understand that. Try again.")

    # --- Handlers ---
    def search_wikipedia(self, topic):
        self.write(f"Searching Wikipedia for '{topic}'...")
        speak("Searching Wikipedia")
        summary = get_gk_summary(topic)
        if summary:
            self.write(summary); speak(summary)
        else:
            self.write("No Wikipedia entry found."); speak("Sorry, I couldn't find that topic.")

    def answer_gk(self, topic):
        if not topic:
            self.write("Please specify the topic for GK.")
            speak("Please say the topic.")
            return
        self.search_wikipedia(topic)

    def answer_time_in(self, tz):
        time = get_local_time(tz)
        if time:
            msg = f"The time in {tz} is {time}."
            self.write(msg); speak(msg)
        else:
            self.write("Couldn't find timezone."); speak("Timezone not recognized.")

    def answer_weather(self, city):
        desc, temp = get_weather(city)
        if desc:
            msg = f"The weather in {city.capitalize()} is {desc}, {temp:.1f} °C."
            self.write(msg); speak(msg)
        else:
            self.write("Could not retrieve weather info."); speak("Sorry, couldn't get weather.")

    def answer_population(self, country):
        pop = get_population(country)
        if pop:
            msg = f"The population of {country.capitalize()} is approximately {pop:,}."
            self.write(msg); speak(msg)
        else:
            self.write("Could not get population data."); speak("Sorry, no data found.")

    def answer_news(self):
        self.write("Fetching news headlines..."); speak("Here are the top headlines:")
        for h in get_world_news():
            self.write(f"- {h}"); speak(h)

    def answer_jk_news(self):
        self.write("Fetching Jammu & Kashmir news..."); speak("Here are the latest JK headlines:")
        for h in get_jk_news():
            self.write(f"- {h}"); speak(h)

# --- Application Launch ---
def main():
    app = QApplication(sys.argv)
    gui = JarvisGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
