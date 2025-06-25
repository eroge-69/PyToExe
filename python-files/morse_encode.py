import tkinter as tk
from tkinter import messagebox

# Morse code mapping
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
}

def encode_to_morse(text):
    """Encodes plain text to Morse code."""
    encoded_words = []
    for word in text.upper().split():
        encoded_letters = [MORSE_CODE_DICT.get(letter, '') for letter in word]
        encoded_words.append(' '.join(encoded_letters))
    return ' / '.join(encoded_words)

def encode_action():
    """Action when 'Encode' button is pressed."""
    text = input_box.get()
    if text:
        result = encode_to_morse(text)
        result_box.delete(1.0, tk.END)           # Clear
        result_box.insert(tk.END, result)        # Insert result
    else:
        messagebox.showerror("Error", "Please enter text to encode.")

# Setup the GUI
root = tk.Tk()
root.title("Morse Encoder")
root.geometry("400x300")

title_label = tk.Label(root, text="Morse Encoder", font=("Helvetica", 16))
title_label.pack(pady=10)

input_label = tk.Label(root, text="Enter text:", font=("Helvetica", 12))
input_label.pack()
input_box = tk.Entry(root, width=40)
input_box.pack(pady=5)

encode_button = tk.Button(root, text="Encode", command=encode_action)
encode_button.pack(pady=10)

results_label = tk.Label(root, text="Morse code result:", font=("Helvetica", 12))
results_label.pack()
result_box = tk.Text(root, height=5, width=40)  # ✅ Copyable
result_box.pack(pady=5)

root.mainloop()
