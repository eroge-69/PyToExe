
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Konfiguration
SOURCE_DIR = Path("Y:/complete")
TARGET_DIR = SOURCE_DIR / "Serien"
DUPLICATE_DIR = TARGET_DIR / "Doppelt"
LOG_FILE = Path("dryrun_log.txt")
VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.avi']
DRY_RUN = True  # Auf False setzen für echten Durchlauf

# Log-Daten sammeln
log_entries = []

def sanitize_series_name(name):
    return re.sub(r'^\[.*?\]\s*', '', name).strip()

def get_episode_number(filename):
    match = re.search(r'(folge|ep|episode|e)\s?(\d{1,3})', filename, re.IGNORECASE)
    if match:
        return int(match.group(2))
    return None

def process_directory():
    for root, dirs, files in os.walk(SOURCE_DIR):
        root_path = Path(root)
        if TARGET_DIR in root_path.parents or root_path == TARGET_DIR:
            continue
        video_files = [f for f in files if Path(f).suffix.lower() in VIDEO_EXTENSIONS]
        if not video_files:
            continue
        series_name = sanitize_series_name(root_path.name)
        series_folder = TARGET_DIR / series_name
        if not DRY_RUN:
            series_folder.mkdir(parents=True, exist_ok=True)
            DUPLICATE_DIR.mkdir(parents=True, exist_ok=True)
        for file in video_files:
            file_path = root_path / file
            episode_number = get_episode_number(file)
            if episode_number is not None:
                filename = f"{series_name} - Folge {episode_number:02d}{Path(file).suffix.lower()}"
            else:
                filename = file
            target_path = series_folder / filename
            if target_path.exists():
                duplicate_path = DUPLICATE_DIR / filename
                counter = 1
                while duplicate_path.exists():
                    duplicate_path = DUPLICATE_DIR / f"{duplicate_path.stem} ({counter}){duplicate_path.suffix}"
                    counter += 1
                log_entries.append(f"DOPPELT: {file_path} -> {duplicate_path}")
                if not DRY_RUN:
                    shutil.move(str(file_path), str(duplicate_path))
            else:
                log_entries.append(f"OK:      {file_path} -> {target_path}")
                if not DRY_RUN:
                    shutil.move(str(file_path), str(target_path))

process_directory()

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"Log vom {datetime.now().isoformat()}\n")
    f.write(f"{'DRY RUN' if DRY_RUN else 'ECHTLAUF'}\n\n")
    for entry in log_entries:
        f.write(entry + "\n")
