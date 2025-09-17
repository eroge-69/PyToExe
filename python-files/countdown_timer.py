import tkinter as tk
from tkinter import font, filedialog, ttk
import pygame
import numpy as np
import platform
import asyncio
import time
from PIL import Image, ImageTk
import io
import base64

class CountdownTimer:
    def __init__(self, root):
        pygame.mixer.init()
        self.root = root
        self.root.title("Countdown Timer")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        self.is_running = False
        self.time_left = 0
        self.bg_image = None
        self.bg_label = None

        # GUI Elements
        self.label = tk.Label(root, text="00:00", font=("Arial", 48), fg="black", bg="#f0f0f0")
        self.label.pack(pady=20)

        self.time_entry = tk.Entry(root, width=5, font=("Arial", 12))
        self.time_entry.insert(0, "60")
        self.time_entry.pack()

        tk.Label(root, text="Seconds", font=("Arial", 10), bg="#f0f0f0").pack()

        # Font settings
        self.font_frame = tk.Frame(root, bg="#f0f0f0")
        self.font_frame.pack(pady=5)
        tk.Label(self.font_frame, text="Font:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.font_var = tk.StringVar(value="Arial")
        self.font_menu = ttk.Combobox(self.font_frame, textvariable=self.font_var, values=font.families(), width=15)
        self.font_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(self.font_frame, text="Size:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="48")
        tk.Entry(self.font_frame, textvariable=self.size_var, width=5).pack(side=tk.LEFT, padx=5)

        tk.Label(self.font_frame, text="Color:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="black")
        self.color_menu = ttk.Combobox(self.font_frame, textvariable=self.color_var, values=["black", "red", "blue", "green", "white"], width=10)
        self.color_menu.pack(side=tk.LEFT, padx=5)

        # Background settings
        self.bg_frame = tk.Frame(root, bg="#f0f0f0")
        self.bg_frame.pack(pady=5)
        tk.Label(self.bg_frame, text="Background:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.bg_color_var = tk.StringVar(value="#f0f0f0")
        self.bg_color_menu = ttk.Combobox(self.bg_frame, textvariable=self.bg_color_var, values=["#f0f0f0", "white", "black", "blue", "green"], width=10)
        self.bg_color_menu.pack(side=tk.LEFT, padx=5)
        tk.Button(self.bg_frame, text="Upload Image", command=self.upload_bg_image).pack(side=tk.LEFT, padx=5)

        # Voice settings
        self.voice_frame = tk.Frame(root, bg="#f0f0f0")
        self.voice_frame.pack(pady=5)
        tk.Label(self.voice_frame, text="Voice:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.voice_var = tk.StringVar(value="None")
        tk.OptionMenu(self.voice_frame, self.voice_var, "None", "Male", "Female").pack(side=tk.LEFT, padx=5)

        # Buttons
        self.button_frame = tk.Frame(root, bg="#f0f0f0")
        self.button_frame.pack(pady=10)
        tk.Button(self.button_frame, text="Start", command=self.start_timer).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Stop", command=self.stop_timer).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Reset", command=self.reset_timer).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Apply Settings", command=self.apply_settings).pack(side=tk.LEFT, padx=5)

    def generate_tone(self, frequency, duration=1):
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        if self.voice_var.get() == "Male":
            wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Lower frequency for male voice
        else:  # Female
            wave = 0.5 * np.sin(2 * np.pi * (frequency * 1.5) * t)  # Higher frequency for female voice
        stereo_wave = np.stack((wave, wave), axis=1)
        sound = pygame.sndarray.make_sound((stereo_wave * 32767).astype(np.int16))
        return sound

    def upload_bg_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize((600, 400), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(image)
                if self.bg_label:
                    self.bg_label.configure(image=self.bg_image)
                else:
                    self.bg_label = tk.Label(self.root, image=self.bg_image)
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    self.label.lift()
                    self.time_entry.lift()
                    self.font_frame.lift()
                    self.bg_frame.lift()
                    self.voice_frame.lift()
                    self.button_frame.lift()
            except Exception as e:
                print(f"Error loading image: {e}")

    def apply_settings(self):
        try:
            font_size = int(self.size_var.get())
            self.label.configure(
                font=(self.font_var.get(), font_size),
                fg=self.color_var.get(),
                bg=self.bg_color_var.get() if not self.bg_image else "transparent"
            )
            if not self.bg_image:
                self.root.configure(bg=self.bg_color_var.get())
        except Exception as e:
            print(f"Error applying settings: {e}")

    def start_timer(self):
        if not self.is_running:
            try:
                self.time_left = int(self.time_entry.get())
                self.is_running = True
                asyncio.ensure_future(self.update_timer())
            except ValueError:
                self.label.configure(text="Invalid input!")

    def stop_timer(self):
        self.is_running = False

    def reset_timer(self):
        self.is_running = False
        self.time_left = int(self.time_entry.get()) if self.time_entry.get().isdigit() else 60
        self.label.configure(text=f"{self.time_left//60:02d}:{self.time_left%60:02d}")

    async def update_timer(self):
        while self.is_running and self.time_left > 0:
            self.label.configure(text=f"{self.time_left//60:02d}:{self.time_left%60:02d}")
            if self.time_left <= 10 and self.voice_var.get() != "None":
                tone = self.generate_tone(440)  # Simple tone for countdown
                tone.play()
            self.time_left -= 1
            await asyncio.sleep(1)
        if self.time_left <= 0:
            self.label.configure(text="Time's up!")
            self.is_running = False

async def main():
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())