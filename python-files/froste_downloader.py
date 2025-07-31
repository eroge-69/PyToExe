import os
import re
import time
import requests

HTML_FILE = "Updated Lil Uzi Vert Tracker - Google Drive.html"
DOWNLOAD_DIR = "Downloads"
SONG_URL_PATTERN = r"https://music\\.froste\\.lol/song/[a-fA-F0-9]+"

def extract_song_links(html_file):
    links = set()
    with open(html_file, "r", encoding="utf-8") as f:
        for line in f:
            matches = re.findall(SONG_URL_PATTERN, line)
            links.update(matches)
    return list(links)

def download_song(link, download_dir):
    try:
        print(f"Downloading: {link}")
        response = requests.get(link, allow_redirects=True)
        if response.status_code == 200:
            content_disp = response.headers.get("Content-Disposition")
            if content_disp:
                match = re.search(r'filename="?(.*?)(\"|;|$)', content_disp)
                if match:
                    filename = match.group(1).strip()
                else:
                    filename = link.split("/")[-1] + ".mp3"
            else:
                filename = link.split("/")[-1] + ".mp3"

            filepath = os.path.join(download_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Saved to: {filepath}")
        else:
            print(f"Failed to download {link} (status code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {link}: {e}")

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    song_links = extract_song_links(HTML_FILE)
    print(f"Found {len(song_links)} song links.")

    for link in song_links:
        download_song(link, DOWNLOAD_DIR)
        time.sleep(1)

if __name__ == "__main__":
    main()