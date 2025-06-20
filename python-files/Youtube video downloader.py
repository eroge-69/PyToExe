from yt_dlp import YoutubeDL

url = input("Enter YouTube video URL: ")

options = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # download best video+audio in mp4
    'outtmpl': '%(title)s.%(ext)s',
    'noplaylist': True  # download only one video, not playlist
}

with YoutubeDL(options) as ydl:
    ydl.download([url])

print("Download completed successfully as MP4!")
