import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog

def download_songs_from_list(txt_path):
    # Ask user to select folder first
    root = tk.Tk()
    root.withdraw()
    download_folder = filedialog.askdirectory(title="Select Download Folder")

    if not download_folder:
        print("❌ No folder selected. Exiting...")
        return

    os.makedirs(download_folder, exist_ok=True)

    with open(txt_path, 'r', encoding='utf-8') as file:
        song_names = [line.strip() for line in file if line.strip()]

    while True:
        choice = input("Choose format - (1) MP4 Video or (2) MP3 Audio only: ").strip()
        if choice in ['1', '2']:
            break
        else:
            print("Invalid input. Please enter 1 for MP4 or 2 for MP3.")

    is_mp3 = (choice == '2')
    success_count = 0
    fail_count = 0

    for i, song in enumerate(song_names, start=1):
        print(f"\n[{i}/{len(song_names)}] Downloading: {song}")
        downloaded_flag = {'downloaded': False}

        def hook(d):
            if d.get('status') == 'finished':
                downloaded_flag['downloaded'] = True

        ydl_opts = {
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': False,
            'default_search': 'ytsearch',
            'progress_hooks': [hook],
        }

        if is_mp3:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song])
                if downloaded_flag['downloaded']:
                    print(f"✅ Successfully downloaded: {song}")
                    success_count += 1
                else:
                    print(f"⚠️ No downloadable item found for: {song}")
                    fail_count += 1
        except Exception as e:
            print(f"❌ Failed to download '{song}': {e}")
            fail_count += 1

    print("\n=== Download Summary ===")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed : {fail_count}")

# === Example usage ===
txt_file = r"C:\Users\jqiwo\OneDrive\Documents\Python\Download_Song\song_names.txt"
download_songs_from_list(txt_file)
