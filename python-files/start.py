import os
import subprocess
import threading
import queue
import time
from datetime import timedelta

# Ordner
INPUT_DIR = r"P:\render"
OUTPUT_DIR = r"P:\render\convert"
FFMPEG_EXE = r"C:\ffmpeg\ffmpeg.exe"

# Encoder-Typen
ENCODERS = {
    "QSV": "hevc_qsv",
    "CUDA": "hevc_nvenc"
}

# Alle MP4-Dateien sammeln
files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".mp4")]
if not files:
    print("❌ Keine Dateien im Render-Ordner gefunden!")
    exit()

# Queue erstellen
file_queue = queue.Queue()
for f in files:
    file_queue.put(f)

# Status-Tracking
status = {"QSV": "", "CUDA": ""}

lock = threading.Lock()

def encode_worker(name, codec):
    global status
    while not file_queue.empty():
        file_name = file_queue.get()
        input_file = os.path.join(INPUT_DIR, file_name)
        output_file = os.path.join(OUTPUT_DIR, file_name)

        with lock:
            status[name] = f"JOB | {file_name}"
            print_status()

        cmd = [
            FFMPEG_EXE, "-y", "-i", input_file,
            "-c:v", codec, "-pix_fmt", "p010le",
            "-b:v", "36M", "-maxrate", "36M", "-bufsize", "72M",
            "-c:a", "aac", "-b:a", "160k",
            "-map_metadata", "0",
            output_file
        ]

        # FFmpeg starten und warten, Ausgabe unterdrücken
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with lock:
            status[name] = f"fertig | {file_name}"
            print_status()
            time.sleep(0.1)
            status[name] = ""  # zurücksetzen nach Fertig

def print_status():
    # Löscht die Konsole-Zeilen und schreibt neuen Status
    print("\rEncoding läuft: ", end="")
    for key in ENCODERS:
        s = status[key] if status[key] else "-"
        print(f"{key}: {s}   ", end="")
    print(end="", flush=True)

# Sicherstellen, dass Output-Ordner existiert
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Stopwatch starten
start_time = time.time()

# Threads starten
threads = []
for name, codec in ENCODERS.items():
    t = threading.Thread(target=encode_worker, args=(name, codec))
    t.start()
    threads.append(t)

# Auf Threads warten
for t in threads:
    t.join()

# Dauer berechnen
elapsed = timedelta(seconds=int(time.time() - start_time))
print(f"\n✅ Alle Dateien fertig!")
print(f"⏱️ Dauer: {elapsed}")
