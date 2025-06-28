import tkinter as tk
from tkinter import scrolledtext
import colorsys
import random
import os

# Your cipher mappings
char_to_code = {
    'a': '3k2s8d',
    'b': 'm7q4t2',
    'c': '9h3p7x',
    'd': 'z1f9w8',
    'e': '5r0k4a',
    'f': '8x2l7m',
    'g': '4p9t6z',
    'h': 'g7d2k1',
    'i': '1v5w8x',
    'j': 't3h8m2',
    'k': 't3h8m3',
    'l': '6r1a9q',
    'm': 'y2p6k4',
    'n': '0f7x3w',
    'o': '8m2g9b',
    'p': '2z9a5k',
    'q': '7d4w1x',
    'r': '4k3p8v',
    's': '9m2g7t',
    't': '3h8j2q',
    'u': '7v0k5m',
    'v': '6w4p7x',
    'w': '1q9z2d',
    'x': '5r8k3b',
    'y': '2m7w9z',
    'z': '4p2x6q'
}

code_to_char = {v: k for k, v in char_to_code.items()}

symbols = ['#', '^', '~', '*', '_', '/', '!', '@', '$', '%', '&']

HISTORY_FILE = "history.txt"

def encode_message(message):
    words = message.lower().split()
    encoded_words = []

    for word in words:
        # Use comprehension with get for efficiency
        codes = [char_to_code.get(ch, ch) for ch in word]
        start_sym = random.choice(symbols)
        end_sym = random.choice(symbols)
        codes_reversed = list(reversed(codes))
        encoded_word = start_sym + ' '.join(codes_reversed) + end_sym
        encoded_words.append(encoded_word)

    return ' '.join(encoded_words)

def decode_message(encoded_message):
    words = encoded_message.split()
    decoded_words = []

    for word in words:
        if len(word) < 2:
            continue
        core = word[1:-1]
        codes = core.split()
        codes = list(reversed(codes))
        # Use comprehension with get for efficiency
        decoded_chars = [code_to_char.get(code, '?') for code in codes]
        decoded_word = ''.join(decoded_chars)
        decoded_words.append(decoded_word)

    return ' '.join(decoded_words)

def generate_brightness_rainbow():
    hue_steps = 100
    hue_start = 0.0
    hue_end = 1.0
    hue_increment = (hue_end - hue_start) / hue_steps
    brightness_levels = [0.3, 0.5, 0.7, 0.9, 1.0]
    brightness_index = 0
    direction = 1
    colors = []

    for i in range(hue_steps):
        hue = hue_start + i * hue_increment
        brightness = brightness_levels[brightness_index]
        rgb = colorsys.hsv_to_rgb(hue, 1.0, brightness)
        rgb_int = tuple(int(c * 255) for c in rgb)
        hex_color = '#%02x%02x%02x' % rgb_int
        colors.append(hex_color)

        # Update brightness index for next iteration
        if brightness_index == 0:
            direction = 1
        elif brightness_index == len(brightness_levels) - 1:
            direction = -1
        brightness_index += direction

    return colors

def rainbow_brightness_bg():
    colors = generate_brightness_rainbow()
    def cycle(index=0):
        root.config(bg=colors[index % len(colors)])
        label_input.config(bg=colors[index % len(colors)])
        label_output.config(bg=colors[index % len(colors)])
        history_label.config(bg=colors[index % len(colors)])
        btn_frame.config(bg=colors[index % len(colors)])
        root.after(100, cycle, index + 1)
    cycle()

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return f.read()
    return ""

def save_history():
    content = history_box.get("1.0", tk.END)
    with open(HISTORY_FILE, 'w') as f:
        f.write(content)

def delete_history_file():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# Tkinter setup
root = tk.Tk()
root.title("TKKCsEncryption")
root.geometry("800x600")

# Start rainbow background
rainbow_brightness_bg()

# Input label and text box
label_input = tk.Label(root, text="Input Message:")
label_input.pack(pady=5)

input_text = scrolledtext.ScrolledText(root, height=6, width=80)
input_text.pack(pady=5)

# Output label and text box
label_output = tk.Label(root, text="Output Message:")
label_output.pack(pady=5)

output_text = scrolledtext.ScrolledText(root, height=6, width=80)
output_text.pack(pady=5)

# History label and box
history_label = tk.Label(root, text="Encryption History:")
history_label.pack(pady=5)

history_box = scrolledtext.ScrolledText(root, height=8, width=80)
history_box.pack(pady=5)

# Load previous history at startup
history_box.insert(tk.END, load_history())

# Button functions
def encrypt():
    msg = input_text.get("1.0", tk.END).strip()
    if msg:
        encrypted = encode_message(msg)
        # Add to history
        history_box.insert(tk.END, encrypted + "\n")
        # Show in output
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, encrypted)

def decrypt():
    msg = input_text.get("1.0", tk.END).strip()
    if msg:
        decrypted = decode_message(msg)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, decrypted)

def reset():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

def save_and_exit():
    save_history()
    root.destroy()

def clear_history():
    # Clear history box and delete the file
    history_box.delete("1.0", tk.END)
    delete_history_file()

# Buttons
btn_frame = tk.Frame(root, bg=root['bg'])
btn_frame.pack(pady=10)

encrypt_btn = tk.Button(btn_frame, text="Encrypt", command=encrypt, width=15)
encrypt_btn.pack(side=tk.LEFT, padx=10)

decrypt_btn = tk.Button(btn_frame, text="Decrypt", command=decrypt, width=15)
decrypt_btn.pack(side=tk.LEFT, padx=10)

reset_btn = tk.Button(btn_frame, text="Reset", command=reset, width=15)
reset_btn.pack(side=tk.LEFT, padx=10)

clear_hist_btn = tk.Button(btn_frame, text="Clear History", command=clear_history, width=15)
clear_hist_btn.pack(side=tk.LEFT, padx=10)

# Save history on closing
root.protocol("WM_DELETE_WINDOW", save_and_exit)

root.mainloop()