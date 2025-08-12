import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

CONFIG_FILE = "config.json"

# Wczytaj lub utwórz domyślną konfigurację
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {"fs22_path": ""}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Funkcje
def choose_file():
    file_path = filedialog.askopenfilename(
        title="Wybierz FarmingSimulator2022.exe",
        filetypes=[("Pliki EXE", "*.exe")]
    )
    if file_path:
        config["fs22_path"] = file_path
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        fs22_path_var.set(file_path)

def start_game():
    if not config["fs22_path"] or not os.path.exists(config["fs22_path"]):
        messagebox.showerror("Błąd", "Ścieżka do gry jest niepoprawna!")
        return
    try:
        subprocess.Popen([config["fs22_path"]], shell=True)
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się uruchomić gry:\n{e}")

# GUI
root = tk.Tk()
root.title("🚜 Launcher FS22")
root.geometry("450x250")
root.resizable(False, False)
root.configure(bg="#2b2b2b")

# Style
style = ttk.Style()
style.theme_use("clam")

style.configure("TLabel", background="#2b2b2b", foreground="white", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8)
style.map("TButton",
          background=[("active", "#3c3f41"), ("!active", "#444444")],
          foreground=[("active", "white"), ("!active", "white")])

# Frame główny
frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# Tytuł
title_label = ttk.Label(frame, text="Farming Simulator 22 Launcher", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=(0, 15))

# Etykieta i pole z lokalizacją
ttk.Label(frame, text="Ścieżka do gry:").pack(anchor="w")
fs22_path_var = tk.StringVar(value=config["fs22_path"])
path_entry = ttk.Entry(frame, textvariable=fs22_path_var, width=50, state="readonly", font=("Segoe UI", 10))
path_entry.pack(anchor="w", pady=5)

# Przyciski
btn_frame = ttk.Frame(frame)
btn_frame.pack(pady=15)

choose_btn = ttk.Button(btn_frame, text="📂 Wybierz plik EXE", command=choose_file)
choose_btn.grid(row=0, column=0, padx=5)

start_btn = ttk.Button(btn_frame, text="▶ Uruchom FS22", command=start_game)
start_btn.grid(row=0, column=1, padx=5)

# Stopka
footer = ttk.Label(frame, text="Made by You", font=("Segoe UI", 9))
footer.pack(side="bottom", pady=(15, 0))

root.mainloop()
