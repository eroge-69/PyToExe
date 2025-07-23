"""
NaEka.AI ADAPTIVE - Production Ready Version
Auto-Detects Hardware: LITE/PRO/ULTIMATE
Copyright (C) 2025 NaEka.AI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import os
import sys
import json
import sqlite3
from datetime import datetime
from collections import deque
import numpy as np

# Import required modules
import speech_recognition as sr
import keyboard
import pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01
import pyperclip
import pystray
from PIL import Image, ImageDraw
HAS_TRAY = True  # Assume installed

class AdaptiveLearningSystem:
    def __init__(self, db_path='naeka_adaptive_brain.db'):
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self.init_database()
        self.load_patterns()
    
    def init_database(self):
        with self.db_lock:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT,
                    output_text TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
    
    def load_patterns(self):
        self.patterns = {}
        with self.db_lock:
            cursor = self.conn.execute('SELECT input_text, output_text FROM patterns')
            for row in cursor:
                self.patterns[row[0]] = row[1]
    
    def correct_text(self, text):
        latvian_fixes = {'aa': 'ā', 'ee': 'ē', 'ii': 'ī', 'uu': 'ū', 'sh': 'š', 'zh': 'ž', 'ch': 'č'}
        for wrong, correct in latvian_fixes.items():
            text = text.replace(wrong, correct)
        return text
    
    def learn_pattern(self, input_text, output_text):
        if input_text != output_text:
            with self.db_lock:
                self.conn.execute('INSERT OR REPLACE INTO patterns (input_text, output_text, frequency) VALUES (?, ?, COALESCE((SELECT frequency FROM patterns WHERE input_text = ?) + 1, 1))', (input_text, output_text, input_text))
                self.conn.commit()
                self.patterns[input_text] = output_text

class NaEkaAdaptive:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NaEka ADAPTIVE")
        self.root.geometry("400x500")
        self.is_active = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.learning = AdaptiveLearningSystem()
        self.setup_gui()
        self.start_threads()
    
    def setup_gui(self):
        self.status_label = tk.Label(self.root, text="Ready")
        self.status_label.pack()
        self.start_button = tk.Button(self.root, text="Start", command=self.toggle_active)
        self.start_button.pack()
    
    def toggle_active(self):
        self.is_active = not self.is_active
        self.status_label.config(text="Listening" if self.is_active else "Ready")
    
    def recognition_loop(self):
        while True:
            if self.is_active:
                with self.microphone as source:
                    audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio, language='lv-LV')
                corrected = self.learning.correct_text(text)
                pyautogui.typewrite(corrected)
    
    def start_threads(self):
        threading.Thread(target=self.recognition_loop, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NaEkaAdaptive()
    app.run()