import os
import json
import shutil
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from PIL import Image
from io import BytesIO
import psutil

SUPPORTED_FORMATS = [".mp3", ".flac", ".m4a", ".aac", ".ogg"]
APPDATA_PATH = os.path.join(os.getenv("APPDATA"), "DAPSyncTool")
SETTINGS_FILE = os.path.join(APPDATA_PATH, "settings.json")
DEFAULT_COVER = os.path.join("assets", "default_cover.jpg")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"source": "", "target": ""}

def save_settings(settings):
    os.makedirs(APPDATA_PATH, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def get_free_space_mb(path):
    drive = os.path.splitdrive(path)[0]
    usage = psutil.disk_usage(drive)
    return usage.free / (1024 * 1024)

def resize_image(image_data):
    img = Image.open(BytesIO(image_data))
    img.thumbnail((500, 500))
    output = BytesIO()
    img.save(output, format="JPEG")
    return output.getvalue()

def embed_album_art(file_path, cover_data):
    ext = os.path.splitext(file_path)[1].lower()
    audio = File(file_path, easy=False)
    if ext == ".mp3" and isinstance(audio, MP3):
        from mutagen.id3 import ID3, APIC, error
        try:
            audio.add_tags()
        except error:
            pass
        audio.tags["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=cover_data
        )
        audio.save()
    elif ext == ".flac" and isinstance(audio, FLAC):
        from mutagen.flac import Picture
        pic = Picture()
        pic.data = cover_data
        pic.type = 3
        pic.mime = "image/jpeg"
        pic.width = pic.height = 500
        audio.clear_pictures()
        audio.add_picture(pic)
        audio.save()
    elif ext in [".m4a", ".aac"] and isinstance(audio, MP4):
        audio["covr"] = [cover_data]
        audio.save()
    elif ext == ".ogg" and isinstance(audio, OggVorbis):
        pass  # OGG embedding optional
    else:
        return

class DAPSyncApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DAP Sync Tool")
        self.geometry("600x400")
        self.settings = load_settings()
        self.create_widgets()

    def create_widgets(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.source_btn = ctk.CTkButton(self, text="Select Source Folder", command=self.choose_source)
        self.source_btn.pack(pady=10)
        self.source_label = ctk.CTkLabel(self, text=self.settings.get("source", ""))
        self.source_label.pack()

        self.target_btn = ctk.CTkButton(self, text="Select Target Folder", command=self.choose_target)
        self.target_btn.pack(pady=10)
        self.target_label = ctk.CTkLabel(self, text=self.settings.get("target", ""))
        self.target_label.pack()

        self.sync_btn = ctk.CTkButton(self, text="SYNC NOW", height=40, width=200, command=self.start_sync)
        self.sync_btn.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.pack(pady=5)
        self.progress.set(0)

        self.logbox = ctk.CTkTextbox(self, height=120, width=560)
        self.logbox.pack(pady=10)

    def choose_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.settings["source"] = folder
            self.source_label.configure(text=folder)
            save_settings(self.settings)

    def choose_target(self):
        folder = filedialog.askdirectory()
        if folder:
            self.settings["target"] = folder
            self.target_label.configure(text=folder)
            save_settings(self.settings)

    def start_sync(self):
        threading.Thread(target=self.sync_files).start()

    def sync_files(self):
        src = self.settings.get("source")
        dst = self.settings.get("target")
        if not src or not dst:
            messagebox.showerror("Error", "Please select both source and target folders.")
            return

        all_files = []
        for root, _, files in os.walk(src):
            for f in files:
                if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS:
                    all_files.append(os.path.join(root, f))

        total_size = sum(os.path.getsize(f) for f in all_files) / (1024 * 1024)
        free_space = get_free_space_mb(dst)
        if free_space < total_size:
            messagebox.showwarning("Warning", "Not enough space on target drive!")
            return

        self.progress.set(0)
        self.logbox.delete("1.0", "end")
        default_cover_data = open(DEFAULT_COVER, "rb").read() if os.path.exists(DEFAULT_COVER) else None

        for i, src_path in enumerate(all_files):
            rel_path = os.path.relpath(src_path, src)
            dst_path = os.path.join(dst, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)

            try:
                audio = File(dst_path)
                has_cover = False
                if audio:
                    if isinstance(audio, MP3) and audio.tags:
                        has_cover = any("APIC" in t for t in audio.tags)
                    elif isinstance(audio, FLAC):
                        has_cover = bool(audio.pictures)
                    elif isinstance(audio, MP4):
                        has_cover = "covr" in audio
                if not has_cover and default_cover_data:
                    embed_album_art(dst_path, resize_image(default_cover_data))
            except Exception as e:
                self.logbox.insert("end", f"[WARN] Failed processing: {src_path}\n")

            self.logbox.insert("end", f"[OK] {rel_path}\n")
            self.progress.set((i + 1) / len(all_files))

        self.logbox.insert("end", "\nSync complete!")