import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser
import re

# Türkçe karakterleri İngilizce'ye çevir
def sanitize_filename(text):
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    text = text.translate(tr_map)
    return re.sub(r'[\\/*?:"<>|]', "_", text)

plans = {
    "Hafta 1": {
        "Sali - Push": [
            "Dumbbell Floor Press – 4x8-12 | RPE 7",
            "Resistance Band Overhead Press – 3x10-15 | RPE 7",
            "Incline Dumbbell Fly – 3x12-15 | RPE 6-7",
            "Dumbbell Overhead Triceps Extension – 3x10-12 | RPE 7"
        ],
        "Carsamba - Pull": [
            "Barbell Row – 4x8 | RPE 8",
            "Dumbbell One-Arm Row – 3x10 | RPE 7",
            "Barbell Curl – 3x10-12 | RPE 7",
            "Hammer Curl – 2x12-15 | RPE 7",
            "Resistance Band Face Pull – 2x15 | RPE 6"
        ],
        "Persembe - Lower A": [
            "Romanian Deadlift – 4x8-10 | RPE 8",
            "Bulgarian Split Squat – 3x10/leg | RPE 7",
            "Resistance Band Glute Bridge – 3x20 | RPE 7",
            "Standing Calf Raise – 4x15 | RPE 6",
            "Wall Sit – 2x30-45s"
        ],
        "Cumartesi - Core + Recovery": [
            "Deadbug – 3x10 | RPE 6",
            "Plank – 3x45-60s | RPE 7",
            "Bird Dog – 3x10 | RPE 6",
            "Foam Rolling – 10-15dk"
        ],
        "Pazar - Lower B": [
            "Front Squat – 4x8-10 | RPE 8",
            "Goblet Squat – 3x12 | RPE 7",
            "Resistance Band Side Walk – 3x15 | RPE 7",
            "Calf Raise – 3x15 | RPE 6"
        ]
    },
    "Hafta 2": {
        "Sali - Push": [
            "Dumbbell Floor Press – 4x8-10 | RPE 8",
            "Resistance Band Overhead Press – 4x10-12 | RPE 8",
            "Incline Dumbbell Fly – 3x10-12 | RPE 7",
            "Triceps Extension – 3x12-15 | RPE 8"
        ],
        "Carsamba - Pull": [
            "Bent Over Row – 4x8 | RPE 9",
            "One-Arm Row – 3x10 | RPE 8",
            "Curl – 3x10-12 | RPE 8",
            "Hammer Curl Hold – 2x12 + 10s | RPE 8",
            "Face Pull – 2x20 | RPE 6-7"
        ],
        "Persembe - Lower A": [
            "Romanian Deadlift – 4x8 | RPE 9",
            "Bulgarian Split Squat – 3x8-10 | RPE 8",
            "Hip Thrust – 3x15 | RPE 8",
            "Calf Raise (tek bacak) – 3x12 | RPE 7",
            "Wall Sit – 2x60s | RPE 8"
        ],
        "Cumartesi - Core": [
            "Deadbug – 3x12 | RPE 7",
            "Side Plank – 3x30-45s | RPE 8",
            "Bird Dog – 3x12 | RPE 7",
            "Step March – 15 dk",
            "Stretching – 10-12 dk"
        ],
        "Pazar - Lower B": [
            "Front Squat – 4x6-8 | RPE 9",
            "Goblet Squat – 3x10 | RPE 8",
            "Side Walk – 3x12 | RPE 8",
            "Wall Sit – 2x60s | RPE 9",
            "Toe-Elevated Calf Raise – 3x15 | RPE 7"
        ]
    }
}

progress_file = "progress.json"

def load_progress():
    try:
        with open(progress_file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_progress(data):
    with open(progress_file, "w") as f:
        json.dump(data, f)

def export_to_txt(week, day, items):
    safe_day = sanitize_filename(day)
    filename = f"{week}_{safe_day}.txt".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{week} - {day}\n\n")
        for item in items:
            f.write(f"- {item}\n")
    messagebox.showinfo("TXT", f"{filename} kaydedildi.")

def search_gif(text):
    name = text.split("–")[0].strip()
    query = f"{name} gif"
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    webbrowser.open(url)

root = tk.Tk()
root.title("Mesocycle Plan Takip (Tam ve Güvenli)")
root.geometry("750x600")
root.configure(bg="#1e1e1e")

progress = load_progress()

tk.Label(root, text="Hafta Seç:", fg="white", bg="#1e1e1e", font=("Arial", 12)).pack(pady=5)
week_combo = ttk.Combobox(root, values=list(plans.keys()))
week_combo.pack()

tk.Label(root, text="Gün Seç:", fg="white", bg="#1e1e1e", font=("Arial", 12)).pack(pady=5)
day_combo = ttk.Combobox(root)
day_combo.pack()

checkboxes = []

def show_day():
    for cb in checkboxes:
        cb.destroy()
    checkboxes.clear()

    week = week_combo.get()
    day = day_combo.get()
    if not week or not day:
        return

    exercises = plans[week][day]
    p_key = f"{week}::{day}"
    completed = progress.get(p_key, {})

    for idx, ex in enumerate(exercises):
        var = tk.BooleanVar(value=completed.get(str(idx), False))
        frame = tk.Frame(root, bg="#1e1e1e")
        frame.grid(row=10+idx, column=0, sticky="w", padx=20, pady=2)

        cb = tk.Checkbutton(frame, text=ex, variable=var, bg="#1e1e1e", fg="white", anchor="w", selectcolor="#444")
        cb.var = var
        cb.pack(side="left")

        btn = tk.Button(frame, text="🔍", command=lambda e=ex: search_gif(e), bg="#333", fg="white", width=3)
        btn.pack(side="left", padx=5)

        checkboxes.append(cb)

def save_day_progress():
    week = week_combo.get()
    day = day_combo.get()
    if not week or not day:
        messagebox.showwarning("Uyarı", "Lütfen önce hafta ve gün seçiniz.")
        return
    key = f"{week}::{day}"
    progress[key] = {str(i): cb.var.get() for i, cb in enumerate(checkboxes)}
    save_progress(progress)
    messagebox.showinfo("Kaydedildi", f"{key} ilerlemesi kaydedildi.")

def export_day_txt():
    week = week_combo.get()
    day = day_combo.get()
    if not week or not day:
        messagebox.showwarning("Uyarı", "Lütfen önce hafta ve gün seçiniz.")
        return
    if not checkboxes:
        messagebox.showwarning("Uyarı", "Önce bir gün seçip egzersizleri yükleyin.")
        return
    items = [cb.cget("text") for cb in checkboxes]
    export_to_txt(week, day, items)

def update_days(event):
    week = week_combo.get()
    day_combo["values"] = list(plans[week].keys())

week_combo.bind("<<ComboboxSelected>>", update_days)
day_combo.bind("<<ComboboxSelected>>", lambda e: show_day())

tk.Button(root, text="Kaydet", command=save_day_progress).pack(pady=10)
tk.Button(root, text="TXT Olarak Kaydet", command=export_day_txt).pack(pady=5)

root.mainloop()
