import tkinter as tk
from tkinter import messagebox, filedialog
import os
import traceback
import datetime
import json

# 🔐 Felhantering & loggning
def log_error(err: Exception, context: str = ""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] FEL i {context}:\n{traceback.format_exc()}\n"
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", "error.log"), "a") as f:
        f.write(msg)
    add_log(f"⛔ FEL i '{context}' – loggad.")

def safe_call(func, context="Okänd", *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error(e, context)
        return None

# 📁 Cache-inställningar med sparning
SETTINGS_FILE = "settings.json"
CACHE_DIR = "cache"

def load_settings():
    global CACHE_DIR
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                CACHE_DIR = json.load(f).get("cache_dir", CACHE_DIR)
        except:
            pass

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"cache_dir": CACHE_DIR}, f)

# 💾 Cache-funktioner
def get_cache_stats():
    if not os.path.exists(CACHE_DIR):
        return 0, 0
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(CACHE_DIR):
        file_count += len(files)
        for f in files:
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return file_count, total_size // (1024 * 1024)

def refresh_stats():
    result = safe_call(get_cache_stats, context="Uppdatera cacheinfo")
    if result:
        files, size = result
        lbl_status.config(text=f"📦 Filer: {files}\n💾 Storlek: {size} MB")
        add_log("🔄 Cache-info uppdaterad")

def clear_cache():
    if messagebox.askyesno("Rensa", f"Rensa innehåll i:\n{CACHE_DIR}?"):
        def rensa():
            for root, dirs, files in os.walk(CACHE_DIR):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                    except:
                        pass
            refresh_stats()
            add_log("🧹 Cache rensad!")
        safe_call(rensa, context="Rensa cache")

def choose_folder():
    global CACHE_DIR
    new_path = filedialog.askdirectory(title="Välj cache-mapp")
    if new_path:
        CACHE_DIR = new_path
        lbl_folder.config(text=f"📁 Mapp: {CACHE_DIR}")
        save_settings()
        refresh_stats()
        add_log(f"📁 Cachemapp satt till: {CACHE_DIR}")

# 🖥️ GUI
load_settings()
root = tk.Tk()
root.title("Lancache GUI – Python Edition")
root.geometry("400x320")

lbl_folder = tk.Label(root, text=f"📁 Mapp: {CACHE_DIR}", wraplength=380)
lbl_folder.pack(pady=6)

btn_choose = tk.Button(root, text="📂 Välj cache-mapp", command=choose_folder)
btn_choose.pack(pady=4)

lbl_status = tk.Label(root, text="Laddar...", font=("Segoe UI", 12))
lbl_status.pack(pady=6)

btn_refresh = tk.Button(root, text="🔄 Uppdatera", command=refresh_stats)
btn_refresh.pack()

btn_clear = tk.Button(root, text="🗑️ Rensa cache", command=clear_cache)
btn_clear.pack(pady=6)

log_frame = tk.LabelFrame(root, text="🔍 Händelser & Logg")
log_frame.pack(fill="both", expand=True, padx=10, pady=8)

log_text = tk.Text(log_frame, height=6, wrap="word", state="normal")
log_text.pack(fill="both", expand=True)

def add_log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text.see(tk.END)

safe_call(refresh_stats, context="Init-statistik")
add_log("✅ Programmet startade")

root.mainloop()