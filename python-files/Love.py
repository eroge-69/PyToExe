import tkinter as tk
import os, sys, time
import random

# --- function to spam YAY messages ---
def spam_yay():
    start = time.time()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    while time.time() - start < 10:  # run for 10 seconds
        win = tk.Toplevel()
        win.title("Yay! 💖✨")
        win.geometry("200x80")
        win.attributes("-topmost", True)

        # random position on screen
        x = random.randint(0, screen_width - 200)
        y = random.randint(0, screen_height - 80)
        win.geometry(f"200x80+{x}+{y}")

        tk.Label(win, text="YAY! 💍", font=("Segoe UI", 16)).pack(expand=True)
        win.update()
        win.after(500, win.destroy)  # window lasts 0.5s
        win.update()
        time.sleep(0.2)  # small gap before next popup

# --- main popup function ---
def ask():
    win = tk.Toplevel()
    win.title("Question")
    win.geometry("300x120")
    win.attributes("-topmost", True)
    tk.Label(win, text="Will you marry me? 💍").pack(pady=10)

    def on_yes():
        win.destroy()
        spam_yay()
        self_delete()

    def on_no():
        win.destroy()  # destroy current popup
        ask()          # spawn a new one

    tk.Button(win, text="Yes", command=on_yes).pack(side="left", padx=10, pady=10)
    tk.Button(win, text="No", command=on_no).pack(side="right", padx=10, pady=10)

# --- self-delete function ---
def self_delete():
    file_path = sys.argv[0]
    bat_path = file_path + ".bat"
    with open(bat_path, "w") as f:
        f.write(f"""
@echo off
ping 127.0.0.1 -n 60 > nul
del "{file_path}"
del "%~f0"
""")
    os.startfile(bat_path)

# --- main program ---
root = tk.Tk()
root.withdraw()
ask()
root.mainloop()
