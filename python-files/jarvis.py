import getpass
import tkinter as tk
from tkinter import messagebox
import pyttsx3
from scipy.datasets import face
import speech_recognition as sr 
import datetime
import webbrowser
import os
import wikipedia
import platform
import pyautogui
import cv2
import openai

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def run_face_auth_optical():
    import cv2

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        speak("Camera not accessible.")
        exit()

    speak("Scanning your face for identity verification...")

    authorized = False
    scan_attempts = 3

    while scan_attempts < 100:
        ret, frame = cap.read()
        if not ret:
            speak("Failed to read from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)  # ✅ CORRECTED

        for (x, y, w, h) in faces:  # ✅ CORRECTED
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            authorized = True
            break  # Only need one face to unlock

        cv2.imshow("Optical Face Unlock", frame)
        if authorized:
            speak("Face detected. Access granted.")
            break

        scan_attempts += 1
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not authorized:
        speak("I could not detect your face. Exiting.")
        exit()


import pyttsx3

def speak(text):
    try:
        engine = pyttsx3.init(driverName='sapi5')  # Use 'sapi5' for Windows
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)  # [0] = male, [1] = female
        engine.setProperty('rate', 170)            # Speed of speech
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("", e)


def wish_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your JARVIS assistant. How can I help you?")

def get_time():
    time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {time}")

def get_date():
    date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {date}")

def search_google():
    speak("What should I search on Google?")
    query = get_voice()
    webbrowser.open(f"https://www.google.com/search?q={query}")

    import getpass

def password_auth():
    correct_password = "jarvis123"  # 🔐 Change this to your secret
    speak("Please enter your password.")
    typed = getpass.getpass("🔐 Enter password: ")
    if typed == correct_password:
        speak("Password correct.")
    else:
        speak("Incorrect password. Access denied.")
        exit()


def search_wikipedia():
    speak("What should I search on Wikipedia?")
    query = get_voice()
    try:
        summary = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        speak(summary)
    except Exception:
        speak("Sorry, I couldn't find any results.")

COMMANDS = {
    "open file explorer": "Open File Explorer",
    "empty recycle bin": "Clear the recycle bin",
    "lock computer": "Lock the system",
    "mute": "Mute system volume",
    "change wallpaper": "Change desktop background",
    "brightness": "Set screen brightness",
    "processes": "Show running processes",
    "close app": "Kill application by name",
    "take note": "Take a text note and save",
    "speech to text": "Convert speech to text",
    "summarize clipboard": "Summarize copied text using AI",
    "installed apps": "List installed programs",
    "calendar event": "Create new Google Calendar event",
    "news": "Get top headlines",
    "joke": "Tell a random joke",
    "fact": "Tell a random fact",
    "youtube download": "Download YouTube video by URL",
    "voice chat": "Start AI voice chat with OpenRouter",
    "weather": "Get current weather",
    "battery": "Show battery level",
    "screenshot": "Take screenshot",
}

def show_all_commands():
    print("\n🧠 Available JARVIS Commands:")
    for cmd, desc in COMMANDS.items():
        print(f"- {cmd}: {desc}")
    speak("All available commands have been listed.")

def search_command(keyword):
    results = {k: v for k, v in COMMANDS.items() if keyword.lower() in k or keyword.lower() in v.lower()}
    if results:
        speak(f"Found {len(results)} matching commands.")
        for cmd, desc in results.items():
            print(f"- {cmd}: {desc}")
    else:
        speak("No matching commands found.")


def open_website():
    speak("Tell me the website name")
    query = get_voice()
    if not query.startswith("http"):
        query = "https://" + query
    webbrowser.open(query)
    speak("Website opened")

def open_app():
    speak("Which app should I open?")
    app = get_voice()
    if "notepad" in app:
        os.system("notepad")
    elif "chrome" in app:
        os.system("start chrome")
    else:
        speak("App not recognized")

def system_info():
    info = f"System: {platform.system()}, Version: {platform.version()}, Processor: {platform.processor()}"
    speak(info)

def take_screenshot():
    img = pyautogui.screenshot()
    img.save("screenshot.png")
    speak("Screenshot saved")

def get_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        return query.lower()
    except sr.UnknownValueError:
        speak("")
        return ""
    except sr.RequestError:
        speak("Voice service unavailable.")
        return ""
    
# ----- Phase 2 Features -----
import smtplib
from email.message import EmailMessage
import time

todos = []
notes = []

def send_email():
    try:
        speak("Who is the receiver? Please enter email address in terminal.")
        receiver = input("Receiver Email: ")
        speak("What is the subject?")
        subject = get_voice()
        speak("What should I say in the email?")
        body = get_voice()

        msg = EmailMessage()
        msg['From'] = 'your_email@example.com'  # Change this
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.set_content(body)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_email@example.com', 'your_password')  # Use Gmail App Password
        server.send_message(msg)
        server.quit()
        speak("Email sent successfully.")
    except Exception as e:
        speak("Failed to send email. Check credentials or internet.")

def set_alarm():
    speak("Tell me the alarm time in HH:MM format")
    alarm_time = input("Enter alarm time (HH:MM): ")
    speak(f"Alarm set for {alarm_time}")
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            speak("Time to wake up! Alarm ringing.")
            break
        time.sleep(10)

def add_todo():
    speak("What should I add to your to-do list?")
    task = get_voice()
    todos.append(task)
    speak("Task added.")

def show_todos():
    if not todos:
        speak("Your to-do list is empty.")
    else:
        for i, task in enumerate(todos, 1):
            speak(f"Task {i}: {task}")

def add_note():
    speak("What note should I write down?")
    note = get_voice()
    notes.append(note)
    speak("Note added.")

def show_notes():
    if not notes:
        speak("No notes yet.")
    else:
        for i, note in enumerate(notes, 1):
            speak(f"Note {i}: {note}")    

# ----- Phase 3 Features -----
import json
import os

reminders = []
calendar_events = []

def set_reminder():
    speak("What should I remind you about?")
    reminder = get_voice()
    reminders.append(reminder)
    speak("Reminder noted.")

def show_reminders():
    if not reminders:
        speak("You have no reminders.")
    else:
        for i, rem in enumerate(reminders, 1):
            speak(f"Reminder {i}: {rem}")

def add_calendar_event():
    speak("What is the event title?")
    title = get_voice()
    speak("What date? Please type in format YYYY-MM-DD")
    date = input("Enter date (YYYY-MM-DD): ")
    calendar_events.append({"title": title, "date": date})
    speak("Event added to calendar.")

def show_calendar_events():
    if not calendar_events:
        speak("No events in your calendar.")
    else:
        for event in calendar_events:
            speak(f"{event['title']} on {event['date']}")

def daily_schedule():
    speak("Your schedule includes:")
    for event in calendar_events:
        speak(f"{event['title']} on {event['date']}")

def calculator():
    speak("Please say your calculation like 2 plus 2")
    expr = get_voice()
    try:
        expr = expr.replace("plus", "+").replace("minus", "-").replace("into", "*").replace("divided by", "/")
        result = eval(expr)
        speak(f"The result is {result}")
    except:
        speak("Sorry, I could not calculate that.")

def save_data():
    with open("jarvis_data.json", "w") as f:
        json.dump({"todos": todos, "notes": notes, "reminders": reminders, "calendar": calendar_events}, f)
    speak("Data saved.")

def load_data():
    if os.path.exists("jarvis_data.json"):
        with open("jarvis_data.json", "r") as f:
            data = json.load(f)
        todos.clear()
        todos.extend(data.get("todos", []))
        notes.clear()
        notes.extend(data.get("notes", []))
        reminders.clear()
        reminders.extend(data.get("reminders", []))
        calendar_events.clear()
        calendar_events.extend(data.get("calendar", []))
        speak("Data loaded.")
    else:
        speak("No saved data found.")

# ----- Phase 4 Features -----
import random
import webbrowser

jokes = [
    "Why did the computer go to the doctor? Because it had a virus!",
    "Why don’t scientists trust atoms? Because they make up everything!",
    "Why did the math book look sad? Because it had too many problems.",
]

stories = [
    "Once upon a time, in a faraway land, there lived a curious AI named Jarvis. One day...",
    "In a quiet village, a boy discovered a talking computer that changed his world forever...",
    "There was a brave robot who wanted to learn emotions. So he traveled across the internet...",
]

movies = [
    "Inception", "Iron Man", "The Matrix", "Interstellar", "Avengers Endgame"
]

def tell_joke():
    joke = random.choice(jokes)
    speak(joke)

def tell_story():
    story = random.choice(stories)
    speak(story)

def suggest_movie():
    movie = random.choice(movies)
    speak(f"I suggest you watch {movie}.")

def play_music():
    music_path = "C:/Users/Public/Music/Sample Music"  # Change this to your music folder
    try:
        os.startfile(music_path)
        speak("Playing music.")
    except:
        speak("Unable to open music folder. Please check the path.")

def open_youtube():
    speak("Opening YouTube")
    webbrowser.open("https://www.youtube.com")

def open_spotify():
    speak("Opening Spotify")
    webbrowser.open("https://open.spotify.com")

def play_game():
    speak("Let's play a game of rock paper scissors. Say your choice.")
    user_choice = get_voice()
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    speak(f"I choose {bot_choice}.")
    if user_choice == bot_choice:
        speak("It's a tie!")
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        speak("You win!")
    else:
        speak("I win!")

def quiz_game():
    questions = {
        "What is the capital of India?": "delhi",
        "Who wrote Harry Potter?": "jk rowling",
        "What planet is known as the Red Planet?": "mars"
    }
    speak("Starting quiz. I will ask 3 questions.")
    score = 0
    for question, answer in questions.items():
        speak(question)
        reply = get_voice()
        if reply.strip().lower() == answer:
            speak("Correct!")
            score += 1
        else:
            speak(f"Wrong. The answer is {answer}.")
    speak(f"Quiz over. Your score is {score} out of 3.")

# ----- Phase 5 Features -----
import hashlib
import base64


def double_password_check():
    speak("Enter the first password in terminal:")
    p1 = input("Password 1: ")
    speak("Enter the second password in terminal:")
    p2 = input("Password 2: ")
    if p1 == "123456" and p2 == "271110":  # Set your passwords
        speak("Access granted.")
        return True
    else:
        speak("Access denied.")
        return False



def load_key():
    return open("secret.key", "rb").read()



def telegram_command():
    speak("Telegram remote command will be available in future.")

def detect_usb():
    speak("USB detection is platform-specific. Simulating event.")
    speak("USB inserted.")

def disable_internet():
    speak("Simulating internet disable. Real action skipped for safety.")

def enable_internet():
    speak("Simulating internet enable.")

def generate_password():
    import string, random
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(12))
    speak(f"Generated password is {password}")

def hash_string():
    speak("What should I hash?")
    data = get_voice()
    result = hashlib.md5(data.encode()).hexdigest()
    speak(f"MD5 hash is {result}")

def encode_base64():
    speak("What should I encode?")
    data = get_voice()
    encoded = base64.b64encode(data.encode()).decode()
    speak(f"Encoded text is {encoded}")

def decode_base64():
    speak("Enter Base64 string to decode:")
    encoded = input("Base64 String: ")
    try:
        decoded = base64.b64decode(encoded.encode()).decode()
        speak(f"Decoded text is: {decoded}")
    except:
        speak("Invalid Base64 string.")

def test_voice():
    speak("Your JARVIS voice engine is working correctly.")

# ----- Phase 6 Features -----
import requests
import pywhatkit as kit
import pyperclip
import pyautogui

def get_weather():
    speak("Tell me the city name.")
    city = get_voice()
    try:
        api_key = "your_openweather_api_key"  # Replace with your API key
        base_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(base_url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak("City not found.")
    except:
        speak("Unable to get weather. Check your internet or API key.")

def openrouter_voice_chat():
    speak("Voice chat mode activated. Ask me anything. Say 'stop chat' to exit.")
    messages = [{"role": "system", "content": "You are JARVIS, an intelligent and helpful assistant."}]

    while True:
        print("\n🎙️ Listening...")
        query = get_voice()
        if "stop chat" in query:
            speak("Exiting voice chat mode.")
            break

        messages.append({"role": "user", "content": query})

        try:
            response = openai.ChatCompletion.create(
                model="mistralai/mistral-7b-instruct",
                messages=messages
            )
            reply = response['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": reply})
            print(f"\n🧠 JARVIS: {reply}")
            speak(reply)
            save_to_log("User: " + query + "\nJARVIS: " + reply + "\n")

        except Exception as e:
            speak("Connection failed.")
            print("❌", e)


def get_location():
    try:
        ip_info = requests.get("https://ipinfo.io/json").json()
        loc = ip_info.get("city", "") + ", " + ip_info.get("region", "")
        speak(f"Your approximate location is {loc}.")
    except:
        speak("Unable to determine your location.")

def save_to_log(text):
    with open("jarvis_conversations.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")


def translate_text():
    from googletrans import Translator
    speak("What should I translate?")
    text = get_voice()
    speak("Which language should I translate to? For example, Hindi or Spanish.")
    lang = get_voice().lower()
    lang_map = {
        "hindi": "hi",
        "spanish": "es",
        "french": "fr",
        "german": "de",
        "chinese": "zh-cn"
    }
    if lang in lang_map:
        translator = Translator()
        translated = translator.translate(text, dest=lang_map[lang])
        speak(f"Translation: {translated.text}")
    else:
        speak("Language not supported yet.")

def search_youtube():
    speak("What should I search on YouTube?")
    topic = get_voice()
    kit.playonyt(topic)

def search_google_quick():
    speak("What should I search on Google?")
    query = get_voice()
    kit.search(query)

def send_whatsapp():
    speak("Enter phone number in terminal with country code (e.g., +919876543210):")
    number = input("Phone number: ")
    speak("What should I send?")
    message = get_voice()
    kit.sendwhatmsg_instantly(number, message)
    speak("Message sent.")

def get_clipboard():
    data = pyperclip.paste()
    speak("You copied: " + data)

def take_screenshot_named():
    speak("What should I name the screenshot?")
    name = get_voice().replace(" ", "_") + ".png"
    img = pyautogui.screenshot()
    img.save(name)
    speak("Screenshot saved as " + name)

def read_screen():
    speak("Reading screen text is a future feature that requires OCR support. Coming soon.")




# ----- Phase 7 Features -----
import webbrowser
import datetime
import pyautogui

def open_google_docs():
    speak("Opening Google Docs.")
    webbrowser.open("https://docs.google.com/document/u/0/")

def open_google_drive():
    speak("Opening Google Drive.")
    webbrowser.open("https://drive.google.com/")

def open_gmail():
    speak("Opening Gmail.")
    webbrowser.open("https://mail.google.com/")

def current_time():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"The current time is {now}")

def current_date():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    speak(f"Today's date is {today}")

def battery_status():
    try:
        import psutil
        battery = psutil.sensors_battery()
        percent = battery.percent
        speak(f"Battery is at {percent} percent")
    except:
        speak("Could not get battery status.")

import openai

def ask_openrouter(prompt):
    openai.api_key = "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"  # ← Replace with your OpenRouter API key
    openai.api_base = "https://openrouter.ai/api/v1"

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",  # or gpt-3.5, llama-3, etc.
            messages=[
                {"role": "system", "content": "You are JARVIS, an intelligent and helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response['choices'][0]['message']['content']
        print(f"\n🧠 JARVIS: {reply}")
        speak(reply)
    except Exception as e:
        print("❌ OpenRouter Error:", e)
        speak("Sorry, I couldn't reach my brain server.")


def volume_up():
    for _ in range(10):
        pyautogui.press("volumeup")
    speak("Volume increased.")

def volume_down():
    for _ in range(10):
        pyautogui.press("volumedown")
    speak("Volume decreased.")

def mute_volume():
    pyautogui.press("volumemute")
    speak("Volume muted.")

def open_camera():
    import subprocess
    try:
        subprocess.run("start microsoft.windows.camera:", shell=True)
        speak("Camera opened.")
    except:
        speak("Failed to open camera.")

# ----- Phase 8 Features -----
import pyttsx3
import time
import webbrowser
import random
import pyautogui

def motivational_quote():
    quotes = [
        "Believe in yourself and all that you are.",
        "You are capable of amazing things.",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "Dream big. Work hard. Stay focused.",
        "Push yourself, because no one else is going to do it for you."
    ]
    speak(random.choice(quotes))

def pomodoro_timer():
    speak("Starting a Pomodoro timer: 25 minutes work and 5 minutes break.")
    time.sleep(2)
    speak("Work session started.")
    time.sleep(25 * 60)  # 25 minutes
    speak("Time for a 5 minute break.")
    time.sleep(5 * 60)   # 5 minutes
    speak("Break over. You can start another session now.")

def open_calendar_web():
    speak("Opening Google Calendar.")
    webbrowser.open("https://calendar.google.com")

def open_notepad():
    speak("Opening Notepad.")
    try:
        os.system("notepad.exe")
    except:
        speak("Notepad not available.")

def open_calculator_app():
    speak("Opening Calculator.")
    try:
        os.system("calc.exe")
    except:
        speak("Calculator not found.")

def open_settings():
    speak("Opening Settings.")
    try:
        os.system("start ms-settings:")
    except:
        speak("Settings not available.")

def lock_screen():
    speak("Locking your screen.")
    os.system("rundll32.exe user32.dll,LockWorkStation")

def shutdown_pc():
    speak("Shutting down your system in 10 seconds. Say cancel to stop.")
    time.sleep(10)
    os.system("shutdown /s /t 1")

def restart_pc():
    speak("Restarting your system.")
    os.system("shutdown /r /t 1")

def sleep_mode():
    speak("Putting your system to sleep.")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

# ----- Phase 9–10 Features (81–100) -----
import glob
import wikipedia
import speedtest
import shutil
import smtplib
import ssl
from email.message import EmailMessage

def voice_file_search():
    speak("Which file should I find?")
    keyword = get_voice().lower()
    files = glob.glob(f"**/*{keyword}*", recursive=True)
    if files:
        speak(f"Found {len(files)} file(s) matching {keyword}")
        for f in files[:3]:
            speak(f)
    else:
        speak("No files found.")

def read_pdf():
    import PyPDF2
    speak("Enter the path to the PDF file:")
    file_path = input("PDF path: ")
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages[:2]:
                text += page.extract_text()
            speak("Reading PDF content:")
            speak(text)
    except:
        speak("Unable to read the PDF.")

import imaplib
import email

def read_gmail():
    try:
        speak("Reading your Gmail inbox.")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("youremail@gmail.com", "yourapppassword")  # Use app password
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        latest_email_id = mail_ids[-1]
        status, data = mail.fetch(latest_email_id, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        subject = msg["subject"]
        from_email = msg["from"]
        speak(f"Latest email is from {from_email} and subject is {subject}.")
    except:
        speak("Unable to read Gmail.")

def send_email():
    speak("Enter receiver email in terminal:")
    receiver = input("Receiver Email: ")
    speak("What is the subject?")
    subject = get_voice()
    speak("What should I say?")
    body = get_voice()
    try:
        email = EmailMessage()
        email["From"] = "youremail@gmail.com"
        email["To"] = receiver
        email["Subject"] = subject
        email.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login("youremail@gmail.com", "yourpassword")
            server.send_message(email)
        speak("Email sent successfully.")
    except:
        speak("Failed to send email.")

def wiki_summary():
    speak("What topic should I search on Wikipedia?")
    topic = get_voice()
    try:
        summary = wikipedia.summary(topic, sentences=2)
        speak(summary)
    except:
        speak("Unable to fetch summary.")

def auto_fill():
    speak("Auto form fill is not implemented yet.")

def generate_resume():
    speak("Resume builder is not ready. Will be added soon.")

def gpt_story():
    speak("Tell me a topic for the story.")
    topic = get_voice()
    story = f"Once upon a time, something amazing happened about {topic}. This is where your AI story begins..."
    speak(story)

def lock_status():
    speak("Screen lock detection is coming in future updates.")

import ctypes
import subprocess
import shutil
import pyautogui
import psutil
import os

def open_file_explorer():
    os.startfile("C:\\")  # or any path
    speak("Opening File Explorer.")

def empty_recycle_bin():
    try:
        import winshell
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
        speak("Recycle bin emptied.")
    except:
        speak("Unable to access recycle bin.")

def lock_computer():
    ctypes.windll.user32.LockWorkStation()

def mute_volume():
    pyautogui.press("volumemute")
    speak("Volume muted.")

def ai_resume_builder():
    speak("Please describe your education, experience, and skills.")
    info = get_voice()
    ask_openrouter(f"Build a professional resume using this info:\n{info}")

def check_battery_status():
    battery = psutil.sensors_battery()
    speak(f"Battery is at {battery.percent} percent.")

def check_cpu_usage():
    usage = psutil.cpu_percent()
    speak(f"CPU usage is at {usage} percent.")

def check_ram_usage():
    mem = psutil.virtual_memory()
    used = mem.used // (1024 ** 2)
    total = mem.total // (1024 ** 2)
    speak(f"RAM used: {used} out of {total} megabytes.")

def open_gmail():
    speak("Opening Gmail.")
    os.system("start https://mail.google.com")

def search_google():
    speak("What should I search?")
    query = get_voice()
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak("Searching Google.")

def open_youtube():
    speak("Opening YouTube.")
    os.system("start https://youtube.com")

def play_youtube_video():
    speak("What do you want to play?")
    song = get_voice()
    import pywhatkit
    pywhatkit.playonyt(song)

def list_files_in_folder():
    speak("Which folder?")
    folder = get_voice()
    try:
        files = os.listdir(folder)
        for f in files:
            print(f)
        speak("Files listed.")
    except:
        speak("Folder not found.")

def delete_file():
    speak("Which file should I delete?")
    filename = get_voice()
    if os.path.exists(filename):
        os.remove(filename)
        speak("File deleted.")
    else:
        speak("File not found.")

def rename_file():
    speak("Old filename?")
    old_name = get_voice()
    speak("New filename?")
    new_name = get_voice()
    try:
        os.rename(old_name, new_name)
        speak("File renamed.")
    except:
        speak("Unable to rename.")


def roll_dice():
    import random
    roll = random.randint(1, 6)
    speak(f"You rolled a {roll}.")

def flip_coin():
    import random
    flip = random.choice(["heads", "tails"])
    speak(f"It's {flip}.")

def ai_email_writer():
    speak("Who is this email for and what's the purpose?")
    prompt = get_voice()
    ask_openrouter(f"Write a formal email for: {prompt}")

def ai_code_explainer():
    speak("Paste the code to explain.")
    import pyperclip
    code = pyperclip.paste()
    ask_openrouter(f"Explain this code:\n{code}")

def change_wallpaper():
    import random
    wallpaper_path = "C:\\Wallpapers\\bg.jpg"  # put your own path or randomize
    ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0)
    speak("Wallpaper changed.")

def adjust_brightness(level=50):  # range 0–100
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        speak(f"Brightness set to {level} percent.")
    except:
        speak("Could not adjust brightness.")

def show_running_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        print(f"{proc.info['pid']} - {proc.info['name']}")
    speak("Displayed all running processes.")

def close_app_by_name(app_name):
    found = False
    for proc in psutil.process_iter():
        if app_name.lower() in proc.name().lower():
            proc.kill()
            found = True
            speak(f"Closed {proc.name()}.")
    if not found:
        speak("Application not found.")

def take_note():
    speak("What would you like me to write?")
    note = get_voice()
    with open("note.txt", "a") as f:
        f.write(note + "\n")
    speak("Note saved.")

def speech_to_text_file():
    speak("Start speaking. I will save what you say.")
    text = get_voice()
    with open("speech_output.txt", "w") as f:
        f.write(text)
    speak("Saved as speech_output.txt")

def summarize_clipboard_ai():
    import pyperclip
    text = pyperclip.paste()
    if len(text.strip()) < 10:
        speak("Clipboard is empty or too short.")
        return
    ask_openrouter(f"Summarize this:\n{text}")

def tell_time():
    from datetime import datetime
    time_now = datetime.now().strftime("%H:%M:%S")
    speak(f"The time is {time_now}.")

def tell_date():
    from datetime import datetime
    date_today = datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {date_today}.")    

def list_installed_apps():
    apps = os.popen("wmic product get name").read()
    print(apps)
    speak("Installed apps listed.")

def create_google_calendar_event():
    speak("Opening Google Calendar.")
    os.system("start https://calendar.google.com/calendar/u/0/r/eventedit")

def get_news():
    import requests
    speak("Fetching top news headlines.")
    url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=YOUR_NEWSAPI_KEY"
    r = requests.get(url).json()
    for article in r["articles"][:5]:
        print(article["title"])
        speak(article["title"])

def random_joke():
    import pyjokes
    joke = pyjokes.get_joke()
    print(joke)
    speak(joke)

def random_fact():
    import requests
    fact = requests.get("https://uselessfacts.jsph.pl/random.json?language=en").json()["text"]
    speak(fact)

def download_youtube_video():
    import pytube
    speak("Please say the YouTube URL.")
    url = get_voice()
    speak("Downloading...")
    yt = pytube.YouTube(url)
    yt.streams.get_highest_resolution().download()
    speak("Download complete.")


import requests

def currency_convert():
    speak("Which currency should I convert from?")
    base = get_voice().upper()
    speak("Which currency should I convert to?")
    target = get_voice().upper()
    speak("How much?")
    amount = float(get_voice())

    url = f"https://api.exchangerate-api.com/v4/latest/{base}"
    try:
        res = requests.get(url)
        rate = res.json()["rates"][target]
        converted = rate * amount
        speak(f"{amount} {base} is equal to {converted:.2f} {target}")
    except:
        speak("Currency conversion failed.")

def save_command_history(command):
    with open("command_history.txt", "a") as f:
        f.write(command + "\\n")

def speed_test():
    speak("Testing your internet speed. Please wait.")
    st = speedtest.Speedtest()
    download = st.download() / 1024 / 1024
    upload = st.upload() / 1024 / 1024
    speak(f"Download speed: {download:.2f} Mbps. Upload speed: {upload:.2f} Mbps.")

def system_cleanup():
    speak("Cleaning temporary files.")
    shutil.rmtree("C:/Windows/Temp", ignore_errors=True)
    speak("Temporary files removed.")

def enable_background_mode():
    speak("Minimizing to tray (simulated).")
    # Future: integrate with pystray

def check_updates():
    speak("Checking for updates. No updates available currently.")

def wake_word_listen():
    speak("This will activate Jarvis only when you say 'Hey Jarvis'. Coming soon.")

def chatbot_mode():
    speak("This will open chat mode with JARVIS AI. Coming soon.")

def backup_notes():
    speak("Backing up notes to Google Drive not implemented yet.")

def profile_settings():
    speak("This will open your personal profile. Future feature.")

def autostart():
    speak("Auto start with Windows setup is coming.")


def jarvis_cli():
    speak("JARVIS  activated. Listening for your command.")
    while True:
        print("\nSay your command ")
        command = get_voice().lower()
        print("You said:", command)

        if "exit" in command:
            speak("Goodbye.")
            break

        # 🔹 AI + OpenRouter
        elif "what" in command or "ai" in command or "question" in command or "who" in command or "How" in command:
            speak("What's your question?")
            query = get_voice()
            ask_openrouter(query)

        elif "explain" in command:
            ask_openrouter(command)

        elif "chat mode" in command or "voice chat" in command:
            openrouter_voice_chat()

        elif "search command" in command:
            speak("What command are you searching for?")
            keyword = get_voice()
            search_command(keyword)

        elif "show all commands" in command:
            show_all_commands()

        # 🔹 Internet & Web
        elif "google" in command:
            search_google_quick()

        elif "youtube" in command:
            search_youtube()

        elif "play video" in command:
            play_youtube_video()

        elif "news" in command:
            get_news()

        elif "weather" in command:
            get_weather()

        elif "location" in command:
            get_location()

        elif "speed test" in command:
            speed_test()

        elif "wikipedia" in command:
            wiki_summary()

        elif "translate" in command:
            translate_text()

        elif "quote" in command:
            motivational_quote()

        # 🔹 Communication
        elif "send whatsapp" in command:
            send_whatsapp()

        elif "email" in command:
            send_email()

        elif "read gmail" in command:
            read_gmail()

        elif "calendar" in command:
            open_calendar_web()

        elif "gmail" in command:
            open_gmail()

        elif "docs" in command:
            open_google_docs()

        elif "drive" in command:
            open_google_drive()

        # 🔹 System Utilities
        elif "notepad" in command:
            open_notepad()

        elif "shutdown" in command:
            shutdown_pc()

        elif "restart" in command:
            restart_pc()

        elif "sleep mode" in command:
            sleep_mode()

        elif "battery" in command:
            battery_status()

        elif "camera" in command:
            open_camera()

        elif "screenshot" in command:
            take_screenshot_named()

        elif "clipboard" in command:
            get_clipboard()

        elif "read pdf" in command:
            read_pdf()

        elif "file explorer" in command:
            open_file_explorer()

        elif "recycle bin" in command:
            empty_recycle_bin()

        elif "lock computer" in command:
            lock_computer()

        elif "mute" in command:
            mute_volume()

        elif "change wallpaper" in command:
            change_wallpaper()

        elif "brightness" in command:
            adjust_brightness(40)

        elif "processes" in command:
            show_running_processes()

        elif "close app" in command:
            speak("Which app should I close?")
            app = get_voice()
            close_app_by_name(app)

        elif "list files" in command:
            list_files_in_folder()

        elif "delete file" in command:
            delete_file()

        elif "rename file" in command:
            rename_file()

        # 🔹 AI Productivity
        elif "build resume" in command:
            ai_resume_builder()

        elif "write email" in command:
            ai_email_writer()

        elif "explain code" in command:
            ai_code_explainer()

        elif "summarize clipboard" in command:
            summarize_clipboard_ai()

        elif "installed apps" in command:
            list_installed_apps()

        # 🔹 Note Tools
        elif "take note" in command:
            take_note()

        elif "speech to text" in command:
            speech_to_text_file()

        # 🔹 Media/YouTube
        elif "youtube download" in command:
            download_youtube_video()

        # 🔹 System Info
        elif "cpu" in command:
            check_cpu_usage()

        elif "ram" in command:
            check_ram_usage()

        # 🔹 Fun & Utilities
        elif "dice" in command:
            roll_dice()

        elif "flip coin" in command:
            flip_coin()

        elif "time" in command:
            current_time()

        elif "date" in command:
            current_date()

        else:
            speak("")


if __name__ == "__main__":
    run_face_auth_optical() 
      # ✅ Step 1: Face recognition
    password_auth()   # ✅ Step 2: Password input
    jarvis_cli()      # 🚀 Step 3: Launch CLI



