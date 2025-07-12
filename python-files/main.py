import tkinter as tk
import vlc
import configparser
import threading
import time

# Konfiguration laden
config = configparser.ConfigParser()
config.read("stations.ini")
stations = config["Stationen"]

# VLC-Instanz
instance = vlc.Instance()
player = instance.media_player_new()
current_url = None

# Funktion zum Stream starten
def play_station(url):
    global current_url
    current_url = url
    media = instance.media_new(url)
    player.set_media(media)
    player.play()

# Lautstärkeregler
def set_volume(val):
    player.audio_set_volume(int(val))

# Auto-Resume-Funktion im Hintergrund
def monitor_stream():
    while True:
        time.sleep(5)
        state = player.get_state()
        # VLC-Zustände: 6 = Error, 0 = NothingSpecial
        if state in [vlc.State.Error, vlc.State.NothingSpecial] and current_url:
            print("Verbindung verloren – versuche neu zu verbinden...")
            play_station(current_url)

# Starte Überwachungsthread
threading.Thread(target=monitor_stream, daemon=True).start()

# GUI erstellen
root = tk.Tk()
root.title("Radioplayer mit Auto-Resume")

# Senderbuttons
for i, (name, url) in enumerate(stations.items()):
    btn = tk.Button(root, text=name, width=15, command=lambda u=url: play_station(u))
    row = i // 4
    col = i % 4
    btn.grid(row=row, column=col, padx=5, pady=5)

# Lautstärkeregler
volume = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Lautstärke", command=set_volume)
volume.set(100)
volume.grid(row=2, column=0, columnspan=4, pady=10)

root.mainloop()
