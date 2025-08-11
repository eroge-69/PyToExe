import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

CLIENT_ID = "9a4c582f7e7240c1b3c3ab675ff03926"
CLIENT_SECRET = "4ba21e33bf7d43f29189d80fa32aa24b"
REDIRECT_URI = "http://127.0.0.1:8080/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
))

root = tk.Tk()
root.title("Spotify Controller")
root.geometry("450x350")
root.configure(bg="#121212")  # Dark grey background close to Spotify's theme

# Container frame for album art and text info
frame = tk.Frame(root, bg="#121212")
frame.pack(padx=20, pady=20)

# Album art display with border to simulate shadow
album_art_label = tk.Label(frame, bg="#121212", bd=3, relief="groove")
album_art_label.grid(row=0, column=0, rowspan=3)

# Now playing title - bold and big
song_label = tk.Label(frame, text="Loading Song...", font=("Helvetica Neue", 18, "bold"), fg="white", bg="#121212", wraplength=250, justify="left")
song_label.grid(row=0, column=1, sticky="w", padx=15)

# Artist label - smaller font and italic
artist_label = tk.Label(frame, text="", font=("Helvetica Neue", 14, "italic"), fg="#b3b3b3", bg="#121212", wraplength=250, justify="left")
artist_label.grid(row=1, column=1, sticky="w", padx=15, pady=(5,0))

# Buttons frame below
button_frame = tk.Frame(root, bg="#121212")
button_frame.pack(pady=15)

btn_style_args = {"bg": "#1DB954", "fg": "white", "width": 10, "font": ("Helvetica Neue", 12, "bold"), "bd": 0, "activebackground": "#17a74a"}

play_btn = tk.Button(button_frame, text="▶ Play", command=lambda: (sp.start_playback(), update_now_playing()), **btn_style_args)
play_btn.grid(row=0, column=0, padx=5)

pause_btn = tk.Button(button_frame, text="⏸ Pause", command=lambda: (sp.pause_playback(), update_now_playing()), **btn_style_args)
pause_btn.grid(row=0, column=1, padx=5)

next_btn = tk.Button(button_frame, text="⏭ Next", command=lambda: (sp.next_track(), update_now_playing()), **btn_style_args)
next_btn.grid(row=0, column=2, padx=5)

prev_btn = tk.Button(button_frame, text="⏮ Prev", command=lambda: (sp.previous_track(), update_now_playing()), **btn_style_args)
prev_btn.grid(row=0, column=3, padx=5)

def update_now_playing():
    try:
        track = sp.current_playback()
    except:
        song_label.config(text="Error fetching playback")
        artist_label.config(text="")
        album_art_label.config(image="")
        return

    if track and track['item']:
        song_name = track['item']['name']
        artist_name = track['item']['artists'][0]['name']
        song_label.config(text=song_name)
        artist_label.config(text=artist_name)

        images = track['item']['album']['images']
        if images:
            album_url = images[0]['url']
            try:
                response = requests.get(album_url)
                img_data = Image.open(BytesIO(response.content))
                img_data = img_data.resize((200, 200))
                img_tk = ImageTk.PhotoImage(img_data)
                album_art_label.config(image=img_tk)
                album_art_label.image = img_tk
            except:
                album_art_label.config(image='')
                album_art_label.image = None
        else:
            album_art_label.config(image='')
            album_art_label.image = None
    else:
        song_label.config(text="No song is playing")
        artist_label.config(text="")
        album_art_label.config(image='')
        album_art_label.image = None

    root.after(4000, update_now_playing)  # refresh every 4 seconds

update_now_playing()
root.mainloop()
