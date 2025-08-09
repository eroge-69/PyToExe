import uuid
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

# -----------------------------
# License key check
# -----------------------------
def check_license_key():
    VALID_KEY = "7F3B-9A1D-C5E8"  # Set your valid key here
    EXPIRY_DATE = datetime(2025, 8, 11)

    root = tk.Tk()
    root.withdraw()  # Hide main window

    key = simpledialog.askstring("Licentie Verificatie", "Voer je licentiesleutel in:")

    if not key:
        messagebox.showerror("Fout", "Er is geen sleutel ingevoerd. Programma wordt afgesloten.")
        root.destroy()
        exit()

    if key != VALID_KEY:
        messagebox.showerror("Fout", "exprired/unvalid key. Program will be closed.")
        root.destroy()
        exit()

    if datetime.utcnow().date() > EXPIRY_DATE.date():
        messagebox.showerror("Fout", "Licentie verlopen. Programma wordt afgesloten.")
        root.destroy()
        exit()

    root.destroy()

# Run license check before main GUI
check_license_key()

# -----------------------------
# Logic
# -----------------------------
def generate_device_id():
    return {
        "uuid": str(uuid.uuid4()),
        "device_string": f"DEV-{uuid.uuid4().hex[:12].upper()}",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def on_generate():
    d = generate_device_id()
    log.append(d)
    add_item(d)
    update_counter()

def on_clear():
    if messagebox.askyesno("Bevestigen", "Weet je zeker dat je alle gegevens wilt wissen?"):
        for widget in list_frame.winfo_children():
            widget.destroy()
        log.clear()
        update_counter()

def on_save():
    if not log:
        messagebox.showwarning("Leeg", "Er zijn nog geen IDs om op te slaan.")
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".jsonl",
        filetypes=[("JSON Lines", "*.jsonl"), ("Alle bestanden", "*.*")]
    )
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            for entry in log:
                f.write(json.dumps(entry) + "\n")
        messagebox.showinfo("Opgeslagen", f"Bestand opgeslagen naar:\n{filepath}")

def update_counter():
    counter_label.config(text=f"Gegenereerd: {len(log)}")

def on_fivem_cheat():
    messagebox.showinfo("FiveM Cheat", "Soon")

def open_spoofer_window():
    spoofer_win = tk.Toplevel(root)
    spoofer_win.title("FiveM Spoofer")
    spoofer_win.geometry("400x300")
    spoofer_win.configure(bg="#1e1e1e")

    label = tk.Label(spoofer_win, text="Spoofer Interface", fg="#5bc0de", bg="#1e1e1e", font=("Segoe UI", 16, "bold"))
    label.pack(pady=20)

    info = tk.Label(spoofer_win, text="Hier kun je je spoofer functies toevoegen.", fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
    info.pack(pady=10)

    def spoof_action():
        info.config(text="Spoofen bezig... even geduld aub...")
        # na 15 seconden update de tekst
        spoofer_win.after(15000, lambda: info.config(text="Helaas spoofen gefaald error #521"))

    spoof_btn = tk.Button(spoofer_win, text="Spoof", bg="#5bc0de", fg="white", font=("Segoe UI", 12, "bold"),
                          command=spoof_action)
    spoof_btn.pack(pady=20)

def on_fivem_spoofer():
    open_spoofer_window()

def add_item(data):
    frame = tk.Frame(list_frame, bg="#242424", pady=10)
    frame.pack(fill="x", padx=10, pady=5)

    icon = tk.Label(frame, text="🖥️", bg="#242424", fg="#4a90e2", font=("Segoe UI", 20))
    icon.pack(side="left", padx=(5,15))

    text_frame = tk.Frame(frame, bg="#242424")
    text_frame.pack(side="left", fill="x", expand=True)

    name_label = tk.Label(text_frame, text="Device ID Simulator", fg="white", bg="#242424", font=("Segoe UI", 14, "bold"))
    name_label.pack(anchor="w")

    expiry = data["timestamp"].split("T")[0]
    expiry_label = tk.Label(text_frame, text=f"Generated: {expiry}", fg="#5ac8fa", bg="#242424", font=("Segoe UI", 10))
    expiry_label.pack(anchor="w")

    cheat_btn = tk.Button(frame, text="FiveM Cheat", bg="#d9534f", fg="white", relief="flat", padx=10, pady=5,
                          activebackground="#c9302c", activeforeground="white", font=("Segoe UI", 10, "bold"),
                          command=on_fivem_cheat)
    cheat_btn.pack(side="right", padx=(10,5))

    spoofer_btn = tk.Button(frame, text="FiveM Spoofer", bg="#5bc0de", fg="white", relief="flat", padx=10, pady=5,
                            activebackground="#31b0d5", activeforeground="white", font=("Segoe UI", 10, "bold"),
                            command=on_fivem_spoofer)
    spoofer_btn.pack(side="right", padx=(10,5))

# -----------------------------
# GUI setup
# -----------------------------
root = tk.Tk()
root.title("Device ID Simulator - Modern Style")
root.geometry("600x500")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

header = tk.Label(root, text="DEVICE ID SIMULATOR", fg="#4a90e2", bg="#1e1e1e", font=("Segoe UI", 16, "bold"))
header.pack(pady=(15, 10))

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=(0, 15))

btn_style = {
    "bg": "#4a90e2",
    "fg": "white",
    "activebackground": "#357ABD",
    "activeforeground": "white",
    "relief": "flat",
    "font": ("Segoe UI", 10, "bold"),
    "padx": 15,
    "pady": 5,
    "bd": 0,
    "width": 15,
}

fivem_cheat_btn = tk.Button(btn_frame, text="FiveM Cheat", command=on_fivem_cheat, **btn_style)
fivem_cheat_btn.grid(row=0, column=0, padx=5)

fivem_spoofer_btn = tk.Button(btn_frame, text="FiveM Spoofer", command=on_fivem_spoofer, **btn_style)
fivem_spoofer_btn.grid(row=0, column=1, padx=5)

counter_label = tk.Label(root, text="Gegenereerd: 0", font=("Segoe UI", 12, "bold"), fg="white", bg="#1e1e1e")
counter_label.pack(pady=(0, 10))

canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
list_frame = tk.Frame(canvas, bg="#1e1e1e")

list_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=list_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True, padx=(10,0))
scrollbar.pack(side="right", fill="y")

log = []

root.mainloop()
