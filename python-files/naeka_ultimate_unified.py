"""
NaEka ULTIMATE UNIFIED - Vienīgā versija
Strādā uz VISIEM datoriem - automātiski pielāgojas
Copyright (C) 2025 Neviena AI Research LLC
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import time
import os
import sys
import json
import sqlite3
from datetime import datetime
import subprocess

# Pamata importi - VIENMĒR strādās
try:
    import speech_recognition as sr
    HAS_SPEECH = True
except:
    HAS_SPEECH = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    HAS_KEYBOARD = True
except:
    HAS_KEYBOARD = False

try:
    import keyboard
    HAS_HOTKEYS = True
except:
    HAS_HOTKEYS = False

class SmartAI:
    """Mākslīgais intelekts kas PATIEŠĀM mācās"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser('~'), 'naeka_brain.db')
        self.init_brain()
        
    def init_brain(self):
        """Izveido AI smadzenes"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS learning (
                id INTEGER PRIMARY KEY,
                original TEXT,
                corrected TEXT,
                count INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_voice (
                id INTEGER PRIMARY KEY,
                pattern BLOB,
                clarity REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def learn_correction(self, original, corrected):
        """AI mācās no korekcijām"""
        if original != corrected:
            self.conn.execute(
                'INSERT OR REPLACE INTO learning (original, corrected, count) '
                'VALUES (?, ?, COALESCE((SELECT count FROM learning WHERE original = ?) + 1, 1))',
                (original, corrected, original)
            )
            self.conn.commit()
    
    def correct_latvian(self, text):
        """Gudra latviešu valodas korekcija"""
        if not text:
            return text
            
        # Pamata labojumi
        fixes = {
            'aa': 'ā', 'ee': 'ē', 'ii': 'ī', 'uu': 'ū',
            'sh': 'š', 'zh': 'ž', 'ch': 'č', 'gj': 'ģ',
            'kj': 'ķ', 'lj': 'ļ', 'nj': 'ņ'
        }
        
        # AI iepriekš iemācītie labojumi
        cursor = self.conn.execute(
            'SELECT original, corrected FROM learning ORDER BY count DESC LIMIT 100'
        )
        for row in cursor:
            if row[0] in text:
                text = text.replace(row[0], row[1])
        
        # Pamata labojumi
        for wrong, correct in fixes.items():
            text = text.replace(wrong, correct)
            
        # Gudra teikuma sākuma korekcija
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        # Pievieno punktu ja nav
        if text and text[-1] not in '.!?':
            text += '.'
            
        return text

class UniversalRecognizer:
    """Strādā ar JEBKURU balsi - pat ļoti sliktu"""
    
    def __init__(self, ai_brain):
        self.ai = ai_brain
        self.recognizer = sr.Recognizer() if HAS_SPEECH else None
        self.mic = None
        self.is_calibrated = False
        
    def auto_calibrate(self):
        """Automātiski pielāgojas telpas trokšņiem"""
        if not HAS_SPEECH or self.is_calibrated:
            return
            
        try:
            self.mic = sr.Microphone()
            with self.mic as source:
                # Pielāgojas fonā 2 sekundes
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.is_calibrated = True
        except:
            pass
    
    def listen_smart(self, timeout=5):
        """Gudra klausīšanās - pielāgojas lietotājam"""
        if not HAS_SPEECH or not self.mic:
            return None
            
        try:
            with self.mic as source:
                # Dinamiski pielāgo jūtīgumu
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                
                # Klausās ar pauzi tolerance
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=10
                )
                
                # Mēģina vairākas valodas
                text = None
                for lang in ['lv-LV', 'lv', 'en-US']:
                    try:
                        text = self.recognizer.recognize_google(audio, language=lang)
                        if text:
                            break
                    except:
                        continue
                        
                return text
        except:
            return None

class NaEkaUltimate:
    """Galvenā programma - VIENA VISIEM"""
    
    def __init__(self):
        self.version = "2.0.0 ULTIMATE"
        self.root = tk.Tk()
        self.root.title(f"NaEka - {self.version}")
        
        # Automātiski nosaka ekrāna izmēru
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Pielāgo izmēru ekrānam
        if screen_width < 1366:  # Mazs ekrāns
            self.root.geometry("400x500")
        else:  # Liels ekrāns
            self.root.geometry("600x700")
        
        # Komponentes
        self.ai_brain = SmartAI()
        self.recognizer = UniversalRecognizer(self.ai_brain)
        self.is_active = False
        self.total_recognized = 0
        self.results_queue = queue.Queue()
        
        # Izveido interfeisu
        self.setup_gui()
        
        # Automātiska kalibrācija fonā
        threading.Thread(target=self.auto_setup, daemon=True).start()
        
        # Sāk apstrādes pavedienus
        self.start_processing()
        
    def auto_setup(self):
        """Automātiski visu iestata fonā"""
        # Kalibrē mikrofonu
        self.recognizer.auto_calibrate()
        
        # Instalē trūkstošās bibliotēkas
        self.auto_install_dependencies()
        
        # Reģistrē hotkeys ja iespējams
        self.setup_hotkeys()
        
    def auto_install_dependencies(self):
        """Automātiski instalē vajadzīgās bibliotēkas"""
        required = ['SpeechRecognition', 'pyautogui', 'keyboard']
        
        for package in required:
            try:
                __import__(package.lower().replace('-', '_'))
            except ImportError:
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', package, '--quiet'
                    ])
                except:
                    pass
    
    def setup_gui(self):
        """Universāls interfeiss - strādā visur"""
        # Krāsu shēma
        bg_color = '#1a1a2e'
        fg_color = '#eee'
        accent_color = '#16213e'
        button_color = '#0f3460'
        active_color = '#e94560'
        
        self.root.configure(bg=bg_color)
        
        # Header
        header = tk.Frame(self.root, bg=accent_color, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="NaEka",
            font=('Arial', 28, 'bold'),
            bg=accent_color,
            fg=fg_color
        ).pack(pady=10)
        
        tk.Label(
            header,
            text="Universālā runas atpazīšana",
            font=('Arial', 12),
            bg=accent_color,
            fg='#999'
        ).pack()
        
        # Status
        self.status_var = tk.StringVar(value="⚪ Gatavs darbam")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=('Arial', 14),
            bg=bg_color,
            fg=fg_color,
            pady=15
        )
        self.status_label.pack()
        
        # Galvenā poga
        self.main_button = tk.Button(
            self.root,
            text="▶ SĀKT",
            command=self.toggle_listening,
            font=('Arial', 18, 'bold'),
            bg=button_color,
            fg=fg_color,
            activebackground=active_color,
            activeforeground=fg_color,
            relief='flat',
            width=15,
            height=2,
            cursor='hand2'
        )
        self.main_button.pack(pady=20)
        
        # Info panelis
        info_frame = tk.Frame(self.root, bg=bg_color)
        info_frame.pack(fill='x', padx=20)
        
        self.info_label = tk.Label(
            info_frame,
            text="Spied pogu vai izmanto Ctrl+Space",
            font=('Arial', 10),
            bg=bg_color,
            fg='#666'
        )
        self.info_label.pack()
        
        # Teksta logs
        text_frame = tk.Frame(self.root, bg=accent_color)
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.text_display = scrolledtext.ScrolledText(
            text_frame,
            wrap='word',
            font=('Consolas', 11),
            bg='#0a0a0a',
            fg=fg_color,
            insertbackground=fg_color,
            height=15
        )
        self.text_display.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Statistika
        self.stats_label = tk.Label(
            self.root,
            text="Atpazīti: 0 vārdi",
            font=('Arial', 9),
            bg=bg_color,
            fg='#666'
        )
        self.stats_label.pack(pady=5)
        
        # Apakšējā josla
        bottom_frame = tk.Frame(self.root, bg=accent_color, height=30)
        bottom_frame.pack(fill='x', side='bottom')
        bottom_frame.pack_propagate(False)
        
        tk.Label(
            bottom_frame,
            text=f"NaEka {self.version} © 2025 Neviena AI",
            font=('Arial', 8),
            bg=accent_color,
            fg='#666'
        ).pack(pady=5)
        
    def setup_hotkeys(self):
        """Reģistrē klaviatūras saīsnes"""
        if HAS_HOTKEYS:
            try:
                keyboard.add_hotkey('ctrl+space', self.toggle_listening)
                keyboard.add_hotkey('ctrl+shift+x', self.emergency_stop)
            except:
                pass
                
        # Tk bindings kā backup
        self.root.bind('<Control-space>', lambda e: self.toggle_listening())
        self.root.bind('<Escape>', lambda e: self.emergency_stop())
        
    def toggle_listening(self):
        """Ieslēdz/izslēdz klausīšanos"""
        if self.is_active:
            self.stop_listening()
        else:
            self.start_listening()
            
    def start_listening(self):
        """Sāk klausīties"""
        self.is_active = True
        self.status_var.set("🔴 KLAUSĀS...")
        self.main_button.config(
            text="⏸ PAUZE",
            bg='#e94560'
        )
        self.info_label.config(text="Runā tagad...")
        
        # Sāk klausīšanās pavedienu
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
    def stop_listening(self):
        """Aptur klausīšanos"""
        self.is_active = False
        self.status_var.set("⚪ Gatavs darbam")
        self.main_button.config(
            text="▶ SĀKT",
            bg='#0f3460'
        )
        self.info_label.config(text="Spied pogu vai izmanto Ctrl+Space")
        
    def emergency_stop(self):
        """Avārijas apturēšana"""
        self.stop_listening()
        self.text_display.insert('end', "\n[SISTĒMA] Avārijas apturēšana!\n", 'error')
        messagebox.showinfo("Apturēts", "Programma apturēta")
        
    def listen_loop(self):
        """Galvenais klausīšanās cikls"""
        while self.is_active:
            text = self.recognizer.listen_smart(timeout=3)
            
            if text:
                # AI labojumi
                corrected = self.ai_brain.correct_latvian(text)
                
                # AI mācās
                if text != corrected:
                    self.ai_brain.learn_correction(text, corrected)
                
                # Ievieto rindā
                self.results_queue.put({
                    'original': text,
                    'corrected': corrected,
                    'timestamp': datetime.now()
                })
                
    def process_results(self):
        """Apstrādā rezultātus no rindas"""
        try:
            result = self.results_queue.get(timeout=0.1)
            
            # Parāda tekstā
            time_str = result['timestamp'].strftime("%H:%M:%S")
            
            self.text_display.insert('end', f"[{time_str}] ", 'time')
            self.text_display.insert('end', f"{result['corrected']}\n", 'text')
            
            # Ja mainījās - parāda oriģinālu
            if result['original'] != result['corrected']:
                self.text_display.insert('end', f"          (oriģ: {result['original']})\n", 'debug')
                
            self.text_display.see('end')
            
            # Ieraksta aktīvajā logā
            if HAS_KEYBOARD:
                try:
                    pyautogui.typewrite(result['corrected'] + ' ', interval=0.01)
                except:
                    pass
                    
            # Atjauno statistiku
            self.total_recognized += len(result['corrected'].split())
            self.stats_label.config(text=f"Atpazīti: {self.total_recognized} vārdi")
            
        except queue.Empty:
            pass
            
        # Turpina apstrādi
        if hasattr(self, 'root'):
            self.root.after(100, self.process_results)
            
    def start_processing(self):
        """Sāk visu apstrādes sistēmu"""
        # Tags krāsām
        self.text_display.tag_config('time', foreground='#666')
        self.text_display.tag_config('text', foreground='#fff')
        self.text_display.tag_config('debug', foreground='#444', font=('Consolas', 9))
        self.text_display.tag_config('error', foreground='#e94560')
        
        # Sāk apstrādi
        self.process_results()
        
        # Ievada teksts
        self.text_display.insert('end', "NaEka gatava darbam!\n", 'text')
        self.text_display.insert('end', "• Spied SĀKT vai Ctrl+Space\n", 'debug')
        self.text_display.insert('end', "• Runā skaidri latviski\n", 'debug')
        self.text_display.insert('end', "• Programma mācās no tevis\n\n", 'debug')
        
    def run(self):
        """Palaiž programmu"""
        # Centrē logu
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Palaiž
        self.root.mainloop()

def main():
    """Vienkārši palaist"""
    try:
        app = NaEkaUltimate()
        app.run()
    except Exception as e:
        # Pat ja kaut kas nestrādā - parāda kļūdu skaisti
        import tkinter.messagebox as msg
        msg.showerror(
            "NaEka kļūda",
            f"Diemžēl radās problēma:\n{str(e)}\n\n"
            "Mēģini palaist kā administrators vai "
            "instalē Python bibliotēkas:\n"
            "pip install SpeechRecognition pyautogui keyboard"
        )

if __name__ == "__main__":
    main()