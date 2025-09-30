#!/usr/bin/env python3
"""
MATA A09 EXP - Multi Agentic Tasks Assistant
Developed by TeamZero - A small group of students in Bangladesh

This is a voice assistant that uses OpenRouter with x-ai/grok-4-fast:free,
speech recognition for voice input, Google Translate TTS for text-to-speech,
and DuckDuckGo for web searches.
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime, timedelta
import re

# Import required libraries
import speech_recognition as sr
from gtts import gTTS
import pygame
import openai
from duckduckgo_search import DDGS
import tempfile
import tkinter as tk
from tkinter import scrolledtext


class MATAA09EXP_GUI:
    def __init__(self, assistant):
        self.assistant = assistant
        self.root = tk.Tk()
        self.root.title("MATA A09 EXP - Multi Agentic Tasks Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a0000')  # Dark red background
        self.root.resizable(True, True)
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Animation variables
        self.animation_active = False
        self.animation_thread = None
        self.pulse_animation_active = False
        self.pulse_thread = None
        
        # Start status update thread
        self.status_thread = threading.Thread(target=self.update_status, daemon=True)
        self.status_thread.start()

    def setup_styles(self):
        """Setup GUI styles and fonts"""
        self.root.option_add('*Font', 'Arial 10')
        self.root.option_add('*Background', '#1a0000')
        self.root.option_add('*Foreground', '#ffcccc')

    def create_widgets(self):
        """Create all GUI widgets"""
        # Header frame with gradient effect
        header_frame = tk.Frame(self.root, bg='#330000', height=100, relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, padx=15, pady=15)
        header_frame.pack_propagate(False)
        
        # Title label with shadow effect
        title_shadow = tk.Label(
            header_frame, 
            text="MATA A09 EXP", 
            font=("Arial", 28, "bold"), 
            fg="#660000", 
            bg="#330000"
        )
        title_shadow.place(x=12, y=22)
        
        title_label = tk.Label(
            header_frame, 
            text="MATA A09 EXP", 
            font=("Arial", 28, "bold"), 
            fg="#ff9999", 
            bg="#330000"
        )
        title_label.place(x=10, y=20)
        
        # Status label with better styling
        self.status_label = tk.Label(
            header_frame, 
            text="Initializing...", 
            font=("Arial", 14, "italic"), 
            fg="#ff6666", 
            bg="#330000"
        )
        self.status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#1a0000')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Voice animation canvas with better design
        self.canvas = tk.Canvas(content_frame, bg='#1a0000', height=200, highlightthickness=0)
        self.canvas.pack(fill=tk.X, pady=10)
        
        # Create voice animation circles with gradient effect
        self.circles = []
        self.circle_centers = []
        for i in range(7):
            x = 100 + i * 70
            self.circle_centers.append(x)
            circle = self.canvas.create_oval(x-25, 85, x+25, 135, fill='#4d0000', outline='#ff3333', width=3)
            self.circles.append(circle)
        
        # Add decorative elements
        self.canvas.create_line(50, 110, 850, 110, fill='#4d0000', width=2, dash=(5, 3))
        
        # Activity log with improved styling
        log_frame = tk.Frame(content_frame, bg='#1a0000')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        log_header = tk.Frame(log_frame, bg='#1a0000')
        log_header.pack(fill=tk.X)
        
        log_label = tk.Label(
            log_header, 
            text="Activity Log:", 
            font=("Arial", 16, "bold"), 
            fg="#ff9999", 
            bg='#1a0000'
        )
        log_label.pack(side=tk.LEFT)
        
        # Scrolled text for logs with better styling
        log_container = tk.Frame(log_frame, bg='#330000', relief=tk.SUNKEN, bd=2)
        log_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            bg='#220000', 
            fg='#ffcccc', 
            font=("Consolas", 11),
            height=12,
            wrap=tk.WORD,
            insertbackground='#ff9999',
            selectbackground='#660000'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.log_text.config(state=tk.DISABLED)
        
        # Control buttons frame with better layout
        button_frame = tk.Frame(self.root, bg='#1a0000')
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Start/Stop button with hover effect simulation
        self.start_stop_button = tk.Button(
            button_frame,
            text="Stop Assistant",
            font=("Arial", 13, "bold"),
            bg='#cc0000',
            fg='white',
            activebackground='#ff3333',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=8,
            command=self.toggle_assistant
        )
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # Clear log button
        clear_button = tk.Button(
            button_frame,
            text="Clear Log",
            font=("Arial", 13),
            bg='#990000',
            fg='white',
            activebackground='#cc3333',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=8,
            command=self.clear_log
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Quit button
        quit_button = tk.Button(
            button_frame,
            text="Quit",
            font=("Arial", 13),
            bg='#660000',
            fg='white',
            activebackground='#993333',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=8,
            command=self.quit_app
        )
        quit_button.pack(side=tk.RIGHT, padx=5)
        
        # Add initial log message
        self.add_log_message("MATA A09 EXP GUI initialized")
        self.add_log_message("Voice assistant starting...")

    def add_log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def update_status(self):
        """Update the status display"""
        while True:
            try:
                if self.assistant.speaking:
                    self.status_label.config(text="🔊 Speaking...", fg="#ff3333")
                    self.start_voice_animation()
                    self.stop_pulse_animation()
                elif self.assistant.listening:
                    self.status_label.config(text="🎤 Listening...", fg="#ff9999")
                    self.stop_voice_animation()
                    self.start_pulse_animation()
                else:
                    self.status_label.config(text="💤 Idle", fg="#ff6666")
                    self.stop_voice_animation()
                    self.stop_pulse_animation()
                
                # Update button text
                if self.assistant.assistant_active:
                    self.start_stop_button.config(text="⏹ Stop Assistant")
                else:
                    self.start_stop_button.config(text="▶ Start Assistant")
                
                time.sleep(0.3)
            except Exception as e:
                print(f"Error updating status: {e}")
                break

    def start_voice_animation(self):
        """Start the voice animation"""
        if not self.animation_active:
            self.animation_active = True
            self.animation_thread = threading.Thread(target=self.animate_voice, daemon=True)
            self.animation_thread.start()

    def stop_voice_animation(self):
        """Stop the voice animation"""
        self.animation_active = False
        # Reset circles to default color and size
        for i, circle in enumerate(self.circles):
            x = self.circle_centers[i]
            self.canvas.coords(circle, x-25, 85, x+25, 135)
            self.canvas.itemconfig(circle, fill='#4d0000', outline='#ff3333')

    def animate_voice(self):
        """Animate the voice visualization with smoother transitions"""
        sizes = [0, 0, 1, 2, 3, 2, 1]
        colors = ['#4d0000', '#660000', '#800000', '#990000', '#b30000', '#800000', '#660000']
        
        while self.animation_active:
            for i in range(len(self.circles)):
                if not self.animation_active:
                    break
                    
                # Calculate index for wave effect
                idx = (i + len(sizes) // 2) % len(sizes)
                
                # Update circle size and color
                size = sizes[idx]
                color = colors[idx]
                
                # Calculate new coordinates
                x = self.circle_centers[i]
                y1 = 85 - size * 8
                y2 = 135 + size * 8
                
                self.canvas.coords(self.circles[i], x-25-size*2, y1, x+25+size*2, y2)
                self.canvas.itemconfig(self.circles[i], fill=color, outline='#ff6666')
                
                time.sleep(0.05)
            
            # Rotate sizes for next frame
            sizes = sizes[1:] + sizes[:1]
            colors = colors[1:] + colors[:1]

    def start_pulse_animation(self):
        """Start the pulse animation for listening state"""
        if not self.pulse_animation_active:
            self.pulse_animation_active = True
            self.pulse_thread = threading.Thread(target=self.animate_pulse, daemon=True)
            self.pulse_thread.start()

    def stop_pulse_animation(self):
        """Stop the pulse animation"""
        self.pulse_animation_active = False
        # Reset center circle to default
        center_circle = self.circles[len(self.circles) // 2]
        x = self.circle_centers[len(self.circles) // 2]
        self.canvas.coords(center_circle, x-25, 85, x+25, 135)
        self.canvas.itemconfig(center_circle, fill='#4d0000', outline='#ff3333')

    def animate_pulse(self):
        """Animate a pulsing effect for listening state"""
        center_idx = len(self.circles) // 2
        center_circle = self.circles[center_idx]
        x = self.circle_centers[center_idx]
        
        pulse_sizes = [0, 1, 2, 3, 2, 1, 0]
        pulse_colors = ['#4d0000', '#660000', '#800000', '#cc0000', '#800000', '#660000', '#4d0000']
        
        while self.pulse_animation_active:
            for i in range(len(pulse_sizes)):
                if not self.pulse_animation_active:
                    break
                    
                size = pulse_sizes[i]
                color = pulse_colors[i]
                
                # Calculate new coordinates
                y1 = 85 - size * 5
                y2 = 135 + size * 5
                x1 = x - 25 - size * 3
                x2 = x + 25 + size * 3
                
                self.canvas.coords(center_circle, x1, y1, x2, y2)
                self.canvas.itemconfig(center_circle, fill=color, outline='#ff6666')
                
                time.sleep(0.15)

    def toggle_assistant(self):
        """Toggle the assistant on/off"""
        if self.assistant.assistant_active:
            self.assistant.assistant_active = False
            self.assistant.speaking = False
            self.assistant.listening = False
            self.add_log_message("Assistant stopped by user")
        else:
            self.assistant.assistant_active = True
            self.assistant.listening = True
            self.add_log_message("Assistant started by user")

    def clear_log(self):
        """Clear the log text"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.add_log_message("Log cleared by user")

    def quit_app(self):
        """Quit the application"""
        self.assistant.assistant_active = False
        self.animation_active = False
        self.pulse_animation_active = False
        self.root.quit()
        self.root.destroy()
        os._exit(0)

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


class MATAA09EXP:
    def __init__(self):
        """Initialize the MATA A09 EXP voice assistant."""
        # Load configuration
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.name = self.config["assistant_name"]
        self.developer = self.config["developer"]
        self.assistant_active = True
        self.listening = False
        self.speaking = False
        self.interrupt_speaking = False
        self.reminders = []
        self.gui = None
        
        # Set up OpenRouter API
        self.openai_client = openai.OpenAI(
            base_url=self.config["base_url"],
            api_key=self.config["api_key"]
        )
        
        # Set up speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        # Initialize pygame mixer only once
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # System prompt for the AI
        self.system_prompt = f"""You are {self.name}, a Multi Agentic Tasks Assistant developed by TeamZero.
You are running on Windows. Your capabilities include:
1. Voice interaction using speech recognition and text-to-speech
2. Web searches using DuckDuckGo
3. File operations (reading/writing/searching)
4. Opening applications on Windows
5. Setting reminders
6. Predicting and recognizing user intentions

Important guidelines:
- Always refer to yourself as "{self.name}"
- Be friendly and helpful
- Be concise in your responses
- If asked to stop, respond appropriately and wait for further instructions
- If you don't understand a request, ask for clarification

Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        print(f"{self.name} initialized. Ready to assist!")
        self.speak(f"Hello, I am {self.name}, your Multi Agentic Tasks Assistant. How can I help you today?")

    def listen(self):
        """Listen for voice input and convert to text."""
        try:
            print("Listening...")
            if self.gui:
                self.gui.add_log_message("Listening for voice input...")
            with self.microphone as source:
                # Listen for 5 seconds, with a 0.5 second pause considered as end of phrase
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing speech...")
            if self.gui:
                self.gui.add_log_message("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            if self.gui:
                self.gui.add_log_message(f"Recognized: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            if self.gui:
                self.gui.add_log_message("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            if self.gui:
                self.gui.add_log_message(f"Speech recognition error: {e}")
            return None

    def speak(self, text):
        """Convert text to speech using Google Translate TTS and play it."""
        try:
            # Set speaking flag
            self.speaking = True
            self.interrupt_speaking = False
            
            print(f"Speaking: {text}")
            if self.gui:
                self.gui.add_log_message(f"Speaking: {text}")
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_filename = temp_file.name
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=self.config["tts_language"])
            tts.save(temp_filename)
            
            # Play the audio using pygame
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish or for interruption
            while pygame.mixer.music.get_busy() and not self.interrupt_speaking:
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
            
            # If interrupted, stop the audio
            if self.interrupt_speaking:
                pygame.mixer.music.stop()
                print("Speech interrupted by user")
                if self.gui:
                    self.gui.add_log_message("Speech interrupted by user")
            
            # Ensure the mixer is done with the file before trying to delete
            pygame.mixer.music.unload()
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            # Clear speaking flag
            self.speaking = False
            self.interrupt_speaking = False
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            if self.gui:
                self.gui.add_log_message(f"TTS error: {e}")
            self.speaking = False
            self.interrupt_speaking = False

    def web_search(self, query):
        """Perform a web search using DuckDuckGo."""
        try:
            print(f"Searching web for: {query}")
            if self.gui:
                self.gui.add_log_message(f"Searching web for: {query}")
            results = []
            with DDGS() as ddgs:
                # Using text search with safesearch off for better results
                for r in ddgs.text(query, max_results=3, safesearch='off'):
                    results.append(r)
            return results
        except Exception as e:
            print(f"Error in web search: {e}")
            if self.gui:
                self.gui.add_log_message(f"Web search error: {e}")
            return []

    def find_chrome_path(self):
        """Find Chrome executable path on Windows."""
        # Common Chrome installation paths on Windows
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\chrome.exe"),
            "chrome.exe"  # Try default PATH
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        return None

    def open_application(self, app_name):
        """Open an application on Windows."""
        try:
            print(f"Opening application: {app_name}")
            if self.gui:
                self.gui.add_log_message(f"Opening application: {app_name}")
            
            # Common application mappings
            app_mappings = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "explorer": "explorer.exe"
            }
            
            # Special handling for Chrome
            if app_name.lower() == "chrome":
                chrome_path = self.find_chrome_path()
                if chrome_path:
                    subprocess.Popen([chrome_path])
                    return "Opening Google Chrome"
                else:
                    # Fallback to system PATH
                    try:
                        subprocess.Popen(["chrome.exe"])
                        return "Opening Google Chrome"
                    except:
                        return "Could not find Google Chrome installation"
            
            # For other applications, try the mapped name first
            if app_name.lower() in app_mappings:
                app_exe = app_mappings[app_name.lower()]
                try:
                    subprocess.Popen(app_exe)
                    return f"Opening {app_name}"
                except:
                    # If that fails, try the raw name
                    try:
                        subprocess.Popen(app_name.lower())
                        return f"Opening {app_name}"
                    except Exception as e:
                        return f"Could not open {app_name}: {str(e)}"
            else:
                # Try to open the application directly
                try:
                    subprocess.Popen(app_name.lower())
                    return f"Opening {app_name}"
                except Exception as e:
                    return f"Could not open {app_name}: {str(e)}"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"

    def search_files(self, search_term):
        """Search for files containing the search term."""
        try:
            print(f"Searching files for: {search_term}")
            if self.gui:
                self.gui.add_log_message(f"Searching files for: {search_term}")
            results = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if search_term.lower() in file.lower():
                        results.append(os.path.join(root, file))
            return results
        except Exception as e:
            print(f"Error searching files: {e}")
            if self.gui:
                self.gui.add_log_message(f"File search error: {e}")
            return []

    def read_file(self, file_path):
        """Read content from a file."""
        try:
            print(f"Reading file: {file_path}")
            if self.gui:
                self.gui.add_log_message(f"Reading file: {file_path}")
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Could not read file {file_path}: {e}"

    def write_file(self, file_path, content):
        """Write content to a file."""
        try:
            print(f"Writing to file: {file_path}")
            if self.gui:
                self.gui.add_log_message(f"Writing to file: {file_path}")
            with open(file_path, 'w') as file:
                file.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Could not write to file {file_path}: {e}"

    def set_reminder(self, reminder_text, minutes):
        """Set a reminder."""
        print(f"Setting reminder: {reminder_text} in {minutes} minutes")
        if self.gui:
            self.gui.add_log_message(f"Setting reminder: {reminder_text} in {minutes} minutes")
        reminder_time = datetime.now() + timedelta(minutes=minutes)
        reminder = {
            "text": reminder_text,
            "time": reminder_time,
            "notified": False
        }
        self.reminders.append(reminder)
        return f"Reminder set for {minutes} minutes from now."

    def check_reminders(self):
        """Check if any reminders are due."""
        current_time = datetime.now()
        for reminder in self.reminders:
            if not reminder["notified"] and current_time >= reminder["time"]:
                self.speak(f"Reminder: {reminder['text']}")
                reminder["notified"] = True

    def process_command(self, command):
        """Process the user's command."""
        if not command:
            return
            
        print(f"Processing command: {command}")
        if self.gui:
            self.gui.add_log_message(f"Processing command: {command}")
            
        # Check for stop command
        if "stop" in command or "exit" in command or "quit" in command:
            self.interrupt_speaking = True
            time.sleep(0.2)  # Give time for interruption to take effect
            self.speak("Stopping MATA A09 EXP. Goodbye!")
            self.assistant_active = False
            return
            
        # Check for sleep/deactivate command
        if "sleep" in command or "wait" in command or "hold" in command:
            self.interrupt_speaking = True
            time.sleep(0.2)  # Give time for interruption to take effect
            self.speak("Going to sleep. Say 'wake up' to activate me again.")
            self.listening = False
            return
            
        # Check for wake up command
        if "wake up" in command and not self.listening:
            self.speak("I'm awake and ready to assist!")
            self.listening = True
            return
            
        # If not listening, don't process other commands
        if not self.listening and not self.assistant_active:
            return
            
        # Handle specific commands
        if "open" in command and ("app" in command or "application" in command):
            # Extract app name
            app_match = re.search(r"open (.+)", command)
            if app_match:
                app_name = app_match.group(1)
                response = self.open_application(app_name)
                self.speak(response)
                return
                
        if "search" in command and ("web" in command or "online" in command or "internet" in command):
            # Extract search query
            search_match = re.search(r"search (.+)", command)
            if search_match:
                query = search_match.group(1)
                results = self.web_search(query)
                if results:
                    # Summarize top result
                    top_result = results[0]
                    summary = f"Top result for {query}: {top_result['title']}. {top_result['body'][:100]}..."
                    self.speak(summary)
                else:
                    self.speak("No results found for your search.")
                return
                
        if "search" in command and ("file" in command or "files" in command):
            # Extract search term
            search_match = re.search(r"search (.+)", command)
            if search_match:
                search_term = search_match.group(1)
                results = self.search_files(search_term)
                if results:
                    response = f"Found {len(results)} files: " + ", ".join(results[:5])
                    self.speak(response)
                else:
                    self.speak("No files found matching your search.")
                return
                
        if "read" in command and ("file" in command):
            # Extract file path
            file_match = re.search(r"read (.+)", command)
            if file_match:
                file_path = file_match.group(1)
                content = self.read_file(file_path)
                self.speak(f"Content of {file_path}: {content[:100]}...")  # Read first 100 chars
                return
                
        if "write" in command and ("file" in command):
            # This would need more sophisticated handling in a real implementation
            self.speak("Writing to files requires more specific instructions. Please specify the file path and content.")
            return
            
        if "remind me" in command:
            # Extract reminder details
            time_match = re.search(r"remind me (.+) in (\d+) minutes", command)
            if time_match:
                reminder_text = time_match.group(1)
                minutes = int(time_match.group(2))
                response = self.set_reminder(reminder_text, minutes)
                self.speak(response)
                return
                
        # Default to AI processing for other commands
        self.process_with_ai(command)

    def process_with_ai(self, user_input):
        """Process user input using the AI model."""
        try:
            print(f"Processing with AI: {user_input}")
            if self.gui:
                self.gui.add_log_message(f"Processing with AI: {user_input}")
            response = self.openai_client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            print(f"AI Response: {ai_response}")
            if self.gui:
                self.gui.add_log_message(f"AI Response: {ai_response}")
            self.speak(ai_response)
        except Exception as e:
            print(f"Error in AI processing: {e}")
            if self.gui:
                self.gui.add_log_message(f"AI processing error: {e}")
            self.speak("Sorry, I encountered an error processing your request.")

    def run(self):
        """Main loop for the voice assistant."""
        # Start with active listening
        self.listening = True
        
        # Start reminder checking thread
        reminder_thread = threading.Thread(target=self.reminder_checker, daemon=True)
        reminder_thread.start()
        
        try:
            while self.assistant_active:
                # Check reminders periodically
                self.check_reminders()
                
                if self.listening:
                    command = self.listen()
                    if command:
                        # If we're currently speaking, interrupt it
                        if self.speaking:
                            self.interrupt_speaking = True
                            time.sleep(0.2)  # Give time for interruption to take effect
                        
                        self.process_command(command)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.interrupt_speaking = True
            time.sleep(0.2)  # Give time for interruption to take effect
            self.speak("Shutting down MATA A09 EXP. Goodbye!")
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.interrupt_speaking = True
            time.sleep(0.2)  # Give time for interruption to take effect
            self.speak("An unexpected error occurred. Shutting down.")

    def reminder_checker(self):
        """Thread function to continuously check reminders."""
        while self.assistant_active:
            self.check_reminders()
            time.sleep(60)  # Check every minute


def main():
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create and run the assistant
    assistant = MATAA09EXP()
    
    # Create GUI in a separate thread
    gui_thread = threading.Thread(target=lambda: run_gui(assistant), daemon=True)
    gui_thread.start()
    
    # Run the assistant
    assistant.run()

def run_gui(assistant):
    """Run the GUI in a separate thread"""
    try:
        assistant.gui = MATAA09EXP_GUI(assistant)
        assistant.gui.run()
    except Exception as e:
        print(f"Error running GUI: {e}")

if __name__ == "__main__":
    main()
