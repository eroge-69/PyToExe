import tkinter as tk
from tkinter import ttk
import random
import string
import threading
import time

generated_password = ""  # Will hold the fake password

def generate_fake_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def copy_to_clipboard():
    if generated_password:
        root.clipboard_clear()
        root.clipboard_append(generated_password)
        copy_button.config(text="Copied!", state="disabled")
        root.after(2000, lambda: copy_button.config(text="Copy to Clipboard", state="normal"))

def start_finding():
    username = entry.get().strip()
    if not username:
        return

    main_frame.pack_forget()
    loading_frame.pack()

    def load():
        for i in range(151):
            progress['value'] = i
            percent_label.config(text=f"Loading... {i * 100 // 150}%")
            time.sleep(0.1)
        loading_frame.pack_forget()
        global generated_password
        generated_password = generate_fake_password()
        result_label.config(
            text=f"Password for {username}:\n\n{generated_password}"
        )
        result_frame.pack()

    threading.Thread(target=load).start()

# Setup window
root = tk.Tk()
root.title("Roblox Password Finder")
root.geometry("600x380")
root.resizable(False, False)

FONT_LARGE = ("Arial", 18)
FONT_MEDIUM = ("Arial", 14)
FONT_SMALL = ("Arial", 12)

# Main frame
main_frame = tk.Frame(root)
tk.Label(main_frame, text="Roblox Username:", font=FONT_LARGE).pack(pady=10)
entry = tk.Entry(main_frame, font=FONT_MEDIUM, width=30)
entry.pack(pady=10)
tk.Button(main_frame, text="Start", font=FONT_MEDIUM, command=start_finding).pack(pady=15)
main_frame.pack(pady=30)

# Loading frame
loading_frame = tk.Frame(root)
tk.Label(loading_frame, text="Loading...", font=FONT_LARGE).pack(pady=10)
progress = ttk.Progressbar(loading_frame, orient="horizontal", length=500, mode="determinate", maximum=150)
progress.pack(pady=5)
percent_label = tk.Label(loading_frame, text="Loading... 0%", font=FONT_SMALL)
percent_label.pack()

# Result frame
result_frame = tk.Frame(root)
result_label = tk.Label(result_frame, text="", font=FONT_MEDIUM, justify="center")
result_label.pack(pady=10)
copy_button = tk.Button(result_frame, text="Copy to Clipboard", font=FONT_SMALL, command=copy_to_clipboard)
copy_button.pack()

root.mainloop()



