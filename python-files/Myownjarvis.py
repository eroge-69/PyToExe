# ---------- Standard Library ----------
import os
import random
import time
import webbrowser
import re
from datetime import datetime
import subprocess
import ctypes
import threading

# ---------- Third-Party Libraries ----------
import pyttsx3
import speech_recognition as sr
import wikipedia
import pyautogui
import keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
import speedtest
import psutil
import pywhatkit
import tkinter as tk
from tkinter import ttk, scrolledtext, PhotoImage, messagebox
from PIL import Image, ImageTk

# ---------- Constants ----------
MOVIE_FOLDER = r"C:\Users\program\Videos\Captures"

# ---------- Initialize ----------
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Faster speech rate
engine.setProperty('volume', 1.0)  # Max volume
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ---------- Global Variables ----------
listening = False
recognizer = sr.Recognizer()

# ---------- Speech Functions ----------
def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()
    update_gui_text(f"Jarvis: {text}")

def take_command():
    global listening
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Quick ambient calibration
        update_gui_text("Listening...")
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)
        except sr.WaitTimeoutError:
            return ""
    try:
        command = recognizer.recognize_google(audio, language='en-US')
        update_gui_text(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Didn't catch that bro, tell me clearly.")
    except sr.RequestError:
        speak("Speech service is unavailable.")
    return ""

def toggle_listening():
    global listening
    if listening:
        listening = False
        listen_button.config(text="Start Listening", bg="#4CAF50")
        update_gui_text("Microphone stopped")
    else:
        listening = True
        listen_button.config(text="Stop Listening", bg="#f44336")
        update_gui_text("Microphone started - Say 'Hello Jarvis'")
        threading.Thread(target=continuous_listening, daemon=True).start()

def continuous_listening():
    global listening
    while listening:
        command = take_command()
        if command:
            process_command(command)
        time.sleep(1)

# ---------- GUI Update Functions ----------
def update_gui_text(message):
    console.config(state=tk.NORMAL)
    console.insert(tk.END, message + "\n")
    console.config(state=tk.DISABLED)
    console.see(tk.END)

def send_text():
    text_to_send = text_entry.get()
    if text_to_send:
        update_gui_text(f"You typed: {text_to_send}")
        text_entry.delete(0, tk.END)
        process_command(text_to_send)

# ---------- Thread Helper ----------
def threaded_command_execution(func, *args):
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()

def wish_user():
    hour = datetime.now().hour
    if hour < 12:
        speak("Good morning bro!")
    elif hour < 15:
        speak("Good afternoon bro!")
    elif hour < 20:
        speak("Good evening bro!")
    else:
        speak("Good night bro!")
    speak("I am Jarvis. How can I help you today bro, please tell?")
    
def extract_wait_time(command):
    pattern = r'(\d+)\s*(second|seconds|minute|minutes)'
    match = re.search(pattern, command)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if "minute" in unit:
            return value * 60
        else:
            return value
    return None
    
def type_text(text):
    speak(f"Typing: {text}")
    pyautogui.write(text, interval=0.05)  # Types the text
    pyautogui.press('enter')             # Presses Enter
    
def calculate_expression(text):
    text = text.lower()
    text = text.replace('plus', '+').replace('minus', '-').replace('times', '*')\
               .replace('multiplied by', '*').replace('divided by', '/').replace('over', '/')
    expression = ''.join(re.findall(r'[\d\.]+|[\+\-\*\/\(\)]', text))
    try:
        return eval(expression)
    except Exception:
        return None

# ---------- Volume Control ----------
def set_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        level = max(0, min(level, 100))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        speak(f"Volume set to {level} percent")
    except Exception as e:
        speak(f"Could not set volume. {e}")

def increase_volume():
    pyautogui.press("volumeup")
    speak("Volume increased")

def decrease_volume():
    pyautogui.press("volumedown")
    speak("Volume decreased")

def mute_volume():
    pyautogui.press("volumemute")
    speak("Volume muted")

# ---------- Brightness Control ----------
def set_brightness(level):
    try:
        sbc.set_brightness(max(0, min(level, 100)))
        speak(f"Brightness set to {level} percent")
    except Exception as e:
        speak(f"Could not change brightness. {e}")

def increase_brightness():
    try:
        current = sbc.get_brightness(display=0)
        current = current[0] if isinstance(current, list) else current
        sbc.set_brightness(min(current + 10, 100))
        speak("Brightness increased")
    except Exception as e:
        speak(f"Error increasing brightness: {e}")

def decrease_brightness():
    try:
        current = sbc.get_brightness(display=0)
        current = current[0] if isinstance(current, list) else current
        sbc.set_brightness(max(current - 10, 0))
        speak("Brightness decreased")
    except Exception as e:
        speak(f"Error decreasing brightness: {e}")

def battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        speak("Sorry, I couldn't get battery information.")
        return
    status = "charging" if battery.power_plugged else "not charging"
    speak(f"Battery is at {battery.percent}% and is currently {status}.")

# ---------- Media ----------
def play_music(song_name=None, music_folder=r"C:\Users\program\Music\New"):
    supported_formats = (".mp3", ".wav", ".aac", ".flac", ".ogg")

    if not os.path.exists(music_folder):
        speak(f"The music folder {music_folder} does not exist.")
        return

    music_files = [f for f in os.listdir(music_folder) if f.lower().endswith(supported_formats)]

    if not music_files:
        speak("No music files found in the folder.")
        return

    if song_name:
        matched = [f for f in music_files if song_name.lower() in f.lower()]
        if matched:
            song_path = os.path.join(music_folder, matched[0])
            speak(f"Playing {matched[0]}")
            os.startfile(song_path)
        else:
            speak(f"Song named {song_name} not found in the folder.")
    else:
        # Play the first song if no name is given
        speak(f"Playing {music_files[0]}")
        os.startfile(os.path.join(music_folder, music_files[0]))

def play_movie(movie_name=None):
    if not os.path.exists(MOVIE_FOLDER):
        speak("Movie folder not found.")
        return
    movies = [f for f in os.listdir(MOVIE_FOLDER) if f.lower().endswith(('.mp4', '.mkv', '.avi'))]
    if not movies:
        speak("No movies found.")
        return
    movie = next((m for m in movies if movie_name and movie_name.lower() in m.lower()), random.choice(movies))
    speak(f"Playing {movie}")
    os.startfile(os.path.join(MOVIE_FOLDER, movie))

def pause_media():
    keyboard.send('play/pause media')
    speak("Pausing media.")

def resume_media():
    keyboard.send('play/pause media')
    speak("Resuming media.")

# ---------- Folder/File ----------
def open_folder(folder_name):
    user = os.path.expanduser("~")
    folders = {
        "home": user, "gallery": os.path.join(user, "Pictures", "Gallery"),
        "onedrive": os.path.join(user, "OneDrive"), "desktop": os.path.join(user, "Desktop"),
        "downloads": os.path.join(user, "Downloads"), "documents": os.path.join(user, "Documents"),
        "pictures": os.path.join(user, "Pictures"), "music": os.path.join(user, "Music"),
        "videos": os.path.join(user, "Videos"), "this pc": "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}",
        "acer": "D:\\Acer", "data": "D:\\Data"
    }
    path = folders.get(folder_name.lower())
    if path:
        try:
            if folder_name.lower() == "this pc":
                os.system(f'explorer shell:{path}')
            else:
                os.startfile(path)
            speak(f"Opening {folder_name}")
        except Exception as e:
            speak(f"Failed to open {folder_name}. {e}")
    else:
        speak(f"Folder {folder_name} not found.")

def create_folder(folder_name, location_name):
    locations = {
        "home": os.path.expanduser("~"),
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos")
    }
    location = locations.get(location_name.lower())
    if location:
        new_folder = os.path.join(location, folder_name)
        try:
            os.makedirs(new_folder, exist_ok=True)
            speak(f"Folder {folder_name} created in {location_name}")
        except Exception as e:
            speak(f"Error creating folder: {e}")
    else:
        speak("Unknown location.")

# ---------- Apps & Web ----------
def open_app(app_name):
    apps = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    }
    try:
        app = app_name.lower()
        if app in apps and os.path.exists(apps[app]):
            os.startfile(apps[app])
        elif app == "notepad":
            os.startfile("notepad.exe")
        elif app == "whatsapp":
            webbrowser.open("https://web.whatsapp.com")
        elif app == "microsoft store":
            os.system("start ms-windows-store:")
        else:
            open_folder(app)
            return
        speak(f"Opening {app_name}")
    except Exception as e:
        speak(f"Failed to open {app_name}. {e}")

def close_app(app_name):
    processes = {
        "chrome": "chrome.exe", "notepad": "notepad.exe",
        "edge": "msedge.exe", "whatsapp": "chrome.exe"
    }
    exe = processes.get(app_name.lower())
    if exe:
        os.system(f"taskkill /f /im {exe}")
        speak(f"Closing {app_name}")
    else:
        speak("App not supported for closing.")

def close_all_apps():
    for app in ["chrome", "notepad", "edge", "whatsapp"]:
        close_app(app)

def open_youtube():
    webbrowser.open("https://www.youtube.com")
    speak("Opening YouTube")

def close_youtube():
    os.system("taskkill /f /im chrome.exe")
    speak("Closing YouTube")

def open_chatgpt():
    webbrowser.open("https://chat.openai.com")
    speak("Opening ChatGPT")

def search_chatgpt(query):
    open_chatgpt()
    time.sleep(5)
    pyautogui.write(query)
    pyautogui.press('enter')
    speak(f"Searching ChatGPT for {query}")

# ---------- Search ----------
def search_in_chrome(query):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    if os.path.exists(chrome_path):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get('chrome').open(url)
        speak(f"Searching for {query} in Chrome")
    else:
        speak("Chrome not found.")

def search_on_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"Searching YouTube for {query}")

def search_wikipedia(query):
    try:
        speak(f"Searching Wikipedia for {query}")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Too many results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("No Wikipedia page found.")
    except Exception as e:
        speak(f"Error: {e}")

def search_on_edge(query):
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    if os.path.exists(edge_path):
        webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
        webbrowser.get('edge').open(url)
        speak(f"Searching on Microsoft Edge for {query}")
    else:
        speak("Edge not found.")

def search_microsoft_store(query):
    os.system("start ms-windows-store:")
    time.sleep(5)
    pyautogui.write(query)
    pyautogui.press('enter')
    speak("Searching Microsoft Store.")

def search_windows_start(query):
    pyautogui.press('winleft')
    time.sleep(1)
    pyautogui.write(query)
    pyautogui.press('enter')
    speak(f"Searching Start menu for {query}")

# ---------- System ----------
def system_control(command):
    if 'shutdown' in command:
        speak("Shutting down.")
        os.system("shutdown /s /t 1")
    elif 'restart' in command:
        speak("Restarting.")
        os.system("shutdown /r /t 1")
    elif 'sleep' in command:
        speak("Sleeping.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif 'lock' in command:
        speak("Locking screen.")
        os.system("rundll32.exe user32.dll,LockWorkStation")

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = os.path.join(os.path.expanduser("~"), "Pictures", f"screenshot_{timestamp}.png")
        screenshot.save(path)
        speak(f"Screenshot saved as {path}")
    except Exception as e:
        speak(f"Failed to take screenshot. {e}")

def start_or_stop_screen_recording():
    try:
        pyautogui.hotkey('winleft', 'alt', 'r')
        speak("Toggled screen recording.")
    except Exception as e:
        speak(f"Failed to toggle screen recording. {e}")

def scroll_up(amount=500):
    try:
        pyautogui.scroll(amount)
        speak("Scrolling up")
    except Exception as e:
        speak(f"Failed to scroll up. {e}")

def scroll_down(amount=500):
    try:
        pyautogui.scroll(-amount)
        speak("Scrolling down")
    except Exception as e:
        speak(f"Failed to scroll down. {e}")
        
def left_click():
    pyautogui.click()
    speak("Left click performed.")

def right_click():
    pyautogui.click(button='right')
    speak("Right click performed.")

def double_click():
    pyautogui.doubleClick()
    speak("Double click performed.")

def check_internet_speed():
    try:
        speak("Testing your internet speed. Please wait...")
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping
        speak(f"Download: {download:.2f} Mbps, Upload: {upload:.2f} Mbps, Ping: {ping:.0f} ms")
    except Exception as e:
        speak(f"Failed to check internet speed. {e}")

def check_laptop_performance():
    try:
        speak("Checking laptop performance.")
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        speak(f"CPU usage: {cpu}%")
        speak(f"Memory: {mem.percent}%, {mem.used / 1e9:.2f} GB used of {mem.total / 1e9:.2f} GB")
        speak(f"Disk: {disk.percent}%, {disk.used / 1e9:.2f} GB used of {disk.total / 1e9:.2f} GB")
    except Exception as e:
        speak(f"Failed to check performance. {e}")

def toggle_action_center():
    try:
        pyautogui.hotkey('winleft', 'a')
        speak("Toggled Action Center.")
    except Exception as e:
        speak(f"Failed to toggle Action Center. {e}")

def disk_cleanup():
    try:
        speak("Starting disk cleanup...")
        subprocess.run("cleanmgr", shell=True)
        temp = os.getenv('TEMP')
        if temp and os.path.exists(temp):
            for root, dirs, files in os.walk(temp, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except Exception:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except Exception:
                        pass
            speak("Temporary files have been deleted.")
    except Exception as e:
        speak(f"Error during disk cleanup: {e}")

def clear_recycle_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        speak("Recycle bin cleared.")
    except Exception as e:
        speak(f"Error clearing Recycle Bin: {e}")
        
def create_file(file_name, location_name, content=""):
    locations = {
        "home": os.path.expanduser("~"),
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos")
    }
    location = locations.get(location_name.lower())
    if location:
        file_path = os.path.join(location, file_name)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            speak(f"File {file_name} created in {location_name}")
        except Exception as e:
            speak(f"Error creating file: {e}")
    else:
        speak("Unknown location.")
        
def open_file(file_name, location_name):
    locations = {
        "home": os.path.expanduser("~"),
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos")
    }

    location = locations.get(location_name.lower())
    if not location:
        speak("Unknown location.")
        return

    file_path = os.path.join(location, file_name)
    if os.path.exists(file_path):
        try:
            os.startfile(file_path)
            speak(f"Opening {file_name}")
        except Exception as e:
            speak(f"Could not open the file. {e}")
    else:
        speak(f"File {file_name} not found in {location_name}")
        
def run_command_in_run_dialog(cmd):
    pyautogui.hotkey('winleft', 'r')   # Opens Run dialog
    time.sleep(1)
    pyautogui.write(cmd)               # Writes the command
    pyautogui.press('enter')           # Presses Enter
    speak(f"Executed {cmd} via Run.")

def tell_time_and_date():
    now = datetime.now()
    speak(f"The current time is {now.strftime('%I:%M %p')}")
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}")

def process_command(command):
    if not command:
        return

    command = command.lower()

    if "hello jarvis" in command or "jarvis" in command:
        speak("I am here, how can I help you rahagavan bro?")
    elif "how are you" in command:
        speak("I am fine, thank you, you are fine sir.")
    elif "yes jarvis" in command:
        speak("Ok sir.")
    elif "what is your name" in command:
        speak("My name is Jarvis AI assistant, I was created by Raghavan bro.")
    elif "thank you jarvis" in command:
        speak("You're welcome!")
    elif "how is your best friend" in command:
        speak("My best friend is Raghavan bro.")
    elif "which cricket player you like" in command:
        speak("I like Virat Kohli, modern-day icon known for his aggressive style and chasing brilliance.")
    elif "who is father of python" in command:
        speak("Guido van Rossum, known as the father of the Python programming language.")
    elif "which actor you like" in command:
        speak("I like Hollywood: Chris Evans and Kollywood: Thalapathy Vijay.")
    elif "your crush" in command:
        speak("Why are you asking me? You're the one saying it, isn't it your friend? My crush is Alexa and ChatGPT.")
    elif "you dialogue" in command:
        speak("Naan oru thadava sonna, nooru thadava sonna maadiri.")
    elif "which hero like in mcu universe" in command:
        speak("I like Ironman.")
    elif "enjoy mode on" in command:
        speak("Siriya varudhu! Let's start with some Tamil memes.")
        webbrowser.open("https://www.youtube.com/results?search_query=tamil+comedy+memes")
    elif "timepass mode on" in command:
        speak("Timepass loading... Opening cat videos to boost mood!")
        webbrowser.open("https://www.youtube.com/results?search_query=funny+cat+videos")
    elif "talk in tamil" in command:
        responses = [
            "Enna da machi, semma scene-u iruku nee!",
            "Oru tea pota super ah irukum bro!",
            "Nee yosikurathu enna da? Moonji la bulb ah?",
            "Chill bro, life-la over build-up edhukku!"
        ]
        speak(random.choice(responses))
    elif "romantic mode" in command:
        responses = [
            "Your smile is like Wi-Fi — weak, but still connecting.",
            "Love is in the air… or maybe that's just your perfume.",
            "You're like Ctrl + S — I always need you.",
            "If I were a function, you'd be my only argument."
        ]
        speak(random.choice(responses))
    elif "troll my friend" in command:
        insults = [
            "Your friend types like they're sending a love letter to lag!",
            "Their fashion sense is like a browser with too many tabs — all confused!",
            "Even autocorrect gave up on their texts!",
            "Tell your friend their brain is still buffering... Enna Raghavan kadupu ayiduchaa unga friendku."
        ]
        speak(random.choice(insults))
    elif "gopi sudakar comedy video" in command or "parithabangal comedy video" in command or "gopi sudhakar" in command:
        speak("Here's a Parithabangal comedy video for you—enjoy!")
        webbrowser.open("https://www.youtube.com/results?search_query=parithabangal+comedy+video")
    elif "quiz time" in command:
        questions = [
            ("Who is known as Thalapathy?", "vijay"),
            ("Capital of Tamil Nadu?", "chennai"),
            ("Vadivelu famous dialogue 'Aaha oho' comes from which movie?", "winner")
        ]
        q, a = random.choice(questions)
        speak(q)
        answer = take_command().lower()
        if a in answer:
            speak("Correct da thambi! Mass-u!")
        else:
            speak(f"Oops! Right answer is {a}")
    elif "truth or dare" in command:
        options = ["Truth", "Dare"]
        choice = random.choice(options)
        speak(f"I choose: {choice}")
        if choice == "Truth":
            speak("What's your most embarrassing moment?")
        else:
            speak("Do 10 pushups now or sing your favorite song loudly!")
    elif "chill mode on" in command:
        speak("Setting chill vibes with lo-fi beats. Sit back and relax!")
        webbrowser.open("https://www.youtube.com/results?search_query=lofi+beats+to+relax")
    elif "motivate me" in command:
        quotes = [
            "Failures are part of success. Keep going!",
            "One day or day one – you decide!",
            "You're stronger than you think, bro!"
        ]
        speak(random.choice(quotes))
    elif "activate roast mode" in command:
        speak("Desi parent roast mode activated! Vaanga sandhoshama alachu tharen!")
    elif "activate tamil mode" in command:
        speak("Sooda iruku da! Tamil slang mode on! Machan, neenga ready ah?")
    elif "balayya video" in command or "balayaa cring video" in command or "NBK cringe video" in command:
        speak("Balayya oru comedy guy da, bro! Seri, YouTube-ala avana video varudhu.enjoy comdey guy balayaa")
        webbrowser.open("https://www.youtube.com/results?search_query=balayaa+cringe+video")
    elif "open game mode" in command:
        speak("Opening a fun game site now!")
        webbrowser.open("https://poki.com")
    elif "open ai art" in command:
        speak("Opening an AI art generator for your creativity!")
        webbrowser.open("https://www.craiyon.com")
    elif "my mobile number" in command:
        speak("Sir, your mobile is: 8220422008")
    elif "bye jarvis" in command or "stop" in command or "exit" in command:
        speak("Goodbye! Have a nice day bro,Aparam pakalam.")
        root.destroy()

    # Volume controls
    elif "increase volume" in command:
        increase_volume()
    elif "decrease volume" in command:
        decrease_volume()
    elif "mute volume" in command:
        mute_volume()
    elif "set volume to" in command:
        try:
            level = int(command.split("set volume to")[-1].strip().replace('%', ''))
            set_volume(level)
        except:
            speak("Please specify a volume level between 0 and 100.")

    # Brightness controls
    elif "increase brightness" in command:
        increase_brightness()
    elif "decrease brightness" in command:
        decrease_brightness()
    elif "set brightness to" in command:
        try:
            level = int(command.split("set brightness to")[-1].strip().replace('%', ''))
            set_brightness(level)
        except:
            speak("Please specify a brightness level between 0 and 100.")

    elif "battery status" in command or "battery" in command:
        battery_status()

    # Media controls
    elif "play music" in command or "play song" in command:
        song_name = None
        if "play music" in command:
            parts = command.split("play music", 1)
            if len(parts) > 1:
                song_name = parts[1].strip()
        elif "play song" in command:
            parts = command.split("play song", 1)
            if len(parts) > 1:
                song_name = parts[1].strip()
        play_music(song_name)

    elif "play movie" in command:
        movie_name = None
        parts = command.split("play movie")
        if len(parts) > 1:
            movie_name = parts[1].strip()
        play_movie(movie_name)
    elif "pause media" in command or "pause music" in command or "pause movie" in command:
        pause_media()
    elif "resume media" in command or "resume music" in command or "resume movie" in command:
        resume_media()

    # Folder operations
    elif "open" in command and any(folder in command for folder in [
        "home", "gallery", "onedrive", "desktop", "downloads", "documents",
        "pictures", "music", "videos", "this pc", "acer", "data"
    ]):
        for folder in ["home", "gallery", "onedrive", "desktop", "downloads", "documents",
                       "pictures", "music", "videos", "this pc", "acer", "data"]:
            if folder in command:
                open_folder(folder)
                break

    elif "create folder" in command:
        try:
            parts = command.split("create folder")
            rest = parts[1].strip()
            folder_name = rest.split(" in ")[0].strip()
            location = rest.split(" in ")[1].strip()
            create_folder(folder_name, location)
        except:
            speak("Please specify folder name and location. Example: create folder Projects in Documents")

    # Application controls
    elif "open" in command and any(app in command for app in ["chrome", "edge", "notepad", "whatsapp", "microsoft store"]):
        for app in ["chrome", "edge", "notepad", "whatsapp", "microsoft store"]:
            if app in command:
                open_app(app)
                break
    elif "close" in command and any(app in command for app in ["chrome", "notepad", "edge", "whatsapp"]):
        for app in ["chrome", "notepad", "edge", "whatsapp"]:
            if app in command:
                close_app(app)
                break

    # YouTube open/close
    elif "open youtube" in command:
        open_youtube()
    elif "close youtube" in command:
        close_youtube()

    elif "close all" in command and "apps" in command:
        close_all_apps()

    # Search commands
    elif "search wikipedia for" in command:
        query = command.split("search wikipedia for")[-1].strip()
        search_wikipedia(query)
    elif "search youtube for" in command:
        query = command.split("search youtube for")[-1].strip()
        search_on_youtube(query)
    elif "search on chrome for" in command:
        query = command.split("search on chrome for")[-1].strip()
        search_in_chrome(query)
    elif "search on microsoft store for" in command:
        query = command.split("search on microsoft store for")[-1].strip()
        search_microsoft_store(query)
    elif "search on edge for" in command:
        query = command.split("search on edge for")[-1].strip()
        search_on_edge(query)
    elif "search windows start for" in command:
        query = command.split("search windows start for")[-1].strip()
        search_windows_start(query)

    # System commands
    elif any(cmd in command for cmd in ["shutdown", "restart", "sleep", "lock"]):
        system_control(command)

    # Screenshot and screen recording
    elif "take screenshot" in command:
        take_screenshot()
    elif "start screen recording" in command or "stop screen recording" in command:
        start_or_stop_screen_recording()

    # Internet speed test
    elif "internet speed" in command or "check internet speed" in command:
        check_internet_speed()

    # Laptop performance test
    elif "check laptop performance" in command or "laptop performance" in command:
        check_laptop_performance()

    # Time and Date
    elif "time" in command and "date" in command:
        tell_time_and_date()
    elif "time" in command:
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
    elif "date" in command:
        now = datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        speak(f"Today is {current_date}")

    # Action center controls
    elif "open action center" in command or "toggle action center" in command or "show notifications" in command:
        toggle_action_center()
    elif "close action center" in command or "hide notifications" in command:
        toggle_action_center()
        speak("Closing Action Center.")

    # Calculation
    elif "calculate" in command or "what is" in command:
        result = calculate_expression(command)
        if result is not None:
            speak(f"The answer is {result}")
        else:
            speak("Sorry, I couldn't understand the calculation.")

    # Disk cleanup
    elif "disk cleanup" in command or "clean up my disk" in command or "clean up my disc" in command:
        disk_cleanup()
    elif "clear recycle bin" in command or "empty recycle bin" in command:
        clear_recycle_bin()

    elif "create file" in command:
        try:
            parts = command.split("create file")
            rest = parts[1].strip()
            file_name = rest.split(" in ")[0].strip()
            location = rest.split(" in ")[1].strip()
            create_file(file_name, location)
        except:
            speak("Please specify file name and location. Example: create file notes.txt in Documents")

    # Run dialog variations
    elif ("open run and type" in command or
          ("type" in command and "in run" in command) or
          ("execute" in command and "using win r" in command)):

        try:
            if "open run and type" in command:
                cmd = command.split("open run and type")[-1].strip()
            elif "type" in command and "in run" in command:
                cmd = command.split("type")[-1].split("in run")[0].strip()
            elif "execute" in command and "using win r" in command:
                cmd = command.split("execute")[-1].split("using win r")[0].strip()
            else:
                cmd = ""

            if cmd:
                run_command_in_run_dialog(cmd)
            else:
                speak("Please tell me what to type in the Run dialog.")
        except:
            speak("Sorry, I couldn't run that command.")

    # Typing text
    elif command.startswith("type "):
        text = command[len("type "):].strip()
        type_text(text)

    # Wait or sleep
    elif "wait" in command or "sleep" in command:
        seconds = extract_wait_time(command)
        if seconds:
            speak(f"Okay, I will wait for {seconds} seconds.")
            time.sleep(seconds)
            speak("I'm back. How can I help you?")
        else:
            speak("Please specify how long I should wait.")
            
    elif "left click" in command:
        left_click()
        
    elif "right click" in command:
        right_click()
    
    elif "double click" in command:
        double_click()

    # Scrolling commands
    elif "scroll" in command:
        if "scroll down by" in command:
            try:
                amount = int(command.split("scroll down by")[-1].strip())
                scroll_down(amount)
            except:
                speak("Please specify a number to scroll by.")
        elif "scroll up by" in command:
            try:
                amount = int(command.split("scroll up by")[-1].strip())
                scroll_up(amount)
            except:
                speak("Please specify a number to scroll by.")
        elif "scroll up" in command:
            if "slowly" in command:
                scroll_up(200)
            elif "quickly" in command:
                scroll_up(1000)
            else:
                scroll_up()
        elif "scroll down" in command:
            if "slowly" in command:
                scroll_down(200)
            elif "quickly" in command:
                scroll_down(1000)
            else:
                scroll_down()

# ---------- GUI Setup ----------
def create_gui():
    global root, console, listen_button, text_entry
    
    root = tk.Tk()
    root.title("Jarvis AI Assistant")
    root.geometry("800x600")
    root.configure(bg="#2c3e50")
    
    # Set window icon
    try:
        root.iconbitmap("jarvis_icon.ico")  # Replace with your icon file if available
    except:
        pass
    
    # Header Frame
    header_frame = tk.Frame(root, bg="#1a1a2e")
    header_frame.pack(fill=tk.X, padx=10, pady=10)
    
    try:
        # Load and resize logo image
        logo_image = Image.open("snow.png")  # Replace with your image file
        logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        
        logo_label = tk.Label(header_frame, image=logo_photo, bg="#1a1a2e")
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side=tk.LEFT, padx=(0, 10))
    except Exception as e:
        print(f"Could not load logo image: {e}")
    
    # Title Label
    title_label = tk.Label(header_frame, text="JARVIS AI ASSISTANT", font=("Helvetica", 18, "bold"), 
                         fg="#00ffaa", bg="#1a1a2e")
    title_label.pack(pady=10)
    
    # Main Content Frame
    main_frame = tk.Frame(root, bg="#2c3e50")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    # Console Output
    console_frame = tk.Frame(main_frame, bg="#2c3e50")
    console_frame.pack(fill=tk.BOTH, expand=True)
    
    console_label = tk.Label(console_frame, text="Conversation Log", font=("Helvetica", 12), 
                           fg="white", bg="#2c3e50")
    console_label.pack(anchor=tk.W)
    
    global console
    console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, width=80, height=20,
                                      font=("Consolas", 10), bg="#1e1e1e", fg="white")
    console.pack(fill=tk.BOTH, expand=True)
    console.config(state=tk.DISABLED)
    
    # Text Input Frame
    text_frame = tk.Frame(main_frame, bg="#2c3e50")
    text_frame.pack(fill=tk.X, pady=(10, 0))
    
    global text_entry
    text_entry = tk.Entry(text_frame, font=("Helvetica", 12), bg="#1e1e1e", fg="white", insertbackground="white")
    text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    text_entry.bind("<Return>", lambda event: send_text())
    
    send_button = tk.Button(text_frame, text="Send", font=("Helvetica", 12), 
                          bg="#4CAF50", fg="white", relief=tk.RAISED, bd=2,
                          command=send_text)
    send_button.pack(side=tk.RIGHT)
    
    # Button Frame
    button_frame = tk.Frame(main_frame, bg="#2c3e50")
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Buttons
    global listen_button
    listen_button = tk.Button(button_frame, text="Start Listening", font=("Helvetica", 12), 
                            bg="#4CAF50", fg="white", relief=tk.RAISED, bd=2,
                            command=toggle_listening)
    listen_button.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
    
    quit_button = tk.Button(button_frame, text="Quit", font=("Helvetica", 12), 
                          bg="#f44336", fg="white", relief=tk.RAISED, bd=2,
                          command=root.destroy)
    quit_button.pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=5)
    
    # Status Bar
    status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                         font=("Helvetica", 10), bg="#1a1a2e", fg="white")
    status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    # Start with welcome message
    wish_user()
    
    root.mainloop()

# ---------- Main Execution ----------
if __name__ == "__main__":
    create_gui()
