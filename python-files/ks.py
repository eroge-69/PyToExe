import tkinter as tk
import os
import pyperclip
import subprocess
import tempfile
import sounddevice as sd
import numpy as np
import pyttsx3
import datetime
import time
import queue
import random
import webbrowser
import psutil
import math
import requests
import json
import smtplib
import speech_recognition as sr
import wikipedia
import pyautogui
from bs4 import BeautifulSoup
from email.message import EmailMessage
from fuzzywuzzy import fuzz
import asyncio
import edge_tts
import threading
import pygame
import re
import shutil
import string
import _wmi
import platform
import pygetwindow as gw
from selenium import webdriver
import threading
import pywhatkit
import keyboard
import cv2
from PIL import Image
import easyocr
import wmi
from gpt4all import GPT4All
import pytesseract
from datetime import datetime, timedelta
# --- INITIALIZATION ---
w = wmi.WMI(namespace="root\\wmi")

# Pygame को audio के लिए initialize करें
pygame.init()
pygame.mixer.init()

# कॉन्फ़िगरेशन फ़ाइलें और सीक्रेट कोड
MEMORY_FILE = "omnix_memory.json"
TASK_FILE = "omnix_tasks.txt"
SECRET_CODE = "j" or "J" # Omnix को शुरू करने के लिए सीक्रेट कोड
global_activity_log = []
last_active_window = None
current_zoom = 100  # Starting zoom percentage





# --- MEMORY MANAGEMENT ---

def load_memory():
    """Memory फ़ाइल से डेटा लोड करता है।"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"name": "Friend"}
    return {"name": "Friend"}

def save_memory():
    """डेटा को memory फ़ाइल में सेव करता है।"""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

memory = load_memory()

# --- APPLICATION MAPPING (FOR OPEN/CLOSE) ---
# बोलकर दिए गए नामों को सिस्टम प्रोसेस नामों से मैप करता है।
APP_PROCESS_NAMES = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "notepad": "notepad.exe",
    "vscode": "Code.exe",
    "visual studio code": "Code.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "terminal": "cmd.exe", # टर्मिनल को भी मैप किया गया है
    "command prompt": "cmd.exe",
}
from fuzzywuzzy import fuzz
def change_brightness(command):
    """
    command: "increase", "decrease", or "increase 30", "decrease 20"
    """
    # Get current brightness
    try:
        output = subprocess.check_output(
            'powershell "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"',
            shell=True
        )
        current = int(output.strip())
    except:
        print("[OMNIX] Error reading current brightness. Using 50% as default.")
        current = 50

    # Parse command
    parts = command.lower().split()
    action = parts[0]
    percent_change = 10  # default change

    if len(parts) > 1:
        try:
            percent_change = int(parts[1])
        except:
            percent_change = 10

    # Adjust brightness using elif
    if action == "increase":
        new_brightness = current + percent_change
    elif action == "decrease":
        new_brightness = current - percent_change
    elif action == "set":
        new_brightness = percent_change
    else:
        print("[OMNIX] Invalid command")
        return

    # Ensure brightness stays in 0-100%
    new_brightness = max(0, min(100, new_brightness))

    # Set brightness via Windows WMI
    cmd = f'powershell "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{new_brightness})"'
    os.system(cmd)
    print(f"[OMNIX] Brightness set to {new_brightness}%")

# --- GPT4ALL INTEGRATION ---
gpt4_model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")  # एक बार ही लोड
def gpt4all_response(query):
    """
    Preloaded GPT4All model से जवाब देता है (तेज़ response के लिए)।
    """
    try:
        speak("Processing your question…")
        # पहले से लोड किए गए मॉडल के साथ chat session
        with gpt4_model.chat_session():
            response = gpt4_model.generate(prompt=query, max_tokens=250)
        print(f"GPT4ALL: {response}")
        speak(response)
        return True
    except Exception as e:
        print(f"GPT4All error: {e}")
        speak("There was a problem generating the response.")
        return False

def suggest_similar_commands(query):
    """ग़लत या अनजाने commands के लिए related suggestions देता है।"""

    known_commands = {
       
       
        "start chatting": ["whatsapp", "send message", "chat"],
        
    }

    scored_suggestions = []
    for cmd, keywords in known_commands.items():
        for keyword in keywords:
            score = fuzz.token_set_ratio(query.lower(), keyword.lower())
            if score >= 60:
                scored_suggestions.append((cmd, score))

    if scored_suggestions:
        top_matches = sorted(scored_suggestions, key=lambda x: x[1], reverse=True)[:5]
        speak("I didn't understand that exactly. Did you mean one of the following?")
        print("\n📌 Suggested Commands:")
        for match in top_matches:
            speak(match[0])
            print(" -", match[0])
    else:
        speak("Sorry, I couldn't understand that. Here are some commands you can try:")
        common = ["open chrome", "start pomodoro", "set a timer", "show my location", "create file", "take screenshot"]
        for c in common:
            speak(c)
            print(" -", c)

def smooth_zoom(target_zoom):
    """
    Smoothly zoom in or out to the target zoom level.
    """
    global current_zoom
    step = 5 if target_zoom > current_zoom else -5
    while (step > 0 and current_zoom < target_zoom) or (step < 0 and current_zoom > target_zoom):
        pyautogui.hotkey('ctrl', '+' if step > 0 else '-')
        current_zoom += step
        time.sleep(0.05)
    print(f"[OMNIX] Zoom: {current_zoom}%")

def smooth_pan(direction, degrees=50):
    """
    Smoothly pan (shift) the screen in the given direction.
    """
    amount = int(degrees)
    if direction == 'up':
        pyautogui.scroll(amount)
    elif direction == 'down':
        pyautogui.scroll(-amount)
    elif direction == 'left':
        pyautogui.keyDown('shift')
        pyautogui.scroll(amount)
        pyautogui.keyUp('shift')
    elif direction == 'right':
        pyautogui.keyDown('shift')
        pyautogui.scroll(-amount)
        pyautogui.keyUp('shift')
    print(f"[OMNIX] Shift {direction} by {amount}")

def handle_zoom_pan(query):
    """
    Detects and handles zoom or shift commands from voice query.
    """
    q = query.lower()

    # Zoom in
    if "zoom in" in q:
        percent = ''.join(filter(str.isdigit, q))
        smooth_zoom(int(percent) if percent else current_zoom + 20)

    # Zoom out
    elif "zoom out" in q:
        percent = ''.join(filter(str.isdigit, q))
        smooth_zoom(int(percent) if percent else current_zoom - 20)

    # Shift right
    elif "shift right" in q:
        degree = ''.join(filter(str.isdigit, q))
        smooth_pan('right', int(degree) if degree else 50)

    # Shift left
    elif "shift left" in q:
        degree = ''.join(filter(str.isdigit, q))
        smooth_pan('left', int(degree) if degree else 50)

    # Shift up
    elif "shift up" in q:
        degree = ''.join(filter(str.isdigit, q))
        smooth_pan('up', int(degree) if degree else 50)

    # Shift down
    elif "shift down" in q:
        degree = ''.join(filter(str.isdigit, q))
        smooth_pan('down', int(degree) if degree else 50)
            
def monitor_screen_activity():
    """This tracks screen activity every few seconds."""
    global last_active_window
    try:
        while True:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title != last_active_window:
                activity_data = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "activity": f"Switched to: {active_window.title}"
                }
                global_activity_log.append(activity_data)
                last_active_window = active_window.title
                print(f"Logged activity: {activity_data}")
            
            # Check every 5 seconds to avoid high CPU load
            time.sleep(5) 
            
    except Exception as e:
        print(f"Error in activity monitor: {e}")

def give_activity_summary():
    """Gives a summary of activities when the user asks."""
    if not global_activity_log:
        speak("Sir, I have not found any activity so far.")
        return
        
    speak("Sir, here is a summary of your recent activities.")
    summary_text = ""
    # Summarize the last 5 activities
    for i, item in enumerate(global_activity_log[-5:]):
        summary_text += f"{i+1}. {item['activity']} at {item['timestamp']}. "
        
    print(f"Summary: {summary_text}")
    speak(summary_text)            
            
def get_fan_speed():
    speeds = []
    for fan in w.MSAcpi_ThermalZoneTemperature():
        temp_c = (fan.CurrentTemperature / 10.0) - 273.15
        speeds.append(temp_c)
    return speeds

def get_cpu_temp():
    temps = psutil.sensors_temperatures()
    if "coretemp" in temps:
        core_temps = [t.current for t in temps["coretemp"]]
        return core_temps
    return []

def show_fan_info():
    cpu_temps = get_cpu_temp()
    fan_temps = get_fan_speed()

    print("CPU Temperatures:", cpu_temps)
    print("Fan Temperatures:", fan_temps)

    speak(f"Current CPU temperatures are {', '.join([str(int(t)) for t in cpu_temps])} degrees Celsius.")
    speak(f"Fan temperatures are {', '.join([str(int(t)) for t in fan_temps])} degrees Celsius.")            
def send_whatsapp_alert():
    try:
        message = "🚨 Emergency alert from Omnix! Please check immediately."
        phone = "+919671781567"  # Must include country code
        hour = time.localtime().tm_hour
        minute = (time.localtime().tm_min + 1) % 60  # Send 1 min later to allow setup
        pywhatkit.sendwhatmsg(phone, message, hour, minute, wait_time=5)
    except Exception as e:
        print("WhatsApp message failed:", e)
def read_active_window():
    try:
# Active window ka title lo
        window = gw.getActiveWindow()
        title = window.title if window else "Unknown"        
         # Select all + copy text (jitna window allow kare)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        text = pyperclip.paste()
        if text.strip():
          speak("Reading the content from your current window.")
          speak(text[:500]) # limit 500 chars
        else:
            speak(f"I couldn't copy readable text from {title}.")
    except Exception as e:
      print("Error in read_active_window:", e)
      speak("Sorry, I couldn't read this window.")        
def emergency_lock_screen():
    def lock_display():
        password = "1"
        cap = cv2.VideoCapture(0)

        while True:
            frame = np.zeros((500, 800, 3), dtype=np.uint8)
            cv2.putText(frame, "Enter password to unlock:", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            key = cv2.waitKey(1)
            if key != -1 and chr(key).isdigit():
                typed = chr(key)
                if typed == password[0]:
                    if keyboard.read_event().name == password:
                        break

            cv2.imshow("EMERGENCY LOCK", frame)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # 1. Send WhatsApp
    threading.Thread(target=send_whatsapp_alert).start()

    # 2. Lock screen full black with password
    lock_display()

    # 3. Done – unlocked
    print("🔓 Emergency lock ended.")

def activate_emergency():
    print("🚨 EMERGENCY MODE ACTIVATED")
    # Close all apps (dangerous ones only)
    os.system("taskkill /f /im chrome.exe")
    os.system("taskkill /f /im code.exe")
    os.system("taskkill /f /im explorer.exe")

    # Lock screen
    emergency_lock_screen()

            
          
def explain_visual_context():
    speak("Analyzing your current activity...")

    try:
        # Get active window title
        active_window = gw.getActiveWindow()
        window_title = active_window.title if active_window else "Unknown"
    except:
        window_title = "Unknown"

    try:
        # Capture screen data
        screenshot = pyautogui.screenshot()
        pixels = screenshot.getdata()

        # Color counters
        red, green, blue, white, dark = 0, 0, 0, 0, 0

        for pixel in pixels[::10000]:  # speed sample
            r, g, b = pixel
            if r > 200 and g > 200 and b > 200:
                white += 1
            elif r > 150 and g < 100 and b < 100:
                red += 1
            elif g > 150 and r < 100:
                green += 1
            elif r < 50 and g < 50 and b < 50:
                dark += 1
            elif b > 150 and r < 100:
                blue += 1

        # Final interpretation message
        context = ""

        title_lower = window_title.lower()

        # App-specific analysis
        if "chrome" in title_lower:
            if red > 5 and white > 10:
                context = "You are watching a video on YouTube or similar platform in Chrome."
            elif white > 20:
                context = "You are reading an article or browsing a website in Chrome."
            else:
                context = "You are using Google Chrome browser."
        elif "code" in title_lower or "visual studio" in title_lower:
            context = "You are working in Visual Studio Code, likely coding or editing a project."
        elif "explorer" in title_lower:
            context = "You are browsing files in Windows Explorer."
        elif "cmd" in title_lower or "terminal" in title_lower or "powershell" in title_lower:
            context = "You are using the command-line interface or terminal."
        elif "vlc" in title_lower or "media player" in title_lower:
            context = "You are watching a video in VLC or another media player."
        elif "notepad" in title_lower or "wordpad" in title_lower:
            context = "You are writing or reading text in a document editor."
        elif "photoshop" in title_lower:
            context = "You are editing an image in Adobe Photoshop."
        elif "paint" in title_lower:
            context = "You are drawing or editing in Microsoft Paint."
        elif "telegram" in title_lower or "whatsapp" in title_lower:
            context = "You are chatting in a messaging application."
        else:
            # Color-based guess
            if dark > 10 and green > 5:
                context = "You're working in a dark-themed editor or code tool."
            elif white > 25:
                context = "You are likely reading or working on a document or web page."
            else:
                context = "You might be using a custom or unknown application."

        speak(context)

    except Exception as e:
        speak("Sorry, I couldn't analyze the screen.")
        print(f"Error in visual context: {e}")  
                  
def omnix_device_analyzer():
    speak("Activating Omnix Smart Device Analyzer... Scanning system details now.")
    print("🔍 Omnix Smart Device Analyzer Results:\n")

    # System Info
    system = platform.uname()
    speak(f"This system is running on {system.system} {system.release}, model {system.node}")
    print(f"🖥️ Device: {system.node} | OS: {system.system} {system.release} | Version: {system.version}")
    print(f"Processor: {system.processor}\n")

    # RAM
    ram = psutil.virtual_memory().total / (1024**3)
    print(f"💾 Installed RAM: {ram:.2f} GB")

    # Battery
    battery = psutil.sensors_battery()
    if battery:
        status = "Charging" if battery.power_plugged else "Not Charging"
        print(f"🔋 Battery: {battery.percent}% | Status: {status}")
    else:
        print("🔋 Battery info not available.")

    # Disk Partitions
    print("\n💽 Storage Devices:")
    partitions = psutil.disk_partitions()
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            total = usage.total / (1024**3)
            free = usage.free / (1024**3)
            print(f"  • {p.device} ({p.fstype}) - Total: {total:.2f} GB | Free: {free:.2f} GB | Mounted at: {p.mountpoint}")
        except:
            continue

    # Network
    print("\n🌐 Network Interfaces:")
    net_if = psutil.net_if_addrs()
    for iface in net_if:
        print(f"  • Interface: {iface}")

    # Manufacturer Info (WMI)
    print("\n🏷️ System Manufacturer Info:")
    try:
        c = _wmi.WMI()
        for board in c.Win32_BaseBoard():
            print(f"  • Manufacturer: {board.Manufacturer} | Product: {board.Product}")
        for sys in c.Win32_ComputerSystem():
            print(f"  • Model: {sys.Model} | Manufacturer: {sys.Manufacturer}")
    except Exception as e:
        print("  • Error getting manufacturer info:", e)

    # Installed Applications
    print("\n📦 Installed Applications:")
    try:
        apps = os.popen("wmic product get name,version").read()
        print(apps)
    except:
        print("  • Could not retrieve application list.")

    # Downloads Folder Info
    print("\n📥 Downloads Folder Scan:")
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    try:
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(downloads_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
                file_count += 1
        total_size_gb = total_size / (1024**3)
        print(f"  • Total Files: {file_count} | Size: {total_size_gb:.2f} GB")
    except:
        print("  • Could not scan Downloads folder.")

    speak("System scan complete. All details are available in your terminal window.")            


def speak_silent(text):
    print("[Omnix Silent Listener]:", text)
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def get_noise_level(duration=2):
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1)
    sd.wait()
    volume_norm = np.linalg.norm(recording)
    return volume_norm

def play_calm_music():
    try:
        os.startfile("calm_music.mp3")  # change to actual music file
    except:
        speak_silent("Calm music not found.")

def analyze_environment():
    noise = get_noise_level()
    if noise < 0.5:
        mood = "Very Quiet"
        speak_silent(random.choice([
            "Are you feeling okay?",
            "Would you like to listen to something calming?",
            "It seems very quiet around."
        ]))
        play_calm_music()
    elif 0.5 <= noise < 3:
        mood = "Calm"
        speak_silent("The environment seems calm and peaceful.")
    elif 3 <= noise < 7:
        mood = "Normal Noise"
        speak_silent("Seems like a normal environment.")
    else:
        mood = "Noisy"
        speak_silent("It's a bit noisy here. Stay focused.")
    print("Detected Volume:", round(noise, 2), "| Mood:", mood)

def start_silent_listener():
    speak_silent("Omnix is silently listening to your environment.")
    for _ in range(5):
        analyze_environment()
        time.sleep(5)



# बोलकर दिए गए नामों को वेबसाइटों से मैप करता है।
WEBSITE_MAP = {
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "snapchat": "https://www.snapchat.com",
    "google": "https://www.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "github": "https://www.github.com",
    "facebook": "https://www.facebook.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
}

# --- JOKES LIST ---
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I'm reading a book on anti-gravity. It's impossible to put down!",
    "What do you call a fake noodle? An impasta!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "I told my wife she should embrace her mistakes. She gave me a hug.",
    "Why do we tell actors to 'break a leg?' Because every play has a cast!",
    "What do you call a snowman with a six-pack? An abdominal snowman!",
    "Why can't a bicycle stand on its own? Because it's two tired!",
]

# --- QUOTES LIST ---
QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "The best way to predict the future is to create it. - Peter Drucker",
    "The secret of getting ahead is getting started. - Mark Twain",
    "You miss 100% of the shots you don't take. - Wayne Gretzky",
    "The only impossible journey is the one you never begin. - Tony Robbins",
]

# --- CORE FUNCTIONS ---
def greet():
    """शुरुआत में एक स्वागत संदेश बोलता है।"""
    speak("Hello, I am Omnix. How may I assist you today?")

async def async_speak(text, voice='en-US-AriaNeural'):
    """Edge-TTS का उपयोग करके भाषण उत्पन्न करने और चलाने के लिए एसिंक्रोनस फ़ंक्शन।"""
    print(f"\nOMNIX: {text}\n")
    try:
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_path = temp_file.name

        await communicate.save(temp_path)

        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        os.remove(temp_path)
    except Exception as e:
        print(f"Error in async_speak: {e}")

def speak(text):
    """टेक्स्ट को भाषण में बदलता है और उसे बोलता है।"""
    asyncio.run(async_speak(text))

def play_startup_sound():
    """स्टार्टअप पर एक साधारण ध्वनि बजाता है।"""
    try:
        # यहाँ एक सिमुलेटेड स्टार्टअप ध्वनि है।
        # आप इसे अपनी खुद की MP3 फ़ाइल से बदल सकते हैं।
        speak("Omnix is online.")
    except Exception as e:
        print(f"Startup sound error: {e}")


def listen():
    """
    यूज़र की आवाज़ सुनता है और उसे टेक्स्ट में बदलता है।
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("Timeout. कृपया फिर से कोशिश करें।")
            return ""

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-US').lower()
        print(f"You said: {query}\n")
        return query
    except sr.UnknownValueError:
        print("Sorry, मैं आपकी बात नहीं समझ पाया।")
        return ""
    except sr.RequestError as e:
        print(f"Google Speech Recognition service से परिणाम नहीं मिल पाए; {e}")
        return ""
    except Exception as e:
        print(f"एक अज्ञात त्रुटि हुई: {e}")
        return ""
GEMINI_API_KEY = "AIzaSyBWbYk44psFGYQxfqL6r8YzWVVUOT75b8g"  # <-- Yaha apni key daalo   
def gemini_reply(query):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {"parts": [{"text": query}]}
        ]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            text_reply = " ".join(part.get("text", "").strip() for part in parts)
            return text_reply if text_reply else None
        else:
            return None
    except Exception as e:
        print("[Gemini Error]", e)
        return None

# --- COMMAND AND QUERY HANDLING ---
def fallback_answer(query):
    print("[DEBUG] fallback_answer CALLED with query:", query)

    # --- 1. Try Gemini API first ---
    gemini_text = gemini_reply(query)
    if gemini_text:
        speak(gemini_text)
        return True

    # --- 2. Try GPT4All (Offline) ---
    if gpt4all_response(query):
        return True
    
    # --- 3. Try Perplexity (Online) ---
    try:
        print("Searching Perplexity...")
        url = f"https://www.perplexity.ai/search?q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find("p")
            if result and result.text.strip():
                speak(result.text.strip())
                return True
    except Exception as e:
        print("Perplexity error:", e)

    # --- 4. Try Wikipedia (Online) ---
    try:
        print("Searching Wikipedia...")
        summary = wikipedia.summary(query, sentences=2, auto_suggest=False)
        speak(summary)
        return True
    except wikipedia.exceptions.PageError:
        print("No page found on Wikipedia.")
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation issue: {e}")
        try:
            summary = wikipedia.summary(e.options[0], sentences=2)
            speak(summary)
            return True
        except Exception:
            pass
    except Exception as e:
        print("Wikipedia error:", e)

    # --- 5. Try Google Scraped Result (Online) ---
    try:
        print("Searching Google...")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        result = (
            soup.find("div", class_="BNeawe iBp4i AP7Wnd") or
            soup.find("div", class_="BNeawe tAd8D AP7Wnd") or
            soup.find("div", class_="BNeawe s3v9rd AP7Wnd")
        )
        if result and result.text.strip():
            speak(result.text.strip())
            return True
    except Exception as e:
        print("Google error:", e)

    # --- 6. Try Omnix Memory Search (Local) ---
    try:
        print("Searching in Omnix memory...")
        for key, value in memory.items():
            if query.lower() in key.lower() or query.lower() in str(value).lower():
                speak(f"I found something in my memory about {query}: {value}")
                return True
    except Exception as e:
        print("Memory search error:", e)

    # --- 7. Nothing Found ---
    speak(f"I'm sorry, I don't have any data about {query}.")
    return False


def give_introduction():
    introductions = [
        "Hey there! I'm Omnix, the intelligent AI assistant created by Kartik. "
        "I'm here to organize, automate, and power up Kartik's digital world with speed and precision.",

        "Hello! I’m Omnix, a next-generation virtual assistant built by Kartik. "
        "I can handle tasks, find information, and keep things running smoothly—always ready to help Kartik shine.",

        "Hi! I’m Omnix, Kartik’s personal AI companion. "
        "Designed for smart automation, creative problem-solving, and a touch of futuristic tech, I make Kartik’s life easier and smarter.",

        "Greetings! I am Omnix, Kartik’s advanced AI partner. "
        "From managing tasks to understanding context and adapting quickly, I’m built to keep Kartik ahead of the curve.",

        "Hello world! Omnix here—crafted by Kartik to be more than just an assistant. "
        "I’m his digital ally, blending intelligence, adaptability, and efficiency into everything I do."
    ]
    intro = random.choice(introductions)
    speak(intro)

# --- NEW ADVANCED FEATURES (Added 20) ---

def open_website(command):
    """
    Parses the command to extract the website name and opens it in the browser.
    Example command: "open website youtube"
    """
    website = command.replace('open website','').strip()
    if website:
        url = f"https://www.{website.replace(' ','')}.com"
        speak(f"Opening {website}")
        webbrowser.open(url)
    else:
        speak("Please provide the website name.")
def start_pomodoro_timer():
    """एक पोमोडोरो टाइमर शुरू करता है (25 मिनट काम, 5 मिनट ब्रेक)।"""
    speak("Starting Pomodoro timer. 25 minutes of focus time. I'll let you know when it's break time.")
    time.sleep(25 * 60)
    speak("25 minutes are up! It's time for a 5 minute break.")
    time.sleep(5 * 60)
    speak("Break time is over. Time to get back to work.")

def get_ip_address():
    """यूज़र का पब्लिक IP एड्रेस बताता है।"""
    try:
        ip = requests.get('https://api.ipify.org').text
        speak(f"Your public IP address is {ip}.")
    except Exception as e:
        print(f"IP address error: {e}")
        speak("I could not retrieve the IP address at this moment.")

def empty_recycle_bin():
    """सिर्फ Windows पर रीसायकल बिन को खाली करता है।"""
    if os.name == 'nt':
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            speak("Recycle Bin has been emptied successfully.")
        except ImportError:
            speak("Winshell module is not installed. Please install it using 'pip install winshell'.")
        except Exception as e:
            print(f"Recycle bin error: {e}")
            speak("There was an error while trying to empty the Recycle Bin.")
    else:
        speak("This command is only available on Windows systems.")

def tell_horoscope():
    """एक सिमुलेटेड राशिफल बताता है।"""
    horoscopes = [
        "Today, you will find a hidden talent you didn't know you had.",
        "A great opportunity is on its way. Stay positive and be ready!",
        "Be careful with new beginnings. They might not be what they seem.",
        "Your hard work will pay off today. Expect good news.",
    ]
    speak(random.choice(horoscopes))

import xml.etree.ElementTree as ET
GENERAL_FEEDS = [
    "https://feeds.feedburner.com/ndtvnews-top-stories",
    "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
]

TOPIC_FEEDS = {
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espn.com/espn/rss/news"
    ],
    "technology": [
        "https://feeds.feedburner.com/ndtvnews-technology",
        "http://feeds.bbci.co.uk/news/technology/rss.xml"
    ],
    "business": [
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    ],
    "entertainment": [
        "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://www.hindustantimes.com/feeds/rss/entertainment/rssfeed.xml"
    ],
    "world": [
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "cricket": [
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"
    ]
}

def fetch_rss_headlines(feed_urls, count=5):
    """Fetch headlines from RSS URLs using requests and ElementTree."""
    random.shuffle(feed_urls)
    headlines = []
    for url in feed_urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            # RSS items are usually under channel/item/title
            for item in root.findall(".//item/title")[:count]:
                title = item.text.strip()
                if title not in headlines:
                    headlines.append(title)
                    if len(headlines) >= count:
                        return headlines
        except Exception as e:
            print(f"Feed error for {url}: {e}")
            continue
    return headlines

def get_news_headlines(topic=None):
    """Fetch general or topic-specific headlines."""
    if topic:
        topic = topic.lower().strip()
        feeds = TOPIC_FEEDS.get(topic)
        if not feeds:
            speak(f"'{topic}' Specific feed not found, playing latest headlines instead..")
            feeds = GENERAL_FEEDS
        headlines = fetch_rss_headlines(feeds)
    else:
        headlines = fetch_rss_headlines(GENERAL_FEEDS)

    if headlines:
        intro = (f"{topic.capitalize()} news:" if topic else "Today's latest news:")
        print(intro)
        speak(intro)
        for i, headline in enumerate(headlines, start=1):
            print(f"{i}. {headline}")
            speak(headline)
    else:
        speak("Koi headlines abhi available nahi hai.")
def analyze_screen():
    last_window = ""
    last_text = ""

    while True:
        try:
            # Get active window
            active_window = gw.getActiveWindow()
            window_title = active_window.title if active_window else "Unknown window"

            # Only announce if window changed
            if window_title != last_window:
                last_window = window_title
                message = f"You are now on {window_title}."
                print(message)
                speak(message)

            # Take screenshot of active window
            if active_window:
                bbox = (active_window.left, active_window.top, active_window.right, active_window.bottom)
                screenshot = pyautogui.screenshot(region=bbox)
                text = pytesseract.image_to_string(screenshot).strip()

                # Only announce new text
                if text and text != last_text:
                    last_text = text[:200]  # limit text to first 200 chars
                    message = f"Screen shows: {last_text}..."
                    print(message)
                    speak(message)

            time.sleep(3)  # check every 3 seconds
        except Exception as e:
            print("Screen analysis error:", e)
            time.sleep(5)
def start_live_screen_analysis():
    t = threading.Thread(target=analyze_screen, daemon=True)
    t.start()                        
def open_terminal():
    """सिस्टम टर्मिनल को खोलता है।"""
    try:
        if os.name == 'nt':
            os.startfile("cmd.exe")
        elif os.name == 'posix':
            subprocess.Popen(['open', '-a', 'Terminal']) # macOS
            subprocess.Popen(['gnome-terminal']) # Ubuntu/Linux
        speak("Opening the system terminal.")
    except Exception as e:
        print(f"Terminal error: {e}")
        speak("I could not open the terminal.")

def type_text(query):
    """यूज़र द्वारा दिए गए टेक्स्ट को टाइप करता है।"""
    match = re.search(r'type (.+)', query)
    if match:
        text_to_type = match.group(1).strip()
        speak("Typing your text now.")
        pyautogui.write(text_to_type, interval=0.1)
    else:
        speak("Please specify what you want me to type.")

def scroll_page(query):
    """पेज को ऊपर या नीचे स्क्रॉल करता है।"""
    if "scroll down" or "next" in query:
        pyautogui.scroll(-500)
        speak("Scrolling down.")
    elif "scroll up"  or "back" in query:
        pyautogui.scroll(500)
        speak("Scrolling up.")
    else:
        speak("Please specify scroll direction, for example: 'scroll down'.")

def set_alarm(query):
    """एक साधारण अलार्म सेट करता है।"""
    match = re.search(r'set an alarm for (.+)', query)
    if match:
        time_str = match.group(1).strip()
        try:
            alarm_time = datetime.datetime.strptime(time_str, '%I:%M %p')
            current_time = datetime.datetime.now()
            # आज के लिए अलार्म सेट करें
            alarm_datetime = current_time.replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)
            if alarm_datetime < current_time:
                alarm_datetime += datetime.timedelta(days=1)
            
            time_to_wait = (alarm_datetime - current_time).total_seconds()
            
            speak(f"Alarm set for {alarm_time.strftime('%I:%M %p')}. I will wake you then.")
            time.sleep(time_to_wait)
            speak("Attention! Your alarm is going off!")
        except ValueError:
            speak("Invalid time format. Please use a format like '10:30 AM'.")
    else:
        speak("Please tell me the time for the alarm.")

def play_random_sound():
    """एक रैंडम ध्वनि प्रभाव बजाता है।"""
    sounds = ["sound_effect_1.mp3", "sound_effect_2.mp3", "sound_effect_3.mp3"] # ये फ़ाइलें होनी चाहिए
    sound_file = random.choice(sounds)
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error:
        speak("I am sorry, the sound file could not be played.")

def get_password():
    """एक मजबूत, रैंडम पासवर्ड उत्पन्न करता है।"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(12))
    speak(f"Here is a new password for you: {password}")
    pyautogui.write(password) # पासवर्ड को सीधे टाइप करें
    speak("The password has also been automatically typed for your convenience.")

def copy_to_clipboard(query):
    """बोले गए टेक्स्ट को क्लिपबोर्ड पर कॉपी करता है।"""
    match = re.search(r'copy (.+?) to clipboard', query)
    if match:
        text_to_copy = match.group(1).strip()
        pyautogui.write(text_to_copy) # पहले टेक्स्ट लिखें
        pyautogui.hotkey('ctrl', 'a') # सब कुछ चुनें
        pyautogui.hotkey('ctrl', 'c') # फिर कॉपी करें
        speak("The text has been copied to your clipboard.")
    else:
        speak("Please specify what text you want me to copy.")

def paste_from_clipboard():
    """क्लिपबोर्ड से टेक्स्ट पेस्ट करता है।"""
    speak("Pasting from clipboard.")
    pyautogui.hotkey('ctrl', 'v')

def rename_file_or_folder(query):
    """डेस्कटॉप पर एक फ़ाइल या फ़ोल्डर का नाम बदलता है।"""
    match = re.search(r'rename (.+?) to (.+)', query)
    if match:
        old_name = match.group(1).strip()
        new_name = match.group(2).strip()
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        old_path = os.path.join(desktop_path, old_name)
        new_path = os.path.join(desktop_path, new_name)
        
        if os.path.exists(old_path):
            try:
                os.rename(old_path, new_path)
                speak(f"Successfully renamed {old_name} to {new_name}.")
            except Exception as e:
                print(f"Rename error: {e}")
                speak("I was unable to rename the file or folder.")
        else:
            speak(f"I could not find a file or folder named {old_name} on the desktop.")
    else:
        speak("Please specify the old name and the new name, for example: 'rename my file to my new file'.")

def move_file_or_folder(query):
    """एक फ़ाइल या फ़ोल्डर को एक स्थान से दूसरे स्थान पर ले जाता है।"""
    match = re.search(r'move (.+?) to (.+)', query)
    if match:
        item_to_move = match.group(1).strip()
        destination = match.group(2).strip()
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        source_path = os.path.join(desktop_path, item_to_move)
        destination_path = os.path.join(desktop_path, destination)
        
        if os.path.exists(source_path) and os.path.exists(destination_path) and os.path.isdir(destination_path):
            try:
                shutil.move(source_path, destination_path)
                speak(f"Successfully moved {item_to_move} to {destination}.")
            except Exception as e:
                print(f"Move error: {e}")
                speak("I was unable to move the item.")
        else:
            speak("I could not find the item to move or the destination folder on the desktop.")
    else:
        speak("Please specify what to move and where to move it, for example: 'move my file to new folder'.")


def read_article_summary(query):
    """URL से एक लेख का सारांश पढ़ता है।"""
    match = re.search(r'read article from (.+)', query)
    if match:
        url = match.group(1).strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, 'html.parser')
            # <p> टैग के भीतर पहले 3 पैराग्राफ खोजें
            paragraphs = soup.find_all('p')
            summary = "\n".join([p.get_text() for p in paragraphs[:3]])
            if summary:
                speak("Here is a summary from the article:")
                speak(summary)
            else:
                speak("I couldn't find a clear summary on that page.")
        except Exception as e:
            print(f"Article summary error: {e}")
            speak("I encountered an error trying to read the article.")
    else:
        speak("Please provide a URL for me to read.")

def search_images(query):
    """Google Images पर छवियों की खोज करता है।"""
    match = re.search(r'search images for (.+)', query)
    if match:
        topic = match.group(1).strip()
        search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}&tbm=isch"
        webbrowser.open(search_url)
        speak(f"Searching for images of {topic} on Google.")
    else:
        speak("Please specify a topic for image search.")

def open_app_with_arg(query):
    """आर्गुमेंट के साथ एक एप्लिकेशन खोलता है।"""
    match = re.search(r'open (.+?) with (.+)', query)
    if match:
        app_name = match.group(2).strip()
        arg = match.group(1).strip()
        executable = APP_PROCESS_NAMES.get(app_name, app_name)
        if os.name == 'nt' and not executable.endswith('.exe'):
            executable += '.exe'
        
        try:
            subprocess.Popen([executable, arg])
            speak(f"Launching {app_name} with the argument {arg}.")
        except FileNotFoundError:
            speak(f"Application {app_name} not found.")
        except Exception as e:
            print(f"Error opening app with argument: {e}")
            speak("An error occurred while trying to open the application.")
    else:
        speak("Please specify an application and an argument.")


def find_and_delete_file(query):
    """डेस्कटॉप पर एक फ़ाइल खोजता है और यूज़र से पुष्टि के बाद उसे हटाता है।"""
    match = re.search(r'find and delete (.+)', query)
    if not match:
        speak("Please specify the file to find and delete.")
        return
        
    filename = match.group(1).strip()
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)

    if os.path.exists(file_path):
        speak(f"I found the file {filename}. Are you sure you want to delete it? Say yes to proceed or no to cancel.")
        response = listen()
        if "yes" in response:
            try:
                os.remove(file_path)
                speak(f"File {filename} has been deleted.")
            except Exception as e:
                speak(f"There was an error deleting the file: {e}")
        else:
            speak("File deletion cancelled.")
    else:
        speak(f"File {filename} was not found on the desktop.")


def read_aloud(query):
    """किसी फ़ाइल की सामग्री को पढ़कर सुनाता है।"""
    match = re.search(r'read file (.+?)\s*(from desktop)?$', query)
    if not match:
        speak("Please specify the file name you want me to read.")
        return
    
    filename = match.group(1).strip()
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            speak(f"Reading the contents of {filename}.")
            speak(content)
        except Exception as e:
            speak(f"There was an error trying to read the file: {e}")
    else:
        speak(f"File not found. I cannot locate {filename} on the desktop.")

def vision_mode():
    while True:
        speak("Scanning your surroundings, please wait.")
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if not ret:
            speak("I could not access the camera.")
            cap.release()
            return
        
        # Save snapshot (optional)
        cv2.imwrite("scan_result.jpg", frame)
        
        # --- Object detection (basic placeholder) ---
        # In future we can use AI model, for now just detect if face exists
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            speak(f"I detected {len(faces)} person in front of you.")
        else:
            speak("I could not detect a person. Probably objects are in front of you.")
        
        cap.release()
        cv2.destroyAllWindows()

        # Ask if scan again
        speak("Do you want me to scan again? Say yes or no.")
        answer = listen()
        if "yes" in answer:
            continue
        else:
            speak("Okay, vision mode deactivated.")
            break
def write_to_file(query):
    """बोले गए टेक्स्ट को डेस्कटॉप पर एक फ़ाइल में लिखता है।"""
    match = re.search(r'write (.+?) to file (.+?)\s*(on desktop)?$', query)
    if not match:
        speak("Please tell me what to write and what to name the file.")
        return

    content_to_write = match.group(1).strip()
    filename = match.group(2).strip()
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_to_write)
        speak(f"I have successfully written the content to {filename} on your desktop.")
    except Exception as e:
        speak(f"There was an error writing to the file: {e}")


def control_system_volume(query):
    """सिस्टम वॉल्यूम को नियंत्रित करता है।"""
    volume_up = re.search(r'volume up|increase volume', query)
    volume_down = re.search(r'volume down|decrease volume', query)
    mute = re.search(r'mute|silence', query)
    
    if volume_up:
        pyautogui.press('volumeup')
        speak("Volume increased.")
    elif volume_down:
        pyautogui.press('volumedown')
        speak("Volume decreased.")
    elif mute:
        pyautogui.press('volumemute')
        speak("Volume muted.")
    else:
        speak("I am sorry, I could not understand the volume command.")


def list_running_processes():
    """वर्तमान में चल रहे सभी प्रक्रियाओं को सूचीबद्ध करता है।"""
    speak("Scanning for all active processes. This may take a moment.")
    processes = [p.info['name'] for p in psutil.process_iter(['name'])]
    
    if processes:
        unique_processes = sorted(list(set(processes)))
        speak("Here are some of the running applications:")
        for proc in unique_processes[:10]: # Top 10 processes को ही बोलें ताकि बहुत ज़्यादा लंबा न हो
            speak(proc.split('.exe')[0])
    else:
        speak("No running processes detected.")


def read_tasks():
    """TASK_FILE से सभी शेड्यूल्ड टास्क को पढ़कर सुनाता है।"""
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r', encoding='utf-8') as f:
            tasks = f.readlines()
        
        if tasks:
            speak("Here are your scheduled tasks:")
            for i, task in enumerate(tasks):
                speak(f"Task number {i + 1}: {task.strip()}")
        else:
            speak("You have no tasks scheduled at the moment.")
    else:
        speak("Task file not found. You have no tasks scheduled.")


# --- FEATURE FUNCTIONS ---

def realistic_youtube_intent(query):
    """
    यह फ़ंक्शन फ़ज़ी मैचिंग का उपयोग करके YouTube के लिए इरादे को पहचानता है।
    """
    print(f"Checking for YouTube intent with query: '{query}'")
    intent_map = {
        "funny videos": ["i am bored", "i want to laugh", "make me laugh", "something funny", "feeling bored"],
        "motivational videos": ["feeling down", "give up", "i need motivation", "inspire me", "motivate me"],
        "relaxing music": ["relaxing music", "calm music", "i need to relax", "peaceful music", "feeling stressed"],
        "party dance music": ["dance music", "party songs", "let's party", "dj songs", "get this party started"],
        "study music": ["study music", "focus music", "concentration music", "i need to study"],
        "wake up sound": ["wake me up", "alarm sound", "good morning", "time to wake up"]
    }

    for topic, phrases in intent_map.items():
        for phrase in phrases:
            score = fuzz.token_set_ratio(phrase.lower(), query.lower())
            print(f"  - Matching '{phrase}' with '{query}': Score = {score}")
            if score >= 80:  # लचीला मिलान थ्रेशोल्ड 80 पर सेट किया गया है
                print(f"  - Match found! Opening YouTube for '{topic}'.")
                url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
                webbrowser.open(url)
                speak(f"You seem to need {topic}. Launching it now.")
                return True
    return False

def set_timer(query):
    """वॉइस कमांड से एक टाइमर सेट करता है।"""
    match = re.search(r'(\d+)\s*(minutes|seconds|minute|second)', query)
    if not match:
        speak("I couldn't find a valid time for the timer.")
        return

    duration = int(match.group(1))
    unit = match.group(2)

    if "minute" in unit:
        duration_in_seconds = duration * 60
    else:
        duration_in_seconds = duration

    speak(f"Setting timer for {duration} {unit}. I will notify you when the time is up.")
    time.sleep(duration_in_seconds)
    speak(f"Your timer for {duration} {unit} is complete.")
    

def set_name():
    """यूज़र का नाम सेट करता है और उसे मेमोरी में सेव करता है।"""
    speak("Please state your name.")
    user_name = listen()
    if user_name:
        memory['name'] = user_name.capitalize()
        save_memory()
        speak(f"Your name has been updated to {memory['name']}. Access granted.")
    else:
        speak("I could not get your name. Please try again.")

def calculate(query):
    """बोले गए गणितीय प्रश्न का विश्लेषण करता है और परिणाम की गणना करता है।"""
    replacements = {
        " plus ": "+", " minus ": "-", " times ": "*", " multiplied by ": "*",
        " divided by ": "/", " to the power of ": "**", " power ": "**",
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0"
    }

    expression = query.replace("calculate", "").strip()
    for word, symbol in replacements.items():
        expression = expression.replace(word, symbol)

    allowed_chars = "0123456789+-*/.() "
    sanitized_expression = "".join(filter(lambda char: char in allowed_chars, expression))

    if not sanitized_expression:
        speak("Calculation query is invalid. Please try again.")
        return

    try:
        result = eval(sanitized_expression)
        speak(f"The result of your calculation is {result}")
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
        print(f"Calculation error: {e}")
        speak("Calculation protocol failed. The expression could not be processed.")
    except Exception as e:
        print(f"An unknown calculation error occurred: {e}")
        speak("An unknown error occurred during the calculation protocol.")

def open_app(app_name):
    """एक एप्लिकेशन या उसकी वेबसाइट खोलता है।"""
    app_name = app_name.lower().strip()

    if app_name in WEBSITE_MAP:
        try:
            webbrowser.open(WEBSITE_MAP[app_name])
            speak(f"Initializing network access for {app_name}. Please wait.")
            return
        except Exception:
            speak(f"Sorry, I could not initiate network access for {app_name}.")
            return

    executable = APP_PROCESS_NAMES.get(app_name, app_name)
    if os.name == 'nt' and not executable.endswith('.exe'):
        executable += '.exe'

    try:
        if os.name == 'nt':
            os.startfile(executable)
        elif os.name == 'posix':
            subprocess.Popen(['open', '-a', executable])
        speak(f"Launching {app_name}. Please stand by.")
    except FileNotFoundError:
        speak(f"Application {app_name} not found in local directories. Initiating network search protocol.")
        webbrowser.open(f'https://www.google.com/search?q={app_name}')
    except Exception as e:
        print(f"An error occurred while trying to open the application: {e}")
        speak(f"An error occurred during the launch of {app_name}.")

def search_on_app(topic, app_name):
    """एक ऐप खोलता है और एक विषय की खोज करता है।"""
    speak(f"Initializing search protocol for {topic} on {app_name}.")
    open_app(app_name)
    time.sleep(5)

    try:
        pyautogui.write(topic, interval=0.1)
        pyautogui.press('enter')
        speak(f"Search protocol complete. Results for {topic} are now displayed in {app_name}.")
    except Exception as e:
        speak(f"Search protocol failed for {app_name}. Please check the system logs.")
        print(f"PyAutoGUI error: {e}")

def close_app(app_name):
    """एक एप्लिकेशन को बंद करता है।"""
    app_name = app_name.lower()
    process_name = APP_PROCESS_NAMES.get(app_name, app_name)
    if os.name == 'nt' and not process_name.endswith('.exe'):
        process_name += '.exe'

    closed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                proc.kill()
                closed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    speak(f"Termination protocol successful. {app_name} has been closed." if closed else f"Termination protocol failed. {app_name} was not running.")

def auto_write_note(topic):
    """एक विषय पर एक नोट बनाता है और उसे डेस्कटॉप पर सहेजता है।"""
    speak(f"Activating note creation protocol for {topic}")
    try:
        text = wikipedia.summary(topic, sentences=5)
    except Exception as e:
        print(f"Could not get content from Wikipedia for the note: {e}")
        text = f"Data not found on the topic: '{topic}' in the historical archives."

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, f"Note_{topic.replace(' ', '_')}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    speak("The data stream has been saved to a file on your Desktop.")

def send_email(to, subject, body):
    """एक ईमेल भेजता है।"""
    SENDER_EMAIL = "your_email@gmail.com"
    SENDER_PASSWORD = "your_app_password"

    if SENDER_EMAIL == "your_email@gmail.com" or SENDER_PASSWORD == "your_app_password":
        speak("The email sub-system is not configured. Please update the configuration files.")
        return

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        speak("Transmission protocol successful. Your message has been sent.")
    except smtplib.SMTPAuthenticationError:
        speak("Transmission protocol failed due to authentication error. Please verify your credentials.")
    except Exception as e:
        print(f"Email error: {e}")
        speak("An unknown error occurred during the transmission protocol.")

def system_info(query):
    """सिस्टम की जानकारी प्रदान करता है।"""
    if "battery" in query:
        battery = psutil.sensors_battery()
        if battery:
            speak(f"Power levels are at {battery.percent} percent. The power source is {'connected' if battery.power_plugged else 'unconnected'}.")
        else:
            speak("No integrated power source detected.")
    elif "ram" in query:
        ram = psutil.virtual_memory()
        speak(f"RAM usage is currently at {ram.percent} percent of total capacity.")
    elif "cpu" in query:
        cpu_percent = psutil.cpu_percent()
        speak(f"CPU load is at {cpu_percent} percent.")
    elif "internet" in query:
        try:
            requests.get("https://www.google.com", timeout=5)
            speak("Connectivity check complete. The system is online.")
        except (requests.ConnectionError, requests.Timeout):
            speak("Connectivity check failed. The system appears to be offline.")

def schedule_task(text):
    """एक कार्य को फ़ाइल में सहेजता है।"""
    with open(TASK_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - {text}\n")
    speak("Task received. It has been logged in your data banks.")

def clear_tasks():
    """सभी शेड्यूल्ड टास्क को हटा देता है।"""
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        f.write("")
    speak("All scheduled tasks have been cleared.")

def chrome_control(query):
    """Chrome ब्राउज़र को नियंत्रित करता है।"""
    commands = {
        "new tab": ('ctrl', 't'), "close tab": ('ctrl', 'w'),
        "next tab": ('ctrl', 'tab'), "previous tab": ('ctrl', 'shift', 'tab'),
        "pause": 'k', "play": 'k', "skip": 'l', "forward": 'l', "back": 'j',
        "volume up": 'volumeup', "volume down": 'volumedown', "mute": 'm',
        "speed up": ('shift', '.'), "slow down": ('shift', ',')
    }

    for command, key in commands.items():
        if command in query:
            if isinstance(key, tuple):
                pyautogui.hotkey(*key)
            else:
                pyautogui.press(key)
            speak(f"Executing command: {command.capitalize()}.")
            return True
    return False



def tell_joke():
    """JOKES सूची से एक रैंडम चुटकुला सुनाता है।"""
    speak(random.choice(JOKES))

def random_quote():
    """QUOTES सूची से एक रैंडम कोटेशन सुनाता है।"""
    speak(random.choice(QUOTES))

def get_time():
    """वर्तमान समय बताता है।"""
    now = datetime.datetime.now()
    speak(f"The current time is {now.strftime('%I:%M %p')}.")

def get_date():
    """वर्तमान तारीख बताता है।"""
    today = datetime.date.today()
    speak(f"Today's date is {today.strftime('%B %d, %Y')}.")

def create_file(filename):
    """डेस्कटॉप पर एक नई फ़ाइल बनाता है।"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)
    try:
        with open(file_path, 'w') as f:
            f.write(f"This file was created by Omnix on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}.")
        speak(f"File creation successful. A new file named {filename} has been created on the desktop.")
    except Exception as e:
        speak(f"File creation protocol failed. An error occurred: {e}")

def create_folder(folder_name):
    """डेस्कटॉप पर एक नया फ़ोल्डर बनाता है।"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_path = os.path.join(desktop_path, folder_name)
    try:
        os.makedirs(folder_path)
        speak(f"Folder creation successful. A new folder named {folder_name} has been created on the desktop.")
    except FileExistsError:
        speak(f"Folder already exists. I cannot create {folder_name} again.")
    except Exception as e:
        speak(f"Folder creation protocol failed. An error occurred: {e}")

def delete_file(filename):
    """डेस्कटॉप से एक फ़ाइल हटाता है।"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            speak(f"File termination successful. {filename} has been deleted from the desktop.")
        except Exception as e:
            speak(f"File termination protocol failed. An error occurred: {e}")
    else:
        speak(f"File not found. I cannot locate {filename} on the desktop.")

def delete_folder(folder_name):
    """डेस्कटॉप से एक फ़ोल्डर हटाता है।"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_path = os.path.join(desktop_path, folder_name)
    if os.path.exists(folder_path):
        try:
            os.rmdir(folder_path)
            speak("I can only delete empty folders. Please clear the folder first.")
        except OSError:
            speak("I can only delete empty folders. Please clear the folder first.")
        except Exception as e:
            speak(f"Folder termination protocol failed. An error occurred: {e}")
    else:
        speak(f"Folder not found. I cannot locate {folder_name} on the desktop.")

def find_file(filename):
    """डेस्कटॉप पर एक फ़ाइल को खोजता है।"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    for root, dirs, files in os.walk(desktop_path):
        if filename in files:
            speak(f"File {filename} found in the path {root}. Opening file location.")
            webbrowser.open(root)
            return
    speak(f"File {filename} was not found on the desktop.")

def list_files_in_directory(directory="Desktop"):
    """किसी दिए गए डायरेक्टरी में फ़ाइलों को सूचीबद्ध करता है।"""
    if directory.lower() == "desktop":
        target_path = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        speak("I can only list files on the desktop for security reasons.")
        return

    try:
        files = os.listdir(target_path)
        if files:
            file_list = ", ".join(files)
            speak(f"Listing files on the desktop: {file_list}")
        else:
            speak("The desktop directory is empty.")
    except Exception as e:
        speak(f"An error occurred while accessing the desktop directory: {e}")

def take_screenshot():
    """एक स्क्रीनशॉट लेता है और उसे डेस्कटॉप पर सहेजता है।"""
    try:
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filepath = os.path.join(desktop_path, filename)
        pyautogui.screenshot(filepath)
        speak(f"Screenshot captured and saved to the desktop as {filename}.")
    except Exception as e:
        speak(f"Screenshot capture protocol failed. An error occurred: {e}")

def lock_pc():
    """Windows PC को लॉक करता है।"""
    try:
        speak("Locking the system. Security protocols initiated.")
        if os.name == 'nt':
            subprocess.run("Rundll32.exe user32.dll,LockWorkStation")
        else:
            speak("This command is only supported on Windows systems.")
    except Exception as e:
        speak(f"System lock protocol failed. An error occurred: {e}")
        print(e)

def shutdown_pc():
    """PC को शटडाउन करता है।"""
    speak("Warning: Initiating shutdown protocol. Are you sure? Say yes to proceed or no to cancel.")
    response = listen()
    if "yes" in response:
        speak("Shutdown sequence initiated. Goodbye.")
        if os.name == 'nt':
            os.system("shutdown /s /t 1")
        elif os.name == 'posix':
            os.system("sudo shutdown -h now")
    else:
        speak("Shutdown protocol canceled.")

def restart_pc():
    """PC को रीस्टार्ट करता है।"""
    speak("Warning: Initiating restart protocol. Are you sure? Say yes to proceed or no to cancel.")
    response = listen()
    if "yes" in response:
        speak("Restart sequence initiated.")
        if os.name == 'nt':
            os.system("shutdown /r /t 1")
        elif os.name == 'posix':
            os.system("sudo shutdown -r now")
    else:
        speak("Restart protocol canceled.")

def sleep_pc():
    """PC को स्लीप मोड में डालता है।"""
    speak("Putting the system to sleep.")
    if os.name == 'nt':
        os.system("powercfg /h off")  # Windows में hibernate बंद करना
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif os.name == 'posix':
        os.system("pmset sleepnow")
    else:
        speak("This command is not fully supported on this OS.")


def tell_fact():
    """एक रैंडम फैक्ट बताता है।"""
    facts = [
        "A jiffy is an actual unit of time for 1/100th of a second.",
        "A group of flamingos is called a flamboyance.",
        "Octopuses have three hearts.",
        "The shortest war in history lasted only 38 to 45 minutes.",
        "Honey never spoils.",
        "Elephants are the only animals that can't jump."
    ]
    speak(random.choice(facts))

def check_internet():
    """इंटरनेट कनेक्टिविटी की जाँच करता है।"""
    try:
        requests.get("https://www.google.com", timeout=5)
        speak("Connectivity check complete. The system is online.")
    except (requests.ConnectionError, requests.Timeout):
        speak("Connectivity check failed. The system appears to be offline.")

def open_url_direct(query):
    """किसी दिए गए URL को सीधे खोलता है।"""
    match = re.search(r'open url (.+)', query)
    if match:
        url = match.group(1).strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        try:
            webbrowser.open(url)
            speak(f"Opening URL: {url}.")
        except Exception:
            speak("Could not open the specified URL.")
    else:
        speak("Please specify a valid URL to open.")

def tell_weather():
    """मौसम की जानकारी प्रदान करता है (यह एक सिमुलेशन है)।"""
    speak("Simulating weather report. Currently, it is sunny with a temperature of 25 degrees Celsius.")

def countdown(query):
    """सेकंड में एक उलटी गिनती शुरू करता है।"""
    match = re.search(r'countdown for (\d+) seconds', query)
    if match:
        seconds = int(match.group(1))
        if seconds > 0 and seconds <= 600: # 10 मिनट की सीमा
            speak(f"Starting countdown for {seconds} seconds.")
            for i in range(seconds, 0, -1):
                print(f"Countdown: {i} seconds remaining...")
                time.sleep(1)
            speak("Countdown complete!")
        else:
            speak("Please specify a duration between 1 and 600 seconds.")
    else:
        speak("Please state the countdown duration, for example: 'countdown for 10 seconds'.")
def start_whatsapp_chat():
    speak("Whom do you want to talk to?")
    contact = listen()

    if not contact:
        speak("No contact name heard. Cancelling.")
        return

    speak(f"What should I say to {contact}?")
    message = listen()

    if not message:
        speak("No message heard. Cancelling.")
        return

    speak("Opening WhatsApp Web...")
    webbrowser.open("https://web.whatsapp.com/")
    time.sleep(12)  # Wait for WhatsApp Web to load

    speak(f"Sending message to {contact}...")
    pyautogui.hotkey('ctrl', 'f')  # Focus search bar
    time.sleep(1)
    pyautogui.write(contact)
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.write(message)
    time.sleep(1)
    pyautogui.press('enter')

    speak(f"Message sent to {contact} successfully!")
def show_all_commands():
    """Display and speak all available commands."""
    command_list = {
        "Open an App": "Say: open chrome / open notepad / open vscode",
        "Close an App": "Say: close chrome / close notepad",
        "Search on YouTube": "Say: play relaxing music on YouTube",
        "Check System Info": "Say: battery / RAM / CPU / internet",
        "Create File/Folder": "Say: create file xyz / create folder work",
        "Delete File/Folder": "Say: delete file xyz / delete folder work",
        "Send WhatsApp Message": "Say: start chatting",
        "Take Screenshot": "Say: take screenshot",
        "Tell a Joke / Quote": "Say: tell me a joke / give me a quote",
        "Set Alarm or Timer": "Say: set alarm for 6:00 AM / set timer for 10 minutes",
        "Play Music / Sound": "Say: play music / play a sound",
        "Calculate Math": "Say: calculate 5 plus 9",
        "Shutdown / Restart": "Say: shutdown / restart / sleep",
        "Clipboard Commands": "Say: copy hello to clipboard / paste from clipboard",
        "System Lock": "Say: lock the system",
        "Check Screen Context": "Say: what is this / explain this screen",
        "Show Command List": "Say: show commands / help / command list",
    }

    speak("Here is the list of commands I can understand:")
    print("\n🔹 Omnix Command List 🔹\n")
    for i, (feature, example) in enumerate(command_list.items(), 1):
        line = f"{i}. {feature} → {example}"
        print(line)
        speak(feature)
    print("\nYou can say any of these to perform the action.")
def omnix_full_detail():
    """On-Screen Intelligence: Give full detail of whatever is on screen"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)

    # Screenshot le
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # ---- EasyOCR text extract ----
    reader = easyocr.Reader(['en', 'hi'])  # English + Hindi support
    filename = "omnix_temp.png"
    cv2.imwrite(filename, img)  # EasyOCR ko image file chahiye
    result = reader.readtext(filename)

    # detected text ko merge kar do
    text = " ".join([det[1] for det in result])

    # Face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if text.strip():  # agar text mila
        first_words = " ".join(text.split()[:5])
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.requote_uri(first_words)
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                summary = data.get("extract", "No details found")
                print("🔎 Full Detail:", summary)
                engine.say(summary)
                engine.runAndWait()

                if "content_urls" in data and "desktop" in data["content_urls"]:
                    webbrowser.open_new_tab(data["content_urls"]["desktop"]["page"])
            else:
                engine.say("Sorry, no details found.")
                engine.runAndWait()
        except Exception as e:
            print("Error fetching wiki:", e)
            engine.say("I could not fetch details.")
            engine.runAndWait()

    elif len(faces) > 0:  # agar face detect hua
        engine.say(f"I detected {len(faces)} face(s) on the screen. Let me open related searches.")
        engine.runAndWait()
        webbrowser.open_new_tab("https://www.google.com/search?q=face recognition celebrity tool")

    else:  # koi object ya random image
        engine.say("I detected an object or image on screen. Opening reverse image search for more details.")
        engine.runAndWait()

        # temporary save image for search
        filename = "omnix_object.png"
        cv2.imwrite(filename, img)
        webbrowser.open_new_tab("https://www.google.com/imghp")  # user manually upload karega image

def activate_chat_command():
    speak("Say your command.")
    cmd = listen()
    if "start chatting" in cmd:
        start_whatsapp_chat()        

def flip_a_coin():
    """एक सिक्का उछालता है।"""
    result = random.choice(["heads", "tails"])
    speak(f"The coin landed on... {result}.")

def roll_a_dice():
    """एक पासा फेंकता है।"""
    result = random.randint(1, 6)
    speak(f"The dice rolled a... {result}.")

def main_authenticated_loop():
    """सफल प्रमाणीकरण (authentication) के बाद चलने वाला मुख्य लूप।"""

    while True:
        query = listen()
        if not query:
            continue
        
        # --- NEW FEATURES CHECK ---
       

        if "start pomodoro" in query:
            start_pomodoro_timer()
        
    
        elif "my ip address" in query or "get my ip" in query:
            get_ip_address()
        elif "empty recycle bin" in query:
            empty_recycle_bin()
        elif "horoscope" in query or "horoscope for today" in query:
            tell_horoscope()
        
        elif "open terminal" in query or "open command prompt" in query:
            open_terminal()
        elif "type" in query or "write" in query:
            type_text(query)
        elif "scroll" in query:
            scroll_page(query)
        elif "set an alarm for" in query:
            set_alarm(query)
        elif "play a sound" in query:
            play_random_sound()
        elif "get a password" in query or "generate password" in query:
            get_password()
        elif "copy to clipboard" in query:
            copy_to_clipboard(query)
        elif "paste from clipboard" in query:
            paste_from_clipboard()
        elif "rename" in query and "to" in query:
            rename_file_or_folder(query)
        elif "move" in query and "to" in query:
            move_file_or_folder(query)
        elif "read article from" in query:
            read_article_summary(query)
        elif "search images for" in query or "search image for" in query or "search photo" in query:
            search_images(query)
        elif "find and delete" in query:
            find_and_delete_file(query)
        elif "open" in query and "with" in query:
            open_app_with_arg(query)
        elif "give summary" in query or " my today activity" in query or "give today result" in query:
             give_activity_summary()
    
        
        # --- EXISTING FEATURES CHECK ---
        elif realistic_youtube_intent(query):
            continue
        elif any(phrase in query for phrase in [
            "show commands", "show command list", "help", "what can you do", "command list", "list of commands"
        ]):
            show_all_commands()

        elif 'start website' in query or "visit website" in query:
             open_website    
        elif "read tasks" in query:
            read_tasks()
        elif "running apps " in query or "running app" in query:
            list_running_processes()
        elif "start chatting" in query:
                   start_whatsapp_chat()
    
        elif re.search(r'read file', query):
            read_aloud(query)
        elif re.search(r'write (.+?) to file', query):
            write_to_file(query)
        elif "volume" in query or "mute" in query:
            control_system_volume(query)
        elif "calculate" in query:
            calculate(query)
        elif "set timer for" in query:
            set_timer(query)
        elif ("play" in query or "listen" in query) and "on" in query:
            try:
                if "play" in query:
                    parts = query.split(" play ")
                else:
                    parts = query.split(" listen to ")

                if len(parts) > 1:
                    topic_app = parts[1].split(" on ")
                    topic = topic_app[0].strip()
                    app_name = topic_app[1].strip()
                    search_on_app(topic, app_name)
                else:
                    speak("Query is incomplete. Please specify both the topic and the application.")
            except IndexError:
                speak("Query is incomplete. Please specify both the topic and the application.")
        elif "open" in query:
            if "search for" in query and "on" in query:
                try:
                    parts = query.split(" on ")
                    app_name = parts[-1].strip()
                    topic = parts[0].replace("search for", "").strip()
                    search_on_app(topic, app_name)
                except IndexError:
                    speak("Query is incomplete. Please try again.")
            else:
                app = query.replace("open", "").strip()
                open_app(app)
        elif "schedule" in query or "task" in query:
            speak("Please state the task for scheduling.")
            task_text = listen()
            if task_text:
                schedule_task(task_text)
        elif "clear tasks" in query:
            clear_tasks()
        elif "change my name" in query or "set my name" in query:
            set_name()
        elif any(x in query for x in ["battery", "ram", "cpu", "internet"]):
            system_info(query)
        elif "close" in query:
            app = query.replace("close", "").strip()
            close_app(app)
        elif "note" in query:
            topic = query.replace("note", "").strip()
            auto_write_note(topic)
        elif "email" in query:
            speak("Please state the recipient's email address."); to_person = listen()
            speak("Please state the subject line."); subject_text = listen()
            speak("Please state the body of the message."); body_text = listen()
            if all([to_person, subject_text, body_text]):
                send_email(to_person, subject_text, body_text)
            else:
                speak("Insufficient data for email transmission. Protocol terminated.")
        elif "time" in query:
            get_time()
        elif "date" in query:
            get_date()
        elif "joke" in query:
            tell_joke()
        elif "quote" in query:
            random_quote()
        elif "screenshot" in query or "take a picture" in query:
            take_screenshot()
        elif "create file" in query:
            speak("What would you like to name the file?"); filename = listen()
            if filename:
                create_file(filename)
        elif "delete file" in query:
            speak("What is the name of the file to delete?"); filename = listen()
            if filename:
                delete_file(filename)
        elif "create folder" in query:
            speak("What would you like to name the folder?"); folder_name = listen()
            if folder_name:
                create_folder(folder_name)
        elif "delete folder" in query:
            speak("What is the name of the folder to delete?"); folder_name = listen()
            if folder_name:
                delete_folder(folder_name)
        elif "find file" in query:
            speak("What is the name of the file to find?"); filename = listen()
            if filename:
                find_file(filename)
        elif "list files" in query or "show files" in query:
            list_files_in_directory()
        elif "lock" in query:
            lock_pc()
        elif "silent listener" in query or "listen silently" in query:
             start_silent_listener() 
        elif "analyze system" in query or "scan connected devices" in query or "device info" in query:
               omnix_device_analyzer()
        elif "read this" in query:
           read_active_window()       
        
        elif "zoom" in query or "shift" in query:
            handle_zoom_pan(query)
        elif "shutdown" in query:
            shutdown_pc()
        elif "restart" in query:
            restart_pc()
        elif "sleep" in query:
            sleep_pc()
        elif "tell me a fact" in query or "random fact" in query:
            tell_fact()
        elif "check internet" in query or "internet connection" in query:
            check_internet()
        elif "weather" in query:
            tell_weather()
        elif "open url" in query:
            open_url_direct(query)
        elif "countdown" in query:
            countdown(query)
        elif "flip a coin" in query:
            flip_a_coin()
        elif "roll a dice" in query:
            roll_a_dice()
        elif any(word in query for word in ["tab", "video", "speed", "pause", "mute", "play"]):
            chrome_control(query)
        elif "what is this" in query or "explain this screen" in query or "what am i doing" in query:
              explain_visual_context()
        elif "emergency" in query:
          activate_emergency()
        elif "what are you see" in query or "scan area" in query:
            vision_mode()
        elif "give me full detail" in query  or "scan this" in query:
            omnix_full_detail()
        elif "show fan status" in query or "fan speed" in query:
            show_fan_info()  
        elif "increase brightness" in query:
            change_brightness(query.replace("increase brightness", "increase").strip())
        elif "who are you" in query or "give your introduction" in query:
            give_introduction()   
        elif "decrease brightness" in query:
            change_brightness(query.replace("decrease brightness", "decrease").strip())
        elif "set brightness" in query:
            change_brightness(query.replace("set brightness", "set").strip())
        # ---- Voice Command Handler ----
        elif "news headlines" in query.lower() or "today latest news" in query.lower():
           topic = None
           for kw in ["of", "about"]:
               if kw in query.lower():
                  topic = query.lower().split(kw, 1)[1].strip()

                  break
               
               get_news_headlines(topic)  # topic=None → general headlines
       
            
        elif "system off" in query or "exit" in query:
            speak("Shutdown protocol initiated. Goodbye.")
            break
        else:
         found = fallback_answer(query)
    
    if not found:
        speak("I couldn’t find a direct answer, but you can try saying it differently.")
def start_omnix_with_code():
    """शुरू होने पर सीक्रेट कोड के साथ Omnix को शुरू करता है।"""
    speak("Please type the secret code to initiate Omnix.")
    code_input = input("Enter secret code: ").strip()

    if code_input.lower() == SECRET_CODE.lower():
        play_startup_sound()
        speak(f"User ID {memory.get('name', 'Friend')} acknowledged. Main systems online.")
        main_authenticated_loop()
    else:
        speak("Unauthorized access. All systems remain offline.")
        print("Incorrect secret code entered. Exiting program.")
        exit()
WIDTH, HEIGHT = 900, 600
CX, CY = WIDTH // 2, HEIGHT // 2

class JarvisApp:
    def __init__(self, root):
        self.root = root
        root.title("⚡ OMNIX — Advanced JARVIS Interface ⚡")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Welcome Kartik (Blink + Glow)
        self.text = self.canvas.create_text(
            CX, 50, text="Welcome Kartik",
            fill="navy", font=("Consolas", 28, "bold")
        )
        self.blink_state = True
        self.animate_text()

        # Central Circle (Jarvis Core)
        self.circle = self.canvas.create_oval(CX-100, CY-100, CX+100, CY+100, outline="cyan", width=3)

        self.angle = 0
        self.animate()

    def animate_text(self):
        """Blink Welcome text"""
        self.canvas.itemconfig(self.text, fill="navy" if self.blink_state else "black")
        self.blink_state = not self.blink_state
        self.root.after(600, self.animate_text)

    def animate(self):
        """Rotating lines around the core"""
        self.canvas.delete("lines")
        for i in range(12):
            angle_rad = math.radians(self.angle + i*30)
            x = CX + 150 * math.cos(angle_rad)
            y = CY + 150 * math.sin(angle_rad)
            self.canvas.create_line(CX, CY, x, y, fill="cyan", tags="lines")
        self.angle += 5
        self.root.after(50, self.animate)          
           
stop_playback_flag = threading.Event()
CPU_THRESHOLD = 90  # %
BATTERY_THRESHOLD = 10  # %
CHECK_INTERVAL = 10  # seconds

# Sample meetings (replace with real calendar integration)
calendar_events = [
    {"title": "Team Meeting", "time": datetime.now() + timedelta(minutes=6)},
    {"title": "Project Review", "time": datetime.now() + timedelta(minutes=15)},
]

# ---------- CORE FUNCTIONS ----------
async def stream_tts(text):
    stop_playback_flag.clear()
    temp_file = "temp_alert.mp3"
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(temp_file)
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        if stop_playback_flag.is_set():
            break
        pygame.time.Clock().tick(10)

def play_tts_thread(text):
    threading.Thread(target=lambda: asyncio.run(stream_tts(text)), daemon=True).start()

def check_system_resources():
    """Check CPU, RAM, Battery and give alerts."""
    while True:
        cpu = psutil.cpu_percent(interval=1)
        battery = psutil.sensors_battery()
        if cpu > CPU_THRESHOLD:
            play_tts_thread(f"Sir, CPU usage is critically high at {cpu} percent.")
        if battery and battery.percent < BATTERY_THRESHOLD:
            play_tts_thread(f"Sir, your battery is critically low at {battery.percent} percent. Should I enable battery saver?")
        time.sleep(CHECK_INTERVAL)

def check_calendar_events():
    """Check upcoming meetings and give proactive reminders."""
    while True:
        now = datetime.now()
        for event in calendar_events:
            delta = (event["time"] - now).total_seconds()
            if 0 < delta <= 300:  # 5 minutes before event
                play_tts_thread(f"Sir, your meeting '{event['title']}' starts in 5 minutes.")
                calendar_events.remove(event)  # avoid repeating
        time.sleep(60)

# ---------- START MONITORS ----------
def start_situational_alerts():
    threading.Thread(target=check_system_resources, daemon=True).start()
    threading.Thread(target=check_calendar_events, daemon=True).start()
# --- Update your run_ai() function and its call ---
if __name__ == "__main__":
    try:
        # Initialize GUI
        root = tk.Tk()
        gui = JarvisApp(root)

        # Initialize pygame for TTS
        pygame.init()
        pygame.mixer.init()

        # ---- Start Omnix AI and Background Modules ----
        def run_ai():
            # Start main Omnix code
            start_omnix_with_code()

            # Start live screen analysis in background
            start_live_screen_analysis()  # Ye naya function jo humne define kiya

            # Start Situational Alerts + Proactive Help
            start_situational_alerts()  # CPU, Battery, Calendar monitoring

        # Run AI + screen analysis + situational alerts in separate thread
        threading.Thread(target=run_ai, daemon=True).start()

        # Start GUI mainloop
        root.mainloop()

    except KeyboardInterrupt:
        print("\nProgram is shutting down.")
    finally:
        pygame.quit()
