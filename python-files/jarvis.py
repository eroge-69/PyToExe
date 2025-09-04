import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import pyjokes
import smtplib
import os
import cv2
import wikipedia
import qrcode
import time
import requests
import pyautogui
import instaloader
from ppadb.client import Client as AdbClient
from deepface import DeepFace
import json
import subprocess
import textwrap
import sys
import numpy as np
import pygetwindow as gw
import psutil

def sptext():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            data = recognizer.recognize_google(audio)
            print(data)
            return data
        except sr.UnknownValueError:
            print("Not Understand")
def speechtx(x):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice',voices[0].id)
    rate = engine.getProperty('rate')
    engine.setProperty('rate',150)
    engine.say(x)
    engine.runAndWait()

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('abhrosaha125@gmail.com', 'qfub msjg kihp upkx')
    server.sendmail('abhrosaha125@gmail.com', to, content)
    server.close()

def generate_qr(data, filename="qrcode.png"):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)
    print(f"QR Code saved as {filename}")
    speechtx("QR Code has been generated and saved.")
def set_alarm(alarm_time):
    speechtx(f"Alarm set for {alarm_time}")
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            speechtx("Wake up! It's time!")
            print("Alarm ringing...")

            music_dir = "C:\\Users\\Abhrajeet\\Music\\music (1)"
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, songs[0]))
            break
        time.sleep(30)  

def connect_phone():
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    if len(devices) == 0:
        speechtx("No smartphone detected. Please connect your device with USB debugging enabled.")
        return None
    device = devices[0]
    speechtx("Smartphone connected successfully")
    return device

def take_screenshot(device, filename="phone_screenshot.png"):
    result = device.screencap()
    with open(filename, "wb") as f:
        f.write(result)
    speechtx("Screenshot has been saved from your phone")

def open_app(device, package_name):
    device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    speechtx(f"App {package_name} has been opened on your smartphone")

def get_location_via_ip(city = "Kolkata"):
    try:
        r = requests.get("https://ipinfo.io/json", timeout=6)
        data = r.json()
        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country", "")
        loc = data.get("loc", "")  # "lat,long"
        spoken = f"You seem to be in {city}, {region}, {country}."
        if loc:
            lat, lon = loc.split(",")
            spoken += f" Coordinates approximately latitude {lat} and longitude {lon}."
        speechtx(spoken)
        print("IP Location:", data)
        return data
    except Exception as e:
        print("Location error:", e)
        speechtx("Sorry, I could not determine your location right now.")
        return None


def take_desktop_screenshot(save_path=None):
    try:
        if save_path is None:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(os.getcwd(), f"screenshot_{ts}.png")
        img = pyautogui.screenshot()
        img.save(save_path)
        speechtx("Screenshot captured and saved.")
        print("Screenshot saved to:", save_path)
        return save_path
    except Exception as e:
        print("Screenshot error:", e)
        speechtx("Sorry, I could not take a screenshot.")
        return None


def download_instagram_dp(username):
    try:
        L = instaloader.Instaloader(
            dirname_pattern="instagram_dp",
            save_metadata=False,
            compress_json=False,
            download_video_thumbnails=False
        )
        
        L.download_profile(username, profile_pic_only=True)
        speechtx(f"Downloaded profile picture of {username}.")
        print(f"Instagram DP downloaded for {username} in the 'instagram_dp' folder.")
        return True
    except Exception as e:
        print("Instagram DP error:", e)
        speechtx("Sorry, I could not download that profile picture.")
        return False

def make_phone_call(device, number):
    try:
        device.shell(f'am start -a android.intent.action.CALL -d tel:{number}')
        speechtx(f"Calling {number} from your smartphone.")
    except Exception as e:
        print("Call error:", e)
        speechtx("Sorry, I could not make the call.")

def detect_emotion():
    cap = cv2.VideoCapture(0)
    speechtx("Looking at you now, please wait a moment.")
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        speechtx("Sorry, I could not capture your face.")
        return

    try:
        
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        
        
        if dominant_emotion == "happy":
            speechtx("I see you are happy. That makes me happy too!")
        elif dominant_emotion == "sad":
            speechtx("You look sad. Don't worry, I am here for you.")
        elif dominant_emotion == "angry":
            speechtx("You seem angry. Take a deep breath, everything will be okay.")
        elif dominant_emotion == "surprise":
            speechtx("Wow, you look surprised. I hope it is good news!")
        elif dominant_emotion == "fear":
            speechtx("You look scared. But don't worry, you are safe with me.")
        else:
            speechtx(f"I sense you are feeling {dominant_emotion}. I care about you.")
        
        print("Detected Emotion:", dominant_emotion)
        
    except Exception as e:
        print("Emotion detection error:", e)
        speechtx("Sorry, I could not understand your emotion.")

def get_weather(city=""):
    try:
        url = f"https://wttr.in/{city}?format=3"  
        res = requests.get(url, timeout=60)
        if res.status_code == 200:
            weather = res.text.strip()
            speechtx(f"The weather in {city} is {weather}")
            print("Weather:", weather)
            return weather
        else:
            speechtx("Sorry, I could not fetch the weather right now.")
            return None
    except Exception as e:
        print("Weather error:", e)
        speechtx("Sorry, I could not get the weather.")
        return None

MEMORY_FILE = "jarvis_memory.json"

def load_memory():
    """Load user memory from file."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    """Save user memory to file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

memory = load_memory()

def remember_task(task):
    """Add a task/note to memory."""
    if "tasks" not in memory:
        memory["tasks"] = []
    memory["tasks"].append(task)
    save_memory(memory)
    speechtx(f"Okay, I will remember that {task}")

def show_tasks():
    """List all remembered tasks."""
    if "tasks" in memory and memory["tasks"]:
        speechtx("Here are your tasks:")
        for i, task in enumerate(memory["tasks"], 1):
            print(f"{i}. {task}")
            speechtx(task)
    else:
        speechtx("You have no tasks stored.")

def clear_tasks():
    """Clear all remembered tasks."""
    memory["tasks"] = []
    save_memory(memory)
    speechtx("All tasks have been cleared.")

def screen_mirror():
    try:
        speechtx("Starting screen mirroring, please wait.")
        scrcpy_path = "C:\\scrapy\\scrcpy-win64-v3.3.1\\scrcpy.exe" 
        subprocess.Popen([scrcpy_path,"--keyboard=uhid"])
    except Exception as e:
        print("Error starting screen mirroring:", e)
        speechtx("Sorry, I could not start screen mirroring.")


def phone_tap(x, y):
    os.system(f"adb shell input tap {x} {y}")
    speechtx(f"Tapping at {x}, {y}")


def phone_swipe(x1, y1, x2, y2, duration=500):
    os.system(f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}")
    speechtx("Swipe performed")


def phone_type(text):
    os.system(f'adb shell input text "{text}"')
    speechtx(f"Typed {text} on phone")

def ensure_pygame():
    try:
        import pygame  
        return True
    except ImportError:
        try:
            speechtx("Pygame not found. Installing now.")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            import pygame  
            return True
        except Exception as e:
            print("Pygame install error:", e)
            speechtx("Sorry, I could not install Pygame automatically.")
            return False

def create_snake_game(filename="snake_game.py", auto_run=True):
    if not ensure_pygame():
        return

    game_code = textwrap.dedent(r'''
    import pygame, sys, random

   
    WIDTH, HEIGHT = 600, 400
    TILE = 20
    SPEED = 10  # higher = faster

    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Jarvis Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

   
    def draw_text(surface, text, pos, color=(255,255,255)):
        surface.blit(font.render(text, True, color), pos)

    def random_cell():
        return (
            random.randrange(0, WIDTH // TILE) * TILE,
            random.randrange(0, HEIGHT // TILE) * TILE
        )

   
    snake = [(WIDTH//2, HEIGHT//2)]
    direction = (TILE, 0)  
    food = random_cell()
    score = 0
    game_over = False

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, TILE):
                    direction = (0, -TILE)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -TILE):
                    direction = (0, TILE)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (TILE, 0):
                    direction = (-TILE, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-TILE, 0):
                    direction = (TILE, 0)
                elif event.key == pygame.K_r and game_over:
                    snake = [(WIDTH//2, HEIGHT//2)]
                    direction = (TILE, 0)
                    food = random_cell()
                    score = 0
                    game_over = False

        if not game_over:
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

           
            new_head = (new_head[0] % WIDTH, new_head[1] % HEIGHT)

            
            if new_head in snake:
                game_over = True
            else:
                snake.insert(0, new_head)

                
                if new_head == food:
                    score += 1
                    food = random_cell()
                else:
                    snake.pop()

        # ---------- Draw ----------
        screen.fill((18,18,18))

        # grid (subtle)
        for x in range(0, WIDTH, TILE):
            pygame.draw.line(screen, (30,30,30), (x,0), (x,HEIGHT))
        for y in range(0, HEIGHT, TILE):
            pygame.draw.line(screen, (30,30,30), (0,y), (WIDTH,y))

        # food
        pygame.draw.rect(screen, (255,80,80), (*food, TILE, TILE))

        # snake
        for i, (x, y) in enumerate(snake):
            color = (80,200,120) if i == 0 else (60,170,100)
            pygame.draw.rect(screen, color, (x, y, TILE, TILE))

        # HUD
        draw_text(screen, f"Score: {score}", (10, 8))
        if game_over:
            draw_text(screen, "Game Over! Press R to restart", (WIDTH//2 - 170, HEIGHT//2 - 10), (255,200,0))

        pygame.display.flip()
        clock.tick(SPEED + score//5)
    ''')

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(game_code)
        print(f"Game saved to {os.path.abspath(filename)}")
        speechtx("Your Snake game has been created.")
        if auto_run:
            try:
                subprocess.Popen([sys.executable, filename])
                speechtx("Launching the game now. Have fun!")
            except Exception as e:
                print("Launch error:", e)
                speechtx("I created the game, but could not launch it.")
    except Exception as e:
        print("Write error:", e)
        speechtx("Sorry, I could not write the game file.")

def create_virtual_assistant():
    """Creates a new Python virtual assistant script."""
    assistant_code = '''import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import pyjokes

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except:
            return ""

def greet():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your mini assistant. How may I help you?")

if __name__ == "__main__":
    greet()
    while True:
        command = listen()
        if "time" in command:
            speak(datetime.datetime.now().strftime("%I:%M %p"))
        elif "youtube" in command:
            webbrowser.open("https://www.youtube.com")
        elif "google" in command:
            webbrowser.open("https://www.google.com")
        elif "joke" in command:
            speak(pyjokes.get_joke())
        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            break
'''
    try:
        with open("mini_assistant.py", "w") as f:
            f.write(assistant_code)
        print("✅ A new virtual assistant 'mini_assistant.py' has been created!")
        speechtx("I have created a new virtual assistant for you. You can run it anytime.")
    except Exception as e:
        print("Error:", e)
        speechtx("Sorry, I could not create the assistant.")

def mirror_iphone():
    try:
        lonelyscreen_path = r"C:\Program Files(x86)\LonelyScreen\LonelyScreen.exe"
        speechtx("Starting iPhone screen mirroring. Please enable AirPlay on your iPhone.")
        os.startfile(lonelyscreen_path)
        time.sleep(8)  # Wait for LonelyScreen to open

        win = None
        for w in gw.getWindowsWithTitle("LonelyScreen"):
            if w.isVisible:
                win = w
                break

        if not win:
            speechtx("Could not detect LonelyScreen window.")
            return

        speechtx("LonelyScreen is ready. Please connect your iPhone now.")

        while True:
            x, y, width, height = win.left, win.top, win.width, win.height
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            cv2.imshow("iPhone Screen", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    except Exception as e:
        speechtx("Sorry, I could not capture the iPhone screen.")
        print("Error:", e)

def check_battery():
    battery = psutil.sensors_battery()
    percent = battery.percent
    charging = battery.power_plugged

    if charging:
        if percent == 100:
            speechtx("Sir, your battery is fully charged. You can unplug the charger.")
        else:
            speechtx(f"Sir, your laptop is charging. Current battery level is {percent} percent.")
    else:
        if percent < 20:
            speechtx(f"Warning Sir! Battery is critically low at {percent} percent. Please plug in the charger.")
            power_saving_mode()
        else:
            speechtx(f"Sir, battery is at {percent} percent and not charging.")

def power_saving_mode():
    speechtx("Enabling power saving mode to conserve battery.")
    try:
        # Reduce screen brightness (Windows only, optional if supported)
        os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,30)")
        # Disable Wi-Fi (Windows)
        os.system("netsh interface set interface Wi-Fi admin=disable")
    except:
        speechtx("Sorry, I could not adjust brightness or Wi-Fi on this system.")
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >=0 and hour < 12:
        speechtx("Good Morning")
    elif hour >=12 and hour < 18  :
        speechtx("Good Afternoon")    
    else:
        speechtx("Good Evening")
    speechtx("I am Jarvis Sir, Please tell me how may I Help you")

def wake_jarvis():
    speechtx("I am awake. What should I do for you?")

if __name__ == '__main__':
    wishMe()
    if 1:
        data1 = sptext().lower()
    if 'wikipedia' in data1:
            speechtx ('Searching Wikipedia...')
            data1 = data1.replace("wikipedia","")
            results = wikipedia.summary(data1, sentences = 4)
            speechtx("According to Wikipedia")
            speechtx(results)
            print(results)

    if "wake up jarvis" in data1 or "hey jarvis" in data1:
            wake_jarvis()
    elif "your name" in data1:
        name = "My name is Jarvis"
        speechtx(name)

    elif "old are you" in data1:
        age = "I am two years old"
        speechtx(age)

    elif "time now" in data1:
        time = datetime.datetime.now().strftime("%I%M%p")
        speechtx(time)

    elif "youtube" in data1:
        webbrowser.open("https://www.youtube.com")
        speechtx("Opening Youtube")

    elif "google" in data1:
        webbrowser.open("https://www.google.com")
        speechtx("Opening Google")

    elif "dps dhaligaon" in data1:
        webbrowser.open("https://www.dpsdhaligaon.com")

    elif "jokes" in data1:
        joke_1 = pyjokes.get_joke(language="en",category="neutral")
        print(joke_1)
        speechtx(joke_1)

    elif 'play music' in data1:
        music_dir = "C:\\Users\\Abhrajeet\\Music\\music (1)"
        songs = os.listdir(music_dir)
        print(songs)
        os.startfile(os.path.join(music_dir, songs[0]))

    elif'open code' in data1:
        codePath = "C:\\Users\\Abhrajeet\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
        os.startfile(codePath)

    elif'send email' in data1:
        speechtx("What should I say?")
        content = sptext()
        to = "abhroboss125@gmail.com"
        sendEmail(to,content) 
        speechtx("Email has been sent!")

    elif'open command prompt' in data1:
        os.system('start cmd')

    elif "qr code" in data1:
        speechtx("Please tell me the text or link for the QR code")
        qrdata = sptext()
        generate_qr(qrdata, "myqrcode.png")
        speechtx("Your QR code has been generated.")

    elif "set alarm" in data1:
        speechtx("Please tell me the time to set alarm in HH:MM format, 24 hour format")
        alarm_input = sptext()
        try:
            set_alarm(alarm_input)
        except Exception as e:
            print(e)
            speechtx("Sorry, I could not set the alarm.")

    elif "smartphone" in data1:
        phone = connect_phone()

    elif "screenshot smartphone" in data1:
        phone = connect_phone()
        if phone:
            take_screenshot(phone)

    elif "open whatsapp" in data1:
        phone = connect_phone()
        if phone:
            open_app(phone, "com.whatsapp")
    
    elif "open free fire max" in data1:
        phone = connect_phone()
        if phone:
            open_app(phone, "Free Fire MAX.exe ")

    elif "find my location" in data1 or "my location" in data1:
        get_location_via_ip()

    elif "take screenshot" in data1 or "screenshot" in data1:
        take_desktop_screenshot()

    elif "download instagram profile picture" in data1 or "download instagram profile" in data1 or "instagram dp" in data1:
        speechtx("Please tell me the Instagram username.")
        uname = sptext()
        if uname:
            uname = uname.replace(" ", "")  
            download_instagram_dp(uname)
        else:
            speechtx("I did not catch the username.")

    elif "make a call" in data1 or "phone call" in data1:
        speechtx("Please tell me the phone number to call.")
        number = sptext()
        if number:
            number = number.replace(" ", "").replace("-", "")
            phone = connect_phone("192.168.1.5")  
            if phone:
                make_phone_call(phone, number)
        else:
            speechtx("I did not catch the number.")

    elif "how am i feeling" in data1 or "my emotion" in data1 or "detect my emotion" in data1:
        detect_emotion()

    elif "weather" in data1 or "forecast" in data1:
        speechtx("Please tell me the city name.")
        city = sptext()
        if city:
            get_weather(city)
        else:
            speechtx("I did not catch the city name.")

    elif "remember" in data1:
        speechtx("What should I remember?")
        task = sptext()
        if task:
            remember_task(task)

    elif "show my tasks" in data1 or "what do you remember" in data1:
        show_tasks()

    elif "clear tasks" in data1 or "forget everything" in data1:
        clear_tasks()

    elif "screen mirror" in data1 or "mirror phone" in data1:
        screen_mirror()

    elif "tap" in data1:
        phone_tap(500, 1000)   

    elif "swipe" in data1:
        phone_swipe(200, 800, 600, 800)

    elif "type message" in data1:
        phone_type("Hello_from_Jarvis")

    elif "open whatsapp" in data1:
        open_app("com.whatsapp")

    elif "open instagram" in data1:
        open_app("com.instagram")    

    elif "create game" in data1 or "make a game" in data1 or "create snake game" in data1:
        speechtx("Creating a Snake game for you.")
        create_snake_game()

    elif "launch game" in data1 or "play the game" in data1:
        try:
            subprocess.Popen([sys.executable, "snake_game.py"])
            speechtx("Launching the game.")
        except Exception as e:
            print("Launch error:", e)
            speechtx("I could not launch the game.")

    elif "create assistant" in data1 or "make assistant" in data1:
        create_virtual_assistant()

    elif "mirror my iphone" in data1 or "iphone screen" in data1:
        mirror_iphone()

    elif "battery" in data1:
        check_battery()

    elif "exit" in data1 or "quit" in data1:
        speechtx("Goodbye Sir, shutting down Jarvis.")
        sys.exit()  
    elif 'open camera' in data1:
        cap = cv2.VideoCapture(0)
        while True:
            ret, img = cap.read()
            cv2.imshow('Camera', img)
            k = cv2.waitKey(50)
            if k == 27:  
                break
        cap.release()              
        cv2.destroyAllWindows()
    
           