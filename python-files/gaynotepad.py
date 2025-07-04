import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import random
import os

# --- Configuration for Fabulous Notes ---
# File where your fabulous notes will be saved and loaded
NOTES_FILENAME = "fabulous_notes.txt"

# Affirmations for the "Add Fabulousness" button
AFFIRMATIONS = [
    "You are valid! 🏳️‍🌈",
    "Shine bright, darling! ✨",
    "Love wins, always. ❤️🧡💛💚💙�",
    "Be yourself, everyone else is already taken. 💖",
    "Embrace your true colors! 🌈",
    "You are loved and celebrated! 🎉",
    "Stay fabulous! 👑",
    "Queer joy is revolutionary! 😊",
    "Your story matters. 📖",
    "Live your truth! 🌟",
    "Be bold, be proud! 🏳️‍⚧️",
    "Your existence is a celebration! 🥳"
]

# --- Main Application Class ---
class FabulousNotepadApp:
    """
    A fabulous and extremely gay notepad application using Tkinter.
    Allows users to write, save, load, and add affirmations to notes.
    """
    def __init__(self, master):
        """
        Initializes the main application window and widgets.
        :param master: The root Tkinter window.
        """
        self.master = master
        master.title("✨ Fabulous Notes: An Extremely Gay Notepad ✨")
        master.geometry("800x600") # Set initial window size
        master.resizable(True, True) # Allow resizing

        # Set a rainbow background for the main window
        master.config(bg="#FFC0CB") # Start with a pinkish hue

        # Create a main frame to hold all widgets, with a fabulous border
        self.main_frame = tk.Frame(master, bg="white", bd=5, relief="raised",
                                   highlightbackground="#FF69B4", highlightthickness=3)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.main_frame.grid_rowconfigure(1, weight=1) # Allow text area to expand vertically
        self.main_frame.grid_columnconfigure(0, weight=1) # Allow text area to expand horizontally

        # Title Label
        self.title_label = tk.Label(self.main_frame,
                                    text="✨ Fabulous Notes ✨",
                                    font=("Inter", 28, "bold"),
                                    fg="#8A2BE2", # Blue violet
                                    bg="white")
        self.title_label.grid(row=0, column=0, columnspan=3, pady=15)

        # Text Area for Notes
        self.note_input = scrolledtext.ScrolledText(self.main_frame,
                                                    wrap=tk.WORD, # Wrap words at the end of lines
                                                    font=("Inter", 12),
                                                    bg="#FFF0F5", # Lavender blush
                                                    fg="#333",
                                                    insertbackground="#8A2BE2", # Cursor color
                                                    bd=2, relief="solid",
                                                    highlightbackground="#FF69B4", highlightthickness=1)
        self.note_input.grid(row=1, column=0, columnspan=3, padx=15, pady=10, sticky="nsew")
        self.note_input.focus_set() # Set focus to the text area on startup

        # --- Buttons ---
        self.button_frame = tk.Frame(self.main_frame, bg="white")
        self.button_frame.grid(row=2, column=0, columnspan=3, pady=15)

        # New Note Button
        self.new_note_btn = self._create_button(
            self.button_frame, "📝 New Sparkle", self.new_note, "#FF69B4", "#FFFFFF" # Hot pink, white text
        )
        self.new_note_btn.pack(side="left", padx=10)

        # Save Note Button
        self.save_note_btn = self._create_button(
            self.button_frame, "💖 Save the Sass", self.save_note, "#8A2BE2", "#FFFFFF" # Blue violet, white text
        )
        self.save_note_btn.pack(side="left", padx=10)

        # Load Note Button
        self.load_note_btn = self._create_button(
            self.button_frame, "📂 Fetch Your Faves", self.load_note, "#ADD8E6", "#333333" # Light blue, dark text
        )
        self.load_note_btn.pack(side="left", padx=10)

        # Add Fabulousness Button
        self.sparkle_btn = self._create_button(
            self.button_frame, "🌈 Add Fabulousness", self.add_fabulousness, "#90EE90", "#333333" # Light green, dark text
        )
        self.sparkle_btn.pack(side="left", padx=10)

        # Message Label for user feedback
        self.message_label = tk.Label(self.main_frame, text="", font=("Inter", 10, "italic"), fg="#555", bg="white")
        self.message_label.grid(row=3, column=0, columnspan=3, pady=5)

        # Load notes on startup if the file exists
        self.load_note(startup=True)

    def _create_button(self, parent, text, command, bg_color, fg_color):
        """
        Helper method to create styled buttons.
        :param parent: The parent widget.
        :param text: The text to display on the button.
        :param command: The function to call when the button is clicked.
        :param bg_color: Background color of the button.
        :param fg_color: Foreground (text) color of the button.
        :return: The created Tkinter Button widget.
        """
        button = tk.Button(parent,
                           text=text,
                           command=command,
                           bg=bg_color,
                           fg=fg_color,
                           font=("Inter", 11, "bold"),
                           padx=15,
                           pady=8,
                           bd=0, # No default border
                           relief="raised",
                           activebackground=self._darken_color(bg_color), # Darken on click
                           activeforeground=fg_color,
                           cursor="hand2") # Change cursor on hover
        # Add a subtle border on hover for extra fabulousness
        button.bind("<Enter>", lambda e: button.config(relief="ridge", bd=2))
        button.bind("<Leave>", lambda e: button.config(relief="raised", bd=0))
        return button

    def _darken_color(self, hex_color, factor=0.8):
        """
        Darkens a hex color by a given factor.
        Used for button active background.
        :param hex_color: The hex color string (e.g., "#RRGGBB").
        :param factor: Factor to darken (0.0 to 1.0).
        :return: Darkened hex color string.
        """
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(int(c * factor) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb

    def show_message(self, message, color="black", duration=2000):
        """
        Displays a temporary message to the user.
        :param message: The message string.
        :param color: The color of the message text.
        :param duration: How long the message should be displayed in milliseconds.
        """
        self.message_label.config(text=message, fg=color)
        self.master.after(duration, lambda: self.message_label.config(text="")) # Clear message after duration

    def new_note(self):
        """Clears the text area for a new note."""
        self.note_input.delete(1.0, tk.END) # Delete all content
        self.show_message("Ready for a new fabulous thought! 💭", color="#8A2BE2") # Blue violet

    def save_note(self):
        """Saves the current note content to the predefined file."""
        content = self.note_input.get(1.0, tk.END).strip() # Get all text and remove leading/trailing whitespace
        if not content:
            self.show_message("Please write something fabulous before saving! ✍️", color="#FF6347") # Tomato
            return

        try:
            with open(NOTES_FILENAME, "w", encoding="utf-8") as f:
                f.write(content)
            self.show_message(f"Fabulous note saved to {NOTES_FILENAME}! ✨", color="#FF69B4") # Hot pink
        except IOError as e:
            self.show_message(f"Failed to save note: {e}. Keep trying, hun! 😥", color="#FF6347") # Tomato
            messagebox.showerror("Save Error", f"Could not save note:\n{e}")

    def load_note(self, startup=False):
        """
        Loads note content from the predefined file.
        :param startup: Boolean, True if called during application startup.
        """
        try:
            if os.path.exists(NOTES_FILENAME):
                with open(NOTES_FILENAME, "r", encoding="utf-8") as f:
                    content = f.read()
                self.note_input.delete(1.0, tk.END)
                self.note_input.insert(1.0, content)
                if not startup:
                    self.show_message(f"Fabulous note loaded from {NOTES_FILENAME}! 💖", color="#8A2BE2") # Blue violet
            elif not startup:
                self.show_message("No fabulous notes found to load! 📂", color="#555")
        except IOError as e:
            self.show_message(f"Failed to load note: {e}. Check file permissions. 😔", color="#FF6347") # Tomato
            messagebox.showerror("Load Error", f"Could not load note:\n{e}")

    def add_fabulousness(self):
        """Inserts a random affirmation into the current note."""
        random_affirmation = random.choice(AFFIRMATIONS)
        current_content = self.note_input.get(1.0, tk.END).strip()
        if current_content:
            self.note_input.insert(tk.END, "\n\n") # Add newlines if content already exists
        self.note_input.insert(tk.END, random_affirmation)
        self.show_message("Feeling fabulous yet? 💖", color="#90EE90") # Light green


# --- Run the application ---
if __name__ == "__main__":
    # Create the main Tkinter window
    root = tk.Tk()
    # Instantiate the FabulousNotepadApp
    app = FabulousNotepadApp(root)
    # Start the Tkinter event loop, which keeps the window open and responsive
    root.mainloop()