import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
from datetime import datetime

dark_mode = True
results_cache = []

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def apply_theme():
    bg = "#1e1e1e" if dark_mode else "#ffffff"
    fg = "white" if dark_mode else "black"
    entry_file.configure(bg=bg, fg=fg, insertbackground=fg)
    preview_text.configure(bg=bg, fg=fg, insertbackground=fg)

def extract_cookies_from_line(line, target):
    if target == "Netflix":
        match = re.search(r'NetflixId\s*=\s*([^\s|]+)', line)
        if match:
            return f"NetflixId={match.group(1)}"
    elif target == "Spotify":
        lines = line.splitlines()
        spotify_lines = [l for l in lines if "spotify.com" in l]
        if spotify_lines:
            return '\n'.join(spotify_lines)
    return None

def detect_country(line):
    match = re.search(r'Country\s*=\s*([^\|]+)', line)
    return match.group(1).strip() if match else "Unknown"

def detect_plan(line, target):
    if target == "Netflix":
        match = re.search(r'memberPlan\s*=\s*([^\|]+)', line)
        return match.group(1).strip() if match else "Unknown"
    elif target == "Spotify":
        line = line.lower()
        if "family" in line:
            return "Family"
        if "duo" in line:
            return "Duo"
        if "student" in line:
            return "Student"
        if "premium" in line:
            return "Premium"
    return "Unknown"

def extract_from_file(filepath, target):
    results = []
    countries = set()
    plans = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        accounts = content.split("\n\n")
        for account in accounts:
            cookie = extract_cookies_from_line(account, target)
            if cookie:
                results.append((cookie, detect_country(account), detect_plan(account, target)))
                countries.add(detect_country(account))
                plans.add(detect_plan(account, target))
    return results, countries, plans

def browse_file():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, path)

def browse_folder():
    path = filedialog.askdirectory()
    if path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, path)

def update_preview():
    selected_plan = combo_plan.get()
    preview_text.delete(1.0, tk.END)
    for cookie, _, plan in results_cache:
        if selected_plan == "Auto" or selected_plan == plan:
            preview_text.insert(tk.END, cookie + "\n\n\n")

def save_results_to_txt():
    folder = filedialog.askdirectory(title="Choisir dossier de sortie")
    if not folder:
        return
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(folder, f"cookies_extracted_{now}.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        selected_plan = combo_plan.get()
        for cookie, _, plan in results_cache:
            if selected_plan == "Auto" or selected_plan == plan:
                f.write(cookie + "\n\n\n")
    messagebox.showinfo("Succès", f"Résultats enregistrés dans :\n{output_path}")

def process(is_folder=False):
    global results_cache
    results_cache.clear()
    path = entry_file.get()
    target = combo_target.get()
    if not path or not target:
        messagebox.showerror("Erreur", "Veuillez choisir un fichier/dossier et une plateforme.")
        return

    files = []
    if is_folder:
        for file in os.listdir(path):
            if file.endswith(".txt"):
                files.append(os.path.join(path, file))
    else:
        files.append(path)

    countries = set()
    plans = set()

    for file in files:
        try:
            extracted, ctry, pln = extract_from_file(file, target)
            results_cache.extend(extracted)
            countries.update(ctry)
            plans.update(pln)
        except Exception as e:
            print(f"Erreur avec {file}: {e}")

    if not results_cache:
        messagebox.showinfo("Aucun résultat", "Aucun cookie extrait.")
        return

    combo_country['values'] = ["Auto"] + sorted(countries)
    combo_country.current(0)
    combo_plan['values'] = ["Auto"] + sorted(plans)
    combo_plan.current(0)
    update_preview()

# --- UI ---
root = tk.Tk()
root.title("Cookie Extractor by Med B'es")
root.geometry("850x600")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# Theme
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground="#2e2e2e", background="#2e2e2e", foreground="white")
style.configure("Vertical.TScrollbar", background="#444", troughcolor="#2e2e2e", arrowcolor="white")

tk.Label(root, text="📂 Choisir un fichier ou un dossier contenant des cookies", fg="white", bg="#1e1e1e").pack(pady=10)
entry_file = tk.Entry(root, width=70)
entry_file.pack()

frame_btns = tk.Frame(root, bg="#1e1e1e")
frame_btns.pack(pady=5)
tk.Button(frame_btns, text="Fichier", command=browse_file).grid(row=0, column=0, padx=5)
tk.Button(frame_btns, text="Dossier", command=browse_folder).grid(row=0, column=1, padx=5)
tk.Button(frame_btns, text="Extraire (Fichier)", bg="#4CAF50", fg="white", command=lambda: process(False)).grid(row=0, column=2, padx=5)
tk.Button(frame_btns, text="Extraire (Dossier)", bg="#2196F3", fg="white", command=lambda: process(True)).grid(row=0, column=3, padx=5)
tk.Button(frame_btns, text="🌙 Mode sombre", command=toggle_dark_mode).grid(row=0, column=4, padx=5)

frame_filters = tk.Frame(root, bg="#1e1e1e")
frame_filters.pack(pady=10)
tk.Label(frame_filters, text="Plateforme:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
combo_target = ttk.Combobox(frame_filters, values=["Netflix", "Spotify"], state="readonly", width=15)
combo_target.current(0)
combo_target.grid(row=0, column=1)

tk.Label(frame_filters, text="Pays:", fg="white", bg="#1e1e1e").grid(row=0, column=2, padx=5)
combo_country = ttk.Combobox(frame_filters, values=["Auto"], state="readonly", width=15)
combo_country.current(0)
combo_country.grid(row=0, column=3)

tk.Label(frame_filters, text="Abonnement:", fg="white", bg="#1e1e1e").grid(row=0, column=4, padx=5)
combo_plan = ttk.Combobox(frame_filters, values=["Auto"], state="readonly", width=15)
combo_plan.current(0)
combo_plan.grid(row=0, column=5)

tk.Button(root, text="🔄 Actualiser", bg="#FF9800", fg="white", command=update_preview).pack(pady=5)

# Preview zone
frame_preview = tk.Frame(root)
frame_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
scrollbar = ttk.Scrollbar(frame_preview, orient=tk.VERTICAL)
preview_text = tk.Text(frame_preview, height=15, yscrollcommand=scrollbar.set, wrap=tk.WORD)
scrollbar.config(command=preview_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
preview_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

tk.Button(root, text="💾 Sauvegarder Résultat", bg="#9C27B0", fg="white", command=save_results_to_txt).pack(pady=10)

apply_theme()
root.mainloop()

