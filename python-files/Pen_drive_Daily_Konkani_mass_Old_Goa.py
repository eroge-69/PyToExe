import os
import subprocess
import json
import logging
import time
import threading
import sys
import re
import shutil
import platform
from datetime import datetime

# ===== CONFIGURATION =====
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLrRLQnaMm1jGUgtkCOIsA0asB_ydFUjnb"
DOWNLOAD_DIR = "downloads"
TRACK_FILE = "downloaded.txt"
LOG_FILE = "script.log"
REQUIRED_KEYWORDS = ["konkani", "mass"]  # All keywords must appear in title
MAX_RESULTS = 15
# ==========================

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name.strip().replace(" ", "_")[:255]

def load_downloaded_ids():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_downloaded_id(video_id):
    with open(TRACK_FILE, "a") as f:
        f.write(video_id + "\n")

def live_clock(stop_event):
    while not stop_event.is_set():
        now = datetime.now().strftime("%H:%M:%S")
        sys.stdout.write(f"\r⏰ Current time: {now}   ")
        sys.stdout.flush()
        time.sleep(1)

def get_latest_matching_video_info(playlist_url, required_keywords, max_results=15):
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--playlist-end", str(max_results), "-J", playlist_url],
            capture_output=True,
            text=True,
            check=True
        )
        playlist_json = json.loads(result.stdout)
        entries = playlist_json.get("entries", [])

        for entry in entries:
            video_id = entry.get("id")
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            try:
                video_result = subprocess.run(
                    ["yt-dlp", "--dump-json", video_url],
                    capture_output=True,
                    text=True,
                    check=True
                )

                video_data = json.loads(video_result.stdout)
                title = video_data.get('title', '')
                is_live = video_data.get('is_live')
                is_upcoming = (
                    video_data.get('release_timestamp') and
                    datetime.fromtimestamp(video_data['release_timestamp']) > datetime.now()
                )

                if is_live or is_upcoming:
                    log(f"Skipping live or upcoming video: {title}")
                    continue

                if all(keyword.lower() in title.lower() for keyword in required_keywords):
                    return video_id, title, video_data['webpage_url']

            except subprocess.CalledProcessError as ve:
                log(f"Skipping video {video_url} due to error: {ve}")
                continue

        log(f"No matching video found in the playlist.")
        return None, None, None

    except Exception as e:
        logging.error(f"Failed to process playlist: {e}")
        return None, None, None

def download_video_and_audio(video_url, title_safe):
    mp4_path = os.path.join(DOWNLOAD_DIR, f"{title_safe}.mp4")
    mp3_path = os.path.join(DOWNLOAD_DIR, f"{title_safe}.mp3")

    try:
        log(f"\n📥 Downloading video to: {mp4_path}")
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "-o", mp4_path,
            video_url
        ], check=True)

        log(f"🎵 Converting to MP3: {mp3_path}")
        subprocess.run([
            "ffmpeg", "-i", mp4_path,
            "-vn", "-ab", "192k", "-ar", "44100", "-y",
            mp3_path
        ], check=True)

        return mp4_path, mp3_path

    except subprocess.CalledProcessError as e:
        logging.error(f"Error during download/conversion: {e}")
        raise

def detect_pendrives():
    drives = []
    system = platform.system()

    if system == "Windows":
        import string
        from ctypes import windll

        bitmask = windll.kernel32.GetLogicalDrives()
        for i, letter in enumerate(string.ascii_uppercase):
            if bitmask & (1 << i):
                drive = f"{letter}:/"
                type_drive = windll.kernel32.GetDriveTypeW(f"{letter}:/")
                if type_drive == 2:  # DRIVE_REMOVABLE
                    drives.append(drive)

    elif system in ("Linux", "Darwin"):
        media_root = "/media" if system == "Linux" else "/Volumes"
        if os.path.exists(media_root):
            for user in os.listdir(media_root):
                mount_path = os.path.join(media_root, user)
                if os.path.ismount(mount_path):
                    drives.append(mount_path)

    return drives

def copy_to_pendrives(files):
    pendrives = detect_pendrives()
    if not pendrives:
        log("⚠️ No pendrives detected.")
        return

    for drive in pendrives:
        for file in files:
            try:
                dest_path = os.path.join(drive, os.path.basename(file))
                shutil.copy2(file, dest_path)
                log(f"✅ Copied {file} → {dest_path}")
            except Exception as e:
                log(f"❌ Failed to copy to {drive}: {e}")

def main():
    start_time = time.time()
    log(f"===== Script started: {datetime.now()} =====")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    stop_event = threading.Event()
    clock_thread = threading.Thread(target=live_clock, args=(stop_event,))
    clock_thread.start()

    try:
        downloaded_ids = load_downloaded_ids()
        video_id, title, video_url = get_latest_matching_video_info(PLAYLIST_URL, REQUIRED_KEYWORDS, MAX_RESULTS)

        if not video_id or not title or not video_url:
            log("\nNo eligible video found. Exiting.")
            return

        if video_id in downloaded_ids:
            log("\nVideo already downloaded. Skipping.")
            return

        title_safe = sanitize_filename(title)
        mp4_path, mp3_path = download_video_and_audio(video_url, title_safe)
        save_downloaded_id(video_id)

        log("\nCopying files to pendrives...")
        copy_to_pendrives([mp4_path, mp3_path])

        log("\n✅ Download and transfer completed.")

    except Exception as e:
        log(f"\n❌ Script error: {e}")

    finally:
        stop_event.set()
        clock_thread.join()

    elapsed = time.time() - start_time
    log(f"\n===== Script finished: {datetime.now()} | Elapsed time: {elapsed:.2f} seconds =====\n")

if __name__ == "__main__":
    main()
