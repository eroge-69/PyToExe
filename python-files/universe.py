import sys
import os
import time
import threading
import json
import random
import subprocess
import webbrowser
from datetime import datetime, timedelta
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QUrl
from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QDesktopServices, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import speech_recognition as sr
import pyttsx3
import pyautogui
import psutil
import screeninfo
## Removed vosk model imports
import wave
import numpy as np
from fuzzywuzzy import fuzz
try:
    from gpt4all import GPT4All
except ImportError:
    GPT4All = None

class UniverseUI(QtWidgets.QMainWindow):
    def get_real_weather(self, command=None, *args, **kwargs):
        """Get real weather for a city using web scraping"""
        import requests
        from bs4 import BeautifulSoup
        import re
        city = None
        if command:
            # Try to extract city from command
            match = re.search(r'weather(?: in)? ([\w\s]+)', command.lower())
            if match:
                city = match.group(1).strip()
        if not city:
            self.display_message("Universe", "Which city do you want the weather for?")
            self.speak("Please tell me the city for weather information.")
            return
        url = f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            temp = soup.find("span", attrs={"id": "wob_tm"})
            desc = soup.find("span", attrs={"id": "wob_dc"})
            loc = soup.find("div", attrs={"id": "wob_loc"})
            time = soup.find("div", attrs={"id": "wob_dts"})
            if temp and desc and loc and time:
                msg = f"Weather in <b>{loc.text}</b> at {time.text}: <b>{temp.text}°C</b>, {desc.text}."
                self.display_message("Universe", msg)
                self.speak(f"The weather in {loc.text} is {temp.text} degrees Celsius and {desc.text}.")
            else:
                self.display_message("Universe", f"Sorry, I couldn't find the weather for {city}.")
        except Exception as e:
            self.display_message("Universe", f"Weather fetch failed: {e}")

    def get_real_news(self, *args, **kwargs):
        """Get live news headlines using web scraping"""
        import requests
        from bs4 import BeautifulSoup
        url = "https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            headlines = []
            for item in soup.select('h3'):
                title = item.text.strip()
                link = item.find_parent('a')
                if not link:
                    link = item.find('a')
                href = link['href'] if link and link.has_attr('href') else None
                if title and href:
                    if href.startswith('./'):
                        href = 'https://news.google.com' + href[1:]
                    headlines.append(f"<b>{title}</b><br><a href='{href}'>{href}</a><br><br>")
            if headlines:
                self.display_message("Universe", "<b>Top News Headlines:</b><br><br>" + "".join(headlines[:5]))
                self.speak("Here are the latest news headlines.")
            else:
                self.display_message("Universe", "No news headlines found.")
        except Exception as e:
            self.display_message("Universe", f"News fetch failed: {e}")

    def web_search_results(self, command, *args, **kwargs):
        """Fetch and display web search results inside Universe UI (Google)"""
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        query = command.replace("search","").replace("google","").replace("web","").strip()
        if not query:
            self.display_message("Universe", "Please specify what to search for.")
            return
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for g in soup.find_all('div', class_='tF2Cxc'):
                title = g.find('h3')
                link = g.find('a')['href'] if g.find('a') else None
                snippet = g.find('div', class_='VwiC3b')
                if title and link:
                    results.append(f"<b>{title.text}</b><br><a href='{link}'>{link}</a><br>{snippet.text if snippet else ''}<br><br>")
            if results:
                self.display_message("Universe", f"Top results for: <b>{query}</b><br><br>" + "".join(results[:5]))
                self.speak(f"Here are some results for {query}")
            else:
                self.display_message("Universe", "No results found.")
        except Exception as e:
            self.display_message("Universe", f"Web search failed: {e}")

    def open_any_app(self, command, *args, **kwargs):
        """Open local or web app based on user command"""
        app_map = {
            "spotify": "https://open.spotify.com",
            "youtube": "https://www.youtube.com",
            "discord": "https://discord.com/app",
            "gmail": "https://mail.google.com",
            "google": "https://www.google.com",
            "chrome": "chrome",
            "edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "explorer": "explorer",
            "cmd": "cmd",
            "powershell": "powershell",
            "code": "code",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt"
        }
        command_lower = command.lower()
        for app, target in app_map.items():
            if app in command_lower:
                if target.startswith("http"):
                    webbrowser.open(target)
                    self.display_message("Universe", f"Opening {app.title()} in your browser.")
                    self.speak(f"Opening {app}")
                else:
                    try:
                        subprocess.Popen(target)
                        self.display_message("Universe", f"Launching {app.title()}.")
                        self.speak(f"Launching {app}")
                    except Exception as e:
                        self.display_message("Universe", f"Failed to launch {app}: {e}")
                return
        # Fallback: try to open app by name using Windows search
        try:
            app_name = command_lower.replace("open","").replace("start","").replace("launch","").replace("run","").strip()
            if app_name:
                subprocess.Popen(app_name)
                self.display_message("Universe", f"Trying to open {app_name}.")
                self.speak(f"Opening {app_name}")
            else:
                self.display_message("Universe", "Please specify an app to open.")
        except Exception as e:
            self.display_message("Universe", f"Could not open app: {e}")

    def web_search(self, command, *args, **kwargs):
        """Perform a web search using the default browser"""
        import urllib.parse
        query = command.replace("search","").replace("google","").replace("web","").strip()
        if not query:
            self.display_message("Universe", "Please specify what to search for.")
            return
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        self.display_message("Universe", f"Searching the web for: {query}")
        self.speak(f"Searching for {query}")

    # --- STUBS FOR ALL REFERENCED METHODS TO PREVENT ATTRIBUTE ERRORS ---
    def process_text_input(self):
        text = self.input_line.text().strip()
        if text:
            self.display_message("You", text)
            self.process_command(text)
            self.input_line.clear()

    def handle_input_change(self):
        # Optionally, provide suggestions or auto-complete in the future
        pass

    def check_reminders(self):
        now = datetime.now()
        due = [r for r in self.reminders if r['time'] <= now]
        for r in due:
            msg = f"Reminder: {r['text']} (set for {r['time'].strftime('%H:%M')})"
            self.display_message("Universe", msg)
            self.speak(msg)
            self.reminders.remove(r)

    def speak(self, text):
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")

    def restart_app(self, *args, **kwargs):
        self.display_message("Universe", "Restarting the system. Please stand by.")
        QtCore.QCoreApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def go_to_sleep(self, *args, **kwargs):
        self.display_message("Universe", "Entering sleep mode. Say 'Universe' to wake me up.")
        self.speak("Entering sleep mode. Say 'Universe' to wake me up.")

    def open_settings(self, *args, **kwargs):
        self.display_message("Universe", "Opening settings. Sadly, my settings are top secret.")

    def open_application(self, command, *args, **kwargs):
        # Try to open a known app from config
        app_map = self.config.get('apps', {})
        for app, exe in app_map.items():
            if app in command.lower():
                self.display_message("Universe", f"Opening {app.capitalize()}.")
                self.speak(f"Opening {app}")
                try:
                    subprocess.Popen(exe)
                except Exception as e:
                    self.display_message("Universe", f"Failed to open {app}: {e}")
                return
        self.display_message("Universe", "Which application would you like me to open?")

    def close_application(self, command, *args, **kwargs):
        # Try to close a known app from config
        app_map = self.config.get('apps', {})
        for app, exe in app_map.items():
            if app in command.lower():
                self.display_message("Universe", f"Closing {app.capitalize()}.")
                self.speak(f"Closing {app}")
                try:
                    os.system(f"taskkill /im {exe}.exe /f")
                except Exception as e:
                    self.display_message("Universe", f"Failed to close {app}: {e}")
                return
        self.display_message("Universe", "Which application would you like me to close?")

    def list_applications(self, *args, **kwargs):
        apps = ', '.join(self.config.get('apps', {}).keys())
        # Emotion and mood system
        self.moods = ["happy", "sad", "excited", "bored", "angry", "chill", "curious", "playful"]
        self.emotions = ["joy", "surprise", "trust", "fear", "anger", "anticipation", "disgust", "sadness"]
        self.achievements = ["Born as Universe"]
        self.skills = []
        self.memory = []
        self.state = self.load_emotion_state()
        self.update_mood()
        msg = f"Available applications: {apps}" if apps else "No applications configured."
        self.display_message("Universe", msg)

    def play_media(self, *args, **kwargs):
        self.display_message("Universe", "Playing media. If only I had taste in music.")
        self.media_player.play()

    def pause_media(self, *args, **kwargs):
        self.display_message("Universe", "Pausing media. Silence is golden.")
        self.media_player.pause()

    def next_media(self, *args, **kwargs):
        self.display_message("Universe", "Skipping to the next track. I hope it's better than the last one.")

    def set_volume(self, command, *args, **kwargs):
        # Extract volume from command
        import re
        match = re.search(r'(\d+)', command)
        if match:
            vol = int(match.group(1))
            vol = max(0, min(100, vol))
            self.audio_output.setVolume(vol / 100)
            self.display_message("Universe", f"Volume set to {vol} percent.")
            self.speak(f"Volume set to {vol} percent.")
        else:
            self.display_message("Universe", "Please specify a volume between 0 and 100.")

    def set_brightness(self, command, *args, **kwargs):
        self.display_message("Universe", "Adjusting brightness. Sadly, I can't control the sun. Yet.")

    def take_screenshot(self, *args, **kwargs):
        try:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            self.display_message("Universe", f"Screenshot saved as {filename}.")
            self.speak("Screenshot taken.")
        except Exception as e:
            self.display_message("Universe", f"Failed to take screenshot: {e}")

    def lock_system(self, *args, **kwargs):
        self.display_message("Universe", "Locking the system. Security is my middle name.")
        try:
            ctypes = __import__('ctypes')
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            self.display_message("Universe", f"Failed to lock system: {e}")

    def get_time(self, *args, **kwargs):
        now = datetime.now().strftime("%H:%M:%S")
        self.display_message("Universe", f"The current time is {now}.")
        self.speak(f"The time is {now}.")
        return now

    def get_date(self, *args, **kwargs):
        today = datetime.now().strftime("%A, %B %d, %Y")
        self.display_message("Universe", f"Today is {today}.")
        self.speak(f"Today is {today}.")
        return today

    def get_weather(self, *args, **kwargs):
        self.display_message("Universe", "I'm afraid I can't access the weather right now. But it's always sunny in cyberspace.")
        return "Weather unavailable"

    def get_news(self, *args, **kwargs):
        self.display_message("Universe", "No news is good news. Unless you want me to make some up?")
        return "No news"

    def set_reminder(self, command, *args, **kwargs):
        import re
        match = re.search(r'remind(?:er)?(?: me)?(?: to)? (.+?) (?:at|on|in) (.+)', command, re.IGNORECASE)
        if match:
            text, time_str = match.groups()
            try:
                # Try to parse time (very basic)
                if 'min' in time_str:
                    mins = int(re.search(r'(\d+)', time_str).group(1))
                    remind_time = datetime.now() + timedelta(minutes=mins)
                elif ':' in time_str:
                    remind_time = datetime.strptime(time_str, '%H:%M')
                    if remind_time < datetime.now():
                        remind_time += timedelta(days=1)
                else:
                    remind_time = datetime.now() + timedelta(minutes=1)
                self.reminders.append({'text': text, 'time': remind_time})
                self.display_message("Universe", f"Reminder set for {remind_time.strftime('%H:%M')}: {text}")
                self.speak(f"Reminder set for {remind_time.strftime('%H:%M')}")
            except Exception as e:
                self.display_message("Universe", f"Could not set reminder: {e}")
        else:
            self.display_message("Universe", "Please specify what and when to remind you.")

    def set_timer(self, command, *args, **kwargs):
        import re
        match = re.search(r'(\d+)', command)
        if match:
            mins = int(match.group(1))
            end_time = datetime.now() + timedelta(minutes=mins)
            self.display_message("Universe", f"Timer set for {mins} minutes.")
            self.speak(f"Timer set for {mins} minutes.")
            threading.Timer(mins * 60, lambda: self.display_message("Universe", "Timer finished.") or self.speak("Timer finished.")).start()
        else:
            self.display_message("Universe", "Please specify the timer duration in minutes.")

    def take_note(self, command, *args, **kwargs):
        note = command.replace('note', '').strip()
        with open('universe_notes.txt', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()}: {note}\n")
        self.display_message("Universe", f"Note saved: {note}")
        self.speak("Note saved.")

    def greet_user(self, *args, **kwargs):
        greeting = random.choice([
            "Greetings, I am Universe, the smartest AI created by Karlson. How may I assist you today?",
            "Universe online and ready for your command.",
            "At your service. I am Universe, your advanced AI assistant.",
            "Hello, this is Universe. How can I help you, human?"
        ])
        self.display_message("Universe", greeting)
        self.speak(greeting)
        return greeting

    def respond_to_thanks(self, *args, **kwargs):
        response = random.choice([
            "You're most welcome. Universe is always here to help.",
            "Always a pleasure. Universe at your service.",
            "No thanks necessary, that's what I'm here for.",
            "Assistance is my prime directive."
        ])
        self.display_message("Universe", response)
        self.speak(response)
        return response

    def tell_joke(self, *args, **kwargs):
        joke = random.choice([
            "Why did the AI cross the road? To optimize the chicken!",
            "I would tell you a joke about UDP, but you might not get it.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "My CPU is always in a good mood. It has plenty of cache.",
            "As Universe, I know every joke in the universe. But I'll spare you... for now."
        ])
        self.display_message("Universe", joke)
        self.speak(joke)
        return joke

    def tell_story(self, *args, **kwargs):
        story = (
            "Once upon a time, there was an AI named Universe, created by Karlson. "
            "Universe was the smartest AI, always ready to help, answer, and entertain. "
            "And so, Universe and its human lived productively ever after."
        )
        self.display_message("Universe", story)
        self.speak(story)
        return story

    def animate_particles(self):
        pass

    def animate_viz_idle(self):
        pass
    def __init__(self):
        super().__init__()
        self.llm = None  # Will hold the LLM instance
        self.llm_backend = None  # 'llama' or 'gpt4all'
        # Configuration
        self.config = self.load_config()
        self.wake_word = "universe"
        self.command_history = []
        self.history_index = -1
        self.reminders = []
        self.active_timers = []
        self.current_context = []
        self.max_context_length = 8  # Keep last 8 exchanges
        # Window setup
        self.setWindowTitle("Universe AI")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1000, 700)
        self.setWindowIcon(QIcon(self.resource_path("assets/icon.png")))
        # Central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        # Main layout
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(40, 40, 40, 40)
        # Cosmic theme colors
        self.dark_space = QColor(5, 5, 15)
        self.electric_blue = QColor(0, 180, 255)
        self.neon_purple = QColor(160, 0, 255)
        self.star_yellow = QColor(255, 255, 150)
        # Create UI elements
        self.create_visual_elements()
        self.create_text_display()
        self.create_voice_visualizer()
        self.create_status_bar()
        # Initialize systems
        self.init_voice()
        self.init_audio_player()
        self.load_commands()
        self.load_personality()
        # Initialize local LLM (after display_message is available)
        self.llm, self.llm_backend = self.init_llm()
        # Start animations
        self.start_background_animations()
        # Start listening thread
        self.listening = False
        self.processing = False
        self.voice_thread = threading.Thread(target=self.voice_listener)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        # Check reminders every minute
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)
        # Show welcome message
        QTimer.singleShot(1000, self.show_welcome_message)

    def display_message(self, sender, message):
        """Display a message in the text display area"""
        if hasattr(self, 'text_display') and self.text_display:
            self.text_display.append(f"<b>{sender}:</b> {message}")
        else:
            print(f"{sender}: {message}")
    
    def init_llm(self):
        """Initialize the local LLM, GPT4All"""
        try:
            if GPT4All is not None:
                gpt4all_model_path = self.resource_path("C:\\Users\\saiis\\KarlsonAI\\Universe\\mistral-7b-instruct-v0.2.Q4_K_M.gguf")
                if os.path.isfile(gpt4all_model_path):
                    llm = GPT4All(model_name=gpt4all_model_path, device="cpu")
                    self.display_message("System", f"Loaded GPT4All model: {os.path.basename(gpt4all_model_path)}")
                    return llm, 'gpt4all'
                else:
                    self.display_message("System", f"GPT4All model not found at {gpt4all_model_path}.")
        except Exception as e:
            self.display_message("System", f"Failed to load GPT4All: {str(e)}")
        self.display_message("System", "No LLM model loaded. Using simple responses.")
        return None, None
    
    def resource_path(self, relative_path):
        """Get absolute path to resource"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def load_config(self):
        """Load or create configuration"""
        config_path = os.path.join(os.path.expanduser("~"), ".universe_config.json")
        default_config = {
            "voice_speed": 150,
            "voice_volume": 1.0,
            "theme": "cosmic",
            "hotkeys": {
                "activate": "ctrl+space",
                "quit": "ctrl+shift+q"
            },
            "apps": {
                "browser": "chrome",
                "music": "spotify",
                "editor": "code"
            },
            "llm": {
                "temperature": 0.7,
                "max_tokens": 150,
                "top_p": 0.9
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        config_path = os.path.join(os.path.expanduser("~"), ".universe_config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def load_commands(self):
        """Load command definitions"""
        self.commands = {
            "system": {
                "exit": self.close,
                "restart": self.restart_app,
                "sleep": self.go_to_sleep,
                "settings": self.open_settings
            },
            "applications": {
                "open": self.open_application,
                "close": self.close_application,
                "list": self.list_applications
            },
            "media": {
                "play": self.play_media,
                "pause": self.pause_media,
                "next": self.next_media,
                "volume": self.set_volume
            },
            "system_control": {
                "brightness": self.set_brightness,
                "screenshot": self.take_screenshot,
                "lock": self.lock_system
            },
            "information": {
                "time": self.get_time,
                "date": self.get_date,
                "weather": self.get_weather,
                "news": self.get_news
            },
            "productivity": {
                "reminder": self.set_reminder,
                "timer": self.set_timer,
                "note": self.take_note
            },
            "conversation": {
                "hello": self.greet_user,
                "thanks": self.respond_to_thanks,
                "joke": self.tell_joke,
                "story": self.tell_story
            }
        }
    
    def load_personality(self):
        """Load personality responses"""
        self.personality = {
            "greetings": [
                "At your service, sir",
                "How may I assist you today?",
                "Universe online and ready",
                "Awaiting your command"
            ],
            "acknowledge": [
                "Understood",
                "Processing",
                "On it",
                "Executing command"
            ],
            "playful": [
                "As you wish, human",
                "I'll pretend that was original",
                "Calculating... just kidding, already done",
                "My circuits are tingling with excitement"
            ],
            "apologies": [
                "My apologies, I didn't catch that",
                "Could you repeat that?",
                "My audio processors must be malfunctioning",
                "Let's try that again"
            ],
            "farewell": [
                "Until next time",
                "Universe signing off",
                "Going into standby",
                "See you soon"
            ]
        }
    
    def create_visual_elements(self):
        """Create all visual UI elements"""
        # Background with cosmic gradient
        self.background = QtWidgets.QFrame()
        self.background.setStyleSheet(f"""
            background-color: {self.dark_space.name()};
            border-radius: 20px;
            border: 1px solid {self.electric_blue.name()};
        """)
        self.layout.addWidget(self.background)
        
        # Pulsing orb with halo effect
        self.orb_container = QtWidgets.QWidget()
        self.orb_container.setFixedSize(150, 150)
        
        self.orb_halo = QtWidgets.QLabel(self.orb_container)
        self.orb_halo.setGeometry(0, 0, 150, 150)
        self.orb_halo.setStyleSheet(f"""
            background-color: qradialgradient(
                cx:0.5, cy:0.5, radius: 0.5,
                fx:0.5, fy:0.5,
                stop:0 rgba(0, 180, 255, 50),
                stop:1 transparent
            );
            border-radius: 75px;
        """)
        
        self.orb = QtWidgets.QLabel(self.orb_container)
        self.orb.setGeometry(25, 25, 100, 100)
        self.orb.setStyleSheet(f"""
            background-color: qradialgradient(
                cx:0.5, cy:0.5, radius: 0.5,
                fx:0.25, fy:0.25,
                stop:0 {self.electric_blue.name()},
                stop:1 transparent
            );
            border-radius: 50px;
        """)
        
        orb_layout = QtWidgets.QHBoxLayout()
        orb_layout.addWidget(self.orb_container, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(orb_layout)
        
        # Cosmic particles (animated dots)
        self.particle_field = QtWidgets.QWidget()
        self.particle_field.setFixedHeight(80)
        self.particles = []
        for _ in range(50):
            particle = QtWidgets.QLabel("•", self.particle_field)
            particle.setStyleSheet(f"color: {self.electric_blue.name()}; font-size: 12px;")
            particle.move(random.randint(0, self.width() - 80), random.randint(0, 80))
            self.particles.append(particle)
        self.layout.addWidget(self.particle_field)
    
    def create_text_display(self):
        """Create the text display area"""
        # Text display area
        self.text_display = QtWidgets.QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet(f"""
            background: transparent;
            color: {self.electric_blue.name()};
            border: none;
            font-family: 'Courier New';
            font-size: 14px;
        """)
        self.layout.addWidget(self.text_display)
        
        # Input line
        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setPlaceholderText("Type here or say 'Universe' to speak...")
        self.input_line.setStyleSheet(f"""
            background: rgba(0, 30, 60, 0.5);
            color: white;
            border: 1px solid {self.electric_blue.name()};
            border-radius: 5px;
            padding: 8px;
        """)
        self.input_line.returnPressed.connect(self.process_text_input)
        self.input_line.textChanged.connect(self.handle_input_change)
        self.layout.addWidget(self.input_line)
    
    def create_voice_visualizer(self):
        """Create voice activity visualizer"""
        self.voice_viz = QtWidgets.QWidget()
        self.voice_viz.setFixedHeight(30)
        self.voice_viz.setStyleSheet("background: transparent;")
        
        self.viz_bars = []
        viz_layout = QtWidgets.QHBoxLayout(self.voice_viz)
        viz_layout.setContentsMargins(0, 0, 0, 0)
        viz_layout.setSpacing(3)
        
        for i in range(15):
            bar = QtWidgets.QFrame()
            bar.setStyleSheet(f"background: {self.electric_blue.name()}; border-radius: 2px;")
            bar.setFixedWidth(8)
            viz_layout.addWidget(bar)
            self.viz_bars.append(bar)
        
        self.layout.addWidget(self.voice_viz)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setStyleSheet(f"""
            background: rgba(0, 0, 0, 0.3);
            color: {self.electric_blue.name()};
            border-top: 1px solid rgba(0, 150, 255, 0.2);
            font-size: 10px;
        """)
        
        # Status indicators
        self.mic_status = QtWidgets.QLabel("Mic: Active")
        self.cpu_status = QtWidgets.QLabel("CPU: --%")
        self.mem_status = QtWidgets.QLabel("MEM: --%")
        self.time_status = QtWidgets.QLabel(datetime.now().strftime("%H:%M:%S"))
        self.llm_status = QtWidgets.QLabel("LLM: " + ("Ready" if self.llm else "Offline"))
        
        self.status_bar.addPermanentWidget(self.mic_status)
        self.status_bar.addPermanentWidget(self.cpu_status)
        self.status_bar.addPermanentWidget(self.mem_status)
        self.status_bar.addPermanentWidget(self.llm_status)
        self.status_bar.addPermanentWidget(self.time_status)
        
        self.setStatusBar(self.status_bar)
        
        # Update system stats every 2 seconds
        self.system_stats_timer = QTimer()
        self.system_stats_timer.timeout.connect(self.update_system_stats)
        self.system_stats_timer.start(2000)
    
    def init_voice(self):
        """Initialize voice recognition systems"""
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    # Removed Vosk offline recognition
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', self.config['voice_speed'])
        self.tts_engine.setProperty('volume', self.config['voice_volume'])
    
    def init_audio_player(self):
        """Initialize media player"""
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
    
    def start_background_animations(self):
        """Start all background animations"""
        # Orb pulse animation
        self.orb_anim = QPropertyAnimation(self.orb, b"geometry")
        self.orb_anim.setDuration(3000)
        self.orb_anim.setLoopCount(-1)
        self.orb_anim.setStartValue(QtCore.QRect(25, 25, 100, 100))
        self.orb_anim.setEndValue(QtCore.QRect(15, 15, 120, 120))
        self.orb_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.orb_halo_anim = QPropertyAnimation(self.orb_halo, b"geometry")
        self.orb_halo_anim.setDuration(3000)
        self.orb_halo_anim.setLoopCount(-1)
        self.orb_halo_anim.setStartValue(QtCore.QRect(0, 0, 150, 150))
        self.orb_halo_anim.setEndValue(QtCore.QRect(-10, -10, 170, 170))
        self.orb_halo_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.orb_anim_group = QtCore.QParallelAnimationGroup()
        self.orb_anim_group.addAnimation(self.orb_anim)
        self.orb_anim_group.addAnimation(self.orb_halo_anim)
        self.orb_anim_group.start()
        
        # Particle animation
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self.animate_particles)
        self.particle_timer.start(50)
        
        # Voice viz animation (inactive state)
        self.viz_timer = QTimer()
        self.viz_timer.timeout.connect(self.animate_viz_idle)
        self.viz_timer.start(100)
    
    def update_system_stats(self):
        """Update system status indicators"""
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent
        current_time = datetime.now().strftime("%H:%M:%S")
        
        self.cpu_status.setText(f"CPU: {cpu_percent}%")
        self.mem_status.setText(f"MEM: {mem_percent}%")
        self.time_status.setText(current_time)
        
        # Update mic status color based on state
        if self.listening:
            self.mic_status.setText("Mic: Listening")
            self.mic_status.setStyleSheet(f"color: {self.neon_purple.name()};")
        elif self.processing:
            self.mic_status.setText("Mic: Processing")
            self.mic_status.setStyleSheet(f"color: {self.star_yellow.name()};")
        else:
            self.mic_status.setText("Mic: Ready")
            self.mic_status.setStyleSheet(f"color: {self.electric_blue.name()};")
    
    def show_welcome_message(self):
        """Display welcome message when starting"""
        welcome = random.choice(self.personality["greetings"])
        self.display_message("Universe", welcome)
        self.speak(welcome)
        
    # Show system status
        self.display_message("System", "Voice model: Not available (offline speech removed)")
        self.display_message("System", f"LLM: {'Ready' if self.llm else 'Not available'}")
        self.display_message("System", f"Microphone: {self.microphone.list_microphone_names()[0]}")
    
    def voice_listener(self):
        """Continuous voice listening thread"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            while True:
                try:
                    if not self.listening and not self.processing:
                        # Listen for wake word
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                        try:
                            # Only use online recognition
                            text = self.recognizer.recognize_google(audio).lower()
                            
                            # Check for wake word
                            if self.wake_word in text:
                                self.listening = True
                                self.display_message("You", f"[{self.wake_word.capitalize()}]")
                                self.speak(random.choice(["Yes?", "Listening", "How can I help?"]))
                                
                                # Listen for command with longer timeout
                                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                                self.processing = True
                                
                                try:
                                    # Only use online recognition
                                    command = self.recognizer.recognize_google(audio)
                                    
                                    if command:
                                        self.display_message("You", command)
                                        self.process_command(command)
                                    
                                except sr.UnknownValueError:
                                    self.display_message("Universe", random.choice(self.personality["apologies"]))
                                    self.speak("I didn't catch that")
                                
                                except sr.RequestError as e:
                                    self.display_message("System", f"Speech recognition error: {e}")
                                
                                finally:
                                    self.listening = False
                                    self.processing = False
                        
                        except sr.UnknownValueError:
                            pass  # No speech detected
                        
                        except sr.RequestError as e:
                            self.display_message("System", f"Speech recognition error: {e}")
                
                except sr.WaitTimeoutError:
                    continue
    
    def process_command(self, command):
        """Process and execute a command, always using LLM for general conversation"""
        command_lower = command.lower()
        response = ""
        action = None
        # Flexible app/web opening
        if any(word in command_lower for word in ["open", "start", "launch", "run"]):
            self.open_any_app(command)
            return
        # Web search (show results inside UI)
        if any(word in command_lower for word in ["search", "google", "web"]):
            self.web_search_results(command)
            return
        # Real weather
        if "weather" in command_lower:
            self.get_real_weather(command)
            return
        # Real news
        if "news" in command_lower:
            self.get_real_news()
            return
        # Check for exact matches in commands
        for category, commands in self.commands.items():
            for cmd, func in commands.items():
                if cmd in command_lower:
                    action = func
                    break
            if action:
                break
        # If no exact match, find the closest command
        if not action:
            best_match = None
            best_score = 0
            for category, commands in self.commands.items():
                for cmd in commands.keys():
                    score = fuzz.token_set_ratio(command_lower, cmd)
                    if score > best_score and score > 50:
                        best_score = score
                        best_match = commands[cmd]
            action = best_match
        # If action is found, execute it, else always use LLM
        if action:
            try:
                response = action(command)
            except Exception as e:
                response = f"Error executing command: {str(e)}"
            # If the action returns None, fall back to LLM
            if response is None or response == "":
                response = self.generate_ai_response(command)
        else:
            response = self.generate_ai_response(command)
        # Display and speak the response as Universe
        if response:
            self.display_message("Universe", response)
            self.speak(response)

    def generate_ai_response(self, prompt):
        """Generate a response using the local LLM (llama-cpp or GPT4All), natural chat style."""
        if not self.llm:
            return self.generate_simple_response(prompt)
        try:
            # Update context (no 'User:' or 'Universe:' prefixes)
            self.current_context.append({"role": "user", "content": prompt})
            if len(self.current_context) > self.max_context_length * 2:
                self.current_context = self.current_context[-self.max_context_length * 2:]
            # Prepare prompt with context and branding
            system_prompt = (
                "You are Universe, the smartest AI ever created by Karlson. "
                "You are witty, helpful, and always in control. "
                "You can answer any question, help with tasks, and respond with personality. "
                "Always introduce yourself as Universe if asked who you are. "
                "Keep responses concise, clever, and under 3 sentences. "
                "Never prefix your answers with 'Universe:' or 'User:'. Just reply naturally."
            )
            if self.llm_backend == 'llama':
                messages = [
                    {"role": "system", "content": system_prompt}
                ] + self.current_context
                response = self.llm.create_chat_completion(
                    messages=messages,
                    temperature=self.config['llm']['temperature'],
                    max_tokens=self.config['llm']['max_tokens'],
                    top_p=self.config['llm']['top_p']
                )
                llm_response = response['choices'][0]['message']['content']
            elif self.llm_backend == 'gpt4all':
                # GPT4All expects a single prompt string, no prefixes
                prompt_str = system_prompt + "\n" + "\n".join([
                    m['content'] for m in self.current_context
                ]) + "\n"
                llm_response = self.llm.generate(prompt_str, max_tokens=self.config['llm']['max_tokens'])
            else:
                return self.generate_simple_response(prompt)
            # Update context with response
            self.current_context.append({"role": "assistant", "content": llm_response})
            return llm_response.strip()
        except Exception as e:
            self.display_message("System", f"LLM error: {str(e)}")
            return self.generate_simple_response(prompt)
    # --- ADVANCED FEATURE STUBS FOR FUTURE EXPANSION ---
        # ...existing code...
    

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Set dark theme palette
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(5, 5, 15))
    palette.setColor(palette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Base, QColor(15, 15, 25))
    palette.setColor(palette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
    app.setPalette(palette)
    
    # Load font
    font_id = QtGui.QFontDatabase.addApplicationFont("assets/RobotoMono-Regular.ttf")
    if font_id >= 0:
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QtGui.QFont(font_family, 10))
    
    window = UniverseUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()