import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

DATA_FILE = "family_profiles.json"

# Load existing data or start fresh
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        profiles = json.load(f)
else:
    profiles = []

def save_profiles():
    with open(DATA_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)

def add_profile():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    relation = relation_entry.get().strip()
    photo = photo_path.get()

    if not name or not age or not relation:
        messagebox.showwarning("⚠️ INPUT ERROR", "All fields must be filled.")
        return

    profiles.append({
        "name": name,
        "age": age,
        "relation": relation,
        "photo": photo
    })

    save_profiles()
    messagebox.showinfo("✅ SUCCESS", f"Profile for {name} saved.")
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    relation_entry.delete(0, tk.END)
    photo_path.set("")

def browse_photo():
    file = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if file:
        photo_path.set(file)

def show_profiles():
    output_window = tk.Toplevel(root)
    output_window.title("🧬 Stored Profiles")
    output_window.configure(bg="black")

    if not profiles:
        tk.Label(output_window, text="No profiles found.", fg="lime", bg="black", font=("Consolas", 12)).pack(pady=20)
        return

    for person in profiles:
        info = (
            f"👤 Name: {person['name']}\n"
            f"🎂 Age: {person['age']}\n"
            f"🧬 Relation: {person['relation']}\n"
            f"🖼️ Photo: {os.path.basename(person['photo']) if person['photo'] else 'None'}\n"
            f"{'-'*30}"
        )
        tk.Label(output_window, text=info, fg="lime", bg="black", justify="left", anchor="w", font=("Consolas", 10)).pack(padx=10, pady=5)

# === GUI SETUP ===
root = tk.Tk()
root.title("👨‍👩‍👧‍👦 Agent Zyron: Family Terminal")
root.geometry("520x500")
root.configure(bg="black")

tk.Label(root, text="⚡ FAMILY PROFILE TERMINAL ⚡", font=("Consolas", 16, "bold"), fg="lime", bg="black").pack(pady=10)

# Entry Fields
def create_label(text):
    tk.Label(root, text=text, font=("Consolas", 10), fg="lime", bg="black").pack(anchor="w", padx=20)

def create_entry(var=None):
    entry = tk.Entry(root, textvariable=var, font=("Consolas", 10), fg="lime", bg="black", insertbackground="lime", width=40)
    entry.pack(pady=2)
    return entry

create_label("👤 Name:")
name_entry = create_entry()

create_label("🎂 Age:")
age_entry = create_entry()

create_label("🧬 Relation:")
relation_entry = create_entry()

create_label("🖼️ Photo Path:")
photo_path = tk.StringVar()
photo_entry = create_entry(photo_path)
tk.Button(root, text="Browse Photo", command=browse_photo, bg="black", fg="lime", font=("Consolas", 9)).pack(pady=5)

# Buttons
tk.Button(root, text="💾 Save Profile", command=add_profile, font=("Consolas", 11), bg="black", fg="lime").pack(pady=10)
tk.Button(root, text="📂 View All Profiles", command=show_profiles, font=("Consolas", 11), bg="black", fg="lime").pack(pady=5)

tk.Label(root, text="© Agent Zyron Secure Terminal", font=("Consolas", 8), fg="green", bg="black").pack(side="bottom", pady=10)

root.mainloop()
