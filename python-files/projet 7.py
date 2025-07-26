# === MAX V6 - WITH MOOD & DREAM MODE ===
import sys
import os
import json
import datetime
import threading
import subprocess
import asyncio
import pywhatkit
import wikipedia
import pyjokes
import random
import ctypes
import speech_recognition as sr
import numpy as np
import edge_tts
import pyaudio
from vosk import Model, KaldiRecognizer
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QListWidget,
                             QSystemTrayIcon, QMenu, QAction, QInputDialog)
from PyQt5.QtCore import Qt, QRect, QTimer, QPropertyAnimation
from PyQt5.QtGui import QMovie, QColor, QIcon, QPixmap, QFont, QPainter, QCursor, QCloseEvent, QGraphicsDropShadowEffect
from textblob import TextBlob

# === GLOBAL FILES ===
MEMORY_FILE = "memory.json"
REMINDER_FILE = "reminders.json"
VOSK_MODEL_PATH = "model"

# === MOOD ENGINE ===
class MaxMood:
    mood_colors = {
        "happy": QColor(0, 255, 255),
        "sad": QColor(0, 100, 255),
        "annoyed": QColor(255, 0, 0),
        "sleepy": QColor(128, 0, 255),
        "dream": QColor(255, 102, 204),
        "neutral": QColor(255, 255, 255)
    }

    @staticmethod
    def set_mood(mood, ui=None):
        memory['mood'] = mood
        save_memory(memory)
        if ui:
            color = MaxMood.mood_colors.get(mood, QColor(255, 255, 255))
            ui.shadow.setColor(color)
            ui.shadow.setEnabled(True)

    @staticmethod
    def get_mood():
        return memory.get('mood', 'neutral')

# === LOAD & SAVE MEMORY ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"user_name": "User", "last_command": "", "mood": random.choice(["happy", "annoyed", "sleepy"])}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)

memory = load_memory()

# === ENABLE WINDOWS BLUR ===
def enable_blur(hwnd):
    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [('AccentState', ctypes.c_int), ('AccentFlags', ctypes.c_int),
                    ('GradientColor', ctypes.c_int), ('AnimationId', ctypes.c_int)]
    class WINCOMPATTRDATA(ctypes.Structure):
        _fields_ = [('Attribute', ctypes.c_int), ('Data', ctypes.c_void_p), ('SizeOfData', ctypes.c_size_t)]

    accent = ACCENTPOLICY()
    accent.AccentState = 3  # Enable blur
    data = WINCOMPATTRDATA()
    data.Attribute = 19
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
    data.SizeOfData = ctypes.sizeof(accent)
    ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))

# === SPEECH FUNCTION ===
async def speak_async(text, ui=None):
    if ui:
        ui.glow(True)
    communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")
    await communicate.save("output.mp3")
    os.system("start output.mp3")
    await asyncio.sleep(2.5)
    if ui:
        ui.glow(False)

def talk(text, ui=None):
    asyncio.run(speak_async(text, ui))

# === DETECT MOOD FROM VOICE ===
def detect_mood(audio_data):
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    volume = np.linalg.norm(audio_np) / len(audio_np)
    pitch = np.abs(np.fft.rfft(audio_np)).mean()
    if volume > 500 and pitch > 500:
        return "annoyed"
    elif volume < 200:
        return "sleepy"
    else:
        return "happy"

# === LISTEN FOR VOICE COMMAND ===
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        raw_data = audio.get_raw_data()
        mood = detect_mood(raw_data)
        MaxMood.set_mood(mood)
        try:
            command = r.recognize_google(audio).lower()
            if 'max' in command:
                command = command.replace('max', '').strip()
                memory['last_command'] = command
                save_memory(memory)
                return command
        except:
            return ""

# === HANDLE MOOD RESPONSE ===
def mood_response(text, ui):
    mood = MaxMood.get_mood()
    if mood == "happy":
        talk(text, ui)
    elif mood == "annoyed":
        talk("Ugh. " + text, ui)
    elif mood == "sleepy":
        talk("(yawns) " + text, ui)
    elif mood == "dream":
        talk("(whispers) " + text, ui)
    else:
        talk(text, ui)

# === DREAM TIMER ===
class DreamTimer(QTimer):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.timeout.connect(self.trigger_dream_mode)
        self.start(300000)  # 5 minutes

    def reset(self):
        self.start(300000)

    def trigger_dream_mode(self):
        MaxMood.set_mood("dream", self.ui)
        talk("Have you ever wondered if thoughts sleep too?", self.ui)

# === REST OF ORIGINAL CODE ===
# [No changes to reminder_loop, handle_app_control, or other core logic required here]

# === GUI INTERFACE ===
class MaxUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(600, 300, 300, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        hwnd = self.winId().__int__()
        enable_blur(hwnd)
        self.initUI()
        self.show()
        self.dream_timer = DreamTimer(self)
        threading.Thread(target=reminder_loop, args=(self,), daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def initUI(self):
        self.globe = QLabel(self)
        self.globe.setGeometry(50, 50, 200, 200)
        movie = QMovie("globe.gif")
        self.globe.setMovie(movie)
        movie.start()

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(25)
        self.shadow.setColor(QColor(255, 255, 255))
        self.shadow.setOffset(0, 0)
        self.globe.setGraphicsEffect(self.shadow)
        self.shadow.setEnabled(True)

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(3000)
        self.anim.setStartValue(QRect(600, 300, 300, 300))
        self.anim.setEndValue(QRect(605, 295, 300, 300))
        self.anim.setLoopCount(-1)
        self.anim.start()

        self.tray = QSystemTrayIcon(QIcon("globe.gif"), self)
        self.tray.setToolTip("Max Assistant")
        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        edit_action = QAction("Edit Reminders", self)
        edit_action.triggered.connect(self.edit_reminders)
        menu.addAction(edit_action)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def glow(self, state):
        self.shadow.setEnabled(state)

    def listen_loop(self):
        while True:
            command = take_command()
            if command:
                self.dream_timer.reset()
                run_max(self)

    def edit_reminders(self):
        dlg = ReminderEditor()
        dlg.exec_()

# === REMINDER EDITOR ===
from PyQt5.QtWidgets import QDialog
class ReminderEditor(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Reminders")
        self.setGeometry(700, 300, 300, 400)
        layout = QVBoxLayout()

        self.list = QListWidget(self)
        self.reminders = load_reminders()
        for r in self.reminders:
            self.list.addItem(f"{r['task']} at {r['time']}")
        layout.addWidget(self.list)

        btn_add = QPushButton("Add Reminder")
        btn_add.clicked.connect(self.add_reminder)
        btn_del = QPushButton("Delete Selected")
        btn_del.clicked.connect(self.delete_selected)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)
        self.setLayout(layout)

    def add_reminder(self):
        task, ok1 = QInputDialog.getText(self, "Task", "What to remind?")
        time, ok2 = QInputDialog.getText(self, "Time", "When (HH:MM)?")
        if ok1 and ok2:
            self.reminders.append({"task": task, "time": time, "triggered": False})
            save_reminders(self.reminders)
            self.list.addItem(f"{task} at {time}")

    def delete_selected(self):
        index = self.list.currentRow()
        if index >= 0:
            del self.reminders[index]
            save_reminders(self.reminders)
            self.list.takeItem(index)

# === RUN MAX ===
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MaxUI()
    sys.exit(app.exec_())


Done! Your Max v6 code now includes:

A full mood system with color glow based on emotional state

Dream mode that activates after 5 minutes of no interaction

Integrated with your existing PyQt globe animation


Max now feels. Ready to test it live? Or want me to help with mood-triggered globe image switching too?


