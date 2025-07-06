import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from PIL import Image, ImageTk
import pygame
import webbrowser
import sys
import random
import time # Added for the typing game


# === CONFIGURE YOUR GAME HERE ===
GAME_NAME = "tweak free"
GAME_PATH = r"C:\Users\khalf\Downloads\game_launcher\aa" # CHANGE THIS TO YOUR GAME
ICON_PATH = "" # Optional image (must be in same folder) - Leave empty if you don't have one

# === MUSIC SETTINGS ===
MUSIC_FILE = r"C:\Users\khalf\Videos\4K Video Downloader+\background_music.mp3" # Your music file (MP3 or WAV)
INITIAL_VOLUME = 0.5 # Default volume (0.0 to 1.0)

# === SOCIAL MEDIA LINKS & COLORS ===
SOCIAL_LINKS = {
    "Discord": {"url": "https://discord.gg/ZAb2EBCqzE", "bg": "#5865F2", "fg": "white", "active_bg": "#4A52C0"},
    "TikTok": {"url": "https://www.tiktok.com/@kbf.0o", "bg": "#000000", "fg": "#FFFFFF", "active_bg": "#333333"},
    "YouTube": {"url": "https://www.youtube.com/ALUZIOO", "bg": "#FF0000", "fg": "white", "active_bg": "#CC0000"},
    "Twitch": {"url": "https://www.twitch.tv/ALUZIOO", "bg": "#9146FF", "fg": "white", "active_bg": "#772DCC"}
}

# === PC TWEAK SETTINGS ===
PC_TWEAK_PATH = r"C:\Users\khalf\Videos\4K Video Downloader+\pc_tweak_script.py"

# === PERIPHERAL SETTINGS ===
KEYBOARD_IMAGE_PATH = r"C:\Users\khalf\Downloads\1-838fc684.png"
KEYBOARD_NAME = "attack shark k86"
MONITOR_IMAGE_PATH = r"C:\Users\khalf\Downloads\3-838fc684.png"
MONITOR_NAME = "benq zowie 240hz"
MOUSE_IMAGE_PATH = r"C:\Users\khalf\Downloads\2-838fc684.png"
MOUSE_NAME = "Razer Viper Mini"
PERIPHERAL_IMAGE_SIZE = (150, 100)

# === GLOBAL BACKGROUND COLOR FOR OVERLAYED LABELS ===
OVERLAY_LABEL_BG = "#1a1a1a" # A dark grey, or use 'black'

# --- BACKGROUND FADING COLORS SETTINGS ---
# Define the colors you want to cycle through (RGB tuples)
FADING_COLORS = [
    (255, 0, 0), # Red
    (255, 127, 0), # Orange
    (255, 255, 0), # Yellow
    (0, 255, 0), # Green
    (0, 0, 255), # Blue
    (75, 0, 130), # Indigo
    (143, 0, 255), # Violet
    (0, 255, 255), # Cyan
    (255, 0, 255) # Magenta
]
FADE_SPEED = 2 # How many steps it takes to transition from one color to the next. Higher = slower transition.
FADE_ANIMATION_DELAY = 30 # Milliseconds between each step of the fade.

# --- TYPING SPEED GAME CLASS ---
class TypingSpeedGame(tk.Toplevel): # Changed from tk.Tk to tk.Toplevel
    def __init__(self, master=None): # Added master argument
        super().__init__(master) # Pass master to Toplevel
        self.title("Typing Speed Test")
        self.geometry("800x500")
        self.resizable(False, False)

        # --- Game Data ---
        self.sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "Never underestimate the power of a good book.",
            "Programming is thinking, not typing.",
            "The early bird catches the worm, but the second mouse gets the cheese.",
            "Innovation distinguishes between a leader and a follower.",
            "The only way to do great work is to love what you do.",
            "Life is what happens when you're busy making other plans.",
            "The future belongs to those who believe in the beauty of their dreams.",
            "Strive not to be a success, but rather to be of value.",
            "The best way to predict the future is to create it."
            "KBF is the best :3"
            "KBF is the best :3"
            "KBF is the best :3"
        ]
        self.current_sentence_index = 0
        self.current_sentence = ""
        self.start_time = 0
        self.end_time = 0
        self.timer_running = False
        self.typed_characters = 0
        self.correct_characters = 0
        self.game_active = False

        self.create_widgets()
        self.reset_game()

        # Add a protocol for when the window is closed by the user
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle window closing event."""
        # You might want to add some cleanup or confirmation here
        self.destroy() # Close the Toplevel window

    def create_widgets(self):
        # --- Main Frame for content ---
        main_frame = tk.Frame(self, bg="#2c3e50", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # --- Title ---
        tk.Label(
            main_frame,
            text="Typing Speed Test",
            font=("Arial", 28, "bold"),
            fg="#ecf0f1", # Light gray
            bg="#2c3e50" # Dark blue-gray
        ).pack(pady=(0, 20))

        # --- Instructions ---
        tk.Label(
            main_frame,
            text="Type the sentence below as fast and accurately as you can!",
            font=("Arial", 12),
            fg="#bdc3c7", # Gray
            bg="#2c3e50"
        ).pack(pady=(0, 15))

        # --- Sentence Display Area ---
        self.sentence_canvas = tk.Canvas(
            main_frame,
            bg="#34495e", # Medium blue-gray
            height=80,
            highlightthickness=0,
            relief="flat"
        )
        self.sentence_canvas.pack(fill="x", pady=10, padx=10)

        # --- Input Entry ---
        self.input_entry = tk.Entry(
            main_frame,
            font=("Consolas", 16),
            bg="#ecf0f1", # Light gray
            fg="#2c3e50", # Dark blue-gray
            insertbackground="#2c3e50", # Cursor color
            justify="left",
            relief="flat",
            bd=2,
            highlightbackground="#3498db", # Blue border
            highlightcolor="#3498db"
        )
        self.input_entry.pack(fill="x", pady=10, padx=10)
        self.input_entry.bind("<KeyRelease>", self.check_input) # Bind key release for real-time check

        # --- Stats Display Frame ---
        stats_frame = tk.Frame(main_frame, bg="#2c3e50")
        stats_frame.pack(pady=10)

        self.wpm_label = tk.Label(
            stats_frame,
            text="WPM: 0",
            font=("Arial", 14, "bold"),
            fg="#2ecc71", # Green
            bg="#2c3e50"
        )
        self.wpm_label.pack(side=tk.LEFT, padx=20)

        self.accuracy_label = tk.Label(
            stats_frame,
            text="Accuracy: 0%",
            font=("Arial", 14, "bold"),
            fg="#e67e22", # Orange
            bg="#2c3e50"
        )
        self.accuracy_label.pack(side=tk.LEFT, padx=20)

        self.timer_label = tk.Label(
            stats_frame,
            text="Time: 0s",
            font=("Arial", 14, "bold"),
            fg="#9b59b6", # Purple
            bg="#2c3e50"
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)

        # --- Buttons Frame ---
        button_frame = tk.Frame(main_frame, bg="#2c3e50")
        button_frame.pack(pady=20)

        self.start_button = tk.Button(
            button_frame,
            text="Start Test",
            command=self.start_game,
            font=("Arial", 16, "bold"),
            bg="#3498db", # Blue
            fg="white",
            activebackground="#2980b9",
            relief="raised",
            bd=3,
            padx=15, pady=8
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_game,
            font=("Arial", 16, "bold"),
            bg="#e74c3c", # Red
            fg="white",
            activebackground="#c0392b",
            relief="raised",
            bd=3,
            padx=15, pady=8
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)

    def reset_game(self):
        """Resets all game variables and UI elements to their initial state."""
        self.game_active = False
        self.timer_running = False
        self.start_time = 0
        self.end_time = 0
        self.typed_characters = 0
        self.correct_characters = 0
        self.current_sentence_index = 0 # Start from the first sentence

        # Shuffle sentences for variety
        random.shuffle(self.sentences)
        self.current_sentence = self.sentences[self.current_sentence_index]

        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state=tk.DISABLED) # Disable input until game starts
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED) # Disable reset until game starts or ends

        self.wpm_label.config(text="WPM: 0")
        self.accuracy_label.config(text="Accuracy: 0%")
        self.timer_label.config(text="Time: 0s")

        self.update_text_display() # Display the first sentence

    def start_game(self):
        """Starts the typing test."""
        self.game_active = True
        self.timer_running = False # Will start on first key press
        self.start_time = 0
        self.typed_characters = 0
        self.correct_characters = 0
        self.current_sentence_index = 0
        self.current_sentence = self.sentences[self.current_sentence_index]

        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus_set() # Set focus to the input box
        self.input_entry.delete(0, tk.END)

        self.start_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)

        self.wpm_label.config(text="WPM: 0")
        self.accuracy_label.config(text="Accuracy: 0%")
        self.timer_label.config(text="Time: 0s")

        self.update_text_display()

    def update_text_display(self):
        """Updates the sentence display with highlighting based on user input."""
        self.sentence_canvas.delete("all")
        typed_text = self.input_entry.get()

        x_offset = 10 # Starting X position for text
        y_offset = self.sentence_canvas.winfo_height() / 2 # Center vertically

        for i, char in enumerate(self.current_sentence):
            color = "white" # Default color for untyped text
            if i < len(typed_text):
                if typed_text[i] == char:
                    color = "#2ecc71" # Green for correct
                else:
                    color = "#e74c3c" # Red for incorrect
            
            text_item = self.sentence_canvas.create_text(
                x_offset, y_offset,
                text=char,
                font=("Consolas", 18),
                fill=color,
                anchor="w" # Anchor to the west (left)
            )
            # Get the width of the character just drawn
            bbox = self.sentence_canvas.bbox(text_item)
            char_width = bbox[2] - bbox[0]
            x_offset += char_width # Move x_offset for the next character

    def check_input(self, event=None):
        """Checks user input, updates stats, and handles game progression."""
        if not self.game_active:
            return

        # Start timer on first key press
        if not self.timer_running and self.input_entry.get():
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

        typed_text = self.input_entry.get()
        self.typed_characters = len(typed_text) # Update total typed characters

        # Recalculate correct characters for current input
        temp_correct_chars = 0
        for i, char in enumerate(typed_text):
            if i < len(self.current_sentence) and typed_text[i] == self.current_sentence[i]:
                temp_correct_chars += 1
        self.correct_characters = temp_correct_chars # Update correct_characters for stats

        self.update_text_display() # Re-render the text with current highlighting
        self.calculate_and_display_stats()

        # Check if the current sentence is fully and correctly typed
        if typed_text == self.current_sentence:
            self.current_sentence_index += 1
            if self.current_sentence_index < len(self.sentences):
                # Move to next sentence
                self.current_sentence = self.sentences[self.current_sentence_index]
                self.input_entry.delete(0, tk.END)
                # Reset typed/correct counts for the *new* sentence
                self.typed_characters = 0
                self.correct_characters = 0
                self.update_text_display()
            else:
                self.end_game()

    def calculate_and_display_stats(self):
        """Calculates and updates WPM and Accuracy."""
        if self.start_time > 0 and self.timer_running:
            time_taken = time.time() - self.start_time
        elif self.end_time > 0: # Game ended
            time_taken = self.end_time - self.start_time
        else: # Game not started yet
            time_taken = 0

        wpm = 0
        accuracy = 0.0

        if time_taken > 0 and self.typed_characters > 0:
            # WPM calculation based on 5 characters per word
            total_time_in_minutes = time_taken / 60
            if total_time_in_minutes > 0:
                wpm = int((self.correct_characters / 5) / total_time_in_minutes)
            
            accuracy = (self.correct_characters / self.typed_characters) * 100

        self.wpm_label.config(text=f"WPM: {wpm}")
        self.accuracy_label.config(text=f"Accuracy: {accuracy:.2f}%")
        self.timer_label.config(text=f"Time: {int(time_taken)}s")

    def update_timer(self):
        """Updates the timer display every second."""
        if self.timer_running and self.game_active:
            time_taken = time.time() - self.start_time
            self.timer_label.config(text=f"Time: {int(time_taken)}s")
            self.after(1000, self.update_timer) # Update every 1 second

    def end_game(self):
        """Ends the game, calculates final stats, and displays results."""
        self.game_active = False
        self.timer_running = False
        self.end_time = time.time()
        self.input_entry.config(state=tk.DISABLED)
        
        time_taken_for_all_sentences = self.end_time - self.start_time
        
        final_wpm = int((self.correct_characters / 5) / (time_taken_for_all_sentences / 60))
        final_accuracy = (self.correct_characters / self.typed_characters) * 100 if self.typed_characters > 0 else 0

        messagebox.showinfo(
            "Test Complete!",
            f"Congratulations!\nYour final WPM: {final_wpm}\nYour Accuracy: {final_accuracy:.2f}%"
        )
        self.reset_game()
        # Ensure the typing game window is destroyed after the message box
        self.destroy() # This will close the typing game window and return control to the launcher


class GameLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Launcher")
        self.geometry("800x600")
        self.resizable(False, False)

        pygame.mixer.init()
        self.music_playing = False

        # Store PhotoImage references to prevent garbage collection
        self.tk_keyboard_img = None
        self.tk_monitor_img = None
        self.tk_mouse_img = None

        # Fading background color variables
        self.current_color_index = 0
        self.fade_step = 0
        self.current_background_rect = None # To store the ID of the background rectangle

        self.create_widgets()

        pygame.mixer.music.set_volume(INITIAL_VOLUME)
        self.volume_slider.set(INITIAL_VOLUME * 100)

        if os.path.exists(MUSIC_FILE):
            self.play_music()
        else:
            messagebox.showwarning("Music Not Found", f"Music file not found at:\n{MUSIC_FILE}\nMusic will not play.")

        # Start fading background animation
        self.animate_fading_background()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # === Canvas for Dynamic Background ===
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Bind resize event to redraw background
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        # Initial draw of the background rectangle (will be updated by animation)
        self.current_background_rect = self.canvas.create_rectangle(0, 0, 800, 600, fill="#000000", outline="")

        # --- IMPORTANT CHANGE HERE ---
        self.content_frame = tk.Frame(self.canvas, bg='') # Changed parent from 'self' to 'self.canvas'
        self.content_frame.pack(expand=True, fill="both")
        # No longer need self.content_frame.lift() if it's already a child of the canvas

        # === Launcher Title ===
        self.launcher_title_label = tk.Label(
            self.content_frame,
            text="GAME LAUNCHER", # Removed "KBF" from here
            font=("Arial", 36, "bold"),
            fg="white",
            bg=OVERLAY_LABEL_BG
        )
        self.launcher_title_label.pack(pady=(20, 5))

        # === Game Title / Icon ===
        try:
            if ICON_PATH and os.path.exists(ICON_PATH):
                img = Image.open(ICON_PATH)
                img = img.resize((500, 200), Image.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(img)
                self.game_icon_label = tk.Label(self.content_frame, image=self.tk_img, bg=OVERLAY_LABEL_BG)
                self.game_icon_label.pack(pady=10)
            else:
                self.game_name_label = tk.Label(
                    self.content_frame,
                    text="🎮 " + GAME_NAME,
                    font=("Arial", 28, "bold"),
                    fg="cyan",
                    bg=OVERLAY_LABEL_BG
                )
                self.game_name_label.pack(pady=10)
        except Exception as e:
            self.game_name_label = tk.Label(
                self.content_frame,
                text="🎮 " + GAME_NAME,
                font=("Arial", 28, "bold"),
                fg="cyan",
                bg=OVERLAY_LABEL_BG
            )
            self.game_name_label.pack(pady=10)
            print(f"Error loading icon: {e}")

        # === Music Controls Frame ===
        music_frame = tk.Frame(self.content_frame, bg='')
        music_frame.pack(pady=5)

        self.play_music_button = tk.Button(
            music_frame,
            text="🎵 Play Music",
            font=("Arial", 12),
            bg="#2980b9",
            fg="white",
            activebackground="#2c3e50",
            padx=10, pady=5,
            command=self.play_music,
            relief="raised",
            bd=3
        )
        self.play_music_button.pack(side=tk.LEFT, padx=5)

        self.stop_music_button = tk.Button(
            music_frame,
            text="🔇 Stop Music",
            font=("Arial", 12),
            bg="#d35400",
            fg="white",
            activebackground="#e67e22",
            padx=10, pady=5,
            command=self.stop_music,
            relief="raised",
            bd=3
        )
        self.stop_music_button.pack(side=tk.RIGHT, padx=5)

        # === Volume Slider ===
        volume_frame = tk.Frame(self.content_frame, bg='')
        volume_frame.pack(pady=5)

        tk.Label(volume_frame, text="Volume:", font=("Arial", 10), fg="white", bg=OVERLAY_LABEL_BG).pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(
            volume_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.set_volume,
            showvalue=0,
            troughcolor="#555555",
            sliderrelief="flat",
            activebackground="#AAAAAA",
            highlightthickness=0,
            bg="#333333",
            fg="white"
        )
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        # === Social Media Links Frame ===
        self.social_media_frame = tk.Frame(self.content_frame, bg='')
        self.social_media_frame.pack(pady=10)

        for platform, data in SOCIAL_LINKS.items():
            tk.Button(
                self.social_media_frame,
                text=platform,
                font=("Arial", 10, "bold"),
                bg=data["bg"],
                fg=data["fg"],
                activebackground=data["active_bg"],
                activeforeground=data["fg"],
                padx=8, pady=4,
                command=lambda url=data["url"]: self.open_link(url),
                relief="raised",
                bd=2
            ).pack(side=tk.LEFT, padx=5)


        # === Action Buttons Frame (Game & Tweak & Typing Game) ===
        action_buttons_frame = tk.Frame(self.content_frame, bg='')
        action_buttons_frame.pack(pady=20)

        tk.Button(
            action_buttons_frame,
            text=f"Play {GAME_NAME}",
            font=("Arial", 20, "bold"),
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            padx=30, pady=15,
            command=self.launch_game,
            relief="raised",
            bd=5
        ).pack(side=tk.LEFT, padx=15)

        tk.Button(
            action_buttons_frame,
            text="🚀 Run PC Tweak",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            padx=20, pady=10,
            command=self.launch_pc_tweak,
            relief="raised",
            bd=5
        ).pack(side=tk.LEFT, padx=15)

        # --- ADDED: Typing Game Button ---
        tk.Button(
            action_buttons_frame,
            text="⌨️ Typing Test",
            font=("Arial", 16, "bold"),
            bg="#8e44ad", # A purple color
            fg="white",
            activebackground="#6c3483",
            padx=20, pady=10,
            command=self.launch_typing_game, # This calls the new method
            relief="raised",
            bd=5
        ).pack(side=tk.LEFT, padx=15)


        # === Peripherals Frame ===
        self.peripherals_frame = tk.Frame(self.content_frame, bg='')
        self.peripherals_frame.pack(pady=15)

        self.add_peripheral_widget(KEYBOARD_IMAGE_PATH, KEYBOARD_NAME, "keyboard")
        self.add_peripheral_widget(MONITOR_IMAGE_PATH, MONITOR_NAME, "monitor")
        self.add_peripheral_widget(MOUSE_IMAGE_PATH, MOUSE_NAME, "mouse")

        # === Exit Button ===
        tk.Button(
            self.content_frame,
            text="Exit Launcher",
            font=("Arial", 14),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            padx=15, pady=8,
            command=self.on_closing
        ).pack(pady=10)

    def add_peripheral_widget(self, image_path, name, identifier):
        """Helper function to create and add peripheral widgets."""
        peripheral_sub_frame = tk.Frame(self.peripherals_frame, bg='')
        peripheral_sub_frame.pack(side=tk.LEFT, padx=10)

        tk_img = None
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize(PERIPHERAL_IMAGE_SIZE, Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                setattr(self, f'tk_{identifier}_img', tk_img)
            except Exception as e:
                print(f"Error loading {identifier} image from {image_path}: {e}")
                messagebox.showwarning("Image Load Error", f"Could not load image for {name} from {image_path}. Check path and format.")

        image_label = tk.Label(peripheral_sub_frame, image=tk_img, bg=OVERLAY_LABEL_BG)
        image_label.image = tk_img
        image_label.pack()

        name_label = tk.Label(
            peripheral_sub_frame,
            text=name,
            font=("Arial", 10, "bold"),
            fg="white",
            bg=OVERLAY_LABEL_BG
        )
        name_label.pack(pady=(5, 0))

    # --- NEW BACKGROUND FADING METHODS ---
    def animate_fading_background(self):
        """Animates the background color by fading between colors in FADING_COLORS."""
        if not self.current_background_rect:
            # Create the rectangle if it doesn't exist (e.g., first run or after resize)
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            if width == 0 or height == 0: # Fallback for initial state
                width, height = 800, 600
            self.current_background_rect = self.canvas.create_rectangle(0, 0, width, height, outline="")

        # Get the current and next target colors
        color1_rgb = FADING_COLORS[self.current_color_index]
        next_color_index = (self.current_color_index + 1) % len(FADING_COLORS)
        color2_rgb = FADING_COLORS[next_color_index]

        # Calculate the interpolation ratio
        ratio = self.fade_step / FADE_SPEED

        # Interpolate RGB values
        r = int(color1_rgb[0] * (1 - ratio) + color2_rgb[0] * ratio)
        g = int(color1_rgb[1] * (1 - ratio) + color2_rgb[1] * ratio)
        b = int(color1_rgb[2] * (1 - ratio) + color2_rgb[2] * ratio)

        # Convert to hex color
        current_hex_color = f"#{r:02x}{g:02x}{b:02x}"

        # Update the background rectangle's color
        self.canvas.itemconfig(self.current_background_rect, fill=current_hex_color)

        self.fade_step += 1
        if self.fade_step > FADE_SPEED:
            self.fade_step = 0
            self.current_color_index = next_color_index # Move to the next color in the list

        self.after(FADE_ANIMATION_DELAY, self.animate_fading_background)

    def on_canvas_resize(self, event):
        """Resizes the background rectangle on window resize."""
        # Update the dimensions of the background rectangle
        if self.current_background_rect:
            self.canvas.coords(self.current_background_rect, 0, 0, event.width, event.height)

    def set_volume(self, val):
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)

    def play_music(self):
        if not pygame.mixer.music.get_busy() and os.path.exists(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                print("Music started.")
                self.play_music_button.config(state=tk.DISABLED)
                self.stop_music_button.config(state=tk.NORMAL)
            except pygame.error as e:
                messagebox.showerror("Music Error", f"Could not play music:\n{e}\nEnsure the file is valid and not corrupted.")
        elif self.music_playing:
            print("Music is already playing.")
        else:
            messagebox.showwarning("Music Not Found", f"Music file not found at:\n{MUSIC_FILE}")

    def stop_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.music_playing = False
            print("Music stopped.")
            self.play_music_button.config(state=tk.NORMAL)
            self.stop_music_button.config(state=tk.DISABLED)
        else:
            print("No music is currently playing.")

    def open_link(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Browser Error", f"Could not open link:\n{url}\nError: {e}")

    def launch_game(self):
        if os.path.exists(GAME_PATH):
            try:
                self.stop_music()
                self.withdraw()
                subprocess.Popen(GAME_PATH)
                self.after(5000, self.check_game_process)
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch the game:\n{e}")
                self.deiconify()
                if os.path.exists(MUSIC_FILE) and self.music_playing:
                    self.play_music()
        else:
            messagebox.showwarning("Not Found", f"Game not found at:\n{GAME_PATH}")

    def launch_pc_tweak(self):
        if not PC_TWEAK_PATH:
            messagebox.showerror("Error", "PC Tweak path is not configured.")
            return

        if PC_TWEAK_PATH.lower().endswith(".py"):
            python_executable = sys.executable
            command = [python_executable, PC_TWEAK_PATH]
        else:
            command = [PC_TWEAK_PATH]

        if os.path.exists(PC_TWEAK_PATH) or (PC_TWEAK_PATH.lower().endswith(".py") and os.path.exists(PC_TWEAK_PATH)):
            try:
                self.stop_music()
                self.withdraw()

                creationflags = 0
                if sys.platform == "win32" and not PC_TWEAK_PATH.lower().endswith(".py"):
                    creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

                subprocess.Popen(command, creationflags=creationflags)
                messagebox.showinfo("PC Tweak", "PC Tweak script launched. A console window may appear.")
                self.after(2000, self.check_tweak_process_completion)
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch PC Tweak:\n{e}")
                self.deiconify()
                if os.path.exists(MUSIC_FILE) and self.music_playing:
                    self.play_music()
        else:
            messagebox.showwarning("Not Found", f"PC Tweak script not found at:\n{PC_TWEAK_PATH}")

    # --- ADDED: Method to launch the Typing Speed Game ---
    def launch_typing_game(self):
        """Launches the embedded Typing Speed Game window."""
        try:
            self.stop_music() # Stop music in launcher
            self.withdraw() # Hide the launcher window

            # Create and run the typing game as a Toplevel window
            # Pass 'self' (the launcher) as the master
            typing_app = TypingSpeedGame(self)
            self.wait_window(typing_app) # Wait until the typing_app window is closed

        except Exception as e:
            messagebox.showerror("Error", f"Could not launch Typing Game:\n{e}")
        finally:
            self.deiconify() # Show the launcher window again
            # Resume music if it was playing and music file exists
            if os.path.exists(MUSIC_FILE) and self.music_playing:
                self.play_music()

    def check_game_process(self):
        self.deiconify()
        if os.path.exists(MUSIC_FILE) and self.music_playing:
            self.play_music()

    def check_tweak_process_completion(self):
        self.deiconify()
        if os.path.exists(MUSIC_FILE) and self.music_playing:
            self.play_music()

    def on_closing(self):
        self.stop_music()
        self.destroy()

if __name__ == "__main__":
    app = GameLauncher()
    app.mainloop()