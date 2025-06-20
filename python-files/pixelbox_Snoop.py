
import tkinter as tk
import random
import configparser

def generate_settings():
    entry_values = {
        "PB Shot Radius": random.randint(5, 70),
        "Pixel Count Min": random.randint(3, 80),
        "Pixel Count Max": random.randint(3, 160),
        "Pixel Threshold": random.randint(0, 90),
        "PB Y Offset": random.randint(0, 40),
        "PB X Offset": random.randint(-10, 10),
        "PB Offset Mod": random.randint(5, 25)
    }
    for label, entry in entries.items():
        entry.delete(0, tk.END)
        entry.insert(0, str(entry_values[label]))
    for var in checkboxes.values():
        var.set(random.choice([True, False]))

def save_settings():
    config = configparser.ConfigParser()
    config['PixelBoxSettings'] = {}
    for label, entry in entries.items():
        config['PixelBoxSettings'][label] = entry.get()
    for label, var in checkboxes.items():
        config['PixelBoxSettings'][label] = str(var.get())
    with open("pixelbox_settings.ini", "w") as configfile:
        config.write(configfile)

# Create window
root = tk.Tk()
root.title("PixelBox AimLock v1.0 Created By Snoop")
root.geometry("416x505")
root.resizable(False, False)
root.configure(bg="black")

# Title
title_label = tk.Label(root, text="PixelBox AimLock v1.0", font=("Arial", 14, "bold"), fg="lime", bg="black")
title_label.pack(pady=5)

# Checkboxes
checkboxes = {}
checkbox_texts = [
    "PB Aim Priority", "PB Shoot on Center",
    "Preview Pixel Box", "Force Symmetry"
]
for text in checkbox_texts:
    var = tk.BooleanVar(value=True)
    check = tk.Checkbutton(root, text=text, variable=var, fg="lime", bg="black", selectcolor="black", font=("Arial", 9))
    check.pack(anchor="w", padx=20)
    checkboxes[text] = var

# Entry fields
entries = {}
entry_fields = [
    "PB Shot Radius", "Pixel Count Min", "Pixel Count Max",
    "Pixel Threshold", "PB Y Offset", "PB X Offset", "PB Offset Mod"
]
for field in entry_fields:
    lbl = tk.Label(root, text=field, fg="lime", bg="black", font=("Arial", 9))
    lbl.pack(anchor="w", padx=20)
    ent = tk.Entry(root)
    ent.pack(fill="x", padx=20, pady=1)
    entries[field] = ent

# Buttons
gen_btn = tk.Button(root, text="🔁 GENERATOR", command=generate_settings, bg="lime", fg="black", font=("Arial", 10, "bold"))
gen_btn.pack(fill="x", padx=20, pady=5)

save_btn = tk.Button(root, text="💾 SAVE", command=save_settings, bg="lime", fg="black", font=("Arial", 10, "bold"))
save_btn.pack(fill="x", padx=20)

root.mainloop()
