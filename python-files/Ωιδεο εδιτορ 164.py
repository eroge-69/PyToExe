import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import pyttsx3
import os
import pickle
import sounddevice as sd
from scipy.io.wavfile import write
from moviepy.editor import *

# --- Global Variables ---
project_data = []  # Each entry: {'image_path': ..., 'text': ..., 'audio_path': ...}
project_filename = None

# --- TTS Engine ---
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# --- Main App ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("VE164 Project Creator")
        self.canvas = tk.Canvas(root, bg='white', width=800, height=500)
        self.canvas.pack()

        self.controls = tk.Frame(root)
        self.controls.pack()

        tk.Button(self.controls, text="New Project", command=self.new_project).pack(side=tk.LEFT)
        tk.Button(self.controls, text="Open Project", command=self.open_project).pack(side=tk.LEFT)
        tk.Button(self.controls, text="Add Image", command=self.add_image).pack(side=tk.LEFT)
        tk.Button(self.controls, text="Save Project", command=self.save_project).pack(side=tk.LEFT)
        tk.Button(self.controls, text="Save Video", command=self.save_video).pack(side=tk.LEFT)

        self.image_frames = []

    def new_project(self):
        global project_data
        project_data = []
        self.refresh_ui()

    def open_project(self):
        global project_data
        path = filedialog.askopenfilename(filetypes=[("VE164 Files", "*.ve164")])
        if path:
            with open(path, 'rb') as f:
                  project_data = pickle.load(f)
        self.refresh_ui()

