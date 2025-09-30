import customtkinter as ctk
from pytubefix import Playlist, YouTube
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import os
import subprocess
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

videos = []
output_dir = os.getcwd()
playlist_url = "https://www.youtube.com/playlist?list=PLRdw3IjKY2gm_kWGipAwvtAe94ukc-5j1"

def fetch_playlist(url):
    return Playlist(url)

def download_streams(video, resolution, progress_callback):
    if resolution == "Auto":
        video_stream = video.streams.filter(file_extension='mp4', progressive=False).order_by('resolution').desc().first()
        resolution = video_stream.resolution if video_stream else "360p"
    else:
        video_stream = video.streams.filter(file_extension='mp4', resolution=resolution, progressive=False).order_by('fps').desc().first()

    audio_stream = video.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()

    if not video_stream or not audio_stream:
        status_label.configure(text="Desired resolution not available. Try another.", text_color="orange")
        return

    video_path = os.path.join(output_dir, "temp_video.mp4")
    audio_path = os.path.join(output_dir, "temp_audio.mp4")
    output_path = os.path.join(output_dir, "current_highlight_video.mp4")

    video_stream.download(output_path=output_dir, filename="temp_video.mp4")
    audio_stream.download(output_path=output_dir, filename="temp_audio.mp4")

    progress_callback(0.9)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(video_path)
    os.remove(audio_path)

    progress_callback(1.0)

def download_thumbnail(video):
    response = requests.get(video.thumbnail_url)
    img = Image.open(BytesIO(response.content))
    upscaled = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    upscaled.save(os.path.join(output_dir, "current_cover_image.png"))
    return upscaled

def update_progress(value):
    progress_bar.set(value)

def start_download_thread():
    thread = threading.Thread(target=download_selected_game)
    thread.start()

def download_selected_game():
    selected_title = game_selector.get()
    selected_res = resolution_selector.get()
    if not selected_title or not selected_res:
        status_label.configure(text="Please select a game and resolution", text_color="red")
        return

    try:
        selected_video = next(video for video in videos if video.title == selected_title)
        status_label.configure(text=f"Downloading: {selected_video.title}", text_color="yellow")
        progress_bar.set(0)
        download_streams(selected_video, selected_res, update_progress)
        download_thumbnail(selected_video)
        status_label.configure(text="Download complete!", text_color="green")
    except Exception as e:
        status_label.configure(text=f"Error: {str(e)}", text_color="red")

def load_week():
    global playlist_url
    playlist_url = url_entry.get()
    try:
        status_label.configure(text="Loading highlights...", text_color="yellow")
        playlist = fetch_playlist(playlist_url)
        global videos
        videos = list(playlist.videos)
        titles = [video.title for video in videos]
        game_selector.configure(values=titles)
        game_selector.set("Select Game")
        resolution_selector.set("")
        thumbnail_canvas.configure(image=None)
        file_size_label.configure(text="")
        status_label.configure(text="Playlist loaded. Select a game.", text_color="white")
    except Exception as e:
        status_label.configure(text=f"Error loading playlist: {str(e)}", text_color="red")

def preview_game():
    selected_title = game_selector.get()
    if not selected_title or not videos:
        status_label.configure(text="No game selected or videos not loaded.", text_color="red")
        return

    try:
        selected_video = next(video for video in videos if video.title == selected_title)

        # Thumbnail preview
        response = requests.get(selected_video.thumbnail_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((300, 170), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        thumbnail_canvas.configure(image=tk_img)
        thumbnail_canvas.image = tk_img

        # Resolution options
        available_streams = selected_video.streams.filter(file_extension='mp4', progressive=False).order_by('resolution').desc()
        resolutions = ["Auto"] + list({stream.resolution for stream in available_streams if stream.resolution})
        resolution_selector.configure(values=resolutions)
        resolution_selector.set("Auto")

        # File size preview
        update_file_size(selected_video, "Auto")

        status_label.configure(text="Preview loaded.", text_color="white")

    except Exception as e:
        status_label.configure(text=f"Error previewing game: {str(e)}", text_color="red")

def update_file_size(video, resolution):
    try:
        if resolution == "Auto":
            stream = video.streams.filter(file_extension='mp4', progressive=False).order_by('resolution').desc().first()
        else:
            stream = video.streams.filter(file_extension='mp4', resolution=resolution, progressive=False).order_by('fps').desc().first()
        file_size = stream.filesize if stream else 0
        mb_size = round(file_size / (1024 * 1024), 2)
        file_size_label.configure(text=f"Estimated file size: {mb_size} MB")
    except:
        file_size_label.configure(text="")

def on_resolution_change(event=None):
    selected_title = game_selector.get()
    selected_res = resolution_selector.get()
    if not selected_title or not selected_res or not videos:
        return
    try:
        selected_video = next(video for video in videos if video.title == selected_title)
        update_file_size(selected_video, selected_res)
    except:
        pass

def choose_directory():
    global output_dir
    selected = filedialog.askdirectory()
    if selected:
        output_dir = selected
        dir_label.configure(text=f"Output folder: {output_dir}")

# GUI setup
app = ctk.CTk()
app.title("NFL Highlights Downloader")
app.geometry("600x750")

ctk.CTkLabel(app, text="NFL Highlights Downloader", font=("Arial", 20)).pack(pady=10)

url_entry = ctk.CTkEntry(app, width=500, placeholder_text="Enter YouTube playlist URL")
url_entry.insert(0, playlist_url)
url_entry.pack(pady=5)

ctk.CTkButton(app, text="Load Playlist", command=load_week).pack(pady=10)

game_selector = ctk.CTkComboBox(app, values=[], width=500)
game_selector.pack(pady=10)

ctk.CTkButton(app, text="Preview Selected Game", command=preview_game).pack(pady=5)

thumbnail_canvas = ctk.CTkLabel(app, text="")
thumbnail_canvas.pack(pady=10)

resolution_selector = ctk.CTkComboBox(app, values=[], width=200)
resolution_selector.set("Auto")
resolution_selector.pack(pady=10)
resolution_selector.bind("<<ComboboxSelected>>", on_resolution_change)

file_size_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
file_size_label.pack(pady=5)

ctk.CTkButton(app, text="Choose Output Folder", command=choose_directory).pack(pady=10)
dir_label = ctk.CTkLabel(app, text=f"Output folder: {output_dir}", font=("Arial", 12))
dir_label.pack(pady=5)

ctk.CTkButton(app, text="Download Selected Game", command=start_download_thread).pack(pady=20)

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(pady=10)

status_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
status_label.pack(pady=10)

app.mainloop()
