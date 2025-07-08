import os, struct, re, subprocess, time, tkinter as tk
from tkinter import messagebox

# Constants
PREFIX = "rustser"
GHUB_EXE = r"C:\Program Files\LGHUB\lghub.exe"
SCRIPT_DST = os.path.expandvars(r"%AppData%\LGHUB\Scripts\macro.lua")
SCRIPT_SRC = "script_template.lua"

# Base85 alphabet
ABC = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"
B85 = {c: i for i, c in enumerate(ABC)}

# Z85 decode
def z85decode(txt):
    if len(txt) % 5 != 0:
        raise ValueError("invalid length")
    out = bytearray()
    for i in range(0, len(txt), 5):
        val = 0
        for c in txt[i:i+5]:
            if c not in B85:
                raise ValueError("invalid char in key")
            val = val * 85 + B85[c]
        out += val.to_bytes(4, "big")
    return out

# Validate licence key
def check_key(key):
    if not key.startswith(PREFIX):
        raise ValueError("invalid prefix")
    raw = z85decode(key[len(PREFIX):])
    if raw[0] != 8 or len(raw) != 8:
        raise ValueError("invalid structure")
    if raw[7] != (raw[0] ^ raw[1] ^ raw[2] ^ raw[3] ^ raw[4] ^ raw[5] ^ raw[6]):
        raise ValueError("invalid checksum")
    uid = struct.unpack("<I", raw[1:5])[0]
    days = struct.unpack("<H", raw[5:7])[0]
    return uid, days

# Patch key into the script
def patch_script(key):
    with open(SCRIPT_SRC, "r", encoding="utf-8") as f:
        lua = f.read()
    lua = re.sub(r'SUPPLIED_KEY%s".-?"' % r"\s*=\s*", f'SUPPLIED_KEY = "{key}"', lua)
    os.makedirs(os.path.dirname(SCRIPT_DST), exist_ok=True)
    with open(SCRIPT_DST, "w", encoding="utf-8") as f:
        f.write(lua)

# Restart G Hub
def restart_ghub():
    subprocess.run(["taskkill", "/F", "/IM", "lghub.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    subprocess.Popen([GHUB_EXE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# GUI Loader
def run_loader():
    key = key_entry.get().strip()
    if not key:
        messagebox.showerror("Missing Key", "Please enter a licence key.")
        return
    try:
        uid, days = check_key(key)
    except Exception as e:
        messagebox.showerror("Invalid Key", str(e))
        return

    try:
        patch_script(key)
        restart_ghub()
        msg = f"Key OK! UID: {uid}, Duration: {'lifetime' if days == 0 else f'{days} days'}\nMacro installed."
        messagebox.showinfo("Success", msg)
    except Exception as e:
        messagebox.showerror("Install Failed", str(e))

# Tkinter GUI
root = tk.Tk()
root.title("Rust Macro Loader")
root.geometry("400x200")
root.configure(bg="#1e1e1e")

tk.Label(root, text="Enter Your Licence Key:", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=15)
key_entry = tk.Entry(root, width=45)
key_entry.pack()

tk.Button(root, text="Inject Macro", command=run_loader).pack(pady=20)
tk.Label(root, text="Your macro will auto-load into G Hub", bg="#1e1e1e", fg="#888888", font=("Arial", 8)).pack()

root.mainloop()
