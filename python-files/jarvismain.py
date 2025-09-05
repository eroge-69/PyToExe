"""
E.V.I.S-MBL Voice Assistant (Windows) - voice only, always-listening, explicit spoken commands
A python file made by Lochan.P
"""

import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import psutil
import requests
import os
import time
import pyautogui
import cv2
import pywhatkit
import smtplib
from email.message import EmailMessage
from deep_translator import GoogleTranslator
from datetime import datetime
import logging
import sys
import re

# ---------------- Configuration (EDIT) ----------------
OPENWEATHER_API_KEY = ""           # Put your OpenWeatherMap API key here (optional)
EMAIL_ADDRESS = ""                 # Your email address for sending email (e.g. Gmail)
EMAIL_APP_PASSWORD = ""            # App password (Gmail) or SMTP password
SPOTIFY_EXE_PATH = None            # e.g. r"C:\Users\You\AppData\Roaming\Spotify\Spotify.exe" (optional)
RECORD_VIDEO_DURATION_DEFAULT = 10 # seconds if not specified
LOG_FILE = "commands.log"
# -----------------------------------------------------

# initialize logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# initialize TTS
engine = pyttsx3.init()
engine.setProperty("rate", 170)  # words per minute

# recognizer
recognizer = sr.Recognizer()

# Language mode: "en" or "hi"
LANGUAGE = "en"  # start in English; switch using commands

# helper speak function
def speak(text: str):
    # if LANGUAGE is hi and you prefer TTS in Hindi, use translator to Hindi
    try:
        if LANGUAGE == "hi":
            # translate English text to Hindi for spoken response if needed
            translated = GoogleTranslator(source='auto', target='hi').translate(text)
            utter = translated
        else:
            utter = text
    except Exception:
        utter = text
    print("E.V.I.S--MBL:", utter)
    try:
        engine.say(utter)
        engine.runAndWait()
    except Exception as e:
        print("TTS error:", e)
    logging.info("SAY: " + text)

# listen once (returns lowercased string)
def listen_once(timeout=5, phrase_time_limit=7):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            lang_code = "hi-IN" if LANGUAGE == "hi" else "en-US"
            text = recognizer.recognize_google(audio, language=lang_code)
            text = text.lower().strip()
            logging.info("HEARD: " + text)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Speech service unavailable. Check your internet.")
            return ""
        except Exception as e:
            print("Listen error:", e)
            return ""

# Utility: open default browser url
def open_url(url, announce=None):
    try:
        webbrowser.open(url)
        if announce:
            speak(announce)
    except Exception as e:
        speak(f"Failed to open URL: {e}")

# ---------------- App control helpers ----------------
def open_chrome():
    try:
        subprocess.Popen("start chrome", shell=True)
        speak("Google Chrome opened.")
    except Exception as e:
        speak(f"Failed to open Chrome: {e}")

def close_chrome():
    close_process_by_name("chrome")

def open_edge():
    try:
        subprocess.Popen("start msedge", shell=True)
        speak("Microsoft Edge opened.")
    except Exception as e:
        speak(f"Failed to open Edge: {e}")

def close_edge():
    close_process_by_name("msedge")

def open_google():
    open_url("https://www.google.com", "Google opened.")

def open_youtube():
    open_url("https://www.youtube.com", "YouTube opened.")

def close_youtube():
    # best-effort: close browsers where YouTube might run
    close_process_by_name("chrome")
    close_process_by_name("msedge")
    close_process_by_name("firefox")
    speak("Attempted to close YouTube browser tabs (closed browser processes).")

def open_chatgpt():
    open_url("https://chat.openai.com", "ChatGPT opened in browser.")

def open_spotify():
    try:
        if SPOTIFY_EXE_PATH and os.path.isfile(SPOTIFY_EXE_PATH):
            subprocess.Popen(SPOTIFY_EXE_PATH)
            speak("Spotify desktop opened.")
            return
        subprocess.Popen("start spotify", shell=True)
        speak("Attempted to open Spotify.")
    except Exception as e:
        speak(f"Failed to open Spotify: {e}. Opening Spotify web instead.")
        open_url("https://open.spotify.com", "Spotify web opened.")

def close_spotify():
    close_process_by_name("spotify")

def open_program(path_or_name):
    if not path_or_name:
        speak("No program name or path provided.")
        return
    # if path exists open it, else try start <name>
    try:
        if os.path.isfile(path_or_name):
            os.startfile(path_or_name)
            speak(f"Opened {path_or_name}.")
            return
        subprocess.Popen(f"start {path_or_name}", shell=True)
        speak(f"Attempted to open {path_or_name}.")
    except Exception as e:
        speak(f"Failed to open program {path_or_name}: {e}")

def close_program(name):
    close_process_by_name(name)

def close_process_by_name(name):
    if not name:
        speak("No process name provided.")
        return
    name_low = name.lower().strip()
    killed = 0
    for proc in psutil.process_iter(['name','cmdline','exe']):
        try:
            pname = (proc.info.get('name') or "").lower()
            pexe = (proc.info.get('exe') or "").lower()
            pcmd = " ".join(proc.info.get('cmdline') or []).lower()
            if name_low in pname or name_low in pexe or name_low in pcmd:
                proc.terminate()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if killed:
        speak(f"Terminated {killed} process(es) matching {name}.")
    else:
        speak(f"No running process matched {name}.")

# ---------------- Mouse & scroll & click ----------------
def move_cursor(direction, pixels):
    try:
        pixels = int(pixels)
    except:
        speak("Please provide a valid integer number of pixels.")
        return
    x, y = pyautogui.position()
    if direction in ("left","l"):
        pyautogui.moveTo(x - pixels, y)
        speak(f"Moved cursor left by {pixels} pixels.")
    elif direction in ("right","r"):
        pyautogui.moveTo(x + pixels, y)
        speak(f"Moved cursor right by {pixels} pixels.")
    elif direction in ("up","u"):
        pyautogui.moveTo(x, y - pixels)
        speak(f"Moved cursor up by {pixels} pixels.")
    elif direction in ("down","d"):
        pyautogui.moveTo(x, y + pixels)
        speak(f"Moved cursor down by {pixels} pixels.")
    else:
        speak("Unknown direction. Use left, right, up or down.")

def scroll_up(amount=300):
    try:
        pyautogui.scroll(amount)
        speak(f"Scrolled up {amount} units.")
    except Exception as e:
        speak(f"Scroll failed: {e}")

def scroll_down(amount=300):
    try:
        pyautogui.scroll(-amount)
        speak(f"Scrolled down {amount} units.")
    except Exception as e:
        speak(f"Scroll failed: {e}")

def click_button(clicks=1, x=None, y=None):
    try:
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), clicks=int(clicks))
        else:
            pyautogui.click(clicks=int(clicks))
        speak("Clicked.")
    except Exception as e:
        speak(f"Click failed: {e}")

# ---------------- Camera: photo & recording ----------------
def take_photo(save_folder="photos"):
    try:
        os.makedirs(save_folder, exist_ok=True)
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if not ret:
            speak("Could not access camera.")
            cap.release()
            return
        filename = os.path.join(save_folder, f"photo_{int(time.time())}.jpg")
        cv2.imwrite(filename, frame)
        cap.release()
        speak(f"Photo saved to {filename}")
    except Exception as e:
        speak(f"Photo failed: {e}")

def record_video(duration=RECORD_VIDEO_DURATION_DEFAULT, save_folder="videos"):
    try:
        os.makedirs(save_folder, exist_ok=True)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Camera not available for recording.")
            return
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = os.path.join(save_folder, f"video_{int(time.time())}.avi")
        fps = 20.0
        ret, frame = cap.read()
        if not ret:
            speak("Camera failed.")
            cap.release()
            return
        height, width = frame.shape[:2]
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        start = time.time()
        speak(f"Recording for {duration} seconds.")
        while time.time() - start < float(duration):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        out.release()
        cap.release()
        speak(f"Recording saved to {filename}")
    except Exception as e:
        speak(f"Recording failed: {e}")

# ---------------- YouTube playback controls (simulate keys) ----------------
def youtube_play_pause():
    pyautogui.press('space')
    speak("Toggled play/pause on video.")

def youtube_seek_left(seconds=5):
    # left arrow => usually 5 seconds
    for _ in range(max(1, int(seconds//5))):
        pyautogui.press('left')
    speak(f"Seeked left approximately {seconds} seconds.")

def youtube_seek_right(seconds=5):
    for _ in range(max(1, int(seconds//5))):
        pyautogui.press('right')
    speak(f"Seeked right approximately {seconds} seconds.")

# ---------------- Weather, time, IP, maps ----------------
def get_time_text():
    now = datetime.now()
    speak("The current time is " + now.strftime("%A, %d %B %Y %I:%M %p"))

def get_weather(city=None):
    if not city:
        # fallback: open search for local weather
        speak("No city provided for weather. Opening web search for local weather.")
        webbrowser.open("https://www.google.com/search?q=weather")
        return
    if OPENWEATHER_API_KEY:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            r = requests.get(url, timeout=8).json()
            if r.get("cod") != 200:
                speak(f"Weather API error: {r.get('message','unknown')}")
                return
            desc = r['weather'][0]['description']
            temp = r['main']['temp']
            speak(f"The weather in {city} is {desc} with temperature {temp} degrees Celsius.")
        except Exception as e:
            speak(f"Weather fetch failed: {e}")
    else:
        # fallback to web search
        speak("OpenWeather API key not set. Showing web results.")
        webbrowser.open(f"https://www.google.com/search?q=weather+in+{city.replace(' ','+')}")

def my_ip_location():
    try:
        ip = requests.get("https://api.ipify.org").text
        data = requests.get(f"http://ip-api.com/json/{ip}", timeout=6).json()
        if data.get("status") == "success":
            speak(f"Your approximate location: {data.get('city')}, {data.get('regionName')}, {data.get('country')}. ISP: {data.get('isp')}")
        else:
            speak("IP location lookup failed.")
    except Exception as e:
        speak(f"IP lookup error: {e}")

def location_for_ip(ip_addr):
    try:
        data = requests.get(f"http://ip-api.com/json/{ip_addr}", timeout=6).json()
        if data.get("status") == "success":
            speak(f"IP {ip_addr}: {data.get('city')}, {data.get('regionName')}, {data.get('country')}. ISP: {data.get('isp')}")
        else:
            speak("IP lookup failed.")
    except Exception as e:
        speak(f"IP lookup error: {e}")

def get_directions(destination):
    if not destination:
        speak("No destination provided.")
        return
    url = f"https://www.google.com/maps/dir//{destination.replace(' ','+')}/"
    open_url(url, f"Opening directions to {destination} in Google Maps")

# ---------------- WhatsApp & Email ----------------
def send_whatsapp(phone_number, message):
    try:
        # opens WhatsApp Web in browser and sends message instantly if logged in
        pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=True)
        speak("WhatsApp message attempted (browser opened).")
    except Exception as e:
        speak(f"WhatsApp send failed: {e}")

def send_email(to_address, subject, body):
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        speak("Email address or app password not configured.")
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg.set_content(body)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        speak("Email sent successfully.")
    except Exception as e:
        speak(f"Email send failed: {e}")

# ---------------- Command lists (exact spoken phrases) ----------------
# Because you requested explicit commands only (no fuzzy matching),
# we list supported spoken phrases (English and Hindi variants).
COMMAND_PHRASES = {
    # open / search / close apps
    "open_youtube": ["open youtube", "youtube open", "youtube खोलो", "यूट्यूब खोलो"],
    "search_youtube": ["search on youtube", "search youtube", "youtube search", "youtube पर खोज", "youtube पर खोजो"],
    "open_google": ["open google", "open chrome", "google open", "गूगल खोलो"],
    "search_google": ["search on google", "search google", "google search", "गूगल पर खोज", "गूगल पर खोजो"],
    "open_edge": ["open edge", "open microsoft edge", "edge open", "एज खोलो"],
    "close_edge": ["close edge", "close microsoft edge", "एज बंद करो"],
    "close_chrome": ["close chrome", "close google", "google बंद करो", "क्रोम बंद करो"],
    "close_youtube": ["close youtube", "close youtube tabs", "यूट्यूब बंद करो"],
    "open_spotify": ["open spotify", "spotify open", "spotify खोलो"],
    "play_spotify": ["play song on spotify", "play on spotify", "spotify play", "spotify में चलाो"],
    "close_spotify": ["close spotify", "spotify बंद करो"],
    # time and weather
    "time": ["time", "what is the time", "time क्या है", "समय क्या है"],
    "weather": ["weather", "what is the weather", "weather in", "मौसम", "मौसम क्या है"],
    # open/close programs
    "open_program": ["open program", "open app", "open application", "प्रोग्राम खोलो"],
    "close_program": ["close program", "close app", "close application", "प्रोग्राम बंद करो"],
    # move mouse with pixels: pattern "move mouse left 100"
    "move_mouse": ["move mouse", "move cursor", "माउस चलाओ", "कर्सर चलाओ"],
    # scroll
    "scroll_up": ["scroll up", "scroll upwards", "ऊपर स्क्रोल", "स्क्रोल ऊपर"],
    "scroll_down": ["scroll down", "scroll downwards", "नीचे स्क्रोल", "स्क्रोल नीचे"],
    # camera
    "take_photo": ["take photo", "take picture", "photo", "तस्वीर लो"],
    "record_video": ["record video", "start recording", "वीडियो रिकॉर्ड करो"],
    # youtube controls
    "youtube_play_pause": ["play video", "pause video", "play pause", "प्ले","पॉज़"],
    "youtube_seek_left": ["seek left", "go back", "rewind", "पीछे जाओ"],
    "youtube_seek_right": ["seek right", "go forward", "forward", "आगे जाओ"],
    # maps/directions
    "open_maps": ["open maps", "open google maps", "maps खोलो"],
    "search_maps": ["search on maps", "search maps", "maps पर खोजो"],
    "directions": ["directions to", "get directions to", "route to", "दिशा बताओ"],
    # ip
    "my_ip_location": ["my ip location", "my ip", "ip location", "मेरी लोकेशन"],
    "given_ip_location": ["location for ip", "ip location for", "ip के लिए लोकेशन"],
    # whatsapp and email
    "send_whatsapp": ["send whatsapp", "whatsapp send", "व्हाट्सप्प भेजो"],
    "send_email": ["send email", "email send", "इमेल भेजो"],
    # stop / exit
    "exit": ["exit", "quit", "stop listening", "shutdown", "bye", "goodbye", "बंद करो", "रुक जाओ"],
    # language switch
    "switch_to_hindi": ["switch to hindi", "हिंदी में बदलो"],
    "switch_to_english": ["switch to english", "अंग्रेजी में बदलो"]
}

# helper to test if spoken text contains any of the phrases for a key
def matches_any(spoken: str, key: str):
    if key not in COMMAND_PHRASES:
        return False
    for phrase in COMMAND_PHRASES[key]:
        if phrase in spoken:
            return True
    return False

# parse patterns like "move mouse left 100"
def parse_move_mouse(spoken: str):
    # look for direction
    direction = None
    for d in ("left","right","up","down"):
        if d in spoken:
            direction = d
            break
    # extract first integer number
    match = re.search(r'(-?\d+)', spoken)
    pixels = match.group(1) if match else None
    return direction, pixels

# parse record video duration: "record video 10 seconds"
def parse_duration(spoken: str):
    match = re.search(r'(\d+)', spoken)
    return int(match.group(1)) if match else None

# main command processing (explicit commands only)
def process_command(spoken: str):
    spoken = spoken.lower()
    logging.info("COMMAND: " + spoken)

    # language switching
    if matches_any(spoken, "switch_to_hindi"):
        global LANGUAGE
        LANGUAGE = "hi"
        speak("भाषा हिंदी में बदल दी गई।")  # spoken in Hindi because LANGUAGE toggles next
        return
    if matches_any(spoken, "switch_to_english"):
        LANGUAGE = "en"
        speak("Language switched to English.")
        return

    # exit
    if matches_any(spoken, "exit"):
        speak("Shutting down. Goodbye.")
        sys.exit(0)

    # open/close apps & search
    if matches_any(spoken, "open_youtube"):
        open_youtube(); return
    if matches_any(spoken, "search_youtube"):
        # parse search query: spoken may be "search on youtube for cats"
        q = spoken
        for prefix in ("search on youtube for", "search on youtube", "search youtube for", "search youtube", "youtube search"):
            q = q.replace(prefix, "")
        q = q.strip()
        if not q:
            speak("What should I search on YouTube?")
            q = listen_once()
        if q:
            # open YouTube video search via pywhatkit.playonyt if you want direct play
            try:
                pywhatkit.playonyt(q)
                speak(f"Searching and opening top YouTube result for {q}")
            except Exception:
                search_youtube_url = "https://www.youtube.com/results?search_query=" + q.replace(" ", "+")
                open_url(search_youtube_url, f"Searching YouTube for {q}")
        return

    if matches_any(spoken, "open_google"):
        open_google(); return
    if matches_any(spoken, "search_google"):
        q = spoken
        for prefix in ("search on google for", "search on google", "search google for", "search google"):
            q = q.replace(prefix, "")
        q = q.strip()
        if not q:
            speak("What should I search on Google?")
            q = listen_once()
        if q:
            open_url("https://www.google.com/search?q=" + q.replace(" ", "+"), f"Searching Google for {q}")
        return

    if matches_any(spoken, "open_edge"):
        open_edge(); return
    if matches_any(spoken, "close_edge"):
        close_edge(); return
    if matches_any(spoken, "close_chrome"):
        close_chrome(); return
    if matches_any(spoken, "close_youtube"):
        close_youtube(); return

    if matches_any(spoken, "open_spotify"):
        open_spotify(); return
    if matches_any(spoken, "play_spotify"):
        q = spoken
        for prefix in ("play song on spotify", "play on spotify", "play on spotify for", "play spotify"):
            q = q.replace(prefix, "")
        q = q.strip()
        if not q:
            speak("Which song should I play on Spotify?")
            q = listen_once()
        if q:
            spotify_url = f"https://open.spotify.com/search/{q.replace(' ','%20')}"
            open_url(spotify_url, f"Searching Spotify for {q}")
        return
    if matches_any(spoken, "close_spotify"):
        close_spotify(); return

    # time / weather
    if matches_any(spoken, "time"):
        get_time_text(); return
    if matches_any(spoken, "weather"):
        # parse city: "weather in delhi"
        city = None
        if "in" in spoken:
            try:
                city = spoken.split("in",1)[1].strip()
            except:
                city = None
        if not city:
            speak("Which city for weather?")
            city = listen_once()
        if city:
            get_weather(city)
        return

    # open/close any program
    if matches_any(spoken, "open_program"):
        # parse after "open program" or "open"
        targ = spoken
        if "open program" in spoken:
            targ = spoken.split("open program",1)[1].strip()
        else:
            targ = spoken.split("open",1)[1].strip()
        if not targ:
            speak("Which program should I open? Say the program name or full path.")
            targ = listen_once()
        if targ:
            open_program(targ)
        return

    if matches_any(spoken, "close_program"):
        targ = spoken
        if "close program" in spoken:
            targ = spoken.split("close program",1)[1].strip()
        else:
            targ = spoken.split("close",1)[1].strip()
        if not targ:
            speak("Which program should I close? Say the process name.")
            targ = listen_once()
        if targ:
            close_program(targ)
        return

    # move mouse commands with pixels
    if matches_any(spoken, "move_mouse"):
        direction, pixels = parse_move_mouse(spoken)
        if not direction:
            speak("Direction not found. Say for example: move mouse left 100")
            direction = listen_once()
        if not pixels:
            speak("Number of pixels?")
            pix_spoken = listen_once()
            m = re.search(r'(-?\d+)', pix_spoken)
            pixels = m.group(1) if m else None
        if direction and pixels:
            move_cursor(direction, pixels)
        else:
            speak("Could not parse direction or pixels.")
        return

    # scroll
    if matches_any(spoken, "scroll_up"):
        # optional number
        m = re.search(r'(-?\d+)', spoken)
        amt = int(m.group(1)) if m else 300
        scroll_up(amt); return
    if matches_any(spoken, "scroll_down"):
        m = re.search(r'(-?\d+)', spoken)
        amt = int(m.group(1)) if m else 300
        scroll_down(amt); return

    # camera
    if matches_any(spoken, "take_photo"):
        take_photo(); return
    if matches_any(spoken, "record_video"):
        dur = parse_duration(spoken) or RECORD_VIDEO_DURATION_DEFAULT
        record_video(dur); return

    # YouTube playback controls
    if matches_any(spoken, "youtube_play_pause"):
        youtube_play_pause(); return
    if matches_any(spoken, "youtube_seek_left"):
        youtube_seek_left(5); return
    if matches_any(spoken, "youtube_seek_right"):
        youtube_seek_right(5); return

    # maps & directions
    if matches_any(spoken, "open_maps"):
        open_url("https://www.google.com/maps","Google Maps opened."); return
    if matches_any(spoken, "search_maps"):
        q = spoken
        for p in ("search on maps", "search maps for", "search maps"):
            q = q.replace(p,"")
        q = q.strip()
        if not q:
            speak("What should I search on Maps?")
            q = listen_once()
        if q:
            open_url(f"https://www.google.com/maps/search/{q.replace(' ','+')}", f"Searching Maps for {q}")
        return
    if matches_any(spoken, "directions"):
        dest = spoken
        for p in ("directions to","get directions to","directions"):
            dest = dest.replace(p,"")
        dest = dest.strip()
        if not dest:
            speak("Where to?")
            dest = listen_once()
        if dest:
            get_directions(dest)
        return

    # IP
    if matches_any(spoken, "my_ip_location"):
        my_ip_location(); return
    if matches_any(spoken, "given_ip_location"):
        speak("Please say the IP address.")
        ipaddr = listen_once()
        if ipaddr:
            location_for_ip(ipaddr)
        return

    # WhatsApp
    if matches_any(spoken, "send_whatsapp"):
        speak("Please say the full phone number with country code, for example +911234567890")
        num = listen_once()
        speak("What is the message?")
        msg = listen_once()
        if num and msg:
            send_whatsapp(num, msg)
        return

    # Email
    if matches_any(spoken, "send_email"):
        if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
            speak("Email is not configured. Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD in the script.")
            return
        speak("Who is the recipient email address?")
        addr = listen_once()
        speak("What is the subject?")
        subj = listen_once()
        speak("What should I write in the email?")
        body = listen_once()
        if addr and subj and body:
            send_email(addr, subj, body)
        return

    # fallback
    speak("Command not recognized. Say help to hear supported commands.")

# ---------------- Main always-listening loop ----------------
def main_loop():
    # greeting text requested
    speak("Greetings I am E.V.I.S-MBL Enhanced Voice Interactive System — Made By Lochan. I Am Online And Ready. ")
    while True:
        try:
            spoken = listen_once()
            if not spoken:
                continue
            process_command(spoken)
            time.sleep(0.25)  # short pause to avoid busy loop
        except KeyboardInterrupt:
            speak("Terminated by keyboard interrupt. Goodbye.")
            break
        except SystemExit:
            break
        except Exception as e:
            print("Runtime error:", e)
            speak("An error occurred, but I will continue listening.")
            time.sleep(0.5)
            continue

if __name__ == "__main__":
    main_loop()
