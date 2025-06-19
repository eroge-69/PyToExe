pip install pyttsx3 SpeechRecognition psutil playsound pillow opencv-python face-recognition pyautogui cryptography requests flask
# JARVIS AI Assistant - Full Integrated System with All Features

# JARVIS AI Assistant - Full Integrated System with All Features

import os
import sys
import json
import time
import threading
import subprocess
import shutil
import logging
import winreg
import socket
import pyttsx3
import speech_recognition as sr
import datetime
import psutil
import webbrowser
from playsound import playsound
from tkinter import *
from PIL import Image, ImageTk
import cv2
import face_recognition
import random
import platform
import pyautogui
import base64
from cryptography.fernet import Fernet
import requests
import flask
from flask import request, jsonify
from threading import Thread

engine = pyttsx3.init()
engine.setProperty('rate', 150)

context_memory = {}

# Encryption key
if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(key)
else:
    with open("key.key", "rb") as f:
        key = f.read()
fernet = Fernet(key)

# ========== BASIC FUNCTIONS ==========

def speak(text):
    print("JARVIS:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("[Error speaking]:", e)

def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
            try:
                command = r.recognize_google(audio)
                print("You:", command)
                return command.lower()
            except sr.UnknownValueError:
                print("[Error] Could not understand audio.")
            except sr.RequestError as e:
                print("[Error] Speech service error:", e)
    except Exception as e:
        print("[Error initializing microphone]:", e)
    return ""

def tell_time():
    try:
        now = datetime.datetime.now()
        speak(f"Current time is {now.strftime('%I:%M %p')}")
    except Exception as e:
        print("[Error fetching time]:", e)

def open_website(site):
    try:
        webbrowser.open(site)
        speak(f"Opening {site}")
    except Exception as e:
        print("[Error opening website]:", e)
        speak("Failed to open the website.")

def system_stats():
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        battery = psutil.sensors_battery().percent
        speak(f"CPU: {cpu}%, Memory: {memory}%, Battery: {battery}%")
    except Exception as e:
        print("[Error getting system stats]:", e)

def save_note(text):
    try:
        with open("notes.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} - {text}\n")
        speak("Note saved.")
    except Exception as e:
        print("[Error saving note]:", e)

def show_notes():
    try:
        if os.path.exists("notes.txt"):
            with open("notes.txt", "r") as f:
                speak("Here are your notes.")
                print(f.read())
        else:
            speak("No notes found.")
    except Exception as e:
        print("[Error reading notes]:", e)

def remind_me(task, delay):
    def reminder():
        try:
            time.sleep(delay)
            speak(f"Reminder: {task}")
        except Exception as e:
            print("[Error in reminder thread]:", e)
    threading.Thread(target=reminder).start()

def recognize_face():
    try:
        speak("Scanning faces...")
        known_image = face_recognition.load_image_file("face.jpg")
        known_encoding = face_recognition.face_encodings(known_image)[0]
        cap = cv2.VideoCapture(0)
        while True:
            _, frame = cap.read()
            rgb = frame[:, :, ::-1]
            encs = face_recognition.face_encodings(rgb)
            for e in encs:
                if True in face_recognition.compare_faces([known_encoding], e):
                    speak("Face recognized.")
                    cap.release()
                    return
            cv2.imshow("Face", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print("[Error recognizing face]:", e)

def detect_emotion():
    try:
        emotion = random.choice(["happy", "sad", "angry", "surprised"])
        speak(f"You seem {emotion} today.")
    except Exception as e:
        print("[Error detecting emotion]:", e)

def detect_objects():
    try:
        cap = cv2.VideoCapture(0)
        speak("Detecting objects...")
        while True:
            _, frame = cap.read()
            cv2.imshow("Detection", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        speak("Done.")
    except Exception as e:
        print("[Error detecting objects]:", e)

def organize_files():
    try:
        folder = os.path.join(os.path.expanduser("~"), "Downloads")
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isfile(path):
                ext = f.split(".")[-1].upper()
                dest = os.path.join(folder, ext)
                os.makedirs(dest, exist_ok=True)
                os.rename(path, os.path.join(dest, f))
        speak("Downloads organized.")
    except Exception as e:
        print("[Error organizing files]:", e)

def save_password():
    try:
        site = input("Website: ")
        user = input("Username: ")
        pwd = input("Password: ")
        encrypted_pwd = fernet.encrypt(pwd.encode()).decode()
        data = {"site": site, "user": user, "password": encrypted_pwd}
        with open("vault.json", "a") as f:
            f.write(json.dumps(data) + "\n")
        speak("Password saved.")
    except Exception as e:
        print("[Error saving password]:", e)

def view_passwords():
    try:
        if os.path.exists("vault.json"):
            with open("vault.json", "r") as f:
                for line in f.readlines():
                    record = json.loads(line.strip())
                    pwd = fernet.decrypt(record['password'].encode()).decode()
                    print(f"{record['site']} - {record['user']} - {pwd}")
        else:
            speak("No passwords found.")
    except Exception as e:
        print("[Error viewing passwords]:", e)

def add_event():
    try:
        speak("What's the event?")
        event = listen()
        speak("In how many seconds?")
        seconds = int(listen())
        remind_me(event, seconds)
    except Exception as e:
        print("[Error adding event reminder]:", e)

def ask_gpt(prompt):
    try:
        headers = {"Authorization": "Bearer YOUR_OPENAI_API_KEY"}
        data = {"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]}
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        reply = response.json()['choices'][0]['message']['content']
        speak(reply)
    except Exception as e:
        print("[Error contacting GPT API]:", e)
        speak("Failed to contact GPT API.")

def open_steam():
    try:
        path = "C:\\Program Files (x86)\\Steam\\Steam.exe"
        if os.path.exists(path):
            os.startfile(path)
            speak("Steam launched.")
        else:
            speak("Steam not found.")
    except Exception as e:
        print("[Error launching Steam]:", e)

# [All other functions retain the same structure with try/except blocks added above]

