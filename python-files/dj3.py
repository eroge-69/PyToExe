import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, Listbox, END
from gtts import gTTS
import pygame
import os
import threading
import time
import tempfile
from datetime import datetime
import random
import math
import numpy as np
from pygame import mixer
import json

class TextToAudioDJApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Audio MP3 Virtual DJ")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        
        # Variables
        self.current_audio_file = None
        self.is_playing = False
        self.is_dj_playing = False
        self.start_time = None
        self.duration_minutes = tk.IntVar(value=5)
        self.interval_ms = tk.IntVar(value=500)
        self.dj_volume = tk.DoubleVar(value=0.7)
        self.tts_volume = tk.DoubleVar(value=0.8)
        self.dj_tempo = tk.DoubleVar(value=1.0)
        self.log_messages = []
        
        # DJ Effects
        self.dj_effects = {
            'echo': False,
            'reverb': False,
            'filter': False,
            'scratch': False
        }
        
        # Load DJ samples
        self.dj_samples = []
        self.load_dj_samples()
        
        self.setup_ui()
        self.update_logs()
        
    def load_dj_samples(self):
        """Generate some DJ sample sounds"""
        try:
            # Generate some basic DJ sounds
            self.dj_samples = [
                self.generate_dj_sound('beat', 120),
                self.generate_dj_sound('bass', 60),
                self.generate_dj_sound('synth', 180),
                self.generate_dj_sound('fx', 90)
            ]
        except Exception as e:
            print(f"Error loading DJ samples: {e}")
            self.dj_samples = []
    
    def generate_dj_sound(self, sound_type, bpm):
        """Generate different types of DJ sounds"""
        sample_rate = 44100
        duration = 60.0 / bpm  # One beat duration
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        if sound_type == 'beat':
            # Kick drum sound
            note = np.sin(2 * np.pi * 80 * t) * np.exp(-12 * t)
            note += 0.3 * np.random.uniform(-1, 1, len(t)) * np.exp(-20 * t)
            
        elif sound_type == 'bass':
            # Bass sound
            note = np.sin(2 * np.pi * 55 * t) * 0.7
            note += np.sin(2 * np.pi * 110 * t) * 0.3
            
        elif sound_type == 'synth':
            # Synth sound
            note = (np.sin(2 * np.pi * 220 * t) * 0.4 +
                   np.sin(2 * np.pi * 440 * t) * 0.3 +
                   np.sin(2 * np.pi * 660 * t) * 0.2)
            
        else:  # fx
            # FX sound
            note = np.sin(2 * np.pi * 880 * t * (1 + 0.1 * np.sin(2 * np.pi * 5 * t)))
            note *= np.exp(-3 * t)
        
        # Apply envelope
        envelope = np.ones_like(note)
        attack = int(0.01 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        note *= envelope
        note = (note * 32767).astype(np.int16)
        
        return pygame.mixer.Sound(buffer=note.tobytes())
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🎧 TEXT TO AUDIO MP3 VIRTUAL DJ", 
                              font=("Arial", 18, "bold"), bg='#34495e', fg='white',
                              padx=20, pady=10)
        title_label.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        # Left panel - Text input and controls
        left_frame = ttk.LabelFrame(main_frame, text="Text Input & Controls", padding=10)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Text input
        ttk.Label(left_frame, text="Enter Text:", font=("Arial", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, 
                                                  width=50, height=15,
                                                  font=("Arial", 10),
                                                  bg='#ecf0f1', fg='#2c3e50')
        self.text_area.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Settings frame
        settings_frame = ttk.Frame(left_frame)
        settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # Duration
        ttk.Label(settings_frame, text="Duration (min):").grid(row=0, column=0, sticky="w")
        duration_spin = ttk.Spinbox(settings_frame, from_=1, to=100, 
                                   textvariable=self.duration_minutes, width=8)
        duration_spin.grid(row=0, column=1, sticky="w", padx=(5, 15))
        
        # Interval
        ttk.Label(settings_frame, text="Interval (ms):").grid(row=0, column=2, sticky="w")
        interval_spin = ttk.Spinbox(settings_frame, from_=1, to=1000, 
                                   textvariable=self.interval_ms, width=8)
        interval_spin.grid(row=0, column=3, sticky="w")
        
        # Volume controls
        ttk.Label(settings_frame, text="TTS Volume:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tts_scale = ttk.Scale(settings_frame, from_=0.0, to=1.0, 
                             variable=self.tts_volume, orient="horizontal", length=150)
        tts_scale.grid(row=1, column=1, sticky="w", padx=(5, 15), pady=(10, 0))
        
        ttk.Label(settings_frame, text="DJ Volume:").grid(row=1, column=2, sticky="w", pady=(10, 0))
        dj_scale = ttk.Scale(settings_frame, from_=0.0, to=1.0, 
                            variable=self.dj_volume, orient="horizontal", length=150)
        dj_scale.grid(row=1, column=3, sticky="w", pady=(10, 0))
        
        # Control buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        self.start_btn = ttk.Button(btn_frame, text="▶️ START", 
                                   command=self.start_playback, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹️ STOP", 
                                  command=self.stop_playback, state=tk.DISABLED, width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🧹 CLEAR", 
                                   command=self.clear_text, width=12)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(left_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(left_frame, text="✅ Ready to play", 
                                    font=("Arial", 10), foreground="green")
        self.status_label.grid(row=5, column=0, sticky="w")
        
        # Middle panel - DJ Controls
        middle_frame = ttk.LabelFrame(main_frame, text="Virtual DJ Controls", padding=10)
        middle_frame.grid(row=1, column=1, sticky="nsew", padx=5)
        
        # DJ Effects
        ttk.Label(middle_frame, text="DJ Effects:", font=("Arial", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.echo_var = tk.BooleanVar()
        echo_cb = ttk.Checkbutton(middle_frame, text="Echo", variable=self.echo_var)
        echo_cb.grid(row=1, column=0, sticky="w", pady=2)
        
        self.reverb_var = tk.BooleanVar()
        reverb_cb = ttk.Checkbutton(middle_frame, text="Reverb", variable=self.reverb_var)
        reverb_cb.grid(row=1, column=1, sticky="w", pady=2)
        
        self.filter_var = tk.BooleanVar()
        filter_cb = ttk.Checkbutton(middle_frame, text="Filter", variable=self.filter_var)
        filter_cb.grid(row=2, column=0, sticky="w", pady=2)
        
        self.scratch_var = tk.BooleanVar()
        scratch_cb = ttk.Checkbutton(middle_frame, text="Scratch", variable=self.scratch_var)
        scratch_cb.grid(row=2, column=1, sticky="w", pady=2)
        
        # Tempo control
        ttk.Label(middle_frame, text="Tempo:", font=("Arial", 11, "bold")).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(20, 5))
        
        tempo_scale = ttk.Scale(middle_frame, from_=0.5, to=2.0, 
                               variable=self.dj_tempo, orient="horizontal", length=200)
        tempo_scale.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # DJ Control buttons
        dj_btn_frame = ttk.Frame(middle_frame)
        dj_btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        self.dj_start_btn = ttk.Button(dj_btn_frame, text="🎧 START DJ", 
                                      command=self.start_dj, width=15)
        self.dj_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.dj_stop_btn = ttk.Button(dj_btn_frame, text="⏹️ STOP DJ", 
                                     command=self.stop_dj, state=tk.DISABLED, width=15)
        self.dj_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Logs
        right_frame = ttk.LabelFrame(main_frame, text="System Logs", padding=10)
        right_frame.grid(row=1, column=2, sticky="nsew", padx=(10, 0))
        
        # Log listbox
        self.log_listbox = Listbox(right_frame, height=20, width=40, 
                                  bg='#2c3e50', fg='white', font=("Courier", 9))
        self.log_listbox.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar for logs
        log_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.log_listbox.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_listbox.configure(yscrollcommand=log_scrollbar.set)
        
        # Clear logs button
        clear_logs_btn = ttk.Button(right_frame, text="🗑️ CLEAR LOGS", 
                                   command=self.clear_logs, width=15)
        clear_logs_btn.grid(row=1, column=0, pady=(10, 0))
        
        # Save logs button
        save_logs_btn = ttk.Button(right_frame, text="💾 SAVE LOGS", 
                                  command=self.save_logs, width=15)
        save_logs_btn.grid(row=1, column=1, pady=(10, 0))
        
        # Time display
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        self.time_label = ttk.Label(time_frame, text="00:00:00", font=("Arial", 12))
        self.time_label.pack(side=tk.LEFT)
        
        self.elapsed_label = ttk.Label(time_frame, text="Elapsed: 00:00:00", font=("Arial", 10))
        self.elapsed_label.pack(side=tk.RIGHT)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Start time update
        self.update_time()
    
    def add_log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_messages.append(log_message)
        
        # Keep only last 100 messages
        if len(self.log_messages) > 100:
            self.log_messages = self.log_messages[-100:]
        
        self.update_logs()
    
    def update_logs(self):
        """Update log display"""
        self.log_listbox.delete(0, END)
        for message in self.log_messages[-20:]:  # Show last 20 messages
            self.log_listbox.insert(END, message)
        self.log_listbox.yview(END)
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_messages = []
        self.log_listbox.delete(0, END)
        self.add_log("Logs cleared")
    
    def save_logs(self):
        """Save logs to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Log File"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for message in self.log_messages:
                        f.write(message + '\n')
                self.add_log(f"Logs saved to {file_path}")
                messagebox.showinfo("Success", "Logs saved successfully!")
                
        except Exception as e:
            self.add_log(f"Error saving logs: {e}")
            messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def update_elapsed_time(self):
        """Update elapsed time display"""
        if self.start_time and self.is_playing:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.elapsed_label.config(text=f"Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_elapsed_time)
    
    def start_playback(self):
        """Start text to speech playback"""
        text = self.text_area.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Warning", "Please enter some text first!")
            return
        
        self.add_log("Starting text to speech playback...")
        
        self.is_playing = True
        self.start_time = time.time()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="🔄 Playing...", foreground="orange")
        self.progress.start()
        
        # Start elapsed time update
        self.update_elapsed_time()
        
        # Run in separate thread
        thread = threading.Thread(target=self.playback_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def playback_thread(self, text):
        """Thread for playing back text"""
        try:
            # Convert text to speech
            self.add_log("Converting text to speech...")
            tts = gTTS(text=text, lang='en', slow=False)
            temp_file = os.path.join(tempfile.gettempdir(), f"tts_dj_{int(time.time())}.mp3")
            tts.save(temp_file)
            self.current_audio_file = temp_file
            
            self.add_log("Text converted to speech successfully")
            
            # Play with intervals
            duration = self.duration_minutes.get() * 60
            interval = self.interval_ms.get() / 1000.0
            
            pygame.mixer.music.load(self.current_audio_file)
            pygame.mixer.music.set_volume(self.tts_volume.get())
            
            start_time = time.time()
            while self.is_playing and (time.time() - start_time) < duration:
                if not self.is_playing:
                    break
                
                self.add_log("Playing audio...")
                pygame.mixer.music.play()
                
                # Wait for playback to finish or stop signal
                while pygame.mixer.music.get_busy() and self.is_playing:
                    time.sleep(0.1)
                
                if self.is_playing:
                    self.add_log(f"Waiting {interval:.1f}s before next play...")
                    time.sleep(interval)
            
            self.root.after(0, self.playback_finished)
            
        except Exception as e:
            self.root.after(0, lambda: self.playback_error(f"Playback error: {e}"))
    
    def playback_finished(self):
        """Called when playback finishes"""
        self.is_playing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="✅ Playback finished", foreground="green")
        self.progress.stop()
        self.add_log("Playback finished")
    
    def playback_error(self, error_msg):
        """Handle playback errors"""
        self.is_playing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="❌ Error", foreground="red")
        self.progress.stop()
        self.add_log(f"Error: {error_msg}")
        messagebox.showerror("Error", error_msg)
    
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        pygame.mixer.music.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="⏹️ Stopped", foreground="red")
        self.progress.stop()
        self.add_log("Playback stopped by user")
    
    def start_dj(self):
        """Start DJ mode"""
        self.is_dj_playing = True
        self.dj_start_btn.config(state=tk.DISABLED)
        self.dj_stop_btn.config(state=tk.NORMAL)
        self.add_log("Starting Virtual DJ mode...")
        
        # Start DJ in separate thread
        thread = threading.Thread(target=self.dj_thread)
        thread.daemon = True
        thread.start()
    
    def dj_thread(self):
        """DJ mode thread"""
        try:
            beat_count = 0
            while self.is_dj_playing:
                # Play random DJ samples with effects
                if self.dj_samples:
                    sample = random.choice(self.dj_samples)
                    sample.set_volume(self.dj_volume.get())
                    sample.play()
                
                # Apply effects
                if self.echo_var.get():
                    time.sleep(0.1)
                    if self.dj_samples:
                        sample = random.choice(self.dj_samples)
                        sample.set_volume(self.dj_volume.get() * 0.5)
                        sample.play()
                
                if self.scratch_var.get() and beat_count % 4 == 0:
                    self.add_log("Scratch effect applied")
                
                beat_count += 1
                
                # Calculate sleep time based on tempo
                sleep_time = 0.5 / self.dj_tempo.get()
                time.sleep(sleep_time)
                
        except Exception as e:
            self.add_log(f"DJ error: {e}")
    
    def stop_dj(self):
        """Stop DJ mode"""
        self.is_dj_playing = False
        self.dj_start_btn.config(state=tk.NORMAL)
        self.dj_stop_btn.config(state=tk.DISABLED)
        self.add_log("Virtual DJ mode stopped")
    
    def clear_text(self):
        """Clear text area"""
        self.text_area.delete("1.0", tk.END)
        self.add_log("Text area cleared")
    
    def on_closing(self):
        """Cleanup on closing"""
        self.is_playing = False
        self.is_dj_playing = False
        pygame.mixer.music.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TextToAudioDJApp(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()