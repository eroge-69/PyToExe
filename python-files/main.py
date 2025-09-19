import os
from yt_dlp import YoutubeDL

# Ask for YouTube link
url = input("Enter the YouTube link: ")

# Ask for format
format_choice = input("Enter the format (mp4/mp3): ").lower()

# Downloads folder
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

# Set yt-dlp options
if format_choice == "mp4":
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),
    }
elif format_choice == "mp3":
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
else:
    print("Invalid format. Please enter 'mp4' or 'mp3'.")
    exit()

# Download the video/audio
try:
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"Download completed! Saved to {downloads_folder}")
except Exception as e:
    print(f"An error occurred: {e}")
