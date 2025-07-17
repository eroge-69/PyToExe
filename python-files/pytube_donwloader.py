from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

# Specify download directory (optional)
download_path = os.path.expanduser("D:/UPDATE LAGU/REQUES")  # Example: Download folder

# Read URLs from file
with open('listdownload.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]  # Remove empty lines and whitespace

for url in urls:
    try:
        print(f"Processing URL: {url}")
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Title: {yt.title}")

        ys = yt.streams.get_highest_resolution()
        print(f"Downloading in resolution: {ys.resolution}")
        
        ys.download(output_path=download_path)
        print("✅ Download berhasil..\n")
    
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}\n")
        continue
