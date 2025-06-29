import tkinter as tk
from tkinter import filedialog, messagebox
import os
import winsound

def wav_to_snd(wav_path, snd_path):
    with open(wav_path, 'rb') as f:
        data = f.read()

    if data[0:4] != b'RIFF' or data[8:12] != b'WAVE':
        messagebox.showerror("Błąd", "To nie jest poprawny plik WAV.")
        return False

    audio_data = data[44:]  # pomijamy nagłówek WAV (44 bajty)
    header = b'SND1' + len(audio_data).to_bytes(4, 'little')

    with open(snd_path, 'wb') as f:
        f.write(header)
        f.write(audio_data)

    return True

def play_snd(snd_path):
    try:
        with open(snd_path, 'rb') as f:
            magic = f.read(4)
            if magic != b'SND1':
                messagebox.showerror("Błąd", "Niepoprawny format pliku .snd")
                return

            size_bytes = f.read(4)
            size = int.from_bytes(size_bytes, 'little')
            audio_data = f.read(size)

        # Tworzymy nagłówek WAV na podstawie danych (16-bit mono, 44100 Hz)
        wav_header = b'RIFF' + (36 + size).to_bytes(4, 'little') + b'WAVEfmt ' + \
                     (16).to_bytes(4, 'little') + (1).to_bytes(2, 'little') + \
                     (1).to_bytes(2, 'little') + (44100).to_bytes(4, 'little') + \
                     (44100 * 2).to_bytes(4, 'little') + (2).to_bytes(2, 'little') + \
                     (16).to_bytes(2, 'little') + b'data' + size_bytes

        temp_wav = 'temp_snd_play.wav'
        with open(temp_wav, 'wb') as wav_file:
            wav_file.write(wav_header)
            wav_file.write(audio_data)

        winsound.PlaySound(temp_wav, winsound.SND_FILENAME)
        os.remove(temp_wav)

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas odtwarzania:\n{e}")

def select_wav_and_convert():
    wav_path = filedialog.askopenfilename(filetypes=[("Pliki WAV", "*.wav")])
    if not wav_path:
        return

    snd_path = filedialog.asksaveasfilename(defaultextension=".snd", filetypes=[("Pliki SND", "*.snd")])
    if not snd_path:
        return

    if wav_to_snd(wav_path, snd_path):
        messagebox.showinfo("Sukces", f"Plik zapisany jako:\n{snd_path}")

def select_snd_and_play():
    snd_path = filedialog.askopenfilename(filetypes=[("Pliki SND", "*.snd")])
    if not snd_path:
        return

    play_snd(snd_path)

# --- GUI ---
root = tk.Tk()
root.title("Odtwarzacz i konwerter .SND")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Twój własny odtwarzacz .SND", font=("Arial", 14, "bold")).pack(pady=10)

btn_convert = tk.Button(frame, text="Konwertuj WAV → SND", width=30, command=select_wav_and_convert)
btn_convert.pack(pady=10)

btn_play = tk.Button(frame, text="Odtwórz plik .SND", width=30, command=select_snd_and_play)
btn_play.pack(pady=10)

tk.Label(frame, text="Format obsługuje WAV 16-bit 44100Hz MONO", font=("Arial", 9)).pack(pady=10)

root.mainloop()
