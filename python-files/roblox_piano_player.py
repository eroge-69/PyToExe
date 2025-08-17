import mido
import time
import threading
import customtkinter as ctk
from tkinter import filedialog
import os
import sys
import ctypes
from pynput import mouse

# -----------------------------------------------------------------------------
# Sekcja niskopoziomowej obsługi klawiatury (bez zmian)
# -----------------------------------------------------------------------------
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure): _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure): _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_short), ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure): _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union): _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]
class Input(ctypes.Structure): _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]
KEYEVENTF_SCANCODE = 0x0008; KEYEVENTF_KEYUP = 0x0002

def press_key(scan_code):
    extra = ctypes.c_ulong(0); ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_); ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(scan_code):
    extra = ctypes.c_ulong(0); ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_); ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

SCAN_CODES = {
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
    'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14, 'y': 0x15, 'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
    'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22, 'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 'b': 0x30, 'n': 0x31, 'm': 0x32,
    'lshift': 0x2A, 'lcontrol': 0x1D, 'lmenu': 0x38
}
NOTE_TO_KEY_MAPPING = {
    36: ('1', False), 38: ('2', False), 40: ('3', False), 41: ('4', False), 43: ('5', False), 45: ('6', False), 47: ('7', False), 48: ('8', False), 50: ('9', False), 52: ('0', False), 53: ('q', False), 55: ('w', False), 57: ('e', False), 59: ('r', False), 60: ('t', False), 62: ('y', False), 64: ('u', False), 65: ('i', False), 67: ('o', False), 69: ('p', False), 71: ('a', False), 72: ('s', False), 74: ('d', False), 76: ('f', False), 77: ('g', False), 79: ('h', False), 81: ('j', False), 83: ('k', False), 84: ('l', False), 86: ('z', False), 88: ('x', False), 89: ('c', False), 91: ('v', False), 93: ('b', False), 95: ('n', False), 96: ('m', False),
    37: ('1', True), 39: ('2', True), 42: ('4', True), 44: ('5', True), 46: ('6', True), 49: ('8', True), 51: ('9', True), 54: ('q', True), 56: ('w', True), 58: ('e', True), 61: ('t', True), 63: ('y', True), 66: ('i', True), 68: ('o', True), 70: ('p', True), 73: ('s', True), 75: ('d', True), 78: ('g', True), 80: ('h', True), 82: ('j', True), 85: ('l', True), 87: ('z', True), 90: ('c', True), 92: ('v', True), 94: ('b', True),
}
GM_INSTRUMENTS = ["Piano", "Bright Piano", "E. Grand Piano", "Honky-tonk", "E. Piano 1", "E. Piano 2", "Harpsichord", "Clavinet", "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ", "Perc. Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Nylon Guitar", "Steel Guitar", "Jazz Guitar", "Clean Guitar", "Muted Guitar", "Overdriven G.", "Distortion G.", "G. Harmonics", "Acoustic Bass", "Finger Bass", "Pick Bass", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Str.", "Pizzicato Str.", "Orchestral Harp", "Timpani", "String Ens. 1", "String Ens. 2", "SynthStrings 1", "SynthStrings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina", "Square Lead", "Saw Lead", "Calliope Lead", "Chiff Lead", "Charang Lead", "Voice Lead", "Fifths Lead", "Bass + Lead", "New Age Pad", "Warm Pad", "Polysynth Pad", "Choir Pad", "Bowed Pad", "Metallic Pad", "Halo Pad", "Sweep Pad", "Rain FX", "Soundtrack FX", "Crystal FX", "Atmosphere FX", "Brightness FX", "Goblins FX", "Echoes FX", "Sci-fi FX", "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bag pipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal", "Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"]
stop_event = threading.Event()

class EmergencyStopListener:
    def __init__(self): self.last_click_time = 0; self.listener = mouse.Listener(on_click=self.on_click)
    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.right and pressed:
            current_time = time.time()
            if current_time - self.last_click_time < 0.3: os._exit(1)
            self.last_click_time = current_time
    def start(self): self.listener.start()

class TrackSelectionWindow(ctk.CTkToplevel):
    def __init__(self, parent, tracks_info):
        super().__init__(parent); self.title("Wybierz ścieżki do odtworzenia"); self.geometry("600x400")
        self.transient(parent); self.grab_set()
        self.selected_indices = []; self.checkboxes = []
        scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Dostępne ścieżki w pliku MIDI"); scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)
        for i, track in enumerate(tracks_info):
            checkbox_text = f"[{track['index']}] {track['name']} ({track['instrument']}) - {track['notes']} nut"
            checkbox = ctk.CTkCheckBox(scrollable_frame, text=checkbox_text); checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w"); checkbox.select()
            self.checkboxes.append((checkbox, track['index']))
        ok_button = ctk.CTkButton(self, text="Zatwierdź", command=self.on_ok); ok_button.pack(pady=10); self.wait_window()
    def on_ok(self): self.selected_indices = [index for checkbox, index in self.checkboxes if checkbox.get() == 1]; self.destroy()

class RobloxPianoApp(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title("Roblox Piano Player"); self.geometry("500x380")
        self.resizable(False, False); ctk.set_appearance_mode("dark")
        self.midi_filepath = ""; self.selected_track_indices = []
        self.main_frame = ctk.CTkFrame(self, corner_radius=10); self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.file_label = ctk.CTkLabel(self.main_frame, text="Nie wybrano pliku MIDI", text_color="gray"); self.file_label.pack(pady=(10, 5))
        self.select_button = ctk.CTkButton(self.main_frame, text="Wybierz plik .mid", command=self.select_and_analyze_file); self.select_button.pack(pady=10)
        self.speed_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent"); self.speed_frame.pack(pady=5, padx=10, fill="x")
        self.speed_label = ctk.CTkLabel(self.speed_frame, text="Prędkość: 1.00x"); self.speed_label.pack(side="left", padx=(10, 5))
        self.speed_slider = ctk.CTkSlider(self.speed_frame, from_=0.5, to=2.0, number_of_steps=150, command=self.update_speed_label)
        self.speed_slider.set(1.0); self.speed_slider.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.play_button = ctk.CTkButton(self.main_frame, text="Odtwarzaj", command=self.start_playback_thread, state="disabled"); self.play_button.pack(pady=10)
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress_bar.set(0); self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.status_label = ctk.CTkLabel(self.main_frame, text="Wybierz plik, aby rozpocząć.", font=ctk.CTkFont(size=14)); self.status_label.pack(pady=(10, 20))

    def update_speed_label(self, value): self.speed_label.configure(text=f"Prędkość: {float(value):.2f}x")
    def update_progress(self, value): self.progress_bar.set(value)

    def select_and_analyze_file(self):
        filepath = filedialog.askopenfilename(title="Wybierz plik MIDI", filetypes=(("Pliki MIDI", "*.mid *.midi"),));
        if not filepath: return
        self.midi_filepath = filepath
        self.file_label.configure(text=os.path.basename(filepath), text_color="white")
        self.play_button.configure(state="disabled"); self.status_label.configure(text="⚙️ Analizowanie pliku..."); self.progress_bar.set(0)
        try:
            mid = mido.MidiFile(filepath); tracks_info = self.analyze_midi(mid)
            if not tracks_info: self.status_label.configure(text="⚠️ W tym pliku nie znaleziono żadnych nut."); return
            dialog = TrackSelectionWindow(self, tracks_info); self.selected_track_indices = dialog.selected_indices
            if self.selected_track_indices: self.status_label.configure(text=f"✔️ Gotowy. Wybrano {len(self.selected_track_indices)} ścieżek."); self.play_button.configure(state="normal")
            else: self.status_label.configure(text="Anulowano wybór. Wybierz ścieżki.")
        except Exception as e: self.status_label.configure(text=f"❌ Błąd analizy pliku: {e}")

    def analyze_midi(self, mid):
        tracks_info = [];
        for i, track in enumerate(mid.tracks):
            track_name = track.name.strip() if track.name else f"Bez nazwy {i}"
            instrument_name = "Perkusja/Inne"; note_count = 0
            for msg in track:
                if msg.type == 'program_change' and msg.channel != 9: instrument_name = GM_INSTRUMENTS[msg.program]
                if msg.type == 'note_on' and msg.velocity > 0: note_count += 1
            if note_count > 5:
                tracks_info.append({"index": i, "name": track_name, "instrument": instrument_name, "notes": note_count})
        return tracks_info

    def start_playback_thread(self): stop_event.clear(); threading.Thread(target=self.play_midi_worker, daemon=True).start()

    def play_midi_worker(self):
        self.play_button.configure(state="disabled"); self.select_button.configure(state="disabled"); self.speed_slider.configure(state="disabled"); self.progress_bar.set(0)
        try:
            mid = mido.MidiFile(self.midi_filepath, clip=True)
            selected_tracks = [mid.tracks[i] for i in self.selected_track_indices if i < len(mid.tracks)]
            if not selected_tracks: raise ValueError("Brak ścieżek do odtworzenia.")
            
            # --- OSTATECZNA POPRAWKA TIMINGU ---
            # 1. Stwórz nowy, pusty obiekt MidiFile w pamięci.
            playback_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
            # 2. Połącz wybrane ścieżki w jeden strumień (czas wciąż w "tyknięciach").
            merged_track = mido.merge_tracks(selected_tracks)
            # 3. Dodaj ten połączony strumień jako nową ścieżkę do naszego pliku w pamięci.
            playback_mid.tracks.append(merged_track)
            
            # 4. Poprawnie oblicz długość utworu w sekundach z nowego pliku.
            total_time = playback_mid.length
            # --- KONIEC POPRAWKI ---

        except Exception as e:
            self.status_label.configure(text=f"Błąd ładowania pliku: {e}")
            self.play_button.configure(state="normal"); self.select_button.configure(state="normal"); self.speed_slider.configure(state="normal")
            return

        for i in range(3, 0, -1):
            if stop_event.is_set(): break
            self.status_label.configure(text=f"Start za {i}... (przełącz się do Roblox!)"); time.sleep(1)
        if not stop_event.is_set(): self.status_label.configure(text="▶️ Odtwarzanie... (Dwuklik PPM aby zatrzymać!)")

        is_shift_pressed = False; pressed_note_keys = set()
        
        try:
            speed_multiplier = self.speed_slider.get()
            elapsed_time = 0.0

            # --- OSTATECZNA, POPRAWNA PĘTLA ODTWARZANIA ---
            # Iterując po obiekcie playback_mid, msg.time jest POPRAWNIE konwertowane na sekundy!
            for msg in playback_mid:
                if stop_event.is_set(): break
                
                wait_time = msg.time / speed_multiplier
                if wait_time > 0: time.sleep(wait_time)
                elapsed_time += msg.time

                if stop_event.is_set(): break
                if total_time > 0: self.after(0, self.update_progress, elapsed_time / total_time)
                if msg.type not in ('note_on', 'note_off'): continue

                key_info = NOTE_TO_KEY_MAPPING.get(msg.note)
                if not key_info: continue
                key_name, needs_shift = key_info
                scan_code = SCAN_CODES[key_name]
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    release_key(SCAN_CODES['lcontrol']); release_key(SCAN_CODES['lmenu'])
                    if needs_shift and not is_shift_pressed:
                        press_key(SCAN_CODES['lshift']); is_shift_pressed = True
                    elif not needs_shift and is_shift_pressed:
                        release_key(SCAN_CODES['lshift']); is_shift_pressed = False
                    press_key(scan_code); pressed_note_keys.add(scan_code)
                
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if scan_code in pressed_note_keys:
                        release_key(scan_code); pressed_note_keys.remove(scan_code)
            
            if not stop_event.is_set(): self.status_label.configure(text="✅ Odtwarzanie zakończone."); self.progress_bar.set(1)

        except Exception as e: self.status_label.configure(text=f"Wystąpił błąd: {e}")
        finally:
            print("Czyszczenie wszystkich wciśniętych klawiszy...")
            if is_shift_pressed: release_key(SCAN_CODES['lshift'])
            release_key(SCAN_CODES['lcontrol']); release_key(SCAN_CODES['lmenu'])
            for code in list(pressed_note_keys): release_key(code)
            
            self.play_button.configure(state="normal"); self.select_button.configure(state="normal"); self.speed_slider.configure(state="normal")
            if not stop_event.is_set(): self.after(1000, lambda: self.progress_bar.set(0))

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except: return False

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        emergency_stopper = EmergencyStopListener(); emergency_stopper.start()
        app = RobloxPianoApp(); app.mainloop()