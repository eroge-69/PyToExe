import sys
import os
import webbrowser
import subprocess
import json
import time
import threading
import requests
from datetime import datetime
import re
from dotenv import load_dotenv

# GUI imports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QTextEdit, 
                            QScrollArea, QLabel, QComboBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

# Speech recognition and synthesis
import speech_recognition as sr
import pyttsx3

# API for LLM interaction
import openai

class SpeechRecognitionThread(QThread):
    """Thread for handling speech recognition to avoid UI freezing"""
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    listening_signal = pyqtSignal(bool)
    
    def __init__(self, language='en'):
        super().__init__()
        self.language = language
        self.recognizer = sr.Recognizer()
        self.stop_listening = False
        
    def run(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.listening_signal.emit(True)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                self.listening_signal.emit(False)
                
                # Map language codes to speech recognition language codes
                lang_map = {'en': 'en-US', 'ro': 'ro-RO'}
                
                text = self.recognizer.recognize_google(audio, language=lang_map.get(self.language, 'en-US'))
                self.result_signal.emit(text)
        except sr.WaitTimeoutError:
            self.error_signal.emit("Speech recognition timeout")
        except sr.UnknownValueError:
            self.error_signal.emit("Speech not recognized")
        except sr.RequestError:
            self.error_signal.emit("Could not request results from Google Speech Recognition service")
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.listening_signal.emit(False)

class AIResponseThread(QThread):
    """Thread for handling AI API calls to avoid UI freezing"""
    response_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, query, language='en', conversation_history=None):
        super().__init__()
        self.query = query
        self.language = language
        self.conversation_history = conversation_history if conversation_history else []
        
    def run(self):
        try:
            # Try to connect to the internet
            requests.get("https://www.google.com", timeout=5)
            
            # Prepare conversation history for context
            messages = [
                {"role": "system", "content": f"You are a helpful AI desktop assistant. Respond in {self.language}. You can help with information and suggest PC commands."}
            ]
            
            # Add conversation history for context
            for entry in self.conversation_history[-5:]:  # Only use the last 5 interactions for context
                messages.append({"role": entry["role"], "content": entry["content"]})
                
            # Add the current query
            messages.append({"role": "user", "content": self.query})
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            self.response_signal.emit(response.choices[0].message.content)
        except requests.exceptions.RequestException:
            # Handle local command if offline
            result = self.process_local_command(self.query)
            self.response_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def process_local_command(self, query):
        """Process commands that can be executed locally without internet"""
        query_lower = query.lower()
        
        # Open application commands
        app_match = re.search(r"open (.*?)(?:$|\s)", query_lower)
        if app_match:
            app_name = app_match.group(1).strip()
            common_apps = {
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "explorer": "explorer.exe",
                "settings": "ms-settings:",
                "control panel": "control",
                "task manager": "taskmgr.exe"
            }
            
            if app_name in common_apps:
                try:
                    subprocess.Popen(common_apps[app_name])
                    return f"Opening {app_name.capitalize()}" 
                except Exception as e:
                    return f"Error opening {app_name}: {str(e)}"
        
        # If no local command matched
        return "I'm currently in offline mode. I can only perform local PC operations."

class AIAssistant(QMainWindow):
    """Main application window for AI Desktop Assistant"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_tts_engine()
        self.conversation_history = []
        
        # Add welcome message
        self.add_message("Hello! I'm your AI desktop assistant. How can I help you today?", False)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AI Desktop Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create chat display area
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        
        # Create input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command or question...")
        self.input_field.returnPressed.connect(self.process_input)
        
        self.mic_button = QPushButton("🎤")
        self.mic_button.clicked.connect(self.start_listening)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.mic_button)
        input_layout.addWidget(self.send_button)
        
        # Add layouts to main layout
        main_layout.addWidget(self.chat_area, 1)
        main_layout.addLayout(input_layout)
        
        self.show()
        
    def init_tts_engine(self):
        """Initialize text-to-speech engine"""
        self.engine = pyttsx3.init()
        
    def process_input(self):
        """Process user input from text field"""
        user_input = self.input_field.text().strip()
        if not user_input:
            return
            
        # Add user message to chat
        self.add_message(user_input, True)
        self.input_field.clear()
        
        # Process user input
        self.ai_response(user_input)
        
    def ai_response(self, query):
        """Get AI response to user query"""
        self.response_thread = AIResponseThread(query)
        self.response_thread.response_signal.connect(self.handle_ai_response)
        self.response_thread.error_signal.connect(self.handle_ai_error)
        self.response_thread.start()
        
    def handle_ai_response(self, response):
        """Handle AI response"""
        self.add_message(response, False)
        
        # Speak response
        self.speak_text(response)
        
    def handle_ai_error(self, error):
        """Handle AI response errors"""
        self.add_message(f"Error: {error}", False)
        
    def start_listening(self):
        """Start speech recognition"""
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.result_signal.connect(self.handle_speech_result)
        self.speech_thread.error_signal.connect(self.handle_speech_error)
        self.speech_thread.start()
        
    def handle_speech_result(self, text):
        """Handle speech recognition result"""
        self.input_field.setText(text)
        self.process_input()
        
    def handle_speech_error(self, error):
        """Handle speech recognition errors"""
        self.add_message(f"Speech recognition error: {error}", False)
        
    def speak_text(self, text):
        """Convert text to speech"""
        threading.Thread(target=self._speak_thread, args=(text,)).start()
        
    def _speak_thread(self, text):
        """Thread for text-to-speech to avoid UI freezing"""
        self.engine.say(text)
        self.engine.runAndWait()
        
    def add_message(self, text, is_user):
        """Add message to chat area"""
        # Implementation depends on specific UI design
        pass

def main():
    app = QApplication(sys.argv)
    assistant = AIAssistant()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()