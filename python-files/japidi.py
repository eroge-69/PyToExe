# skibidi_gui.py
import os
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Try import pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

# ======= CONFIG =======
AUDIO_FILENAME = "skibidi_toilet.mp3"  # place the mp3 in same folder to play locally
BACKGROUND_IMAGE = "background.png"   # optional background image (same folder)
YOUTUBE_FALLBACK = "https://www.youtube.com/results?search_query=skibidi+toilet"  # opens if mp3 not found
WINDOW_TITLE = "Skibidi Toilet"
WINDOW_SIZE = (640, 480)
# ======================

class SkibidiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.resizable(False, False)

        # Initialize pygame mixer if available
        self.audio_ready = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.audio_ready = True
            except Exception as e:
                print("pygame mixer init failed:", e)
                self.audio_ready = False

        # Main container
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Load background (image or fallback)
        self._load_background()

        # Floating button frame centered
        self._create_button()

        # A small label to show status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.container, textvariable=self.status_var)
        self.status_label.place(relx=0.5, rely=0.93, anchor="center")

    def _load_background(self):
        if os.path.exists(BACKGROUND_IMAGE):
            try:
                img = Image.open(BACKGROUND_IMAGE)
                img = img.resize(WINDOW_SIZE, Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                self.bg_label = tk.Label(self.container, image=self.bg_image)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print("Error loading background image:", e)
                self._draw_fallback_bg()
        else:
            self._draw_fallback_bg()

    def _draw_fallback_bg(self):
        # Create a canvas and draw a playful toilet-ish scene
        c = tk.Canvas(self.container, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1], highlightthickness=0)
        c.pack(fill="both", expand=True)

        # sky
        c.create_rectangle(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1], fill="#E8F6FF", outline="")
        # floor
        c.create_rectangle(0, WINDOW_SIZE[1]*0.7, WINDOW_SIZE[0], WINDOW_SIZE[1], fill="#F6F6F6", outline="")
        # stylized toilet bowl
        cx = WINDOW_SIZE[0]*0.75
        cy = WINDOW_SIZE[1]*0.6
        c.create_oval(cx-80, cy-40, cx+80, cy+80, fill="white", outline="#CCC", width=2)
        c.create_rectangle(cx-60, cy+40, cx+60, cy+80, fill="white", outline="#CCC", width=2)
        # water sparkle
        c.create_text(cx+10, cy-5, text="🚽", font=("Arial", 36))
        # title text
        c.create_text(WINDOW_SIZE[0]*0.25, WINDOW_SIZE[1]*0.25, text="Skibidi Toilet", font=("Impact", 36), fill="#333")
        # keep reference
        self.canvas = c

    def _create_button(self):
        # Large "skibidi" button
        btn = tk.Button(self.container, text="skibidi", font=("Helvetica", 26, "bold"),
                        command=self.on_skibidi_click, bd=4, relief="raised")
        # place button centered a bit above bottom
        btn.place(relx=0.5, rely=0.6, anchor="center", width=240, height=80)
        self.skibidi_button = btn

    def _play_local_audio(self):
        if not PYGAME_AVAILABLE:
            self.status_var.set("pygame not installed — opening fallback")
            webbrowser.open(YOUTUBE_FALLBACK)
            return

        if not os.path.exists(AUDIO_FILENAME):
            self.status_var.set("No local MP3 found — opening fallback")
            webbrowser.open(YOUTUBE_FALLBACK)
            return

        try:
            # Load and play (non-blocking)
            pygame.mixer.music.load(AUDIO_FILENAME)
            pygame.mixer.music.play()
            self.status_var.set("Playing (local): " + AUDIO_FILENAME)
            # Optionally: after music ends update status. We'll poll.
            self.after(500, self._poll_music)
        except Exception as e:
            print("Audio playback failed:", e)
            self.status_var.set("Playback error — opening fallback")
            webbrowser.open(YOUTUBE_FALLBACK)

    def _poll_music(self):
        # If music still playing, check again
        try:
            if pygame.mixer.music.get_busy():
                self.after(500, self._poll_music)
            else:
                self.status_var.set("Ready")
        except Exception:
            # if mixer died
            self.status_var.set("Ready")

    def on_skibidi_click(self):
        """Handler when user clicks the skibidi button."""
        # Visual feedback: flash the button and status
        self.skibidi_button.config(relief="sunken")
        self.status_var.set("Skibidi!")
        self.after(150, lambda: self.skibidi_button.config(relief="raised"))

        # Play audio in a thread so GUI remains responsive
        t = threading.Thread(target=self._play_local_audio, daemon=True)
        t.start()

        # Extra flair: little pop animation on canvas if fallback used
        if hasattr(self, "canvas"):
            # temporary text on canvas
            txt = self.canvas.create_text(WINDOW_SIZE[0]*0.5, WINDOW_SIZE[1]*0.4, text="SKIBIDI!!", font=("Impact", 28))
            def remove_text():
                try:
                    self.canvas.delete(txt)
                except Exception:
                    pass
            self.after(900, remove_text)

if __name__ == "__main__":
    # If pygame is not installed, tell user but still let UI run
    if not PYGAME_AVAILABLE:
        print("Note: 'pygame' not available. Install with: pip install pygame")
    app = SkibidiApp()
    app.mainloop()
