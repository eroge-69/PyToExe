import tkinter as tk
from tkinter import messagebox
import threading
import random
import time

# === Sign-Up Window ===

def show_signup_window():
    signup = tk.Tk()
    signup.title("Nitro Generator V1")
    signup.configure(bg="black")
    signup.geometry("400x300")

    tk.Label(signup, text="Nitro Generator V1", font=("Arial", 18), fg="white", bg="black").pack(pady=20)

    tk.Label(signup, text="Username", fg="white", bg="black").pack()
    username_entry = tk.Entry(signup)
    username_entry.pack()

    tk.Label(signup, text="Password", fg="white", bg="black").pack()
    password_entry = tk.Entry(signup, show="*")
    password_entry.pack()

    def on_signup():
        if username_entry.get() and password_entry.get():
            signup.destroy()
            threading.Thread(target=show_loading_window).start()
        else:
            messagebox.showerror("Error", "Please fill in both fields")

    tk.Button(signup, text="Sign Up", command=on_signup).pack(pady=20)
    signup.mainloop()

# === Loading Screen ===

def show_loading_window():
    loading = tk.Tk()
    loading.title("Loading...")
    loading.geometry("500x300")

    label = tk.Label(loading, text="", font=("Arial", 20, "bold"))
    label.pack(expand=True)

    loading_texts = ["Loading...", "Loading The Asset...", "Creating the Acc", "Done."]
    text_index = 0

    def random_color():
        return "#%06x" % random.randint(0, 0xFFFFFF)

    def random_bg():
        return random.choice(["black", "white"])

    def update_label():
        nonlocal text_index
        if text_index < len(loading_texts):
            label.config(text=loading_texts[text_index], fg=random_color(), bg=random_bg())
            loading.config(bg=label["bg"])
            text_index += 1
            loading.after(800, update_label)
        else:
            loading.destroy()
            show_bsod()

    update_label()
    loading.mainloop()

# === Fake Blue Screen ===

def show_bsod():
    bsod = tk.Tk()
    bsod.attributes("-fullscreen", True)
    bsod.attributes("-topmost", True)
    bsod.configure(bg="blue")
    bsod.title("Critical Error")

    bsod_text = """A problem has been detected and Windows has been shut down to prevent damage
to your computer.

The problem seems to be caused by the following file: DISCORD_NITRO.EXE

PAGE_FAULT_IN_NONPAGED_AREA

*** STOP: 0x00000050 (0xFFFFF880009AA000, 0x0000000000000000, 0xFFFFF80002ACD123, 0x0000000000000005)
"""

    label = tk.Label(bsod, text=bsod_text, fg="white", bg="blue", font=("Consolas", 14), justify="left")
    label.pack(padx=40, pady=40, anchor="nw")

    def proceed():
        bsod.destroy()
        show_rainbow_screen()

    bsod.after(3000, proceed)
    bsod.mainloop()

# === Rainbow Blocks Screen ===

def show_rainbow_screen():
    screen = tk.Tk()
    screen.attributes("-fullscreen", True)
    screen.attributes("-topmost", True)
    screen.configure(bg="black")
    screen.title("Virus Mode")

    width = screen.winfo_screenwidth()
    height = screen.winfo_screenheight()

    def random_color():
        return "#%06x" % random.randint(0, 0xFFFFFF)

    def place_block():
        x = random.randint(0, width - 50)
        y = random.randint(0, height - 50)
        size = random.randint(30, 70)

        block = tk.Frame(screen, bg=random_color(), width=size, height=size)
        block.place(x=x, y=y)

        screen.after(100, place_block)  # every 0.1s

    def on_key(event):
        if event.char.lower() == 'p':
            screen.destroy()

    screen.bind("<Key>", on_key)
    place_block()
    screen.mainloop()

# === Start It All ===
show_signup_window()
