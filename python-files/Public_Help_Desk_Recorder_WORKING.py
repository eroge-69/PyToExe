
import cv2
import numpy as np
import pyautogui
import pyaudio
import wave
import threading
import tkinter as tk
import pytesseract
import time
from datetime import datetime

# Set path to Tesseract executable (Windows default path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

recording = False
paused = False
audio_frames = []

# Audio config
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def record_audio():
    global audio_frames
    audio_frames = []
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while recording:
        if not paused:
            data = stream.read(CHUNK)
            audio_frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()

def blur_text(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            roi = frame[y:y+h, x:x+w]
            blur = cv2.GaussianBlur(roi, (23, 23), 30)
            frame[y:y+h, x:x+w] = blur
    return frame

def blur_keywords(frame, keywords=["aadhaar", "account", "dob", "pan", "ifsc", "mobile"]):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    for i, word in enumerate(data["text"]):
        for keyword in keywords:
            if keyword.lower() in word.lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                roi = frame[y:y+h, x:x+w]
                blur = cv2.GaussianBlur(roi, (31, 31), 0)
                frame[y:y+h, x:x+w] = blur
    return frame

def zoom_on_keywords(frame, keywords=["name", "aadhaar", "dob", "pin", "mobile"]):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    for i, word in enumerate(data["text"]):
        for keyword in keywords:
            if keyword.lower() in word.lower():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                x1, y1 = max(0, x - 50), max(0, y - 50)
                x2, y2 = min(frame.shape[1], x + w + 50), min(frame.shape[0], y + h + 50)
                zoomed_area = frame[y1:y2, x1:x2]
                if zoomed_area.size > 0:
                    zoomed = cv2.resize(zoomed_area, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
                    return zoomed
    return frame

def record_screen(filename="recording"):
    global paused
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(f"{filename}.avi", fourcc, 20.0, screen_size)
    while recording:
        if not paused:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = blur_keywords(frame)
            frame = blur_text(frame)
            frame = zoom_on_keywords(frame)
            out.write(frame)
        else:
            time.sleep(0.1)
    out.release()

def save_audio(filename):
    wf = wave.open(f"{filename}.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

def start():
    global recording
    recording = True
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    threading.Thread(target=record_screen, args=(now,), daemon=True).start()
    threading.Thread(target=record_audio, daemon=True).start()
    status_label.config(text="Recording...")

def stop():
    global recording
    recording = False
    time.sleep(1)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_audio(now)
    status_label.config(text="Stopped and Saved")

def toggle():
    global paused
    paused = not paused
    pause_button.config(text="Resume" if paused else "Pause")
    status_label.config(text="Paused" if paused else "Recording...")

# GUI
root = tk.Tk()
root.title("Public Help Desk Recorder")
root.geometry("300x200")

tk.Label(root, text="🎥 Public Help Desk Recorder", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Start Recording", command=start).pack(pady=5)
tk.Button(root, text="Stop Recording", command=stop).pack(pady=5)
pause_button = tk.Button(root, text="Pause", command=toggle)
pause_button.pack(pady=5)
status_label = tk.Label(root, text="Status: Idle")
status_label.pack(pady=10)

root.mainloop()
