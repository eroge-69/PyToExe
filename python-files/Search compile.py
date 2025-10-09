import os
import time
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import pyautogui as pag
import psutil

# Made by Xaedhn Waisome
try:
    import keyboard
except ImportError:
    messagebox.showerror("Missing Module", "Please install the 'keyboard' module using 'pip install keyboard'")
    exit(1)

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Word banks
nouns = ["office", "dinner", "camera", "market", "garden"]
verbs = ["jumps", "writes", "calls", "drinks", "paints"]
adjectives = ["happy", "strong", "bright", "quick", "lively"]
misc_words = ["quickly", "yesterday", "bravely", "elegantly", "gracefully"]
articles = ["the", "a"]

def is_edge_running():
    return any(proc.info['name'] == 'msedge.exe' for proc in psutil.process_iter(['name']))

def activate_edge():
    try:
        windows = pag.getWindowsWithTitle('Edge')
        if windows:
            for window in windows:
                if window.isMinimized:
                    window.restore()
                window.activate()
                pag.hotkey('ctrl', 't')
                time.sleep(1)
                return
        else:
            os.startfile(EDGE_PATH)
            time.sleep(5)
    except Exception:
        os.startfile(EDGE_PATH)
        time.sleep(5)

def log_query(query):
    log_path = os.path.expanduser("~/Documents/search_log.txt")
    with open(log_path, "a") as log:
        log.write(query + "\n")

def generate_query(length):
    word_pool = nouns + verbs + adjectives + misc_words + articles
    words = random.choices(word_pool, k=length)
    return " ".join(words).capitalize() + "."

class SearchCompile:
    def __init__(self, root):
        self.root = root
        self.root.title("Xaedhn Waisome Microsoft Rewards Search Compiler")
        self.root.configure(bg="#f0f8ff")
        self.running = False
        self.search_limit = tk.IntVar(value=50)
        self.typing_speed = tk.StringVar(value="Medium")
        self.sentence_length = tk.IntVar(value=10)
        self.new_word = tk.StringVar()

        # Search count
        tk.Label(root, text="Number of Searches:", bg="#f0f8ff", font=("Segoe UI", 11)).pack()
        tk.Entry(root, textvariable=self.search_limit, font=("Segoe UI", 11), width=10).pack(pady=5)

        # Typing speed
        tk.Label(root, text="Typing Speed:", bg="#f0f8ff", font=("Segoe UI", 11)).pack()
        ttk.Combobox(root, textvariable=self.typing_speed, values=["Slow", "Medium", "X-EVENT"], width=10).pack(pady=5)

        # Sentence length
        tk.Label(root, text="Sentence Length:", bg="#f0f8ff", font=("Segoe UI", 11)).pack()
        tk.Scale(root, from_=5, to=20, orient="horizontal", variable=self.sentence_length).pack(pady=5)

        # Add new word
        tk.Label(root, text="Add a Word:", bg="#f0f8ff", font=("Segoe UI", 11)).pack()
        tk.Entry(root, textvariable=self.new_word, font=("Segoe UI", 11), width=20).pack(pady=5)
        tk.Button(root, text="Add to Generator", command=self.add_word, bg="#4682b4", fg="white", font=("Segoe UI", 10)).pack(pady=5)

        # Status and preview
        self.status = tk.Label(root, text="Status: Idle", fg="blue", bg="#f0f8ff", font=("Segoe UI", 11))
        self.status.pack(pady=10)
        self.preview = tk.Label(root, text="", bg="#f0f8ff", font=("Segoe UI", 10), wraplength=300)
        self.preview.pack(pady=5)

        # Start/Stop buttons
        tk.Button(root, text="Start", command=self.start_loop, bg="#32cd32", fg="white", font=("Segoe UI", 11), width=10).pack(pady=5)
        tk.Button(root, text="Stop", command=self.stop_loop, bg="#ff4c4c", fg="white", font=("Segoe UI", 11), width=10).pack(pady=5)

    def add_word(self):
        word = self.new_word.get().strip()
        if word:
            nouns.append(word)
            verbs.append(word)
            adjectives.append(word)
            misc_words.append(word)
            self.new_word.set("")
            messagebox.showinfo("Word Added", f"'{word}' added to generator!")

    def start_loop(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.search_loop, daemon=True).start()
            self.status.config(text="Status: Running", fg="green")

    def stop_loop(self):
        self.running = False
        self.status.config(text="Status: Stopped", fg="red")

    def get_speed(self):
        speed = self.typing_speed.get()
        if speed == "Slow":
            return random.uniform(0.2, 0.4)
        elif speed == "X-EVENT":
            return random.uniform(0.01, 0.05)
        else:
            return random.uniform(0.05, 0.2)

    def search_loop(self):
        count = 0
        previous_queries = set()
        while self.running and count < self.search_limit.get():
            activate_edge()
            pag.hotkey('ctrl', 'l')
            time.sleep(1)
            pag.typewrite(' ')
            query = generate_query(self.sentence_length.get())
            while query in previous_queries:
                query = generate_query(self.sentence_length.get())
            previous_queries.add(query)
            log_query(query)
            self.preview.config(text=f"Searching: {query}")
            self.status.config(text=f"Searching...", fg="#800080")
            for char in query:
                pag.typewrite(char, interval=self.get_speed())
            pag.press("Enter")
            count += 1
            time.sleep(random.uniform(4, 8))
            if random.random() < 0.1:
                time.sleep(random.uniform(10, 20))
        self.running = False
        self.status.config(text="Search: Completed", fg="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchCompile(root)
    root.mainloop()