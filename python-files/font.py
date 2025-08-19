import tkinter as tk
from tkinter import ttk
import pyperclip  # for clipboard copy (install with: pip install pyperclip)

# Small caps mapping
small_caps_map = {
    "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ",
    "f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ",
    "k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ",
    "p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ",
    "u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ"
}

def to_small_caps(text: str) -> str:
    return "".join(small_caps_map.get(ch.lower(), ch) for ch in text)

def update_output(*args):
    text = entry.get()
    result.set(to_small_caps(text))

def copy_to_clipboard():
    text = result.get()
    if text:
        pyperclip.copy(text)
        copy_status.set("✅ Copied!")
    else:
        copy_status.set("⚠️ Nothing to copy")

# Tkinter Window
root = tk.Tk()
root.title("Small Caps Generator")
root.geometry("400x250")
root.resizable(False, False)

# Style
style = ttk.Style()
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12))

# Input box
ttk.Label(root, text="Enter your text:").pack(pady=5)
entry = ttk.Entry(root, width=40)
entry.pack(pady=5)

# Output label
result = tk.StringVar()
ttk.Label(root, text="Generated Small Caps:").pack(pady=5)
output_label = ttk.Entry(root, textvariable=result, font=("Arial", 14), width=40, state="readonly")
output_label.pack(pady=5)

# Copy button
copy_status = tk.StringVar()
ttk.Button(root, text="Copy", command=copy_to_clipboard).pack(pady=5)
ttk.Label(root, textvariable=copy_status, font=("Arial", 10)).pack()

# Live update
entry.bind("<KeyRelease>", update_output)

# Run App
root.mainloop()
