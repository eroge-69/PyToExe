import tkinter as tk
from tkinter import filedialog, messagebox
import os
import struct
import platform
import time

try:
    import winsound
except ImportError:
    winsound = None

MAX_NOTES = 60
VALID_OCTAVES = [3, 4, 5]

# MIDI-Note → Nibbler Notation
MIDI_TO_NOTE = {
    48: "C3", 49: "C3#", 50: "D3", 51: "D3#", 52: "E3", 53: "F3", 54: "F3#", 55: "G3",
    56: "G3#", 57: "A3", 58: "A3#", 59: "B3",
    60: "C4", 61: "C4#", 62: "D4", 63: "D4#", 64: "E4", 65: "F4", 66: "F4#", 67: "G4",
    68: "G4#", 69: "A4", 70: "A4#", 71: "B4",
    72: "C5", 73: "C5#", 74: "D5", 75: "D5#", 76: "E5", 77: "F5", 78: "F5#", 79: "G5",
    80: "G5#", 81: "A5", 82: "A5#", 83: "B5",
}

# Frequenzen für Tonvorschau
NOTE_FREQUENCIES = {
    "C3": 130.81, "C3#": 138.59, "D3": 146.83, "D3#": 155.56, "E3": 164.81,
    "F3": 174.61, "F3#": 185.00, "G3": 196.00, "G3#": 207.65, "A3": 220.00, "A3#": 233.08, "B3": 246.94,
    "C4": 261.63, "C4#": 277.18, "D4": 293.66, "D4#": 311.13, "E4": 329.63,
    "F4": 349.23, "F4#": 369.99, "G4": 392.00, "G4#": 415.30, "A4": 440.00, "A4#": 466.16, "B4": 493.88,
    "C5": 523.25, "C5#": 554.37, "D5": 587.33, "D5#": 622.25, "E5": 659.25,
    "F5": 698.46, "F5#": 739.99, "G5": 783.99, "G5#": 830.61, "A5": 880.00, "A5#": 932.33, "B5": 987.77
}

# Dauer-Tabelle in Millisekunden
LENGTH_MS = {
    "1/1": 1600,
    "1/2": 800,
    "1/4": 400,
    "1/8": 200,
    "1/16": 100
}

def ticks_to_note_length(duration_ticks, ticks_per_beat):
    beats = duration_ticks / ticks_per_beat
    if abs(beats - 1.0) < 0.1:
        return "1/1"
    elif abs(beats - 0.5) < 0.1:
        return "1/2"
    elif abs(beats - 0.25) < 0.05:
        return "1/4"
    elif abs(beats - 0.125) < 0.02:
        return "1/8"
    elif abs(beats - 0.0625) < 0.01:
        return "1/16"
    else:
        return "1/4"

def parse_midi_bytes_smart(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    if not data.startswith(b'MThd'):
        raise ValueError("Keine gültige MIDI-Datei")

    ticks_per_beat = struct.unpack(">H", data[12:14])[0]

    notes = []
    i = 14
    while i < len(data) - 4 and len(notes) < MAX_NOTES:
        if data[i] >= 0x90 and data[i+2] > 0:
            midi_note = data[i+1]
            if midi_note not in MIDI_TO_NOTE:
                i += 3
                continue
            duration = 0
            j = i + 3
            while j < len(data) - 2:
                if (data[j] >= 0x80 and data[j] <= 0x9F) and data[j+1] == midi_note:
                    break
                duration += 1
                j += 1
            note_name = MIDI_TO_NOTE[midi_note]
            try:
                if int(note_name[-1]) not in VALID_OCTAVES:
                    i += 3
                    continue
            except:
                i += 3
                continue
            note_len = ticks_to_note_length(duration, ticks_per_beat)
            notes.append(f"{note_name}_{note_len}")
        i += 1
    return notes

def generate_nibbler_code(note_list):
    code = ["play_my_song_1:"]
    for i, note in enumerate(note_list):
        code.append(f"\ntone_{i+1:03}:\n    jmp {note}")
    code.append("\n    jmp end_song")
    return "\n".join(code)

def convert_midi():
    file_path = filedialog.askopenfilename(filetypes=[("MIDI-Dateien", "*.mid")])
    if not file_path:
        return
    try:
        notes = parse_midi_bytes_smart(file_path)
        if not notes:
            messagebox.showwarning("Hinweis", "Keine gültigen Noten gefunden.")
            return
        code = generate_nibbler_code(notes)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, code)
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim MIDI-Lesen:\n{e}")

def convert_manual():
    raw_text = manual_input.get("1.0", tk.END).strip().splitlines()
    notes = [line.strip() for line in raw_text if "_" in line][:MAX_NOTES]
    if not notes:
        messagebox.showwarning("Hinweis", "Keine gültigen Noten erkannt.")
        return
    code = generate_nibbler_code(notes)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, code)

def play_note_sequence(note_lines):
    if winsound is None or platform.system() != "Windows":
        messagebox.showinfo("Nicht unterstützt", "Tonvorschau funktioniert nur unter Windows.")
        return

    for line in note_lines:
        line = line.strip()
        if "_" not in line:
            continue
        try:
            tone, length = line.split("_")
            freq = NOTE_FREQUENCIES.get(tone)
            duration = LENGTH_MS.get(length, 400)
            if freq:
                winsound.Beep(int(freq), duration)
            else:
                time.sleep(duration / 1000.0)
        except:
            continue

def preview_sound():
    lines = output_text.get("1.0", tk.END).strip().splitlines()
    note_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("jmp "):
            note_lines.append(line[4:])
    if not note_lines:
        messagebox.showwarning("Keine Daten", "Keine konvertierten Noten zum Abspielen.")
        return
    play_note_sequence(note_lines)

def copy_to_clipboard():
    code = output_text.get("1.0", tk.END).strip()
    if not code:
        messagebox.showinfo("Hinweis", "Kein Text zum Kopieren.")
        return
    root.clipboard_clear()
    root.clipboard_append(code)
    messagebox.showinfo("Kopiert", "Nibbler-Code wurde in die Zwischenablage kopiert.")

# === GUI ===
root = tk.Tk()
root.title("🎵 Nibbler Musik-Konverter")
root.geometry("900x700")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="MIDI Datei laden & umwandeln", command=convert_midi).pack(side=tk.LEFT, padx=10)
tk.Button(frame, text="Noten aus Eingabe umwandeln", command=convert_manual).pack(side=tk.LEFT, padx=10)
tk.Button(frame, text="🎧 Tonvorschau abspielen", command=preview_sound).pack(side=tk.LEFT, padx=10)
tk.Button(frame, text="📋 In Zwischenablage kopieren", command=copy_to_clipboard).pack(side=tk.LEFT, padx=10)

tk.Label(root, text="🎼 Manuelle Eingabe (z. B. C4_1/4, D5_1/2 ...):").pack()
manual_input = tk.Text(root, height=8)
manual_input.pack(fill=tk.X, padx=20)

tk.Label(root, text="🧾 Nibbler Assembler Ausgabe:").pack()
output_text = tk.Text(root, height=20)
output_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

root.mainloop()
