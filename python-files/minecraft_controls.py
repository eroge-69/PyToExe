import os
import subprocess
import webbrowser
import speech_recognition as sr
import pyttsx3
import tkinter as tk
from threading import Thread
import pyautogui
import time
import json

class UltimateVoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Voice Assistant v2.0")
        self.root.geometry("700x500")
        
        # States
        self.voice_typing_active = False
        self.voice_commands_active = False
        self.current_language = "en-US"
        
        # Load comprehensive commands database
        self.load_comprehensive_commands()
        
        # Supported languages
        self.supported_languages = {
            "English": "en-US",
            "Hindi": "hi-IN",
            "Spanish": "es-ES",
            "French": "fr-FR"
        }
        
        # Initialize speech components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Create GUI
        self.create_widgets()
    
    def load_comprehensive_commands(self):
        """Load comprehensive commands database"""
        self.commands = {
            "apps": {
                # Windows System Apps
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "outlook": "outlook.exe",
                "photos": "ms-photos:",
                "mail": "outlook.exe",
                "calendar": "outlook.exe /c ipm.appointment",
                "store": "ms-windows-store:",
                "settings": "ms-settings:",
                "control panel": "control.exe",
                "task manager": "taskmgr.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "registry": "regedit.exe",
                "defender": "windowsdefender:",
                
                # Browsers
                "chrome": "chrome.exe",
                "edge": "msedge.exe",
                "firefox": "firefox.exe",
                
                # Media
                "media player": "wmplayer.exe",
                "camera": "microsoft.windows.camera:",
                
                # Utilities
                "file explorer": "explorer.exe",
                "disk cleanup": "cleanmgr.exe",
                "character map": "charmap.exe",
                "snipping tool": "snippingtool.exe",
                "sticky notes": "stikynot.exe",
                "magnifier": "magnify.exe",
                "remote desktop": "mstsc.exe",
                
                # Development
                "visual studio": "devenv.exe",
                "vs code": "code.exe",
                "python": "python.exe",
                
                # Third-party (common paths - may need adjustment)
                "whatsapp": os.path.expanduser("~\\AppData\\Local\\WhatsApp\\WhatsApp.exe"),
                "zoom": "zoom.exe",
                "teams": "teams.exe",
                "spotify": "spotify.exe",
                "vlc": "vlc.exe"
            },
            "websites": {
                # Education
                "physics wallah": "https://www.pw.live",
                "khan academy": "https://www.khanacademy.org",
                "coursera": "https://www.coursera.org",
                "udemy": "https://www.udemy.com",
                "byjus": "https://byjus.com",
                
                # Search Engines
                "google": "https://google.com",
                "bing": "https://bing.com",
                "duckduckgo": "https://duckduckgo.com",
                
                # Social Media
                "youtube": "https://youtube.com",
                "facebook": "https://facebook.com",
                "instagram": "https://instagram.com",
                "twitter": "https://twitter.com",
                "linkedin": "https://linkedin.com",
                
                # Productivity
                "gmail": "https://mail.google.com",
                "drive": "https://drive.google.com",
                "docs": "https://docs.google.com",
                "sheets": "https://sheets.google.com",
                "slides": "https://slides.google.com",
                
                # News
                "bbc": "https://bbc.com",
                "cnn": "https://cnn.com",
                
                # Shopping
                "amazon": "https://amazon.com",
                "flipkart": "https://flipkart.com",
                
                # Entertainment
                "netflix": "https://netflix.com",
                "prime video": "https://primevideo.com",
                "hotstar": "https://hotstar.com"
            },
            "search_prefixes": ["search", "find", "look up", "google", "what is", "who is"],
            "system_commands": {
                "shutdown": "shutdown /s /t 0",
                "restart": "shutdown /r /t 0",
                "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                "lock": "rundll32.exe user32.dll,LockWorkStation"
            }
        }
    
    def create_widgets(self):
        """Create the GUI interface"""
        # Configure main window
        self.root.configure(bg="#f0f0f0")
        
        # Header
        header = tk.Frame(self.root, bg="#4b8bbe", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="ULTIMATE VOICE ASSISTANT", font=('Arial', 16, 'bold'), 
                bg="#4b8bbe", fg="white").pack(pady=15)
        
        # Main content frame
        content = tk.Frame(self.root, bg="#f0f0f0")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(content, bg="#f0f0f0")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Language selection
        tk.Label(left_panel, text="Select Language:", bg="#f0f0f0", font=('Arial', 10)).pack(anchor=tk.W)
        self.lang_var = tk.StringVar(value="English")
        lang_menu = tk.OptionMenu(left_panel, self.lang_var, *self.supported_languages.keys())
        lang_menu.config(width=15)
        lang_menu.pack(pady=5, fill=tk.X)
        
        # Voice Typing Button
        self.typing_btn = tk.Button(
            left_panel,
            text="🎤 Start Voice Typing",
            command=self.toggle_voice_typing,
            bg="#5cb85c",
            fg="white",
            font=('Arial', 10, 'bold'),
            width=20,
            height=2,
            relief=tk.FLAT
        )
        self.typing_btn.pack(pady=10, fill=tk.X)
        
        # Voice Commands Button
        self.commands_btn = tk.Button(
            left_panel,
            text="🗣️ Start Voice Commands",
            command=self.toggle_voice_commands,
            bg="#5bc0de",
            fg="white",
            font=('Arial', 10, 'bold'),
            width=20,
            height=2,
            relief=tk.FLAT
        )
        self.commands_btn.pack(pady=10, fill=tk.X)
        
        # Status frame
        status_frame = tk.Frame(left_panel, bg="#f0f0f0")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.typing_status = tk.Label(status_frame, text="Voice Typing: OFF", fg="red", bg="#f0f0f0")
        self.typing_status.pack(anchor=tk.W)
        
        self.commands_status = tk.Label(status_frame, text="Voice Commands: OFF", fg="red", bg="#f0f0f0")
        self.commands_status.pack(anchor=tk.W)
        
        # Right panel - Command display
        right_panel = tk.Frame(content, bg="white", relief=tk.SUNKEN, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Command list display with scrollbar
        scrollbar = tk.Scrollbar(right_panel)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.command_display = tk.Text(
            right_panel,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            font=('Consolas', 9),
            padx=10,
            pady=10
        )
        self.command_display.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.command_display.yview)
        
        # Configure tags for styling
        self.command_display.tag_config('header', font=('Consolas', 10, 'bold'), foreground="#4b8bbe")
        self.command_display.tag_config('app', foreground="#5cb85c")
        self.command_display.tag_config('web', foreground="#5bc0de")
        self.command_display.tag_config('sys', foreground="#d9534f")
        self.command_display.tag_config('search', foreground="#f0ad4e")
        
        self.update_command_display()
    
    def update_command_display(self):
        """Update the command list display with styling"""
        self.command_display.delete(1.0, tk.END)
        
        # Display apps
        self.command_display.insert(tk.END, "APPLICATIONS (say 'open [app]')\n", 'header')
        for app in sorted(self.commands['apps'].keys()):
            self.command_display.insert(tk.END, f"  • {app}\n", 'app')
        
        # Display websites
        self.command_display.insert(tk.END, "\nWEBSITES (say 'open [site]')\n", 'header')
        for site in sorted(self.commands['websites'].keys()):
            self.command_display.insert(tk.END, f"  • {site}\n", 'web')
        
        # Display system commands
        self.command_display.insert(tk.END, "\nSYSTEM COMMANDS\n", 'header')
        for cmd in sorted(self.commands['system_commands'].keys()):
            self.command_display.insert(tk.END, f"  • {cmd} \n", 'sys')
        
        # Display search prefixes
        self.command_display.insert(tk.END, "\nSEARCH COMMANDS\n", 'header')
        for prefix in sorted(self.commands['search_prefixes']):
            self.command_display.insert(tk.END, f"  • {prefix} [query]\n", 'search')
        
        self.command_display.insert(tk.END, "\n\nTIP: Say 'stop typing' or 'stop commands' to deactivate modes", 'header')
    
    def toggle_voice_typing(self):
        """Toggle voice typing mode"""
        self.voice_typing_active = not self.voice_typing_active
        self.current_language = self.supported_languages[self.lang_var.get()]
        
        if self.voice_typing_active:
            self.typing_btn.config(text="🛑 Stop Voice Typing", bg="#d9534f")
            self.typing_status.config(text="Voice Typing: ON (Say 'stop typing' to stop)", fg="green")
            Thread(target=self.voice_typing_loop, daemon=True).start()
        else:
            self.typing_btn.config(text="🎤 Start Voice Typing", bg="#5cb85c")
            self.typing_status.config(text="Voice Typing: OFF", fg="red")
    
    def toggle_voice_commands(self):
        """Toggle voice commands mode"""
        self.voice_commands_active = not self.voice_commands_active
        self.current_language = self.supported_languages[self.lang_var.get()]
        
        if self.voice_commands_active:
            self.commands_btn.config(text="🛑 Stop Voice Commands", bg="#d9534f")
            self.commands_status.config(text="Voice Commands: ON (Say 'stop commands' to stop)", fg="green")
            Thread(target=self.voice_commands_loop, daemon=True).start()
        else:
            self.commands_btn.config(text="🗣️ Start Voice Commands", bg="#5bc0de")
            self.commands_status.config(text="Voice Commands: OFF", fg="red")
    
    def voice_typing_loop(self):
        """Handle voice typing"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self.voice_typing_active:
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio, language=self.current_language).lower()
                    
                    if "stop typing" in text:
                        self.root.after(0, self.toggle_voice_typing)
                        break
                    
                    # Type the recognized text
                    pyautogui.write(text + " ", interval=0.05)
                    
                except (sr.UnknownValueError, sr.WaitTimeoutError):
                    continue
                except Exception as e:
                    print(f"Voice typing error: {e}")
                    continue
    
    def voice_commands_loop(self):
        """Handle voice commands"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self.voice_commands_active:
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio, language=self.current_language).lower()
                    
                    if "stop commands" in command:
                        self.root.after(0, self.toggle_voice_commands)
                        break
                    
                    self.process_command(command)
                    
                except (sr.UnknownValueError, sr.WaitTimeoutError):
                    continue
                except Exception as e:
                    print(f"Voice command error: {e}")
                    continue
    
    def process_command(self, command):
        """Process voice commands"""
        print(f"Processing command: {command}")
        
        # Open applications
        if command.startswith("open "):
            target = command[5:].strip()
            if target in self.commands['apps']:
                try:
                    os.startfile(self.commands['apps'][target])
                    self.speak(f"Opening {target}")
                except Exception as e:
                    self.speak(f"Failed to open {target}. Error: {str(e)}")
            elif target in self.commands['websites']:
                webbrowser.open(self.commands['websites'][target])
                self.speak(f"Opening {target}")
            else:
                self.speak(f"I don't know how to open {target}")
        
        # System commands
        elif " computer" in command:
            cmd = command.replace(" computer", "")
            if cmd in self.commands['system_commands']:
                os.system(self.commands['system_commands'][cmd])
                self.speak(f"Executing {cmd} command")
        
        # Search commands
        else:
            for prefix in self.commands['search_prefixes']:
                if command.startswith(prefix + " "):
                    query = command[len(prefix)+1:].strip()
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                    self.speak(f"ok mohit opening {query}")
                    return
        
        # If no command matched
        self.speak("done mohit")
    
    def speak(self, text):
        """Convert text to speech"""
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateVoiceAssistant(root)
    root.mainloop()