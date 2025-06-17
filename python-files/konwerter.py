import os
import datetime
import subprocess
import yt_dlp

LINKS_FILE = 'linki.txt'

today = datetime.datetime.today().strftime('%Y-%m-%d')
output_dir = os.path.join(os.getcwd(), today)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def download_youtube_mp3(link, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def download_spotify_playlist(playlist_url, output_dir):
    cmd = [
        "spotdl",
        "--no-cache",
        playlist_url,
        "--output", os.path.join(output_dir, "{artist} - {title}"),
        "--ffmpeg", "ffmpeg",
        "--overwrite", "force",
        "--threads", "5",
        "--log-level", "ERROR"
    ]
    # Uruchom subprocess bez przechwytywania stdout/stderr,
    # by progress bar działał interaktywnie w konsoli
    subprocess.run(cmd, check=True)

def main():
    print("Co chcesz zrobić?")
    print("1 - YouTube -> mp3 (z pliku linki.txt)")
    print("2 - Spotify playlist -> mp3")
    choice = input("Wybierz 1 lub 2: ").strip()

    if choice == "1":
        if not os.path.isfile(LINKS_FILE):
            print(f"Nie znaleziono pliku {LINKS_FILE}")
            return
        with open(LINKS_FILE, 'r') as f:
            links = [line.strip() for line in f if line.strip()]
        for link in links:
            try:
                download_youtube_mp3(link, output_dir)
            except Exception as e:
                print(f"Błąd przy linku {link}: {e}")
    elif choice == "2":
        playlist_url = input("Podaj link do playlisty Spotify: ").strip()
        os.system("cls")
        if playlist_url:
            try:
                download_spotify_playlist(playlist_url, output_dir)
            except Exception as e:
                print(f"Błąd przy pobieraniu playlisty: {e}")
        else:
            print("Nie podano linku.")
    else:
        print("Nieprawidłowy wybór.")

if __name__ == '__main__':
    main()
