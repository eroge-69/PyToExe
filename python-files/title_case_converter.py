import tkinter as tk
from tkinter import messagebox

def title_case(sentence):
    exceptions = {"a", "an", "and", "as", "at", "but", "by", "for", "in",
                  "nor", "of", "on", "or", "so", "the", "to", "up", "yet"}
    words = sentence.lower().split()
    if not words:
        return ""
    titled = [words[0].capitalize()]
    for word in words[1:]:
        titled.append(word if word in exceptions else word.capitalize())
    return " ".join(titled)

def on_paste(event=None):
    # Schedule a small delay so the paste action completes before reading content
    root.after(50, process_text)

def process_text():
    input_text = input_box.get("1.0", tk.END).strip()
    if not input_text:
        clear_output()
        return
    if input_text.lower() == "exit":
        root.destroy()
        return
    result = title_case(input_text)
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, result)
    output_box.tag_add("yellow_text", "1.0", "end")
    output_box.config(state="disabled")

    # Copy to clipboard automatically
    root.clipboard_clear()
    root.clipboard_append(result)

def clear_output():
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")

def reset_all():
    input_box.delete("1.0", tk.END)
    clear_output()

# Root window setup
root = tk.Tk()
root.title("Title Case Converter")
root.geometry("620x470")
root.resizable(False, False)
root.configure(bg="#1e1e1e")  # Very dark background

# Fonts & colors
FONT_MAIN = ("Segoe UI", 14)
FONT_BUTTON = ("Segoe UI", 12, "bold")
COLOR_BG = "#1e1e1e"
COLOR_TEXT = "#e0e0e0"
COLOR_YELLOW = "#f1c40f"
COLOR_BUTTON_BG = "#2d2d2d"
COLOR_BUTTON_HOVER = "#3c3c3c"

# Title Label
title_label = tk.Label(root, text="Paste Your Text Below (paste triggers auto-convert):", font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT)
title_label.pack(pady=(20, 8))

# Input Text box with subtle border
input_box = tk.Text(root, height=6, width=72, font=FONT_MAIN, bg="#2b2b2b", fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
                    relief="flat", bd=0, highlightthickness=2, highlightbackground="#444444", highlightcolor="#666666")
input_box.pack(padx=20, pady=(0, 15))

# Bind Ctrl+V (paste) and right-click paste
input_box.bind("<Control-v>", on_paste)
input_box.bind("<<Paste>>", on_paste)  # Handles some systems' paste event

# Button frame for layout (only Reset button now)
button_frame = tk.Frame(root, bg=COLOR_BG)
button_frame.pack(pady=(0, 15))

# Reset button for clearing both boxes
reset_button = tk.Button(button_frame, text="Reset", command=reset_all,
                         font=FONT_BUTTON, bg=COLOR_BUTTON_BG, fg=COLOR_TEXT, activebackground=COLOR_BUTTON_HOVER,
                         activeforeground=COLOR_TEXT, relief="flat", bd=0, padx=14, pady=8, cursor="hand2")
reset_button.pack()

# Separator line
separator = tk.Frame(root, height=2, bg="#444444", bd=0)
separator.pack(fill="x", padx=20, pady=(0,15))

# Output Text box
output_box = tk.Text(root, height=8, width=72, font=FONT_MAIN, bg="#2b2b2b", fg=COLOR_YELLOW, insertbackground=COLOR_YELLOW,
                     relief="flat", bd=0, highlightthickness=2, highlightbackground="#444444", highlightcolor="#666666",
                     state="disabled")
output_box.pack(padx=20, pady=(0,20))

# Define a tag for yellow text coloring
output_box.tag_configure("yellow_text", foreground=COLOR_YELLOW)

root.mainloop()
