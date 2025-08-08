import webbrowser
import subprocess
import os

# Path to Chrome (update if different)
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# YouTube URL
youtube_url = "https://www.youtube.com"

# Check if Chrome exists
if os.path.exists(chrome_path):
    subprocess.Popen([chrome_path, youtube_url])
else:
    webbrowser.open(youtube_url)
