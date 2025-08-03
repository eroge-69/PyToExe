import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json
import os
import requests
import speech_recognition as sr
import pygame
import io
import tempfile
import time
import datetime
import webbrowser
import subprocess
import psutil
import socket
import platform
from typing import Dict, Any, Optional
import configparser
import sys

class JarvisConfig:
    def __init__(self):
        self.config_file = "jarvis_config.ini"
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        self.config['API'] = {
            'openai_key': '',
            'elevenlabs_key': '',
            'jarvis_voice_id': 'pNInz6obpgDQGcFmaJgB'  # Default voice ID
        }
        self.config['SETTINGS'] = {
            'wake_word': 'jarvis',
            'response_speed': '1.0',
            'always_listening': 'true'
        }
        self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

class VoiceEngine:
    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        pygame.mixer.init()
    
    def text_to_speech(self, text: str) -> bool:
        try:
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name
                
                pygame.mixer.music.load(tmp_file_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                os.unlink(tmp_file_path)
                return True
            else:
                print(f"TTS Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"TTS Exception: {e}")
            return False

class GPTBrain:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.conversation_history = []
        self.system_prompt = """You are JARVIS, Tony Stark's AI assistant. You are highly intelligent, efficient, and professional. 
        You have access to system information and can help with various tasks. Keep responses concise but informative.
        You do not express emotions but maintain a helpful and sophisticated tone. Address the user as 'Sir' when appropriate."""
    
    def get_response(self, user_input: str, system_info: Dict[str, Any] = None) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if system_info:
                system_context = f"Current system information: {json.dumps(system_info, indent=2)}"
                messages.append({"role": "system", "content": system_context})
            
            messages.extend(self.conversation_history[-10:])  # Keep last 10 messages
            messages.append({"role": "user", "content": user_input})
            
            data = {
                "model": "gpt-4",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
            else:
                return f"I apologize, Sir. I'm experiencing connectivity issues. Status: {response.status_code}"
        
        except Exception as e:
            return f"I'm sorry, Sir. I encountered an error: {str(e)}"

class SystemMonitor:
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": f"{memory.available / (1024**3):.2f} GB",
                "disk_usage": disk.percent,
                "disk_free": f"{disk.free / (1024**3):.2f} GB",
                "platform": platform.system(),
                "platform_version": platform.version(),
                "processor": platform.processor(),
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

class JarvisUI:
    def __init__(self):
        self.root = tk.Tk()
        self.config = JarvisConfig()
        self.setup_ui()
        self.voice_engine = None
        self.gpt_brain = None
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.setup_apis()
        
    def setup_ui(self):
        self.root.title("J.A.R.V.I.S - Just A Rather Very Intelligent System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        # Stark Industries style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Stark.TFrame', background='#0a0a0a')
        style.configure('Stark.TLabel', background='#0a0a0a', foreground='#00d4ff', 
                       font=('Arial', 12))
        style.configure('Stark.TButton', background='#1a1a1a', foreground='#00d4ff',
                       font=('Arial', 10, 'bold'))
        
        # Main frame
        main_frame = ttk.Frame(self.root, style='Stark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="J.A.R.V.I.S", 
                               font=('Arial', 24, 'bold'), style='Stark.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Just A Rather Very Intelligent System",
                                  font=('Arial', 12), style='Stark.TLabel')
        subtitle_label.pack()
        
        # Status indicator
        self.status_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Status: Offline",
                                     font=('Arial', 12, 'bold'), style='Stark.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        # System info frame
        info_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.system_info_text = tk.Text(info_frame, height=8, bg='#1a1a1a', fg='#00d4ff',
                                       font=('Consolas', 10), insertbackground='#00d4ff')
        self.system_info_text.pack(fill=tk.X)
        
        # Chat area
        chat_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.chat_display = tk.Text(chat_frame, bg='#1a1a1a', fg='#00d4ff',
                                   font=('Arial', 11), insertbackground='#00d4ff')
        scrollbar = tk.Scrollbar(chat_frame, command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=scrollbar.set)
        
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Subtitle area
        self.subtitle_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        self.subtitle_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.subtitle_label = ttk.Label(self.subtitle_frame, text="",
                                       font=('Arial', 14, 'bold'), style='Stark.TLabel',
                                       wraplength=1000)
        self.subtitle_label.pack()
        
        # Control buttons
        control_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        control_frame.pack(fill=tk.X)
        
        self.listen_button = ttk.Button(control_frame, text="Start Listening",
                                       command=self.toggle_listening, style='Stark.TButton')
        self.listen_button.pack(side=tk.LEFT, padx=(0, 10))
        
        system_info_button = ttk.Button(control_frame, text="System Info",
                                       command=self.update_system_info, style='Stark.TButton')
        system_info_button.pack(side=tk.LEFT, padx=(0, 10))
        
        settings_button = ttk.Button(control_frame, text="Settings",
                                    command=self.open_settings, style='Stark.TButton')
        settings_button.pack(side=tk.LEFT)
        
        # Initial system info
        self.update_system_info()
        
    def setup_apis(self):
        openai_key = self.config.get('API', 'openai_key')
        elevenlabs_key = self.config.get('API', 'elevenlabs_key')
        
        if not openai_key or not elevenlabs_key:
            self.request_api_keys()
        else:
            self.initialize_engines()
    
    def request_api_keys(self):
        dialog = APIKeyDialog(self.root, self.config)
        self.root.wait_window(dialog.dialog)
        self.initialize_engines()
    
    def initialize_engines(self):
        try:
            openai_key = self.config.get('API', 'openai_key')
            elevenlabs_key = self.config.get('API', 'elevenlabs_key')
            voice_id = self.config.get('API', 'jarvis_voice_id')
            
            if openai_key and elevenlabs_key:
                self.gpt_brain = GPTBrain(openai_key)
                self.voice_engine = VoiceEngine(elevenlabs_key, voice_id)
                self.status_label.config(text="Status: Online")
                self.add_to_chat("JARVIS", "System initialized successfully, Sir.")
                self.speak("System initialized successfully, Sir.")
            else:
                self.status_label.config(text="Status: API Keys Required")
        except Exception as e:
            self.add_to_chat("SYSTEM", f"Initialization error: {e}")
    
    def add_to_chat(self, speaker: str, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {speaker}: {message}\n")
        self.chat_display.see(tk.END)
    
    def speak(self, text: str):
        self.subtitle_label.config(text=text)
        if self.voice_engine:
            threading.Thread(target=self.voice_engine.text_to_speech, args=(text,), daemon=True).start()
    
    def toggle_listening(self):
        if self.listening:
            self.listening = False
            self.listen_button.config(text="Start Listening")
            self.status_label.config(text="Status: Online")
        else:
            self.listening = True
            self.listen_button.config(text="Stop Listening")
            self.status_label.config(text="Status: Listening...")
            threading.Thread(target=self.listen_for_commands, daemon=True).start()
    
    def listen_for_commands(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        while self.listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio)
                self.add_to_chat("USER", text)
                
                # Process command
                threading.Thread(target=self.process_command, args=(text,), daemon=True).start()
                
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"Listening error: {e}")
    
    def process_command(self, command: str):
        if not self.gpt_brain:
            return
        
        # Get system info for context
        system_info = SystemMonitor.get_system_info()
        
        # Check for specific commands first
        response = self.handle_specific_commands(command)
        
        if not response:
            # Use GPT for general responses
            response = self.gpt_brain.get_response(command, system_info)
        
        self.add_to_chat("JARVIS", response)
        self.speak(response)
    
    def handle_specific_commands(self, command: str) -> Optional[str]:
        command_lower = command.lower()
        
        if "time" in command_lower:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}, Sir."
        
        elif "date" in command_lower:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}, Sir."
        
        elif "system" in command_lower and "info" in command_lower:
            self.update_system_info()
            return "System information updated, Sir."
        
        elif "open" in command_lower:
            if "browser" in command_lower or "chrome" in command_lower:
                webbrowser.open("https://www.google.com")
                return "Opening browser, Sir."
            elif "calculator" in command_lower:
                subprocess.Popen("calc.exe")
                return "Opening calculator, Sir."
            elif "notepad" in command_lower:
                subprocess.Popen("notepad.exe")
                return "Opening notepad, Sir."
        
        elif "weather" in command_lower:
            return "I would need access to weather services to provide current weather information, Sir."
        
        elif "shutdown" in command_lower:
            return "I cannot perform system shutdown for security reasons, Sir."
        
        return None
    
    def update_system_info(self):
        system_info = SystemMonitor.get_system_info()
        info_text = f"""SYSTEM STATUS REPORT
========================
CPU Usage: {system_info.get('cpu_usage', 'N/A')}%
Memory Usage: {system_info.get('memory_usage', 'N/A')}%
Memory Available: {system_info.get('memory_available', 'N/A')}
Disk Usage: {system_info.get('disk_usage', 'N/A')}%
Disk Free: {system_info.get('disk_free', 'N/A')}
Platform: {system_info.get('platform', 'N/A')} {system_info.get('platform_version', 'N/A')}
Processor: {system_info.get('processor', 'N/A')}
Last Updated: {system_info.get('timestamp', 'N/A')}
========================"""
        
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(1.0, info_text)
    
    def open_settings(self):
        settings_dialog = SettingsDialog(self.root, self.config)
        self.root.wait_window(settings_dialog.dialog)
        self.initialize_engines()  # Reinitialize with new settings
    
    def run(self):
        self.root.mainloop()

class APIKeyDialog:
    def __init__(self, parent, config):
        self.config = config
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("API Configuration")
        self.dialog.geometry("500x300")
        self.dialog.configure(bg='#0a0a0a')
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.transient(parent)
        
        main_frame = ttk.Frame(self.dialog, style='Stark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(main_frame, text="JARVIS API Configuration",
                               font=('Arial', 16, 'bold'), style='Stark.TLabel')
        title_label.pack(pady=(0, 20))
        
        # OpenAI API Key
        ttk.Label(main_frame, text="OpenAI API Key:", style='Stark.TLabel').pack(anchor=tk.W)
        self.openai_entry = tk.Entry(main_frame, width=60, show="*", bg='#1a1a1a', fg='#00d4ff')
        self.openai_entry.pack(fill=tk.X, pady=(5, 15))
        
        # ElevenLabs API Key
        ttk.Label(main_frame, text="ElevenLabs API Key:", style='Stark.TLabel').pack(anchor=tk.W)
        self.elevenlabs_entry = tk.Entry(main_frame, width=60, show="*", bg='#1a1a1a', fg='#00d4ff')
        self.elevenlabs_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Voice ID
        ttk.Label(main_frame, text="Jarvis Voice ID (optional):", style='Stark.TLabel').pack(anchor=tk.W)
        self.voice_entry = tk.Entry(main_frame, width=60, bg='#1a1a1a', fg='#00d4ff')
        self.voice_entry.pack(fill=tk.X, pady=(5, 20))
        self.voice_entry.insert(0, self.config.get('API', 'jarvis_voice_id', fallback='pNInz6obpgDQGcFmaJgB'))
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        button_frame.pack(fill=tk.X)
        
        save_button = ttk.Button(button_frame, text="Save", command=self.save_keys, style='Stark.TButton')
        save_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy, style='Stark.TButton')
        cancel_button.pack(side=tk.RIGHT)
    
    def save_keys(self):
        openai_key = self.openai_entry.get().strip()
        elevenlabs_key = self.elevenlabs_entry.get().strip()
        voice_id = self.voice_entry.get().strip()
        
        if not openai_key or not elevenlabs_key:
            messagebox.showerror("Error", "Both API keys are required!")
            return
        
        self.config.set('API', 'openai_key', openai_key)
        self.config.set('API', 'elevenlabs_key', elevenlabs_key)
        self.config.set('API', 'jarvis_voice_id', voice_id)
        
        messagebox.showinfo("Success", "API keys saved successfully!")
        self.dialog.destroy()

class SettingsDialog:
    def __init__(self, parent, config):
        self.config = config
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("JARVIS Settings")
        self.dialog.geometry("400x250")
        self.dialog.configure(bg='#0a0a0a')
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, style='Stark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(main_frame, text="JARVIS Settings",
                               font=('Arial', 16, 'bold'), style='Stark.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Wake word
        ttk.Label(main_frame, text="Wake Word:", style='Stark.TLabel').pack(anchor=tk.W)
        self.wake_word_entry = tk.Entry(main_frame, bg='#1a1a1a', fg='#00d4ff')
        self.wake_word_entry.pack(fill=tk.X, pady=(5, 15))
        self.wake_word_entry.insert(0, self.config.get('SETTINGS', 'wake_word', fallback='jarvis'))
        
        # API Keys button
        api_button = ttk.Button(main_frame, text="Configure API Keys", 
                               command=self.open_api_dialog, style='Stark.TButton')
        api_button.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Stark.TFrame')
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings, style='Stark.TButton')
        save_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy, style='Stark.TButton')
        cancel_button.pack(side=tk.RIGHT)
    
    def open_api_dialog(self):
        APIKeyDialog(self.dialog, self.config)
    
    def save_settings(self):
        wake_word = self.wake_word_entry.get().strip()
        self.config.set('SETTINGS', 'wake_word', wake_word)
        messagebox.showinfo("Success", "Settings saved successfully!")
        self.dialog.destroy()

def main():
    app = JarvisUI()
    app.run()

if __name__ == "__main__":
    main()