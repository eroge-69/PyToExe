import os
import time
import wave
import threading
import queue
import pyaudio
import numpy as np
import speech_recognition as sr
import pyttsx3
import webbrowser
import random
import subprocess
import psutil # For process management (closing apps, system health, running processes)
import ctypes # For Windows-specific system calls like locking workstation
import datetime
import json
import re
import sys
import requests # For web requests (API, web scraping)
import speedtest # For internet speed testing
import pyjokes # For jokes
import pyautogui # For GUI automation (keyboard, mouse, screenshots, window control)
import pyperclip # For clipboard operations
import cv2 # For webcam access, screen recording (though placeholders currently)
import pdfplumber # For reading PDF files
import phonenumbers # For phone number parsing
from phonenumbers import geocoder as phone_geocoder
from phonenumbers import carrier
from pytube import YouTube # For YouTube video/audio download
import instaloader # For Instagram profile download
import wikipedia # For Wikipedia searches
import pygetwindow as gw # Used for getting window information and control on Windows
from PIL import ImageGrab # Alternative for screenshots, used in screen recording placeholder
from newsapi import NewsApiClient # For fetching news headlines
import socket # Added: For retrieving IP address
import platform # Added: For getting OS information
from urllib.parse import urlparse # Added: For parsing URLs in ping_website

# Imports for Voice Training (Machine Learning components)
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from scipy.io import wavfile
import python_speech_features as mfcc
import pickle
       
# Tkinter imports for the GUI
import tkinter as tk
import math
# win32gui and win32con are Windows-specific for GUI manipulation
import win32gui, win32con


# Pygame is used for audio playback (e.g., notification sound, YouTube audio).
from pygame import mixer

# ========== CONFIGURATION ==========
# User-facing information
APP_NAME = "J.A.R.V.I.S"
USER_NAME = "sir" # Changed from "Krish" to "sir"
# Set to True to record audio for training when commands are successfully recognized.
# This helps in building a custom voice model for better recognition over time.
SECRET_RECORDING = True

# Audio and speech recognition settings
AUDIO_SAVE_PATH = "voice_training_data" # Directory to save recorded audio for training
MODEL_SAVE_PATH = "voice_model.pkl" # Path to save the trained voice model (e.g., for speaker recognition)
SAMPLE_RATE = 16000 # Standard sample rate for speech
CHUNK = 1024 # Number of frames per buffer for audio processing
FORMAT = pyaudio.paInt16 # Audio format (16-bit integers)
CHANNELS = 1 # Mono audio
SILENCE_THRESHOLD = 500  # Adjust based on your microphone's sensitivity. Higher value = less sensitive.
SILENCE_DURATION = 1.5  # Seconds of silence to stop recording after speech.

# GUI settings (used by JarvisGUI)
POPUP_WIDTH = 360 # These are now mostly for reference, as the GUI is fixed size
POPUP_HEIGHT = 120
MARGIN_FROM_EDGE = 24
SLIDE_MS = 300
DISPLAY_MS = 5000
# Paths to assets. Ensure these files exist (jarvis.jpg, jarvis.mp3) in the same directory as the script or provide full paths.
# ICON_PATH is no longer used for notifications directly, but could be for the GUI window icon if desired.
ICON_PATH = "jarvis.jpg"
SOUND_PATH = "jarvis.mp3" # Still used for pygame mixer
THEME_BG = "#0A0E14" # No longer directly used by Tkinter GUI
THEME_FG = "#D8E0E8" # No longer directly used by Tkinter GUI
THEME_ACCENT = "#00D084" # No longer directly used by Tkinter GUI
FONT_FAMILY = "Segoe UI" # No longer directly used by Tkinter GUI

# API Keys (Replace with your own keys)
# The provided keys are placeholders. You need to obtain actual API keys
# from the respective services (NewsAPI, OpenCage Geocoding, OpenWeatherMap) for these features to work.
NEWS_API_KEY = "f2cdcacf1b7d4b76a888dd938357c5c5"  # Replace with your News API Key from newsapi.org
OPENCAGE_API_KEY = "8c63892f325847a28c0eb71de5c7df39"  # Replace with your OpenCage Geocoding API Key from opencagedata.com
WEATHER_API_KEY = "d1e9e1a3b3a04c0a8c1f5f5f5f5f5f5f" # Replace with your OpenWeatherMap API key from openweathermap.org

# Create directories if they don't exist
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)

# Initialize pygame mixer for audio playback
try:
    mixer.init()
except Exception as e:
    print(f"Pygame mixer initialization failed: {e}. Audio playback features might not work.")

# Global reference to the GUI application instance
app_gui = None

# Global variables for voice model (used in training and potentially for speaker recognition)
voice_model = None
scaler = None

# ========== MICROPHONE UTILITIES ==========
def list_microphones():
    """Prints a list of available audio input devices to help with microphone selection."""
    p = pyaudio.PyAudio()
    print("\nAvailable Audio Devices:")
    try:
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for i in range(num_devices):
            dev = p.get_device_info_by_host_api_device_index(0, i)
            if dev['maxInputChannels'] > 0:
                print(f"  {i}: {dev['name']} (Input channels: {dev['maxInputChannels']})")
    except Exception as e:
        print(f"  Error listing devices: {e}")
    finally:
        p.terminate()

def get_default_microphone():
    """
    Tries to get the default microphone index from speech_recognition.
    Falls back to index 0 if detection fails.
    """
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            return source.device_index
    except Exception as e:
        print(f"Could not determine default microphone: {e}. Falling back to device 0.")
        return 0

# Initialize microphone index and print devices for user guidance
DEFAULT_MIC_INDEX = get_default_microphone()
print(f"Attempting to use microphone index: {DEFAULT_MIC_INDEX}")
list_microphones()


# ========== JARVIS GUI (TKINTER) ==========
class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x600+100+100")
        self.root.overrideredirect(True) # Remove window decorations
        self.root.wm_attributes("-transparentcolor", "black") # Make black background transparent
        self.root.configure(bg="black")
        self.offset_x = 0
        self.offset_y = 0
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        self.root.bind("<Escape>", self.fade_exit)  # Smooth exit on Escape key

        # Always on top - Windows specific
        # This makes the GUI window stay on top of other applications.
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        if hwnd:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

        self.canvas = tk.Canvas(root, width=900, height=600, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Animation state variables
        self.state = "idle" # Can be "idle", "listening", "processing", "speaking"
        self.volume_level = 0 # For microphone visualization
        self.outer_ring_angle = 0
        self.third_ring_angle = 0
        self.glow_phase = 0
        self.progress_angle = 0
        self.waveform_phase = 0

        # === Hidden Resizable Button (for dragging/resizing the transparent window) ===
        self.hidden_button_size = 50
        self.hidden_button_x = 10
        self.hidden_button_y = 10
        self.dragging_resize = False # Flag for resize operation
        self.hidden_button = self.canvas.create_rectangle(
            self.hidden_button_x, self.hidden_button_y,
            self.hidden_button_x + self.hidden_button_size,
            self.hidden_button_y + self.hidden_button_size,
            fill="", outline="", tags="hidden_btn" # Invisible rectangle
        )
        # Bind mouse events to the hidden button for dragging/resizing
        self.canvas.tag_bind("hidden_btn", "<Button-1>", self.hidden_button_click)
        self.canvas.tag_bind("hidden_btn", "<B1-Motion>", self.resize_hidden_button)

        # Start a separate thread for continuous microphone listening for visualization
        # This thread only captures raw audio for volume/waveform, not for speech recognition.
        self.audio_viz_thread = threading.Thread(target=self.listen_microphone_for_viz, daemon=True)
        self.audio_viz_thread.start()

        self.animate() # Start the GUI animation loop

    # === Hidden Button Logic ===
    def hidden_button_click(self, event):
        """Handles click on the hidden button (e.g., for toggling transparency)."""
        print("Hidden button clicked! (Toggle or secret action here)")
        # Example: Toggle window transparency
        current_alpha = self.root.attributes("-alpha")
        if current_alpha > 0.5: # If mostly visible, make it more transparent
            self.root.attributes("-alpha", 0.2)
        else: # If transparent, make it fully opaque
            self.root.attributes("-alpha", 1.0)

    def resize_hidden_button(self, event):
        """Allows resizing the hidden button by dragging it."""
        # Update the size of the hidden button based on mouse movement
        new_size = max(20, event.x - self.hidden_button_x) # Minimum size 20
        self.hidden_button_size = new_size
        self.canvas.coords(self.hidden_button,
                           self.hidden_button_x, self.hidden_button_y,
                           self.hidden_button_x + self.hidden_button_size,
                           self.hidden_button_y + self.hidden_button_size)

    # === Dragging Window ===
    def start_drag(self, event):
        """Records initial mouse position for window dragging."""
        self.offset_x = event.x
        self.offset_y = event.y

    def do_drag(self, event):
        """Moves the window as the mouse is dragged."""
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    # === GUI State Updates (called by main J.A.R.V.I.S. logic) ===
    def update_state(self, state):
        """Updates the internal state of the GUI for animation changes."""
        self.state = state
        # Optionally, trigger a redraw immediately for critical state changes
        # self.draw_gui()

    def update_volume(self, level):
        """Updates the volume level for microphone visualization."""
        self.volume_level = level

    # === Drawing Functions ===
    def draw_gui(self):
        """Draws all elements of the J.A.R.V.I.S. GUI on the canvas."""
        self.canvas.delete("all") # Clear previous drawings
        cx, cy = 450, 300 # Center of the canvas

        # Redraw hidden button (invisible, but keeps its binding)
        self.hidden_button = self.canvas.create_rectangle(
            self.hidden_button_x, self.hidden_button_y,
            self.hidden_button_x + self.hidden_button_size,
            self.hidden_button_y + self.hidden_button_size,
            fill="", outline="", tags="hidden_btn"
        )
        # Re-bind to ensure events are captured after redraw
        self.canvas.tag_bind("hidden_btn", "<Button-1>", self.hidden_button_click)
        self.canvas.tag_bind("hidden_btn", "<B1-Motion>", self.resize_hidden_button)

        # Glowing Triangle (Inner core)
        triangle_radius = 120
        triangle_points = []
        for i in range(3):
            angle_deg = 90 + i * 120 # Start at top, then 120 deg apart
            angle_rad = math.radians(angle_deg)
            x = cx + triangle_radius * math.cos(angle_rad)
            y = cy + triangle_radius * math.sin(angle_rad)
            triangle_points.extend([x, y])

        # Interpolate color for glow effect
        glow_strength = (math.sin(self.glow_phase) + 1) / 2 # Oscillates between 0 and 1
        glow_color = self.interpolate_color("#003333", "#00ffff", glow_strength) # Dark teal to bright cyan
        self.canvas.create_polygon(triangle_points, fill=glow_color, outline="")
        self.canvas.create_text(cx, cy + 10, text="JARVIS", fill="black", font=("Arial Black", 24))

        # Rings
        self.canvas.create_oval(cx-120, cy-120, cx+120, cy+120, outline="#00bfff", width=2) # Innermost ring
        self.canvas.create_oval(cx-170, cy-170, cx+170, cy+170, outline="#00bfff", width=2) # Middle ring
        self.canvas.create_oval(cx-270, cy-270, cx+270, cy+270, outline="#00bfff", width=2) # Outermost ring

        # Animated joined rectangles on rings
        self.draw_joined_rectangles(cx, cy, 170, 12, self.third_ring_angle, "#00ffff") # On middle ring
        self.draw_joined_rectangles(cx, cy, 270, 16, self.outer_ring_angle, "#00ffff") # On outermost ring
        self.draw_progress_ring(cx, cy, 200, 6, self.progress_angle) # Animated arc

        # Conditional drawing based on J.A.R.V.I.S. state
        if self.state == "listening":
            self.draw_waveform(cx, cy, 145, 30, self.waveform_phase) # Draw waveform when listening
            # Pulsating circle based on volume
            scale = min(self.volume_level / 2000, 2.0) # Normalize volume for scaling
            r = 150 + 40 * scale # Radius changes with volume
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#00FF44", width=2) # Green pulsating ring
        elif self.state == "processing" or self.state == "speaking":
            # Show a different visual for processing/speaking if desired
            self.canvas.create_text(cx, cy + 50, text=self.state.upper(), fill="white", font=("Arial", 16))


    def draw_progress_ring(self, cx, cy, radius, width, angle):
        """Draws an animated arc representing progress."""
        extent = (math.sin(math.radians(angle)) + 1) * 150 # Arc length oscillates
        self.canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius,
                               start=90, extent=extent, outline="lime", width=width, style="arc")

    def draw_waveform(self, cx, cy, radius, bars, phase):
        """Draws a circular waveform based on microphone input."""
        for i in range(bars):
            angle = math.radians(i * (360 / bars)) # Angle for each bar
            amp = 10 + 10 * math.sin(phase + i * 0.5) # Amplitude changes with phase
            x1 = cx + (radius - amp) * math.cos(angle)
            y1 = cy + (radius - amp) * math.sin(angle)
            x2 = cx + (radius + amp) * math.cos(angle)
            y2 = cy + (radius + amp) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill="#33ffff", width=2) # Cyan lines

    def draw_joined_rectangles(self, cx, cy, radius, segments, base_angle, color):
        """Draws segments of joined rectangles around a circle."""
        angle_step = 360 / segments
        rect_length = 40
        rect_thickness_inner = 8
        rect_thickness_outer = 18
        for i in range(segments):
            angle_deg = base_angle + i * angle_step
            angle_rad = math.radians(angle_deg)
            # Calculate points for a trapezoidal shape rotated around the center
            x = cx + radius * math.cos(angle_rad)
            y = cy + radius * math.sin(angle_rad)
            ux, uy = math.cos(angle_rad), math.sin(angle_rad) # Unit vector pointing outwards
            px, py = -uy, ux # Perpendicular unit vector
            
            x1 = x - rect_length/2 * ux - rect_thickness_inner/2 * px
            y1 = y - rect_length/2 * uy - rect_thickness_inner/2 * py
            x2 = x + rect_length/2 * ux - rect_thickness_outer/2 * px
            y2 = y + rect_length/2 * uy - rect_thickness_outer/2 * py
            x3 = x + rect_length/2 * ux + rect_thickness_outer/2 * px
            y3 = y + rect_length/2 * uy + rect_thickness_outer/2 * py
            x4 = x - rect_length/2 * ux + rect_thickness_inner/2 * px
            y4 = y - rect_length/2 * uy + rect_thickness_inner/2 * py
            self.canvas.create_polygon([x1, y1, x2, y2, x3, y3, x4, y4], fill=color, outline="")

    def interpolate_color(self, start_hex, end_hex, factor):
        """Interpolates between two hex colors."""
        def hex_to_rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
        def rgb_to_hex(rgb): return "#%02x%02x%02x" % rgb
        start = hex_to_rgb(start_hex)
        end = hex_to_rgb(end_hex)
        blended = tuple(int(start[i] + (end[i] - start[i]) * factor) for i in range(3))
        return rgb_to_hex(blended)

    def animate(self):
        """Main animation loop for the GUI."""
        # Update animation phases
        self.glow_phase += 0.05
        self.waveform_phase += 0.12
        self.progress_angle = (self.progress_angle + 1.5) % 360
        self.outer_ring_angle = (self.outer_ring_angle + 1.2) % 360
        self.third_ring_angle = (self.third_ring_angle + 1.8) % 360
        
        self.draw_gui() # Redraw all elements
        self.root.after(33, self.animate) # Call animate again after 33ms (approx 30 FPS)

    def fade_exit(self, event=None):
        """Smoothly fades out the window before destroying it."""
        for i in range(10, -1, -1):
            self.root.attributes("-alpha", i/10) # Decrease transparency
            self.root.update() # Update the window immediately
            time.sleep(0.05) # Small delay
        self.root.destroy() # Destroy the window after fading

    def listen_microphone_for_viz(self):
        """
        Continuously listens to the microphone for volume data for GUI visualization.
        This runs in a separate thread and does NOT perform speech recognition.
        """
        p = pyaudio.PyAudio()
        stream = None
        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100,
                            input=True, frames_per_buffer=1024,
                            input_device_index=DEFAULT_MIC_INDEX) # Use the same default mic
            
            while True:
                try:
                    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
                    volume = np.linalg.norm(data) # Calculate RMS volume
                    self.update_volume(volume)
                except Exception as e:
                    # Handle audio errors gracefully without stopping the thread
                    print(f"Error in audio visualization stream: {e}")
                    self.update_volume(0) # Reset volume on error
                time.sleep(0.01) # Small delay to prevent excessive CPU usage
        except Exception as e:
            print(f"Failed to open audio stream for visualization: {e}")
            # If the stream can't be opened, ensure volume is 0 and thread exits gracefully
            self.update_volume(0)
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()


# ========== VOICE COMMAND PROCESSING (Modified for GUI interaction) ==========
def wish():
    """Greets the user based on the time of day and updates GUI."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning sir, I am your personal assistant Jarvis."
    elif 12 <= hour < 16:
        greeting = "Good afternoon sir, I am your personal assistant Jarvis."
    elif 16 <= hour < 21:
        greeting = "Good evening sir, I am your personal assistant Jarvis."
    else:
        greeting = "Working late tonight sir? How can I assist you?"
    
    speak(greeting)
    # No PySide6 notification, so we can update GUI text if we add a text display
    # For now, just print to console.
    print(f"GUI Notification Placeholder: {APP_NAME}, {greeting.split(',')[0]}")

def speak(audio):
    """Converts text to speech using pyttsx3 and updates GUI state."""
    if app_gui:
        app_gui.update_state("speaking")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        selected_voice_id = None

        # Try to find a male voice
        for voice in voices:
            # Check for keywords in name or if gender attribute is available and male
            # Note: 'gender' attribute might not be consistently available across all platforms/pyttsx3 versions.
            if "male" in voice.name.lower() or (hasattr(voice, 'gender') and voice.gender == 'male'):
                selected_voice_id = voice.id
                break

        if selected_voice_id:
            engine.setProperty('voice', selected_voice_id)
            # Attempt to make it sound deeper by lowering the rate
            current_rate = engine.getProperty('rate')
            engine.setProperty('rate', current_rate * 0.85) # Reduce speed by 15%
        else:
            print("No male voice found. Using default voice.")
            print("Available voices (consider manually setting a voice ID for a deep male voice):")
            for voice in voices:
                print(f"  ID: {voice.id}, Name: {voice.name}, Languages: {voice.languages}")

        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS failed: {e}. Please ensure pyttsx3 is correctly installed and configured.")
    finally:
        if app_gui:
            app_gui.update_state("idle") # Return to idle after speaking

def take_command(recorder=None):
    """
    Listens for a command from the microphone and returns it as a string.
    Updates GUI state during listening and processing.
    """
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 1.0
    
    for attempt in range(3):
        try:
            with sr.Microphone(device_index=DEFAULT_MIC_INDEX) as source:
                print(f"Adjusting for ambient noise (attempt {attempt+1}/3)...")
                if app_gui:
                    app_gui.update_state("listening") # Update GUI to listening state
                r.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                
                audio = r.listen(source, timeout=5, phrase_time_limit=15)
                print("Processing audio...")
                if app_gui:
                    app_gui.update_state("processing") # Update GUI to processing state
                
                query = ""
                try:
                    query = r.recognize_google(audio, language='en-in').lower()
                    print(f"Google recognized: {query}")
                    if SECRET_RECORDING and recorder:
                        recorder.save_training_data(audio.frame_data, query) 
                    return query
                except sr.UnknownValueError:
                    print("Google couldn't understand audio. Trying Sphinx (offline)...")
                except sr.RequestError as e:
                    print(f"Google request error: {e}. Check internet connection or API limits. Trying Sphinx (offline)...")

                try:
                    query = r.recognize_sphinx(audio).lower()
                    print(f"Sphinx recognized: {query}")
                    if SECRET_RECORDING and recorder:
                        recorder.save_training_data(audio.frame_data, query)
                    return query
                except sr.UnknownValueError:
                    print("Sphinx couldn't understand audio either. No recognition.")
                except Exception as e:
                    print(f"Sphinx error: {e}. Ensure Sphinx models are installed if using offline recognition.")

        except sr.WaitTimeoutError:
            print("No speech detected within time limit.")
            if attempt < 2:
                speak("I didn't hear anything. Please speak again.")
        except Exception as e:
            print(f"Error in listening: {e}")
            if "device_index" in str(e) or "Error opening audio device" in str(e):
                speak("Microphone not available. Please check your audio settings and ensure it's not in use by another application.")
                break 
            if attempt < 2:
                speak("There was an audio error. Please try again.")
        finally:
            if app_gui:
                app_gui.update_state("idle") # Always return to idle after an attempt
    
    speak("I'm having trouble understanding. Please try again later.")
    return ""

def split_commands(query):
    """
    Splits a complex query into individual commands based on common conjunctions.
    This helps in processing multi-part requests.
    """
    delimiters = r'\b(?:and|then|also|next|after that|followed by)\b'
    commands = re.split(delimiters, query, flags=re.IGNORECASE)
    commands = [cmd.strip() for cmd in commands if cmd.strip()]
    
    # Remove the wake word from the beginning of each command for cleaner processing
    commands = [re.sub(r'^(jarvis|hey jarvis|ok jarvis)\s*', '', cmd, flags=re.IGNORECASE).strip()
                for cmd in commands]
    
    return [cmd for cmd in commands if cmd] # Return only non-empty commands

def execute_multi_commands(commands):
    """Iterates through and executes a list of commands sequentially."""
    speak(f"Executing {len(commands)} commands.")
    # Removed PySide6 notification, now speak directly
    # show_notification("Multi-Command", f"Executing {len(commands)} tasks.")
    
    for command in commands:
        print(f"Executing command: {command}")
        status = process_command(command)
        if status == "exit": # If any command signals an exit, stop processing
            break
        time.sleep(1) # Small delay between commands for better user experience

def process_command(command):
    """The main command processing logic, mapping recognized phrases to functions."""
    command = command.lower() # Convert command to lowercase for consistent matching

    # Basic interactions
    if "hello" in command or "hi jarvis" in command:
        responses = ["Hello sir, how can I assist you?", "Hi there! What can I do for you?"]
        speak(random.choice(responses))
        
    elif "how are you" in command or "what's up" in command:
        responses = ["I'm functioning optimally, sir. Ready to assist!", "All systems operational, ready for your commands!"]
        speak(random.choice(responses))
        
    elif "thank you" in command or "thanks" in command:
        speak("You're welcome, sir!")
        
    elif "your name" in command or "who are you" in command:
        speak(f"I am Jarvis, your personal assistant. Created by Krish Sir!") # Updated developer name
        
    # System commands (Windows specific via os.system or ctypes)
    elif "shutdown pc" in command or "shut down computer" in command:
        system_command("shutdown")
    elif "restart pc" in command or "reboot computer" in command:
        system_command("restart")
    elif "lock pc" in command or "lock computer" in command:
        system_command("lock")
    elif "sleep pc" in command or "put computer to sleep" in command:
        system_command("sleep")
    elif "hibernate pc" in command or "hibernate computer" in command:
        system_command("hibernate")
    elif "log off pc" in command or "sign out" in command:
        system_command("log off")
    elif "show running processes" in command or "what processes are running" in command:
        show_running_processes()
    elif "show my ip address" in command or "what is my ip" in command:
        show_ip_address()
    elif "flush dns" in command:
        flush_dns()
    elif "set screen brightness to" in command:
        try:
            level = int(re.search(r'\d+', command).group())
            set_screen_brightness(level) # Placeholder
        except (AttributeError, ValueError):
            speak("Please specify a valid brightness level, for example, 'set screen brightness to 50 percent'.")
    elif "empty recycle bin" in command:
        empty_recycle_bin() # Placeholder
    elif "open calculator" in command:
        open_application("calculator")
    elif "open notepad" in command:
        open_application("notepad")
    elif "open paint" in command:
        open_application("paint")
    elif "open file explorer" in command or "open my computer" in command:
        open_application("explorer") # Windows File Explorer
    elif "open task manager" in command:
        open_application("taskmgr") # Windows Task Manager
    elif "open control panel" in command:
        open_application("control") # Windows Control Panel
    elif "open device manager" in command:
        open_application("devmgmt.msc") # Windows Device Manager
    elif "open services" in command:
        open_application("services.msc") # Windows Services
    elif "open event viewer" in command:
        open_application("eventvwr.msc") # Windows Event Viewer
    elif "open registry editor" in command:
        open_application("regedit") # Windows Registry Editor (use with caution!)
    elif "open system information" in command:
        open_application("msinfo32") # Windows System Information
    elif "open directx diagnostic" in command:
        open_application("dxdiag") # DirectX Diagnostic Tool
    elif "open disk management" in command:
        open_application("diskmgmt.msc") # Disk Management
    elif "open firewall" in command:
        open_application("wf.msc") # Windows Defender Firewall with Advanced Security
    elif "open programs and features" in command:
        open_application("appwiz.cpl") # Programs and Features (Add/Remove Programs)
    elif "open downloads folder" in command:
        open_special_folder("downloads")
    elif "open documents folder" in command:
        open_special_folder("documents")
    elif "open desktop folder" in command:
        open_special_folder("desktop")
    elif "open program files" in command:
        open_special_folder("program files")
    elif "open startup folder" in command:
        open_special_folder("startup")
    elif "create new folder" in command:
        folder_name = command.replace("create new folder", "").strip()
        if folder_name:
            create_new_folder(folder_name)
        else:
            speak("Please tell me the name of the folder you want to create.")
    elif "delete file" in command or "delete folder" in command:
        item_name = command.replace("delete file", "").replace("delete folder", "").strip()
        if item_name:
            delete_item(item_name) # Placeholder due to high risk
        else:
            speak("Please tell me the name of the file or folder to delete.")
    elif "kill process" in command:
        process_name = command.replace("kill process", "").strip()
        if process_name:
            kill_process_by_name(process_name)
        else:
            speak("Please specify the name of the process to kill.")
    elif "what is my os" in command or "operating system info" in command:
        get_os_info()
    elif "ping" in command:
        url = command.replace("ping", "").strip()
        if url:
            ping_website(url)
        else:
            speak("Please specify a website or IP address to ping.")
    elif "search for file" in command:
        filename = command.replace("search for file", "").strip()
        if filename:
            search_for_file(filename) # Placeholder
        else:
            speak("Please tell me the name of the file to search for.")
    elif "battery" in command: # New command for battery percentage
        get_battery_percentage()

    # Web browsing
    elif "open youtube" in command:
        open_website("youtube.com")
        
    elif "open github" in command:
        open_website("github.com")
        
    elif "open google" in command:
        open_website("google.com")
        
    elif "open my youtube channel" in command:
        webbrowser.open("https://youtube.com/@kj-gaming-781")
        speak("Opening your YouTube channel.")
        # show_notification(APP_NAME, "Opening YouTube channel") # Removed PySide6 notification
        
    elif "search for" in command:
        search_query = command.split("search for")[-1].strip()
        if search_query:
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            speak(f"Searching for {search_query}.")
            # show_notification("Search", f"Looking for {search_query}") # Removed PySide6 notification
    elif "search youtube for" in command:
        query = command.replace("search youtube for", "").strip()
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            speak(f"Searching YouTube for {query}.")
    elif "search wikipedia for" in command:
        query = command.replace("search wikipedia for", "").strip()
        if query:
            wikipedia_summary(query) # Re-use existing wikipedia function
    elif "search amazon for" in command:
        query = command.replace("search amazon for", "").strip()
        if query:
            webbrowser.open(f"https://www.amazon.com/s?k={query}")
            speak(f"Searching Amazon for {query}.")
            
    elif "open" in command: # Generic open command for apps and websites
        site_name = command.replace("open", "").strip()
        if site_name:
            app_map_names = {
                "notepad": "notepad", "calculator": "calculator", "camera": "camera",
                "command prompt": "command prompt", "paint": "paint", "discord": "discord",
                "vs code": "vs code", "word": "word", "excel": "excel",
                "powerpoint": "powerpoint", "chrome": "chrome", "firefox": "firefox",
                "edge": "msedge.exe", "spotify": "spotify.exe", "vlc": "vlc.exe",
                "brave": "brave.exe", "opera": "opera.exe", "telegram": "telegram.exe", "zoom": "zoom",
                "microsoft teams": "teams"
            }
            app_found = False
            for app_key, app_display_name in app_map_names.items():
                if app_key in site_name:
                    open_application(app_display_name)
                    app_found = True
                    break
            
            if not app_found:
                open_website(site_name) # Fallback to opening as a website if not a known app
        
    elif "close" in command:
        app_name = command.split("close", 1)[1].strip()
        if app_name:
            close_application(app_name)
    elif "minimize window" in command or "hide window" in command:
        minimize_current_window()
    elif "maximize window" in command or "full screen window" in command:
        maximize_current_window()
    elif "restore window" in command or "unmaximize window" in command:
        restore_current_window()
    elif "switch to" in command:
        app_name = command.replace("switch to", "").strip()
        if app_name:
            switch_to_window(app_name)
        else:
            speak("Please tell me which application to switch to.")
    elif "type" in command:
        text_to_type = command.replace("type", "").strip()
        if text_to_type:
            type_text(text_to_type)
        else:
            speak("What would you like me to type?")
    elif "press enter" in command:
        pyautogui.press("enter")
        speak("Pressed Enter.")
    elif "press escape" in command:
        pyautogui.press("escape")
        speak("Pressed Escape.")
    elif "press tab" in command:
        pyautogui.press("tab")
        speak("Pressed Tab.")
    elif "scroll up" in command:
        scroll_page("up")
    elif "scroll down" in command:
        scroll_page("down")
    elif "go back" in command: # For web browsers
        pyautogui.hotkey("alt", "left")
        speak("Going back.")
    elif "go forward" in command: # For web browsers
        pyautogui.hotkey("alt", "right")
        speak("Going forward.")
    elif "refresh page" in command:
        pyautogui.press("f5")
        speak("Refreshing page.")
            
    # Media control (Volume) - uses pyautogui, generally cross-platform but relies on OS
    elif "volume up" in command:
        pyautogui.press("volumeup")
        speak("Volume increased.")
        
    elif "volume down" in command:
        pyautogui.press("volumedown")
        speak("Volume decreased.")
        
    elif "set volume to" in command:
        try:
            level = int(re.search(r'\d+', command).group())
            # Placeholder: Actual volume setting might need external tools or more complex ctypes
            speak(f"Attempting to set volume to {level} percent. (Feature under development)")
            # show_notification("Volume", f"Set to {level}% (approx)") # Removed PySide6 notification
        except (AttributeError, ValueError):
            speak("Please specify a valid volume level, for example, 'set volume to 50 percent'.")
            
    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Volume muted.")
        # show_notification("Volume", "Muted") # Removed PySide6 notification
    elif "unmute" in command:
        pyautogui.press("volumemute") # Toggles mute
        speak("Volume unmuted.")
        # show_notification("Volume", "Unmuted") # Removed PySide6 notification
        
    elif "play" in command and ("music" in command or "song" in command):
        speak("Playing music. (This feature is a placeholder and requires a music player integration).")
        # show_notification("Music", "Playing (placeholder)") # Removed PySide6 notification
    elif "pause" in command and ("music" in command or "song" in command):
        speak("Pausing music. (This feature is a placeholder).")
        # show_notification("Music", "Paused (placeholder)") # Removed PySide6 notification
    elif "next song" in command:
        pyautogui.press("nexttrack")
        speak("Playing next song.")
    elif "previous song" in command:
        pyautogui.press("prevtrack")
        speak("Playing previous song.")
    elif "play/pause" in command:
        pyautogui.press("playpause")
        speak("Toggling play/pause.")
        
    # Information
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")
        # show_notification("Time", current_time) # Removed PySide6 notification
        
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {current_date}.")
        # show_notification("Date", current_date) # Removed PySide6 notification
        
    elif "day of the week" in command:
        day_of_week = datetime.datetime.now().strftime("%A")
        speak(f"Today is {day_of_week}.")
        # show_notification("Day", day_of_week) # Removed PySide6 notification

    elif "weather" in command:
        city = command.split("in")[-1].strip() if "in" in command else None
        get_weather(city)
        
    elif "internet speed" in command:
        check_internet_speed()
    
    elif "define" in command:
        word_to_define = command.replace("define", "").strip()
        if word_to_define:
            define_word(word_to_define)
        else:
            speak("Please tell me the word you want to define.")
    elif "translate" in command:
        # Example: "translate hello to spanish"
        match = re.search(r'translate (.+) to (.+)', command)
        if match:
            text_to_translate = match.group(1).strip()
            target_language = match.group(2).strip()
            translate_text(text_to_type, target_language) # Placeholder
        else:
            speak("Please specify what to translate and to which language.")
    elif "read selected text" in command:
        read_selected_text() # Placeholder
        
    # Personal features
    elif "remember that" in command:
        info = command.replace("remember that", "").strip()
        if info:
            remember_information(info) # Placeholder
            
    elif "what do you remember" in command:
        recall_information() # Placeholder
        
    elif "call kk" in command or "call kay kay" in command:
        whatsapp_call_kk() # Placeholder
        
    elif "joke" in command:
        joke = pyjokes.get_joke()
        speak(joke)
        # show_notification("Joke", joke) # Removed PySide6 notification
        
    elif "birthday" in command:
        speak("Happy birthday sir! May all your wishes come true!") # Changed from "Krish sir!"
        # show_notification("Birthday", "Happy birthday sir!") # Removed PySide6 notification
        
    # System utilities
    elif "screenshot" in command or "take a screenshot" in command:
        take_screenshot()
    elif "snip" in command or "open snipping tool" in command:
        open_application("SnippingTool") # Windows Snipping Tool
        
    # Location commands
    elif "where am i" in command or "my location" in command:
        get_location()
        
    elif "cursor position" in command or "mouse location" in command:
        get_screen_location()
        
    # Clipboard operations
    elif "copy" in command:
        clipboard_operation("copy")
    elif "paste" in command:
        clipboard_operation("paste")
    elif "cut" in command:
        clipboard_operation("cut")
    elif "select all" in command:
        clipboard_operation("select all")
        
    # File operations
    elif "open file" in command:
        file_query = command.replace("open file", "").strip()
        if file_query:
            open_specific_file(file_query) # Placeholder
        else:
            speak("Please specify a file to open.")
            
    elif "recycle bin" in command:
        if "empty" in command:
            empty_recycle_bin() # Placeholder
        else:
            open_recycle_bin() # Placeholder
            
    # System settings (Windows specific)
    elif "open settings" in command:
        setting_type = command.replace("open settings", "").strip()
        open_settings(setting_type) # Placeholder
        
    elif "wifi" in command or "wi-fi" in command:
        if "on" in command:
            toggle_wifi("on") # Placeholder
        elif "off" in command:
            toggle_wifi("off") # Placeholder
        else:
            open_settings("wifi") # Placeholder
            
    elif "bluetooth" in command:
        if "on" in command:
            toggle_bluetooth("on") # Placeholder
        elif "off" in command:
            toggle_bluetooth("off") # Placeholder
        else:
            open_settings("bluetooth") # Placeholder
            
    elif "location settings" in command:
        open_settings("location") # Placeholder
        
    # Screen recording
    elif "screen record" in command:
        duration = 30  # default
        numbers = [int(s) for s in re.findall(r'\b\d+\b', command)]
        if numbers:
            duration = numbers[0]
        screen_recording(duration) # Placeholder
        
    # Voice recording
    elif "record voice" in command or "voice recording" in command:
        duration = 30  # default
        numbers = [int(s) for s in re.findall(r'\b\d+\b', command)]
        if numbers:
            duration = numbers[0]
        voice_recording(duration) # Placeholder
        
    # Webcam access
    elif "access webcam" in command or "open camera" in command:
        access_webcam() # Placeholder
        
    # Phone number location
    elif "locate phone number" in command:
        numbers = re.findall(r'\d+', command)
        if numbers:
            phone = ''.join(numbers)
            locate_phone_number(phone)
        else:
            speak("Please specify a phone number.")
            
    # PDF reading
    elif "read pdf" in command:
        file_query = command.replace("read pdf", "").strip()
        if file_query:
            read_pdf(file_query)
        else:
            speak("Please specify a PDF file.")
            
    # Latest news
    elif "latest news" in command:
        topic = None
        if "about" in command:
            topic = command.split("about")[-1].strip()
        get_latest_news(topic)
        
    # System condition
    elif "system condition" in command or "system health" in command:
        check_system_condition()
        
    # Play YouTube song
    elif "play youtube song" in command:
        query = command.replace("play youtube song", "").strip()
        if query:
            play_youtube_song(query)
        else:
            speak("Please specify a song name.")
            
    # Download YouTube song
    elif "download youtube song" in command:
        urls = re.findall(r'https?://\S+', command)
        if urls:
            download_youtube_song(urls[0])
        else:
            speak("Please provide a YouTube URL.")
            
    # Download Instagram profile
    elif "download instagram profile" in command:
        username = command.replace("download instagram profile", "").replace("@", "").strip()
        if username:
            download_instagram_profile(username)
        else:
            speak("Please specify an Instagram username.")
            
    # Programming joke
    elif "programming joke" in command:
        tell_programming_joke()
        
    # Wikipedia search
    elif "wikipedia" in command:
        query = command.replace("wikipedia", "").replace("search", "").strip()
        if query:
            wikipedia_summary(query)
        else:
            speak("What should I search on Wikipedia?")
            
    # Voice Model Training
    elif "train my voice" in command or "retrain jarvis" in command:
        speak("Starting voice model training. This might take a few moments.")
        # show_notification("Voice Training", "Training model...") # Removed PySide6 notification
        train_voice_model()
        speak("Voice model training complete.")
        # show_notification("Voice Training", "Training finished.") # Removed PySide6 notification

    # Exit command
    elif any(cmd in command for cmd in ["exit", "goodbye", "shut down", "quit"]):
        farewells = ["Shutting down systems. Goodbye sir!",
                     "Powering off. Have a great day!",
                     "Jarvis signing off. Until next time!"]
        farewell = random.choice(farewells)
        speak(farewell)
        # show_notification(APP_NAME, farewell.split(".")[0]) # Removed PySide6 notification
        if app_gui:
            app_gui.fade_exit() # Trigger smooth GUI exit
        return "exit"
        
    # Fallback for unrecognized commands
    else:
        speak("I didn't understand that command. Could you rephrase?")
        # show_notification("Command Error", "Could not process command") # Removed PySide6 notification
        
    return "continue"

# ========== COMMAND IMPLEMENTATIONS ==========
def system_command(action):
    """Performs a system-level action like shutdown, restart, or lock. These are Windows-specific."""
    try:
        if action == "shutdown":
            speak("Shutting down the system. Goodbye!")
            # Use /s for shutdown, /t 1 for 1 second delay
            subprocess.run(["shutdown", "/s", "/t", "1"], check=True)
        elif action == "restart":
            speak("Restarting the system.")
            # Use /r for restart, /t 1 for 1 second delay
            subprocess.run(["shutdown", "/r", "/t", "1"], check=True)
        elif action == "lock":
            speak("Locking the system.")
            # Windows API call to lock the workstation
            ctypes.windll.user32.LockWorkStation()
        elif action == "sleep":
            speak("Putting the system to sleep.")
            # This command can be tricky and may require specific power settings.
            # It attempts to put the system into a low-power sleep state.
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
        elif action == "hibernate":
            speak("Hibernating the system.")
            # Use /h for hibernate
            subprocess.run(["shutdown", "/h"], check=True)
        elif action == "log off":
            speak("Logging off.")
            # Use /l for log off
            subprocess.run(["shutdown", "/l"], check=True)
        # show_notification("System Command", f"Executed: {action}") # Removed PySide6 notification
    except Exception as e:
        speak(f"Failed to perform {action} command. This might require administrator privileges or specific system configurations.")
        print(f"System command error ({action}): {e}")
        # show_notification("System Error", f"Failed to {action}") # Removed PySide6 notification

def show_running_processes():
    """Lists currently running processes."""
    try:
        processes = [p.name() for p in psutil.process_iter()]
        speak(f"There are {len(processes)} processes running. For example, {', '.join(processes[:5])}.")
        # show_notification("Running Processes", f"{len(processes)} processes active.") # Removed PySide6 notification
    except Exception as e:
        speak("Could not retrieve running processes.")
        print(f"Process list error: {e}")
        # show_notification("Error", "Failed to get processes.") # Removed PySide6 notification

def show_ip_address():
    """Displays the system's local IP address."""
    try:
        # This gets the local IP address of the machine, not necessarily the public one.
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        speak(f"Your local IP address is {ip_address}.")
        # show_notification("IP Address", ip_address) # Removed PySide6 notification
    except Exception as e:
        speak("Could not retrieve IP address.")
        print(f"IP address error: {e}")
        # show_notification("Error", "Failed to get IP.") # Removed PySide6 notification

def flush_dns():
    """Flushes the DNS resolver cache on Windows."""
    try:
        # This command requires administrator privileges to execute successfully.
        subprocess.run(["ipconfig", "/flushdns"], check=True, capture_output=True, text=True)
        speak("DNS cache flushed successfully.")
        # show_notification("DNS", "Cache flushed.") # Removed PySide6 notification
    except subprocess.CalledProcessError as e:
        speak("Failed to flush DNS cache. This might require administrator privileges.")
        print(f"DNS flush error: {e.stderr}")
        # show_notification("Error", "DNS flush failed.") # Removed PySide6 notification
    except FileNotFoundError:
        speak("ipconfig command not found. This feature is for Windows only.")
        # show_notification("Error", "ipconfig not found.") # Removed PySide6 notification
    except Exception as e:
        speak("An unexpected error occurred while flushing DNS.")
        print(f"DNS flush unexpected error: {e}")
        # show_notification("Error", "DNS flush failed.") # Removed PySide6 notification

def set_screen_brightness(level):
    """
    Placeholder for setting screen brightness.
    This functionality is highly OS-specific and often requires external libraries or direct
    interaction with Windows APIs (e.g., WMI, or third-party tools).
    """
    speak(f"Setting screen brightness to {level} percent. This feature requires specific Windows APIs or tools and is currently a placeholder.")
    # show_notification("Brightness", f"Set to {level}% (placeholder)") # Removed PySide6 notification

def create_new_folder(folder_name):
    """Creates a new folder in the current working directory."""
    try:
        os.makedirs(folder_name, exist_ok=True)
        speak(f"Folder '{folder_name}' created successfully.")
        # show_notification("Folder Created", folder_name) # Removed PySide6 notification
    except Exception as e:
        speak(f"Failed to create folder '{folder_name}'.")
        print(f"Create folder error: {e}")
        # show_notification("Error", f"Failed to create {folder_name}") # Removed PySide6 notification

def delete_item(item_name):
    """
    Placeholder for deleting a file or folder.
    WARNING: This is a highly dangerous command. Implement with extreme caution and user confirmation
    (e.g., a GUI confirmation dialog) to prevent accidental data loss.
    """
    speak(f"I cannot delete '{item_name}' directly for safety reasons. This feature is a placeholder and requires explicit confirmation and careful implementation.")
    # show_notification("Deletion Warning", "Deletion command disabled for safety.") # Removed PySide6 notification

def open_special_folder(folder_type):
    """Opens common Windows special folders."""
    paths = {
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos"),
        "program files": os.environ.get("ProgramFiles", "C:\\Program Files"), # Common path for Program Files
        "startup": os.path.join(os.environ.get("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup") # Common path for Startup folder
    }
    target_path = paths.get(folder_type.lower())
    if target_path and os.path.exists(target_path):
        try:
            # 'explorer' command opens the specified path in File Explorer on Windows.
            subprocess.Popen(f'explorer "{target_path}"', shell=True)
            speak(f"Opening your {folder_type} folder.")
            # show_notification("Folder", f"Opened {folder_type}") # Removed PySide6 notification
        except Exception as e:
            speak(f"Failed to open {folder_type} folder.")
            print(f"Open folder error: {e}")
            # show_notification("Error", f"Failed to open {folder_type}") # Removed PySide6 notification
    else:
        speak(f"I cannot find the {folder_type} folder or it's not a recognized special folder.")
        # show_notification("Error", f"Unknown folder: {folder_type}") # Removed PySide6 notification

def kill_process_by_name(process_name):
    """Kills a running process by its name. Requires psutil."""
    try:
        found_and_killed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower() or process_name.lower() in proc.info['name'].lower():
                proc.terminate() # or proc.kill() for a more forceful termination
                speak(f"Process {process_name} terminated.")
                # show_notification("Process Control", f"Killed: {process_name}") # Removed PySide6 notification
                found_and_killed = True
                break
        if not found_and_killed:
            speak(f"No running process found with the name {process_name}.")
            # show_notification("Process Control", f"Process not found: {process_name}") # Removed PySide6 notification
    except psutil.AccessDenied:
        speak(f"Access denied to terminate process {process_name}. This might require administrator privileges.")
        # show_notification("Process Control Error", "Access denied.") # Removed PySide6 notification
    except Exception as e:
        speak(f"Failed to kill process {process_name}.")
        print(f"Kill process error: {e}")
        # show_notification("Process Control Error", f"Failed to kill {process_name}") # Removed PySide6 notification

def get_os_info():
    """Retrieves and speaks basic operating system information."""
    try:
        os_name = platform.system()
        os_version = platform.release()
        os_arch = platform.machine()
        speak(f"You are running {os_name} version {os_version} on a {os_arch} architecture.")
        # show_notification("OS Info", f"{os_name} {os_version} ({os_arch})") # Removed PySide6 notification
    except Exception as e:
        speak("Could not retrieve operating system information.")
        print(f"OS info error: {e}")
        # show_notification("Error", "Failed to get OS info.") # Removed PySide6 notification

def ping_website(url):
    """Pings a website or IP address to check connectivity."""
    try:
        # Add http:// if missing for consistent ping behavior
        if not url.startswith("http"):
            url = "http://" + url
        
        # Extract hostname from URL
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc if parsed_url.netloc else url
        
        # Use -n 1 for Windows (1 packet), -c 1 for Linux/macOS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', hostname]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if "Reply from" in result.stdout or "bytes from" in result.stdout:
            speak(f"Successfully pinged {hostname}. The website is reachable.")
            # show_notification("Ping Success", f"{hostname} is reachable.") # Removed PySide6 notification
        else:
            speak(f"Could not ping {hostname}. The website might be down or unreachable.")
            # show_notification("Ping Failed", f"{hostname} unreachable.") # Removed PySide6 notification
    except subprocess.CalledProcessError as e:
        speak(f"Failed to ping {url}. Error: {e.stderr.strip()}")
        print(f"Ping error: {e.stderr}")
        # show_notification("Ping Error", f"Failed to ping {url}") # Removed PySide6 notification
    except Exception as e:
        speak(f"An unexpected error occurred while trying to ping {url}.")
        print(f"Ping unexpected error: {e}")
        # show_notification("Ping Error", f"Unexpected error for {url}") # Removed PySide6 notification

def search_for_file(filename):
    """
    Placeholder for searching for a file on the system.
    This would require iterating through directories or using OS-specific search tools.
    """
    speak(f"Searching for file '{filename}'. This feature is a placeholder and requires more advanced file system traversal or indexing.")
    # show_notification("File Search", "Feature under development.") # Removed PySide6 notification

def get_battery_percentage():
    """Retrieves and speaks the current battery percentage and status."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "plugged in" if battery.power_plugged else "not plugged in"
            speak(f"Your battery is at {percent} percent and is {plugged}.")
            # show_notification("Battery Status", f"{percent}% {plugged}") # Removed PySide6 notification
        else:
            speak("Could not retrieve battery information. This device might not have a battery.")
            # show_notification("Battery Status", "No battery detected.") # Removed PySide6 notification
    except Exception as e:
        speak("Failed to get battery information.")
        print(f"Battery info error: {e}")
        # show_notification("Error", "Failed to get battery info.") # Removed PySide6 notification

def minimize_current_window():
    """Minimizes the currently active window."""
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            active_window.minimize()
            speak("Window minimized.")
            # show_notification("Window Control", "Minimized current window.") # Removed PySide6 notification
        else:
            speak("No active window found to minimize.")
    except Exception as e:
        speak("Failed to minimize window.")
        print(f"Minimize window error: {e}")
        # show_notification("Error", "Failed to minimize.") # Removed PySide6 notification

def maximize_current_window():
    """Maximizes the currently active window."""
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            active_window.maximize()
            speak("Window maximized.")
            # show_notification("Window Control", "Maximized current window.") # Removed PySide6 notification
        else:
            speak("No active window found to maximize.")
    except Exception as e:
        speak("Failed to maximize window.")
        print(f"Maximize window error: {e}")
        # show_notification("Error", "Failed to maximize.") # Removed PySide6 notification

def restore_current_window():
    """Restores the currently active window from minimized/maximized state."""
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            active_window.restore()
            speak("Window restored.")
            # show_notification("Window Control", "Restored current window.") # Removed PySide6 notification
        else:
            speak("No active window found to restore.")
    except Exception as e:
        speak("Failed to restore window.")
        print(f"Restore window error: {e}")
        # show_notification("Error", "Failed to restore.") # Removed PySide6 notification

def switch_to_window(app_name):
    """Switches to an open window by application name."""
    try:
        # pygetwindow finds windows by title. Case sensitivity and exact matching can be an issue.
        windows = gw.getWindowsWithTitle(app_name)
        if windows:
            windows[0].activate() # Activate the first matching window
            speak(f"Switched to {app_name}.")
            # show_notification("Window Switch", f"Switched to {app_name}") # Removed PySide6 notification
        else:
            speak(f"No window found for {app_name}.")
            # show_notification("Window Switch", f"No window for {app_name}") # Removed PySide6 notification
    except Exception as e:
        speak(f"Failed to switch to {app_name}.")
        print(f"Switch window error: {e}")
        # show_notification("Error", "Failed to switch window.") # Removed PySide6 notification

def type_text(text):
    """Types the given text using pyautogui."""
    try:
        pyautogui.write(text)
        speak(f"Typed: {text}")
        # show_notification("Typing", text) # Removed PySide6 notification
    except Exception as e:
        speak("Failed to type the text.")
        print(f"Type text error: {e}")
        # show_notification("Error", "Failed to type.") # Removed PySide6 notification

def scroll_page(direction):
    """Scrolls the current window up or down."""
    try:
        if direction == "up":
            pyautogui.scroll(200) # Scroll up 200 units
            speak("Scrolling up.")
        elif direction == "down":
            pyautogui.scroll(-200) # Scroll down 200 units
            speak("Scrolling down.")
        # show_notification("Scroll", f"Scrolled {direction}") # Removed PySide6 notification
    except Exception as e:
        speak("Failed to scroll.")
        print(f"Scroll error: {e}")
        # show_notification("Error", "Failed to scroll.") # Removed PySide6 notification

def define_word(word):
    """Defines a word by searching Google Dictionary (web scraping)."""
    speak(f"Searching for the definition of {word}.")
    try:
        search_url = f"https://www.google.com/search?q=define+{word}"
        webbrowser.open(search_url)
        speak(f"Here's what I found for {word}.")
        # show_notification("Definition", f"Searching for {word}") # Removed PySide6 notification
        # A more advanced implementation would parse the search results for the definition
        # For now, just opening the browser is the practical approach.
    except Exception as e:
        speak(f"Failed to find a definition for {word}.")
        print(f"Define word error: {e}")
        # show_notification("Error", "Definition failed.") # Removed PySide6 notification

def translate_text(text, target_language):
    """Placeholder for text translation. Requires a translation API."""
    speak(f"Translating '{text}' to {target_language}. This feature requires a translation API and is currently a placeholder.")
    # show_notification("Translation", "Feature under development.") # Removed PySide6 notification

def read_selected_text():
    """Placeholder for reading selected text. Requires OS-level text selection access."""
    speak("Reading selected text. This feature requires advanced system interaction and is currently a placeholder.")
    # show_notification("Read Text", "Feature under development.") # Removed PySide6 notification

def open_website(site_name):
    """Opens a website in the default browser."""
    try:
        url = site_name
        if not site_name.startswith("http"):
            url = f"https://{site_name.replace(' ', '')}"
            
        webbrowser.open(url)
        speak(f"Opening {site_name}.")
        # show_notification("Web Browser", f"Opening {site_name}") # Removed PySide6 notification
    except Exception as e:
        speak(f"Failed to open {site_name}.")
        print(f"Error opening website: {e}")
        # show_notification("Error", f"Failed to open {site_name}") # Removed PySide6 notification

def open_application(app_name):
    """
    Launches a local application using subprocess.
    Assumes common Windows executable names and that they are in the system's PATH.
    Some applications might require full paths if not in PATH.
    """
    app_map = {
        "notepad": "notepad.exe", "calculator": "calc.exe", "camera": "camerad.exe", # Note: camerad.exe might not be universal
        "command prompt": "cmd.exe", "paint": "mspaint.exe", "discord": "Discord.exe",
        "vs code": "code.exe", "word": "winword.exe", "excel": "excel.exe",
        "powerpoint": "powerpnt.exe", "chrome": "chrome.exe", "firefox": "firefox.exe",
        "edge": "msedge.exe", "spotify": "spotify.exe", "vlc": "vlc.exe",
        "brave": "brave.exe", "opera": "opera.exe", "telegram": "telegram.exe", "zoom": "zoom.exe",
        "microsoft teams": "teams.exe",
        "explorer": "explorer.exe", "task manager": "taskmgr.exe", "control panel": "control.exe",
        "device manager": "devmgmt.msc", "services": "services.msc", "event viewer": "eventvwr.msc",
        "registry editor": "regedit.exe", "system information": "msinfo32.exe",
        "directx diagnostic": "dxdiag.exe", "disk management": "diskmgmt.msc",
        "firewall": "wf.msc", "programs and features": "appwiz.cpl",
        "snipping tool": "SnippingTool.exe"
    }
    app_exe = app_map.get(app_name.lower())
    if not app_exe:
        speak(f"Sorry, I don't know how to open {app_name}.")
        # show_notification("Error", f"Could not find application: {app_name}") # Removed PySide6 notification
        return

    try:
        # shell=True is used for simple execution of known commands/executables on Windows
        # For .msc files, direct execution works. For .cpl, it also works.
        subprocess.Popen(app_exe, shell=True)
        speak(f"Opening {app_name}.")
        # show_notification("Application", f"Opening {app_name}") # Removed PySide6 notification
    except FileNotFoundError:
        speak(f"Sorry, I could not find the application {app_name}. Please ensure it is installed and in your system's PATH.")
        # show_notification("Error", f"Could not find {app_name}") # Removed PySide6 notification
    except Exception as e:
        speak(f"An error occurred while trying to open {app_name}.")
        print(f"Error opening application: {e}")
        # show_notification("Error", f"Failed to open {app_name}") # Removed PySide6 notification

def close_application(app_name):
    """
    Closes an application by process name. Uses psutil for cross-platform process management.
    Note: Some applications might have different process names than their display names.
    """
    try:
        # Mapping common names to their typical Windows process names
        process_name_map = {
            "chrome": "chrome.exe", "firefox": "firefox.exe", "notepad": "notepad.exe",
            "calculator": "Calculator.exe", "camera": "WindowsCamera.exe", "command prompt": "cmd.exe",
            "paint": "mspaint.exe", "discord": "Discord.exe", "vs code": "Code.exe",
            "word": "WINWORD.EXE", "excel": "EXCEL.EXE", "powerpoint": "POWERPNT.EXE",
            "edge": "msedge.exe", "spotify": "spotify.exe", "vlc": "vlc.exe",
            "brave": "brave.exe", "opera": "opera.exe", "telegram": "telegram.exe", "zoom": "zoom.exe",
            "microsoft teams": "teams.exe",
            "explorer": "explorer.exe", "task manager": "taskmgr.exe", "control panel": "control.exe",
            "device manager": "mmc.exe", # devmgmt.msc runs under mmc.exe
            "services": "mmc.exe", # services.msc runs under mmc.exe
            "event viewer": "mmc.exe", # eventvwr.msc runs under mmc.exe
            "registry editor": "regedit.exe", "system information": "msinfo32.exe",
            "directx diagnostic": "dxdiag.exe", "disk management": "mmc.exe", # diskmgmt.msc runs under mmc.msc
            "firewall": "mmc.exe", # wf.msc runs under mmc.msc
            "programs and features": "rundll32.exe", # appwiz.cpl runs under rundll32.exe
            "snipping tool": "SnippingTool.exe"
        }
        target_process_name = process_name_map.get(app_name.lower())
        
        if not target_process_name:
            speak(f"I don't know the process name for {app_name}.")
            return False

        found_and_closed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == target_process_name.lower():
                proc.terminate() # Terminate the process
                found_and_closed = True
                speak(f"Closing {app_name}.")
                # show_notification("Application", f"Closing {app_name}") # Removed PySide6 notification
                break # Assuming we only need to close one instance for now
        
        if not found_and_closed:
            speak(f"Could not find any running application named {app_name}.")
        return found_and_closed
    except Exception as e:
        speak("An error occurred while trying to close the application.")
        print(f"Error closing application: {e}")
        return False

def get_location():
    """Fetches the user's current location based on IP address. Requires internet."""
    try:
        speak("Locating your position, please wait...")
        # show_notification("Location", "Finding your position") # Removed PySide6 notification
        
        response = requests.get('https://ipinfo.io/json')
        response.raise_for_status() # Raise an exception for HTTP errors (e.g., 404, 500)
        
        data = response.json()
        city = data.get('city', 'Unknown City')
        region = data.get('region', 'Unknown Region')
        country = data.get('country', 'Unknown Country')
        location = f"{city}, {region}, {country}"
        speak(f"You are currently in {location}.")
        # show_notification("Location Found", location) # Removed PySide6 notification
    except requests.exceptions.RequestException as e:
        speak("Could not determine your location. The location service is unavailable. Please check your internet connection.")
        print(f"Location error: {e}")
        # show_notification("Location Error", "Service unavailable") # Removed PySide6 notification

def get_screen_location():
    """Announces the current mouse cursor position. Uses pyautogui."""
    try:
        x, y = pyautogui.position()
        position = f"X={x}, Y={y}"
        speak(f"Cursor is at position {position}.")
        # show_notification("Cursor Position", position) # Removed PySide6 notification
    except Exception as e:
        speak("Failed to get cursor position.")
        print(f"Position error: {e}")
        # show_notification("Position", "Service unavailable") # Removed PySide6 notification

def take_screenshot():
    """Takes a screenshot of the primary monitor and saves it. Uses pyautogui."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(filename)
        speak(f"Screenshot saved as {filename}.")
        # show_notification("Screenshot", f"Saved as {filename}") # Removed PySide6 notification
    except Exception as e:
        speak("Failed to take a screenshot. Ensure you have the necessary permissions.")
        print(f"Screenshot error: {e}")
        # show_notification("Screenshot Error", "Operation failed") # Removed PySide6 notification

def get_weather(city=None):
    """Fetches and announces the weather for a specified city or the current location. Requires OpenWeatherMap API key."""
    if not WEATHER_API_KEY or WEATHER_API_KEY == "your_weather_api_key":
        speak("Weather API key is not configured. Please add a valid key from openweathermap.org.")
        # show_notification("API Error", "Weather API key missing.") # Removed PySide6 notification
        return
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    try:
        if not city:
            # Attempt to get the city from the user's IP if not specified
            ip_response = requests.get('https://ipinfo.io/json')
            ip_response.raise_for_status()
            ip_data = ip_response.json()
            city = ip_data.get('city', 'New York') # Default to a known city if IP info fails
            
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        weather_response = requests.get(base_url, params=params)
        weather_response.raise_for_status() # Raise an exception for HTTP errors
        
        weather_data = weather_response.json()
        main_weather = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        
        message = f"The weather in {city} is currently {main_weather} with a temperature of {temperature}°C."
        speak(message)
        # show_notification("Weather", message) # Removed PySide6 notification
    except requests.exceptions.RequestException as e:
        speak(f"Could not retrieve weather for {city}. Please check the city name and your internet connection.")
        print(f"Weather API error: {e}")
        # show_notification("Weather Error", "Failed to retrieve data.") # Removed PySide6 notification

def check_internet_speed():
    """Checks and announces the user's internet download and upload speed. Uses speedtest-cli."""
    speak("Testing internet speed, please wait. This may take a moment.")
    # show_notification("Internet Speed", "Running speed test...") # Removed PySide6 notification
    
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        
        message = f"Your internet speed is approximately {download_speed:.2f} megabits per second download and {upload_speed:.2f} megabits per second upload."
        speak(message)
        # show_notification("Speed Test Complete", f"Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps") # Removed PySide6 notification
    except Exception as e:
        speak("Failed to test internet speed. Please check your connection.")
        print(f"Speed test error: {e}")
        # show_notification("Error", "Failed to run speed test.") # Removed PySide6 notification

def get_latest_news(topic=None):
    """Fetches and announces the latest news headlines from a specified topic or general. Requires NewsAPI key."""
    if not NEWS_API_KEY or NEWS_API_KEY == "your_news_api_key":
        speak("News API key is not configured. Please add a valid key from newsapi.org.")
        # show_notification("API Error", "News API key missing.") # Removed PySide6 notification
        return
        
    try:
        news_api = NewsApiClient(api_key=NEWS_API_KEY)
        if topic:
            top_headlines = news_api.get_top_headlines(q=topic, language='en', country='in')
            speak(f"Here are the latest news headlines about {topic}:")
            # show_notification("News", f"Top headlines for {topic}") # Removed PySide6 notification
        else:
            top_headlines = news_api.get_top_headlines(language='en', country='in')
            speak("Here are the latest top news headlines:")
            # show_notification("News", "Top headlines") # Removed PySide6 notification
            
        if top_headlines['status'] == 'ok' and top_headlines['articles']:
            for i, article in enumerate(top_headlines['articles'][:5]): # Limit to 5 articles
                title = article['title']
                speak(f"News number {i + 1}: {title}.")
                time.sleep(1) # Pause between articles for readability
        else:
            speak("Sorry, I could not fetch the news at this moment.")
            
    except Exception as e:
        speak("Failed to get news headlines.")
        print(f"News API error: {e}")
        # show_notification("News Error", "Failed to retrieve data.") # Removed PySide6 notification

def check_system_condition():
    """Announces key system health metrics like CPU, RAM, and disk usage. Uses psutil."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        message = f"System health report: CPU is at {cpu_percent} percent usage. RAM is at {ram_percent} percent usage. Disk space is {disk_percent} percent full."
        speak(message)
        # show_notification("System Health", f"CPU: {cpu_percent}% | RAM: {ram_percent}% | Disk: {disk_percent}%") # Removed PySide6 notification
    except Exception as e:
        speak("I'm unable to check the system's condition at this time.")
        print(f"System health error: {e}")
        # show_notification("Error", "Could not check system health.") # Removed PySide6 notification
        
def play_youtube_song(query):
    """Searches YouTube for a song and plays its audio stream. Uses pytube and pygame."""
    try:
        speak(f"Searching for {query} on YouTube.")
        # show_notification("YouTube", f"Searching for {query}") # Removed PySide6 notification
        
        search_query = query.replace(' ', '+')
        # Perform a quick search to get the first video URL
        html = requests.get(f'https://www.youtube.com/results?search_query={search_query}')
        video_ids = re.findall(r'/watch\?v=(.{11})', html.text)
        if not video_ids:
            speak("Sorry, I couldn't find any videos for that query.")
            return

        yt_url = f'https://www.youtube.com/watch?v={video_ids[0]}'
        yt = YouTube(yt_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        # Download the audio to a temporary file for pygame to play
        audio_file_path = audio_stream.download(filename="temp_audio.mp4")
        
        # Load and play with pygame mixer
        mixer.music.load(audio_file_path)
        mixer.music.play()
        
        speak(f"Playing {yt.title}.")
        # show_notification("YouTube", f"Playing: {yt.title}") # Removed PySide6 notification
        
    except Exception as e:
        speak("Sorry, I could not find or play that song. Ensure you have an active internet connection.")
        print(f"YouTube playback error: {e}")
        # show_notification("Error", "Failed to play YouTube song.") # Removed PySide6 notification

def download_youtube_song(url):
    """Downloads a YouTube video as an MP3 file. Uses pytube."""
    try:
        speak("Downloading YouTube song.")
        # show_notification("YouTube Downloader", "Downloading audio...") # Removed PySide6 notification
        
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        out_file = audio_stream.download() # Downloads to current directory
        
        # Rename the file to .mp3
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        
        speak(f"Downloaded '{yt.title}' successfully.")
        # show_notification("Download Complete", f"Saved as: {new_file}") # Removed PySide6 notification
    except Exception as e:
        speak("An error occurred during the download. Check the URL and your internet connection.")
        print(f"YouTube download error: {e}")
        # show_notification("Error", "Failed to download YouTube song.") # Removed PySide6 notification

def download_instagram_profile(username):
    """Downloads a public Instagram profile picture. Uses instaloader."""
    try:
        speak(f"Downloading profile picture for {username}.")
        # show_notification("Instagram", f"Downloading {username}'s profile...") # Removed PySide6 notification
        
        L = instaloader.Instaloader()
        # Note: For private profiles or rate limits, you might need to log in.
        # L.load_session_from_file("your_username", "your_session_file") 
        L.download_profile(username, profile_pic_only=True)
        
        speak("Profile picture downloaded successfully.")
        # show_notification("Success", f"Profile picture for {username} saved.") # Removed PySide6 notification
    except Exception as e:
        speak("Failed to download the profile picture. Please check the username and your internet connection. Instagram might also have rate limits or require login.")
        print(f"Instagram download error: {e}")
        # show_notification("Error", "Failed to download profile.") # Removed PySide6 notification

def wikipedia_summary(query):
    """Fetches and reads a summary from Wikipedia. Uses wikipedia library."""
    try:
        speak(f"Searching Wikipedia for {query}.")
        result = wikipedia.summary(query, sentences=2) # Get 2 sentences summary
        speak("According to Wikipedia:")
        speak(result)
        # show_notification("Wikipedia", f"Summary for: {query}") # Removed PySide6 notification
    except wikipedia.exceptions.PageError:
        speak("Sorry, I could not find any information on that topic on Wikipedia.")
    except Exception as e:
        speak("An error occurred while fetching information from Wikipedia. Check your internet connection.")
        print(f"Wikipedia error: {e}")
        # show_notification("Error", "Failed to fetch data from Wikipedia.") # Removed PySide6 notification

def read_pdf(file_path):
    """Reads the text content of a PDF file. Uses pdfplumber."""
    try:
        if not os.path.exists(file_path):
            speak(f"The file {file_path} was not found.")
            # show_notification("PDF Error", "File not found.") # Removed PySide6 notification
            return

        speak("Reading PDF file. This may take a moment.")
        # show_notification("PDF Reader", f"Reading {os.path.basename(file_path)}") # Removed PySide6 notification
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        if text:
            # Read only the first 500 characters to avoid reading a whole book.
            speak(f"Reading the first part of the document: {text[:500]}...")
            # show_notification("PDF Reader", "Reading complete.") # Removed PySide6 notification
        else:
            speak("The PDF file appears to be empty or could not be read.")
            # show_notification("PDF Reader", "File is empty.") # Removed PySide6 notification
    except Exception as e:
        speak("An error occurred while trying to read the PDF. Ensure the file is a valid PDF.")
        print(f"PDF read error: {e}")
        # show_notification("Error", "Failed to read PDF file.") # Removed PySide6 notification

def locate_phone_number(phone_number):
    """Tries to locate the region and carrier of a phone number. Uses phonenumbers and OpenCage Geocoding API."""
    if not OPENCAGE_API_KEY or OPENCAGE_API_KEY == "your_opencage_api_key":
        speak("OpenCage API key is not configured. Please add a valid key from opencagedata.com.")
        # show_notification("API Error", "OpenCage API key missing.") # Removed PySide6 notification
        return
        
    try:
        speak(f"Locating phone number: {phone_number}.")
        # show_notification("Phone Locator", f"Searching for {phone_number}") # Removed PySide6 notification
        
        parsed_number = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(parsed_number):
            speak("The phone number is invalid.")
            # show_notification("Phone Error", "Invalid number.") # Removed PySide6 notification
            return False
            
        carrier_name = carrier.name_for_number(parsed_number, "en")
        region = phone_geocoder.description_for_number(parsed_number, "en")
        
        location = "Unknown location"
        if region:
            try:
                response = requests.get(
                    f"https://api.opencagedata.com/geocode/v1/json?q={region}&key={OPENCAGE_API_KEY}"
                )
                response.raise_for_status() # Raise an exception for HTTP errors
                data = response.json()
                if data['results']:
                    location = data['results'][0]['formatted']
            except requests.exceptions.RequestException as e:
                print(f"OpenCage API error: {e}")
                location = region # Fallback to the region name if geocoding fails
        
        result = f"This number appears to be from {location}, carrier: {carrier_name}."
        speak(result)
        # show_notification("Phone Location", result) # Removed PySide6 notification
        return True
    except Exception as e:
        speak("Could not locate the phone number. Check the number format and your internet connection.")
        print(f"Phone location error: {e}")
        # show_notification("Location Error", "Service unavailable.") # Removed PySide6 notification
        return False
        
def clipboard_operation(action):
    """Performs clipboard actions like copy, paste, and cut. Uses pyautogui."""
    try:
        if action == "copy":
            pyautogui.hotkey("ctrl", "c")
            speak("Copied to clipboard.")
        elif action == "paste":
            pyautogui.hotkey("ctrl", "v")
            speak("Pasted from clipboard.")
        elif action == "cut":
            pyautogui.hotkey("ctrl", "x")
            speak("Cut to clipboard.")
        elif action == "select all":
            pyautogui.hotkey("ctrl", "a")
            speak("All text selected.")
        # show_notification("Clipboard", f"Action: {action.capitalize()}") # Removed PySide6 notification
    except Exception as e:
        speak(f"Failed to perform clipboard operation: {action}. Ensure the application has focus.")
        print(f"Clipboard error: {e}")
        # show_notification("Clipboard Error", f"Failed to {action}.") # Removed PySide6 notification

# Placeholder functions for features not fully implemented or requiring external setup
# These functions are included to prevent errors if called, but their full implementation
# would require more complex, platform-specific code or external integrations.
def whatsapp_call_kk():
    speak("I am sorry, this feature is not yet implemented.")
    # show_notification("Coming Soon", "WhatsApp call feature is not yet available.") # Removed PySide6 notification
    
def remember_information(info):
    speak("I'm sorry, my memory function is still under development.")
    # show_notification("Coming Soon", "Memory function is not yet available.") # Removed PySide6 notification
    
def recall_information():
    speak("I have not been given anything to remember yet.")
    # show_notification("Coming Soon", "Memory function is not yet available.") # Removed PySide6 notification

def screen_recording(duration=30):
    # This function requires more robust implementation for cross-platform compatibility
    # and proper audio/video synchronization. It's complex to get right universally.
    speak("I'm sorry, the screen recording function is currently disabled due to technical issues.")
    # show_notification("Coming Soon", "Screen recording is not yet available.") # Removed PySide6 notification
    
def voice_recording(duration=30):
    # This function requires more robust implementation for proper audio recording.
    speak("I'm sorry, the voice recording function is currently disabled due to technical issues.")
    # show_notification("Coming Soon", "Voice recording is not yet available.") # Removed PySide6 notification
    
def access_webcam():
    # This function requires more robust implementation for cross-platform compatibility.
    speak("I'm sorry, the webcam access function is currently disabled due to technical issues.")
    # show_notification("Coming Soon", "Webcam access is not yet available.") # Removed PySide6 notification

def open_specific_file(file_query):
    # This would require a file dialog or a known file path.
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "File access is not yet available.") # Removed PySide6 notification

def clear_recycle_bin():
    # This would require platform-specific commands or libraries.
    # Example for Windows: import winshell; winshell.empty_recycle_bin()
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "Recycle bin clearing is not yet available.") # Removed PySide6 notification

def open_recycle_bin():
    # This would require platform-specific commands or libraries.
    # Example for Windows: subprocess.Popen('explorer.exe shell:RecycleBinFolder')
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "Recycle bin access is not yet available.") # Removed PySide6 notification

def open_settings(setting_type):
    # This would require platform-specific commands to open system settings.
    # Example for Windows: subprocess.Popen(['ms-settings:display']) for display settings
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "System settings are not yet available.") # Removed PySide6 notification

def toggle_wifi(state):
    # This would require platform-specific commands or network libraries.
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "Wi-Fi toggling is not yet available.") # Removed PySide6 notification

def toggle_bluetooth(state):
    # This would require platform-specific commands or Bluetooth libraries.
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "Bluetooth toggling is not yet available.") # Removed PySide6 notification

def set_volume(level):
    # This would require platform-specific commands or audio control libraries.
    speak("This feature is not yet implemented.")
    # show_notification("Coming Soon", "Volume setting is not yet available.") # Removed PySide6 notification

def tell_programming_joke():
    # This function is already implemented using pyjokes.
    joke = pyjokes.get_joke(category='neutral') # Using neutral category for general jokes
    speak(joke)
    # show_notification("Joke", joke) # Removed PySide6 notification

# ========== VOICE TRAINING IMPLEMENTATION ==========
class VoiceRecorder:
    """Records audio snippets and saves them for training."""
    def __init__(self, audio_save_path):
        self.audio_save_path = audio_save_path
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stream = None

    def start_recording_raw(self):
        if self.is_recording:
            return
        self.frames = []
        try:
            self.stream = self.audio.open(format=FORMAT,
                                          channels=CHANNELS,
                                          rate=SAMPLE_RATE,
                                          input=True,
                                          frames_per_buffer=CHUNK,
                                          input_device_index=DEFAULT_MIC_INDEX)
            self.is_recording = True
            print("Raw recording started...")
        except Exception as e:
            print(f"Error starting raw recording: {e}")
            self.is_recording = False

    def stop_recording_raw(self):
        if not self.is_recording:
            return
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        print("Raw recording stopped.")

    def save_training_data(self, audio_data_frames, text):
        """Saves audio frames and their transcription."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.audio_save_path, f"audio_{timestamp}.wav")
        text_filename = os.path.join(self.audio_save_path, f"audio_{timestamp}.txt")

        # Save WAV file
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data_frames)
            wf.close()

            # Save transcription
            with open(text_filename, 'w') as f:
                f.write(text)
            print(f"Saved training data: {filename}, {text_filename}")
        except Exception as e:
            print(f"Error saving training data: {e}")

    def __del__(self):
        # Ensure PyAudio is terminated when the object is destroyed
        if self.audio:
            self.audio.terminate()

def extract_features(audio_path):
    """Extracts MFCC features from an audio file."""
    try:
        rate, signal = wavfile.read(audio_path)
        # Ensure signal is float for MFCC calculation if it's int
        if signal.dtype == np.int16:
            signal = signal.astype(np.float64) / 32768.0 # Normalize to -1.0 to 1.0
        
        mfcc_features = mfcc.mfcc(signal, rate, numcep=13) # 13 MFCC coefficients
        return mfcc_features.flatten() # Flatten for SVM input
    except Exception as e:
        print(f"Error extracting features from {audio_path}: {e}")
        return None

def train_voice_model():
    """Trains a voice recognition model using collected audio data."""
    global voice_model, scaler
    
    audio_files = [f for f in os.listdir(AUDIO_SAVE_PATH) if f.endswith('.wav')]
    if not audio_files:
        speak("No training data found. Please speak some commands first to collect data.")
        # show_notification("Voice Training", "No data to train.") # Removed PySide6 notification
        return

    X = []
    y = [] # In a simple command recognition, y would be the command itself or a label

    # For this basic training, we'll just try to learn a general voice pattern.
    # A more advanced system would need labeled data (e.g., "open browser" audio labeled "open browser").
    # For now, we'll just use a dummy label or assume all collected data is "user's voice".
    
    for audio_file in audio_files:
        audio_path = os.path.join(AUDIO_SAVE_PATH, audio_file)
        features = extract_features(audio_path)
        if features is not None:
            X.append(features)
            y.append(1) # Dummy label indicating "user's voice"

    if not X:
        speak("Could not extract features from any audio files. Training failed.")
        # show_notification("Voice Training", "Feature extraction failed.") # Removed PySide6 notification
        return

    X = np.array(X)
    y = np.array(y)

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train a simple SVM classifier
    # In a real scenario, you'd have multiple classes (commands) and more data.
    # Here, we're just training a binary classifier (is it the user's voice, or not).
    voice_model = SVC(kernel='linear', probability=True)
    voice_model.fit(X_scaled, y)

    # Save the trained model and scaler
    try:
        with open(MODEL_SAVE_PATH, 'wb') as f:
            pickle.dump({'model': voice_model, 'scaler': scaler}, f)
        speak("Voice model trained and saved successfully.")
        # show_notification("Voice Training", "Model saved.") # Removed PySide6 notification
    except Exception as e:
        speak("Failed to save the voice model.")
        print(f"Error saving model: {e}")
        # show_notification("Voice Training", "Save failed.") # Removed PySide6 notification

def load_voice_model():
    """Loads a pre-trained voice recognition model."""
    global voice_model, scaler
    if os.path.exists(MODEL_SAVE_PATH):
        try:
            with open(MODEL_SAVE_PATH, 'rb') as f:
                data = pickle.load(f)
                voice_model = data['model']
                scaler = data['scaler']
            print("Voice model loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading voice model: {e}")
            voice_model = None
            scaler = None
            return False
    return False

# ========== MAIN LOOP ==========
def jarvis_main_loop():
    """The main logic loop for J.A.R.V.I.S. commands."""
    global app_gui
    # Give the GUI thread a moment to initialize before proceeding.
    time.sleep(1)

    # Initialize the voice recorder
    recorder = VoiceRecorder(AUDIO_SAVE_PATH)

    # Load existing voice model if available
    load_voice_model()

    print("J.A.R.V.I.S is starting...")
    wish() # Greet the user

    while True:
        query = take_command(recorder=recorder) 
        if query:
            print(f"User said: {query}")
            
            commands = split_commands(query)
            if not commands:
                commands = [query]
                
            status = execute_multi_commands(commands)
            if status == "exit":
                break

if __name__ == "__main__":
    root = tk.Tk()
    app_gui = JarvisGUI(root) # Create the GUI instance
    
    # Start the J.A.R.V.I.S. command processing in a separate thread
    jarvis_thread = threading.Thread(target=jarvis_main_loop, daemon=True)
    jarvis_thread.start()

    # Start the Tkinter main loop (this must be in the main thread)
    root.mainloop() 
