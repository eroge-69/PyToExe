import vlc
import tkinter as tk
import os
import time

# =========================
# 1. Putanja do VLC DLL-ova
# Ako koristiš VLC portable, stavi putanju do foldera gde je libvlc.dll
# Primer: r"D:\vlc_portable"
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")  # ili zameni sa VLC portable folder

# =========================
# 2. Putanja do tvog video fajla
video_path = r"D:\Game Develop\Mario kart world Video\videoplayback.mp4"

# =========================
# 3. Kreiranje fullscreen Tkinter prozora
root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='black')

# Labela/frame za VLC embed
frame = tk.Frame(root, bg='black')
frame.pack(expand=True, fill='both')

# =========================
# 4. VLC player
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new(video_path)
player.set_media(media)

# Embed u Tkinter prozor
hwnd = frame.winfo_id()
player.set_hwnd(hwnd)

# Pusti video
player.play()

# =========================
# 5. Escape za izlazak
def exit_fullscreen(event):
    player.stop()
    root.destroy()

root.bind("<Escape>", exit_fullscreen)

# =========================
# 6. Tkinter mainloop
root.mainloop()
