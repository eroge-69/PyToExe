import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import threading
import time
import os

# Messages shown in popups
messages = [
    "Are you blushing?",
    "Caught you staring 😳",
    "Too hot for your GPU!",
    "System overheating!",
    "Warning: Simping detected.",
    "This is... art, right?",
    "Waifu.exe has launched."
]

# Fake progress messages
fake_tasks = [
    "Installing Anime Viewer...",
    "Downloading Waifus...",
    "Boosting Fan Speed...",
    "Scanning for Best Girl...",
    "Loading... Senpai Mode",
    "Compiling Moe Core...",
    "Injecting Kawaii.dll..."
]

# Load all image files from images/ folder
def load_image_files():
    image_folder = os.path.join(os.path.dirname(__file__), "images")
    if not os.path.exists(image_folder):
        return []
    files = os.listdir(image_folder)
    return [os.path.join(image_folder, f) for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

image_files = load_image_files()

def show_explosion():
    boom = tk.Toplevel(root)
    boom.title("💥 BOOM 💥")
    boom.geometry("400x200")
    boom.configure(bg="black")
    boom.attributes("-topmost", True)
    label = tk.Label(boom, text="💥 SYSTEM OVERLOAD 💥", font=("Impact", 24), fg="red", bg="black")
    label.pack(expand=True)
    boom.after(4000, boom.destroy)

def start_popup_spam():
    def create_popup():
        popup = tk.Toplevel(root)
        popup.title("Anime Alert!")
        popup.geometry(f"300x300+{random.randint(0, 1000)}+{random.randint(0, 600)}")
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        frame = tk.Frame(popup, bg="white")
        frame.pack(fill="both", expand=True)

        if image_files:
            img_path = random.choice(image_files)
            img = Image.open(img_path).resize((200, 200))
            tk_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(frame, image=tk_img, bg="white")
            img_label.image = tk_img
            img_label.pack(pady=5)

        msg_label = tk.Label(frame, text=random.choice(messages), font=("Comic Sans MS", 12), bg="white")
        msg_label.pack()

        popup.bind("<Button-1>", lambda e: popup.destroy())

    def spam_loop():
        while True:
            time.sleep(random.uniform(0.4, 0.8))  # faster popups
            root.after(0, create_popup)

    threading.Thread(target=spam_loop, daemon=True).start()

def start_fake_progress():
    def run_progress():
        progress_value = 0
        while progress_value < 100:
            progress_value += random.randint(5, 10)
            progress_value = min(progress_value, 100)
            progress["value"] = progress_value
            status_label.config(text=random.choice(fake_tasks))
            time.sleep(0.3)
        root.after(0, show_explosion)
        time.sleep(4.5)
        root.after(0, start_popup_spam)

    threading.Thread(target=run_progress, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("System Task - Please Wait")
root.geometry("400x150")
root.resizable(False, False)
root.attributes("-topmost", True)

status_label = tk.Label(root, text="Preparing...", font=("Arial", 12))
status_label.pack(pady=10)

progress = ttk.Progressbar(root, length=300, mode='determinate')
progress.pack(pady=20)

start_fake_progress()
root.mainloop()
