import subprocess
import tkinter as tk
from tkinter import filedialog
import re
import os

def adb_getprop_all():
    try:
        res = subprocess.run(["adb", "shell", "getprop"], capture_output=True, text=True, timeout=10)
        return res.stdout
    except Exception as e:
        print("❌ Gagal membaca getprop:", e)
        return ""

def parse_props(text):
    props = {}
    for line in text.splitlines():
        match = re.match(r"\[(.+?)\]: \[(.*?)\]", line)
        if match:
            key, val = match.groups()
            props[key] = val
    return props

def detect_software(props):
    if "ro.coloros.version" in props:
        return f"ColorOS {props['ro.coloros.version']}"
    if "ro.build.version.opporom" in props:
        return f"ColorOS {props['ro.build.version.opporom']}"
    if "ro.miui.ui.version.name" in props:
        return f"MIUI {props['ro.miui.ui.version.name']}"
    if "ro.build.version.oneui" in props:
        return f"One UI {props['ro.build.version.oneui']}"
    if "ro.build.version.emui" in props:
        return f"EMUI {props['ro.build.version.emui']}"
    return props.get("ro.build.display.id", "Android OS")

def is_device_connected():
    try:
        res = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        return any("\tdevice" in line for line in res.stdout.strip().splitlines())
    except:
        return False

def get_metadata_from_adb():
    print("📡 Mendeteksi metadata dari perangkat...")
    raw = adb_getprop_all()
    props = parse_props(raw)

    brand = props.get("ro.product.brand", "").strip()
    model = props.get("ro.product.model", "").strip()
    software = detect_software(props).strip()
    device_name = f"{brand} {model}".strip()

    if not brand or not model:
        return None  # Metadata tidak lengkap

    return {
        "title": f"Recorded with {device_name} Camera",
        "encoder": device_name,
        "make": device_name,
        "model": model,
        "software": software
    }

def get_metadata_fallback():
    print("✏️  Masukkan metadata manual:")
    title = input("Judul metadata [default: Recorded with Android Camera]: ") or "Recorded with Android Camera"
    encoder = input("Encoder [default: Android Device]: ") or "Android Device"
    brand = input("Merk perangkat [default: Android]: ") or "Android"
    model = input("Model perangkat [default: Unknown]: ") or "Unknown"
    software = input("Software [default: Android OS]: ") or "Android OS"

    return {
        "title": title.strip(),
        "encoder": encoder.strip(),
        "make": brand.strip(),
        "model": model.strip(),
        "software": software.strip()
    }

# ─── GUI Picker ───
tk.Tk().withdraw()
input_file = filedialog.askopenfilename(
    title="Pilih video yang ingin diubah",
    filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.flv"), ("All Files", "*.*")]
)
if not input_file:
    print("❌ Tidak ada file dipilih.")
    exit()

# Nama file output
output_name = input("Masukkan nama file output (tanpa ekstensi): ").strip()
if not output_name:
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_name = base_name + "_edited"
output_file = output_name + ".mp4"

# ─── Ambil metadata ───
if is_device_connected():
    meta = get_metadata_from_adb()
    if not meta:
        print("⚠️ Metadata tidak lengkap, gunakan input manual.")
        meta = get_metadata_fallback()
else:
    print("⚠️ Tidak ada perangkat ADB terdeteksi, gunakan input manual.")
    meta = get_metadata_fallback()

# Bersihkan metadata (hilangkan karakter aneh)
for k in meta:
    meta[k] = meta[k].replace('"', '').replace("'", '').strip()
    if not meta[k]:
        meta[k] = "Unknown"

# ─── Perintah FFmpeg ───
command = [
    "ffmpeg", "-y",
    "-i", input_file,
    "-vf", "fps=30,scale=720:1280",
    "-r", "30",
    "-c:v", "libx264",
    "-preset", "faster",
    "-x264-params", "nal-hrd=cbr:force-cfr=1",
    "-b:v", "2500k",
    "-minrate", "2500k",
    "-maxrate", "2500k",
    "-bufsize", "5000k",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "160k",
    "-ar", "44100",
    "-metadata", f"title={meta['title']}",
    "-metadata", f"encoder={meta['encoder']}",
    "-metadata", f"make={meta['make']}",
    "-metadata", f"model={meta['model']}",
    "-metadata", f"software={meta['software']}",
    "-metadata:s:v", "rotate=90",
    "-movflags", "+faststart+use_metadata_tags",
    output_file
]

# Jalankan FFmpeg
print("\n🎬 Menjalankan proses FFmpeg...\n")
res = subprocess.run(command)

if res.returncode == 0 and os.path.exists(output_file):
    print(f"\n✅ Video berhasil dibuat dan metadata disematkan:\n📁 {output_file}")
else:
    print("❌ FFmpeg gagal memproses video.")
