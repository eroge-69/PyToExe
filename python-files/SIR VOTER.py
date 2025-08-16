import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Mapping dictionary
remap = {
    "A": "$", "B": "%", "C": "&", "D": "'", "E": "(", "F": ")",
    "G": "*", "H": "+", "I": ",", "J": "-", "K": ".", "L": "/",
    "M": "0", "N": "1", "O": "2", "P": "3", "Q": "4", "R": "5",
    "S": "6", "T": "7", "U": "8", "V": "9", "W": ":", "X": ">",
    "Y": "<", "Z": "=", 

    "a": "D", "b": "E", "c": "F", "d": "G", "e": "H", "f": "I",
    "g": "J", "h": "K", "i": "L", "j": "M", "k": "N", "l": "O",
    "m": "P", "n": "Q", "o": "R", "p": "S", "q": "T", "r": "U",
    "s": "V", "t": "W", "u": "X", "v": "Y", "w": "Z", "x": "[",
    "y": "\\", "z": "]"
}

# Function to convert text
def convert_text():
    input_text = input_box.get("1.0", tk.END).strip()
    output_text = "".join(remap.get(ch, ch) for ch in input_text)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_text)

# GUI setup (modern theme)
root = ttk.Window(themename="cyborg")  # try "flatly", "superhero", etc.
root.title("🔑 Keyboard Code Converter")
root.geometry("700x500")

# Title
title = ttk.Label(root, text="🔑 SNA ADVANCE SEARCH ", font=("Segoe UI", 18, "bold"))
title.pack(pady=15)

# Input box
ttk.Label(root, text="Input Text:", font=("Segoe UI", 14)).pack(anchor="w", padx=20)
input_box = tk.Text(root, height=6, width=70, font=("Consolas", 16), bd=2, relief="solid")
input_box.pack(padx=20, pady=8)

# Convert button
btn_convert = ttk.Button(root, text="Convert →", bootstyle=PRIMARY, command=convert_text)
btn_convert.pack(pady=15)

# Output box
ttk.Label(root, text="Output Text:", font=("Segoe UI", 14)).pack(anchor="w", padx=20)
output_box = tk.Text(root, height=6, width=70, font=("Consolas", 16), bd=2, relief="solid", fg="green")
output_box.pack(padx=20, pady=8)

root.mainloop()
