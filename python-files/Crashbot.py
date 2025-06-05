import os import cv2 import json import time import threading import requests import pyttsx3 import speech_recognition as sr import serial from deep_translator import GoogleTranslator from langdetect import detect from datetime import datetime

========== CONFIGURATION ==========

API_KEY = "your_groq_api_key_here" MODEL = "llama3-70b-8192" MEMORY_FILE = "ai_memory.json" VIDEO_FILE = "last_seen.mp4" CAMERA_INDEX = 0 ARDUINO_PORT = "/dev/ttyUSB0"  # Adjust if needed SCREEN_WIDTH = 480 SCREEN_HEIGHT = 320

========== INITIAL SETUP ==========

engine = pyttsx3.init() recognizer = sr.Recognizer() cap = cv2.VideoCapture(CAMERA_INDEX) face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1)

========== MEMORY MANAGEMENT ==========

def load_memory(): if os.path.exists(MEMORY_FILE): with open(MEMORY_FILE, 'r') as f: return json.load(f) return {"user_name": "Alex", "friends": [], "faces": {}}

def save_memory(memory): with open(MEMORY_FILE, 'w') as f: json.dump(memory, f)

memory = load_memory()

========== INTRODUCTION ==========

def intro(): intro_text = "Now let me introduce myself. I am CrashBot, a virtual artificial intelligence developed by Nova. Keeping my every friend a step forward." speak(intro_text)

========== LANGUAGE HANDLING ==========

def translate_text(text, target_lang='en'): try: return GoogleTranslator(source='auto', target=target_lang).translate(text) except: return text

def detect_language(text): try: return detect(text) except: return 'en'

========== VOICE HANDLING ==========

def speak(text, lang='en'): translated = translate_text(text, lang) engine.say(translated) engine.runAndWait()

def listen(): with sr.Microphone() as source: print("🎤 Listening...") audio = recognizer.listen(source) try: query = recognizer.recognize_google(audio) return query except: return ""

========== CHAT WITH GROQ ==========

def chat_with_groq(message): headers = { "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json" } system_prompt = f""" You are CrashBot, a cool sci-fi AI created by Nova. Always reply smartly, logically, calmly and refer to known people by name. Your known users are: {memory['user_name']} and friends: {', '.join(memory['friends'])}. """ data = { "model": MODEL, "messages": [ {"role": "system", "content": system_prompt}, {"role": "user", "content": message} ], "temperature": 0.7 } response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data) if response.status_code == 200: return response.json()['choices'][0]['message']['content'] return "Something went wrong."

========== FACE MEMORY ==========

def recognize_face(): , frame = cap.read() gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) faces = face_cascade.detectMultiScale(gray, 1.3, 5) for (x, y, w, h) in faces: face_img = gray[y:y+h, x:x+w] face_id = f"face{x}{y}" if face_id not in memory['faces']: name = f"Person{len(memory['faces'])+1}" memory['faces'][face_id] = name save_memory(memory) speak(f"Hello {name}, nice to meet you.") else: speak(f"Welcome back, {memory['faces'][face_id]}.") break

========== EMOTION DISPLAY ==========

def show_emotion(emotion="cool"): img = 255 * np.ones((SCREEN_HEIGHT, SCREEN_WIDTH, 3), np.uint8) eye_color = (0, 255, 255) if emotion == "cool" else (0, 0, 255) cv2.circle(img, (120, 160), 30, eye_color, -1) cv2.circle(img, (360, 160), 30, eye_color, -1) cv2.imshow("CrashBot Face", img) cv2.waitKey(1)

========== VIDEO RECORDING ==========

def record_video(duration=10): fourcc = cv2.VideoWriter_fourcc(*'XVID') out = cv2.VideoWriter(VIDEO_FILE, fourcc, 20.0, (640, 480)) start_time = time.time() while time.time() - start_time < duration: ret, frame = cap.read() if ret: out.write(frame) out.release() speak("Video recording complete.")

def play_video(): cap2 = cv2.VideoCapture(VIDEO_FILE) while cap2.isOpened(): ret, frame = cap2.read() if not ret: break cv2.imshow('Playback', frame) if cv2.waitKey(30) & 0xFF == ord('q'): break cap2.release() cv2.destroyAllWindows()

========== ARDUINO COMMUNICATION ==========

def send_to_arduino(cmd): arduino.write((cmd + '\n').encode())

========== MAIN LOOP ==========

def main(): intro() show_emotion("cool") while True: recognize_face() query = listen() lang = detect_language(query) if query.strip() == "exit": break if "record video" in query: record_video(5) continue if "play video" in query: play_video() continue if query.startswith("add friend"): name = query.replace("add friend", "").strip() if name not in memory['friends']: memory['friends'].append(name) save_memory(memory) speak(f"I will remember {name} as your friend.", lang) continue reply = chat_with_groq(query) speak(reply, lang) send_to_arduino(f"cmd:{query}")

if name == "main": main()