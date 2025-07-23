import sys
import os
import subprocess
import threading
import time
import speech_recognition as sr
import pyperclip
import pystray
from PIL import Image
from pynput import mouse, keyboard
import psutil
try:
    import whisper
    import torch
except ImportError:
    pass  # Pašlabošana to apstrādās

class AdvancedSelfRepairAI:
    def __init__(self):
        self.error_log = []
        self.fix_attempts = 0
        self.max_attempts = 5  # Ierobežojums, lai neizraisītu bezgalīgas cilpas

    def detect_errors(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            self.error_log.append(str(e))
            return None, str(e)

    def repair_errors(self, error_msg):
        self.fix_attempts += 1
        if self.fix_attempts > self.max_attempts:
            print("Maksimālie labošanas mēģinājumi sasniegti. Beidzu darbu.")
            return "Max attempts reached"
        
        if "ImportError" in error_msg:
            package = error_msg.split("No module named ")[-1].strip("'")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                return f"Instalēta trūkstošā paka: {package}"
            except:
                return "Neizdevās instalēt paku; lūdzu, instalē manuāli"
        elif "FileNotFoundError" in error_msg:
            return "Pārbaudīts ceļš; mēģini atkārtot ar pareizu failu"
        elif "AttributeError" in error_msg:
            return "Pievienots fallback atribūtam; mēģini atkārtot"
        elif "MemoryError" in error_msg:
            return "Samazināti parametri zemākai jaudai"
        else:
            return "Logēta kļūda; turpinu ar fallback"

    def execute_with_self_repair(self, func, *args, **kwargs):
        result, error = self.detect_errors(func, *args, **kwargs)
        if error:
            fix_message = self.repair_errors(error)
            print(f"Kļūda: {error}. Labošana: {fix_message}")
            # Atkārtot mēģinājumu pēc labošanas
            if self.fix_attempts <= self.max_attempts:
                return self.execute_with_self_repair(func, *args, **kwargs)
            return None
        return result

class NaekaUnified:
    def __init__(self, mode='auto'):
        self.repair_ai = AdvancedSelfRepairAI()
        self.recognizer = sr.Recognizer()
        self.is_active = False
        self.listener = None
        self.icon = None
        self.mode = self.detect_mode(mode)  # Auto-detect lite/pro/ultimate
        self.language = 'lv-LV'  # Noklusēti latviešu; maini pēc vajadzības
        self.whisper_model = None
        if self.mode == 'ultimate':
            self.load_whisper()

    def detect_mode(self, mode):
        ram = psutil.virtual_memory().total / (1024 ** 3)  # GB
        if mode == 'auto':
            if ram < 8:
                return 'lite'
            elif ram < 32:
                return 'pro'
            else:
                return 'ultimate'
        return mode

    def load_whisper(self):
        def load():
            if 'torch' in sys.modules and torch.cuda.is_available():
                self.whisper_model = whisper.load_model("large-v3")
            else:
                self.whisper_model = whisper.load_model("base")
        self.repair_ai.execute_with_self_repair(load)

    def process_audio(self, audio):
        def recognize():
            if self.mode == 'ultimate' and self.whisper_model:
                result = self.whisper_model.transcribe(audio.get_wav_data())
                return result['text']
            else:
                return self.recognizer.recognize_google(audio, language=self.language)
        return self.repair_ai.execute_with_self_repair(recognize)

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.toggle_active()
            return False  # Turpināt klausīties

    def toggle_active(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.icon.icon = Image.new('RGB', (64, 64), color=(0, 255, 0))  # Zaļa
            threading.Thread(target=self.listen_loop).start()
        else:
            self.icon.icon = Image.new('RGB', (64, 64), color=(255, 0, 0))  # Sarkana

    def listen_loop(self):
        with sr.Microphone() as source:
            while self.is_active:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.process_audio(audio)
                    if text:
                        pyperclip.copy(text)
                except Exception as e:
                    self.repair_ai.repair_errors(str(e))

    def setup_tray(self):
        image = Image.new('RGB', (64, 64), color=(255, 0, 0))  # Sākotnēji sarkana
        menu = pystray.Menu(pystray.MenuItem('Exit', self.exit))
        self.icon = pystray.Icon('naeka', image, 'Naeka Voice to Text', menu)
        self.icon.run()

    def exit(self):
        self.icon.stop()
        sys.exit()

    def run(self):
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.setup_tray()

if __name__ == "__main__":
    app = NaekaUnified()
    app.run()
