
import tkinter as tk
from tkinter import messagebox

def unicode_to_krutidev(text):
    conversions = [
        ("क्", "d"), ("क", "d"), ("ख", "[k"), ("ग", "x"), ("घ", "X"), ("ङ", "¨"),
        ("च", "p"), ("छ", "P"), ("ज", "N"), ("झ", "t"), ("ञ", ">"), ("ट", "V"),
        ("ठ", "B"), ("ड", "M"), ("ढ", "<"), ("ण", ".k"), ("त", "r"), ("थ", "Fk"),
        ("द", "n"), ("ध", "/k"), ("न", "u"), ("प", "i"), ("फ", "Q"), ("ब", "c"),
        ("भ", "Hk"), ("म", "e"), ("य", ";"), ("र", "j"), ("ल", "y"), ("व", "o"),
        ("श", "'k"), ("ष", '"k'), ("स", "l"), ("ह", "g"), ("अ", "v"), ("आ", "vk"),
        ("इ", "b"), ("ई", "bZ"), ("उ", "m"), ("ऊ", "Å"), ("ए", ","), ("ऐ", "_"),
        ("ओ", ",s"), ("औ", ","), ("ा", "k"), ("ि", "f"), ("ी", "h"), ("ु", "q"),
        ("ू", "w"), ("े", "s"), ("ै", "S"), ("ो", "ks"), ("ौ", "kS"), ("ं", "M"),
        ("ः", "%"), ("्", ""), ("।", "v"), ("ऽ", "~"), ("०", "0"), ("१", "1"),
        ("२", "2"), ("३", "3"), ("४", "4"), ("५", "5"), ("६", "6"), ("७", "7"),
        ("८", "8"), ("९", "9"),
    ]
    for src, tgt in conversions:
        text = text.replace(src, tgt)
    return text

def convert():
    input_text = input_box.get("1.0", tk.END).strip()
    output_text = unicode_to_krutidev(input_text)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_text)

def clear_text():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)

def copy_output():
    output = output_box.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(output)
    messagebox.showinfo("Copied", "KrutiDev output copied to clipboard.")

root = tk.Tk()
root.title("Unicode to KrutiDev Converter")
root.geometry("800x500")
root.configure(bg="#f2f2f2")

tk.Label(root, text="Unicode Hindi Text:", font=("Arial", 12, "bold")).pack(pady=5)
input_box = tk.Text(root, height=8, font=("Mangal", 14))
input_box.pack(padx=10, pady=5, fill=tk.BOTH)

tk.Button(root, text="Convert", command=convert, bg="#4a148c", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Clear", command=clear_text, font=("Arial", 10)).pack(pady=2)

tk.Label(root, text="KrutiDev Output:", font=("Arial", 12, "bold")).pack(pady=5)
output_box = tk.Text(root, height=8, font=("Kruti Dev 010", 14))
output_box.pack(padx=10, pady=5, fill=tk.BOTH)

tk.Button(root, text="Copy Output", command=copy_output, font=("Arial", 10)).pack(pady=5)

root.mainloop()
