import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import threading
import time
import json
import platform
import os
from datetime import datetime

# Try different audio libraries
AUDIO_METHOD = None
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_METHOD = "pygame"
    print("Using pygame for audio")
except ImportError:
    try:
        if platform.system() == "Windows":
            import winsound
            AUDIO_METHOD = "winsound"
            print("Using winsound for audio")
        else:
            # For Linux/Mac, we'll use system beep or simple tone generation
            AUDIO_METHOD = "system"
            print("Using system audio")
    except ImportError:
        AUDIO_METHOD = None
        print("No audio library available")

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Piano Virtual 5 Oktav")
        self.root.geometry("1200x400")
        self.root.configure(bg='#2c3e50')
        
        # Audio settings
        self.volume = 0.5
        self.audio_enabled = AUDIO_METHOD is not None
        
        # Piano settings
        self.octaves = 5
        self.current_octave = 2  # Middle octave
        
        # Note mapping
        self.white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.black_notes = ['C#', 'D#', '', 'F#', 'G#', 'A#', '']
        
        # Keyboard mapping
        self.key_mapping = {
            'a': 'C', 's': 'C#', 'd': 'D', 'f': 'D#', 'g': 'E',
            'h': 'F', 'j': 'F#', 'k': 'G', 'l': 'G#', ';': 'A',
            "'": 'A#', 'Return': 'B',
            'q': 'C5', '2': 'C#5', 'w': 'D5', '3': 'D#5', 'e': 'E5',
            'r': 'F5', '5': 'F#5', 't': 'G5', '6': 'G#5', 'y': 'A5',
            '7': 'A#5', 'u': 'B5'
        }
        
        # Recording
        self.recording = False
        self.recorded_notes = []
        self.record_start_time = None
        
        # Active keys
        self.active_keys = set()
        
        # Audio cache for pygame
        if AUDIO_METHOD == "pygame":
            self.sound_cache = {}
            self.generate_all_sounds()
        
        self.setup_ui()
        self.setup_keyboard_bindings()
        
    def generate_all_sounds(self):
        """Pre-generate all piano sounds for pygame"""
        if AUDIO_METHOD != "pygame":
            return
            
        print("Generating piano sounds...")
        for octave in range(self.octaves):
            for note in self.white_notes + [n for n in self.black_notes if n]:
                note_id = f"{note}{octave}"
                frequency = self.get_frequency(note, octave)
                sound_data = self.generate_tone_data(frequency, 1.0)
                
                # Convert to pygame sound
                try:
                    sound = pygame.sndarray.make_sound(sound_data)
                    self.sound_cache[note_id] = sound
                except:
                    # Fallback method
                    pass
        print(f"Generated {len(self.sound_cache)} sounds")
    
    def generate_tone_data(self, frequency, duration):
        """Generate tone data as numpy array for pygame"""
        import numpy as np
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate sine wave with envelope
        t = np.linspace(0, duration, frames)
        envelope = np.exp(-t * 2)  # Exponential decay
        wave = envelope * np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit integers
        wave = (wave * 32767 * self.volume).astype(np.int16)
        
        # Make stereo
        stereo_wave = np.array([wave, wave]).T
        return stereo_wave
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Audio status
        audio_status = "🔊 Audio: " + (AUDIO_METHOD.upper() if self.audio_enabled else "MUTE")
        tk.Label(control_frame, text=audio_status, bg='#34495e', fg='white').pack(side='left', padx=5)
        
        # Volume control
        tk.Label(control_frame, text="Volume:", bg='#34495e', fg='white').pack(side='left', padx=5)
        self.volume_var = tk.DoubleVar(value=50)
        volume_scale = tk.Scale(control_frame, from_=0, to=100, orient='horizontal',
                              variable=self.volume_var, command=self.update_volume,
                              bg='#34495e', fg='white', highlightthickness=0)
        volume_scale.pack(side='left', padx=5)
        
        # Octave control
        tk.Label(control_frame, text="Oktav:", bg='#34495e', fg='white').pack(side='left', padx=(20, 5))
        self.octave_var = tk.IntVar(value=self.current_octave)
        octave_spin = tk.Spinbox(control_frame, from_=0, to=4, textvariable=self.octave_var,
                               command=self.update_octave, width=5)
        octave_spin.pack(side='left', padx=5)
        
        # Recording controls
        self.record_btn = tk.Button(control_frame, text="🔴 Record", command=self.toggle_recording,
                                  bg='#e74c3c', fg='white', relief='flat')
        self.record_btn.pack(side='left', padx=10)
        
        self.play_btn = tk.Button(control_frame, text="▶️ Play", command=self.play_recording,
                                bg='#27ae60', fg='white', relief='flat')
        self.play_btn.pack(side='left', padx=5)
        
        self.save_btn = tk.Button(control_frame, text="💾 Save", command=self.save_recording,
                                bg='#3498db', fg='white', relief='flat')
        self.save_btn.pack(side='left', padx=5)
        
        self.load_btn = tk.Button(control_frame, text="📁 Load", command=self.load_recording,
                                bg='#9b59b6', fg='white', relief='flat')
        self.load_btn.pack(side='left', padx=5)
        
        # Sustain pedal
        self.sustain_var = tk.BooleanVar()
        sustain_check = tk.Checkbutton(control_frame, text="Sustain", variable=self.sustain_var,
                                     bg='#34495e', fg='white', selectcolor='#34495e')
        sustain_check.pack(side='left', padx=10)
        
        # Piano frame
        piano_frame = tk.Frame(main_frame, bg='#2c3e50')
        piano_frame.pack(fill='both', expand=True)
        
        # Create piano keys
        self.create_piano_keys(piano_frame)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#34495e', relief='sunken', bd=1)
        status_frame.pack(fill='x', side='bottom')
        
        audio_msg = f" | Audio: {AUDIO_METHOD}" if self.audio_enabled else " | Audio: DISABLED"
        self.status_label = tk.Label(status_frame, 
                                   text=f"Piano siap digunakan | Gunakan mouse atau keyboard{audio_msg}",
                                   bg='#34495e', fg='white', anchor='w')
        self.status_label.pack(fill='x', padx=5, pady=2)
        
    def create_piano_keys(self, parent):
        self.white_keys = {}
        self.black_keys = {}
        
        key_width = 40
        key_height = 200
        black_key_width = 25
        black_key_height = 120
        
        # Create white keys
        for octave in range(self.octaves):
            for i, note in enumerate(self.white_notes):
                x = octave * len(self.white_notes) * key_width + i * key_width
                
                key_id = f"{note}{octave}"
                key = tk.Button(parent, text=f"{note}\n{octave}",
                              width=3, height=8,
                              bg='white', fg='black',
                              relief='raised', bd=2,
                              font=('Arial', 8))
                key.place(x=x, y=50, width=key_width-2, height=key_height)
                
                # Bind events
                key.bind('<Button-1>', lambda e, n=key_id: self.key_press(n))
                key.bind('<ButtonRelease-1>', lambda e, n=key_id: self.key_release(n))
                key.bind('<Enter>', lambda e, k=key: k.configure(bg='#f0f0f0'))
                key.bind('<Leave>', lambda e, k=key, kid=key_id: k.configure(bg='white') if kid not in self.active_keys else None)
                
                self.white_keys[key_id] = key
        
        # Create black keys
        for octave in range(self.octaves):
            for i, note in enumerate(self.black_notes):
                if note:  # Skip empty positions
                    x = octave * len(self.white_notes) * key_width + i * key_width + key_width - black_key_width // 2
                    
                    key_id = f"{note}{octave}"
                    key = tk.Button(parent, text=f"{note}\n{octave}",
                                  width=2, height=5,
                                  bg='black', fg='white',
                                  relief='raised', bd=2,
                                  font=('Arial', 7))
                    key.place(x=x, y=50, width=black_key_width, height=black_key_height)
                    
                    # Bind events
                    key.bind('<Button-1>', lambda e, n=key_id: self.key_press(n))
                    key.bind('<ButtonRelease-1>', lambda e, n=key_id: self.key_release(n))
                    key.bind('<Enter>', lambda e, k=key: k.configure(bg='#333333'))
                    key.bind('<Leave>', lambda e, k=key, kid=key_id: k.configure(bg='black') if kid not in self.active_keys else None)
                    
                    self.black_keys[key_id] = key
    
    def setup_keyboard_bindings(self):
        self.root.bind('<KeyPress>', self.keyboard_press)
        self.root.bind('<KeyRelease>', self.keyboard_release)
        self.root.focus_set()
    
    def keyboard_press(self, event):
        key = event.keysym.lower()
        if key in self.key_mapping:
            note = self.key_mapping[key]
            if note.endswith('5'):  # Upper octave
                note_name = note[:-1] + str(min(self.current_octave + 1, 4))
            else:
                note_name = note + str(self.current_octave)
            self.key_press(note_name)
    
    def keyboard_release(self, event):
        key = event.keysym.lower()
        if key in self.key_mapping:
            note = self.key_mapping[key]
            if note.endswith('5'):
                note_name = note[:-1] + str(min(self.current_octave + 1, 4))
            else:
                note_name = note + str(self.current_octave)
            if not self.sustain_var.get():
                self.key_release(note_name)
    
    def key_press(self, note_id):
        if note_id in self.active_keys:
            return
            
        self.active_keys.add(note_id)
        self.play_note(note_id)
        
        # Visual feedback
        if note_id in self.white_keys:
            self.white_keys[note_id].configure(bg='#ffd700')
        elif note_id in self.black_keys:
            self.black_keys[note_id].configure(bg='#555555')
        
        # Record if recording
        if self.recording:
            current_time = time.time() - self.record_start_time
            self.recorded_notes.append({'note': note_id, 'time': current_time, 'action': 'press'})
        
        self.status_label.configure(text=f"Playing: {note_id} | Method: {AUDIO_METHOD or 'VISUAL'}")
    
    def key_release(self, note_id):
        if note_id in self.active_keys:
            self.active_keys.remove(note_id)
        
        # Reset visual
        if note_id in self.white_keys:
            self.white_keys[note_id].configure(bg='white')
        elif note_id in self.black_keys:
            self.black_keys[note_id].configure(bg='black')
        
        # Record if recording
        if self.recording:
            current_time = time.time() - self.record_start_time
            self.recorded_notes.append({'note': note_id, 'time': current_time, 'action': 'release'})
    
    def play_note(self, note_id):
        if not self.audio_enabled:
            return
            
        try:
            # Extract note and octave
            if '#' in note_id:
                note_name = note_id[:-1]
                octave = int(note_id[-1])
            else:
                note_name = note_id[:-1]
                octave = int(note_id[-1])
            
            # Calculate frequency
            frequency = self.get_frequency(note_name, octave)
            
            # Play based on available method
            if AUDIO_METHOD == "pygame":
                self.play_pygame_sound(note_id)
            elif AUDIO_METHOD == "winsound":
                self.play_winsound(frequency)
            elif AUDIO_METHOD == "system":
                self.play_system_beep(frequency)
                
        except Exception as e:
            print(f"Error playing note {note_id}: {e}")
    
    def play_pygame_sound(self, note_id):
        """Play sound using pygame"""
        if note_id in self.sound_cache:
            sound = self.sound_cache[note_id]
            sound.set_volume(self.volume)
            sound.play()
        else:
            # Generate on-the-fly if not cached
            if '#' in note_id:
                note_name = note_id[:-1]
                octave = int(note_id[-1])
            else:
                note_name = note_id[:-1]
                octave = int(note_id[-1])
            
            frequency = self.get_frequency(note_name, octave)
            threading.Thread(target=self.play_generated_tone, args=(frequency,), daemon=True).start()
    
    def play_winsound(self, frequency):
        """Play sound using Windows winsound"""
        def play():
            try:
                duration = 500  # milliseconds
                winsound.Beep(int(frequency), duration)
            except:
                pass
        threading.Thread(target=play, daemon=True).start()
    
    def play_system_beep(self, frequency):
        """Play sound using system beep (Linux/Mac)"""
        def play():
            try:
                if platform.system() == "Linux":
                    # Try using speaker-test or beep
                    os.system(f"timeout 0.5 speaker-test -t sine -f {int(frequency)} >/dev/null 2>&1 &")
                else:
                    # Mac OS
                    os.system(f"afplay /System/Library/Sounds/Pop.aiff &")
            except:
                pass
        threading.Thread(target=play, daemon=True).start()
    
    def play_generated_tone(self, frequency, duration=0.5):
        """Generate and play tone for pygame fallback"""
        try:
            import numpy as np
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            # Generate sine wave
            t = np.linspace(0, duration, frames)
            envelope = np.exp(-t * 3)  # Exponential decay
            wave = envelope * np.sin(2 * np.pi * frequency * t)
            
            # Convert to pygame format
            wave = (wave * 32767 * self.volume).astype(np.int16)
            stereo_wave = np.array([wave, wave]).T
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.play()
            
        except Exception as e:
            print(f"Error generating tone: {e}")
    
    def get_frequency(self, note_name, octave):
        # Note frequencies relative to C
        note_frequencies = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        
        # Calculate frequency using equal temperament
        semitones = octave * 12 + note_frequencies[note_name] - 48  # A4 = 440Hz reference
        frequency = 440 * (2 ** (semitones / 12))
        
        return max(50, min(frequency, 8000))  # Limit frequency range
    
    def update_volume(self, value):
        self.volume = float(value) / 100
    
    def update_octave(self):
        self.current_octave = self.octave_var.get()
    
    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.recorded_notes = []
            self.record_start_time = time.time()
            self.record_btn.configure(text="⏹️ Stop", bg='#c0392b')
            self.status_label.configure(text="🔴 Recording...")
        else:
            self.recording = False
            self.record_btn.configure(text="🔴 Record", bg='#e74c3c')
            self.status_label.configure(text=f"Recording stopped. {len(self.recorded_notes)} events recorded.")
    
    def play_recording(self):
        if not self.recorded_notes:
            messagebox.showwarning("Warning", "Tidak ada recording untuk dimainkan!")
            return
        
        def play_thread():
            self.status_label.configure(text="▶️ Playing recording...")
            start_time = time.time()
            
            for event in sorted(self.recorded_notes, key=lambda x: x['time']):
                # Wait for the right time
                elapsed = time.time() - start_time
                if elapsed < event['time']:
                    time.sleep(event['time'] - elapsed)
                
                if event['action'] == 'press':
                    self.root.after(0, lambda n=event['note']: self.key_press(n))
                else:
                    self.root.after(0, lambda n=event['note']: self.key_release(n))
            
            self.root.after(0, lambda: self.status_label.configure(text="Playback selesai."))
        
        threading.Thread(target=play_thread, daemon=True).start()
    
    def save_recording(self):
        if not self.recorded_notes:
            messagebox.showwarning("Warning", "Tidak ada recording untuk disimpan!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Simpan Recording"
        )
        
        if filename:
            try:
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'notes': self.recorded_notes,
                    'audio_method': AUDIO_METHOD
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                self.status_label.configure(text=f"Recording disimpan ke {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan file: {e}")
    
    def load_recording(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Recording"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                self.recorded_notes = data['notes']
                self.status_label.configure(text=f"Recording loaded dari {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat file: {e}")

def main():
    root = tk.Tk()
    
    # Show audio status
    if AUDIO_METHOD:
        audio_msg = f"Audio menggunakan: {AUDIO_METHOD.upper()}"
    else:
        audio_msg = "Mode Visual - Tidak ada audio yang tersedia"
    
    app = PianoApp(root)
    
    # Help message
    help_text = f"""
    🎹 PIANO VIRTUAL 5 OKTAV 🎹
    
    {audio_msg}
    
    CARA PENGGUNAAN:
    
    🖱️  Mouse: Klik tuts untuk bermain
    ⌨️  Keyboard: 
       - Baris bawah (a,s,d,f,g,h,j,k,l,;,') untuk oktav saat ini
       - Baris atas (q,w,e,r,t,y,u) untuk oktav +1
    
    🎛️  Kontrol:
       - Volume: Geser slider untuk mengatur volume
       - Oktav: Ubah oktav base untuk keyboard
       - Sustain: Tahan nada lebih lama
    
    🎵 Recording:
       - Record: Mulai/stop recording
       - Play: Putar ulang recording
       - Save/Load: Simpan/muat recording ke file
    
    📦 Install Audio (Opsional):
       pip install pygame
    
    Selamat bermain! 🎶
    """
    
    messagebox.showinfo("Piano Virtual - Bantuan", help_text)
    
    root.mainloop()

if __name__ == "__main__":
    main()