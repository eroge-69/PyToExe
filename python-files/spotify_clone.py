import os
import pygame
import base64
import tempfile
import customtkinter as ctk

# Görünüm
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Mini Spotify")
app.geometry("400x300")

pygame.mixer.init()

songs = []
current_index = 0
paused = False
temp_files = []

# Klasörden müzikleri al
def load_songs():
    all_files = [f for f in os.listdir() if f.lower().endswith((".mp3", ".wav", ".txt"))]
    return all_files

def decode_base64_file(txt_file):
    with open(txt_file, "r") as f:
        base64_data = f.read().strip()
    audio_bytes = base64.b64decode(base64_data)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_bytes)
    temp_file.close()
    temp_files.append(temp_file.name)
    return temp_file.name

def play_song():
    global paused
    if songs:
        track = songs[current_index]
        if track.endswith(".txt"):
            file_to_play = decode_base64_file(track)
        else:
            file_to_play = track
        pygame.mixer.music.load(file_to_play)
        pygame.mixer.music.play()
        status_label.configure(text=f"🎶 Çalıyor: {track}")
        paused = False
    else:
        status_label.configure(text="⚠ Klasörde şarkı yok")

def pause_song():
    global paused
    if not paused:
        pygame.mixer.music.pause()
        paused = True
        status_label.configure(text="⏸ Duraklatıldı")
    else:
        pygame.mixer.music.unpause()
        paused = False
        status_label.configure(text=f"🎶 Çalıyor: {songs[current_index]}")

def stop_song():
    pygame.mixer.music.stop()
    status_label.configure(text="⏹ Durduruldu")

def next_song():
    global current_index
    if songs:
        current_index = (current_index + 1) % len(songs)
        play_song()

def prev_song():
    global current_index
    if songs:
        current_index = (current_index - 1) % len(songs)
        play_song()

# Başlık
ctk.CTkLabel(app, text="🎧 Mini Spotify", font=("Arial", 22, "bold")).pack(pady=10)

# Kontrol butonları
btn_frame = ctk.CTkFrame(app, fg_color="transparent")
btn_frame.pack(pady=10)

prev_btn = ctk.CTkButton(btn_frame, text="⏮ Önceki", command=prev_song, width=80)
prev_btn.grid(row=0, column=0, padx=5)

play_btn = ctk.CTkButton(btn_frame, text="▶ Oynat", command=play_song, width=80)
play_btn.grid(row=0, column=1, padx=5)

pause_btn = ctk.CTkButton(btn_frame, text="⏸ Duraklat", command=pause_song, width=100)
pause_btn.grid(row=0, column=2, padx=5)

stop_btn = ctk.CTkButton(app, text="⏹ Durdur", command=stop_song, width=100)
stop_btn.pack(pady=5)

next_btn = ctk.CTkButton(app, text="⏭ Sonraki", command=next_song, width=100)
next_btn.pack(pady=5)

# Durum yazısı
status_label = ctk.CTkLabel(app, text="Hoşgeldin 🎵", font=("Arial", 16))
status_label.pack(pady=20)

# Başlangıçta şarkıları yükle
songs = load_songs()
if songs:
    status_label.configure(text=f"✅ {len(songs)} şarkı bulundu")
else:
    status_label.configure(text="⚠ Şarkı bulunamadı")

app.mainloop()
