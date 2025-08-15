"""
Guess Game
==========

A simple Windows GUI game built with Tkinter. When you run this script it
opens a window containing a drawing canvas and a text entry field. The
game chooses one of three basic shapes (circle, square or triangle)
and renders it on the canvas. The player must type the name of the
shape into the entry box and press the "NEXT" button to submit their
guess. If the guess is correct a message "You won" is shown; otherwise
"You lost" appears. A "PLAY AGAIN" button lets the user restart the
game with a new random shape.

This script does not require any external libraries beyond the Python
standard library and works on Windows without modification. To convert
it into a standalone executable you can install pyinstaller and run
`pyinstaller --onefile --windowed guess_game.py`. This will produce
`guess_game.exe` in the `dist` directory.
"""

import random
import tkinter as tk
from tkinter import messagebox


class GuessGameApp(tk.Tk):
    """Main application window for the guessing game."""

    def __init__(self):
        super().__init__()
        self.title("Guess the Shape Game")
        # Set a fixed window size that's comfortable on most displays.
        self.resizable(False, False)
        window_width = 460
        window_height = 560
        self.geometry(f"{window_width}x{window_height}")

        # List of possible shapes the game can choose from.
        self.shapes = ["circle", "square", "triangle"]
        # Setup the UI components.
        self.create_widgets()
        # Start a new game.
        self.new_round()

    def create_widgets(self) -> None:
        """Create and layout all the widgets in the window."""
        # Canvas for drawing the shape.
        self.canvas = tk.Canvas(self, width=400, height=400, bg="white")
        self.canvas.pack(pady=10)

        # Frame for the input field and buttons.
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)

        # Entry widget where the player types their guess.
        self.guess_entry = tk.Entry(input_frame, width=25, font=("Arial", 14))
        self.guess_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.guess_entry.bind("<Return>", lambda event: self.check_guess())

        # Button to submit the guess and advance.
        self.next_button = tk.Button(
            input_frame,
            text="NEXT",
            font=("Arial", 12, "bold"),
            command=self.check_guess,
            width=10,
        )
        self.next_button.pack(side=tk.LEFT)

        # Label to display messages about wins and losses.
        self.message_label = tk.Label(self, text="", font=("Arial", 14))
        self.message_label.pack(pady=5)

        # Button that appears after each round to reset the game.
        self.play_again_button = tk.Button(
            self,
            text="PLAY AGAIN",
            font=("Arial", 12, "bold"),
            command=self.new_round,
            width=15,
        )
        # It is hidden by default; shown after each guess.

    def draw_shape(self, shape: str) -> None:
        """Draw the specified shape on the canvas."""
        # Clear previous drawings.
        self.canvas.delete("all")
        # Use a random pastel color for each shape for variety.
        color = random.choice(
            [
                "#FFCDD2",
                "#F8BBD0",
                "#E1BEE7",
                "#D1C4E9",
                "#C5CAE9",
                "#BBDEFB",
                "#B2EBF2",
                "#B2DFDB",
                "#C8E6C9",
                "#DCEDC8",
                "#FFF9C4",
                "#FFECB3",
            ]
        )
        if shape == "circle":
            # Draw a circle centered in the canvas.
            radius = 150
            x0 = 200 - radius
            y0 = 200 - radius
            x1 = 200 + radius
            y1 = 200 + radius
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black", width=2)
        elif shape == "square":
            # Draw a square centered in the canvas.
            side = 300
            x0 = (400 - side) / 2
            y0 = (400 - side) / 2
            x1 = x0 + side
            y1 = y0 + side
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black", width=2)
        elif shape == "triangle":
            # Draw an equilateral triangle centered in the canvas.
            size = 320
            height = (size * 3 ** 0.5) / 2
            # Coordinates of the triangle's corners.
            x_center = 200
            y_center = 200
            points = [
                x_center,
                y_center - (2 / 3) * height,
                x_center - size / 2,
                y_center + (1 / 3) * height,
                x_center + size / 2,
                y_center + (1 / 3) * height,
            ]
            self.canvas.create_polygon(points, fill=color, outline="black", width=2)

    def new_round(self) -> None:
        """Start a new round by choosing a new shape and resetting the UI."""
        # Choose a shape at random.
        self.current_shape = random.choice(self.shapes)
        # Draw the new shape on the canvas.
        self.draw_shape(self.current_shape)
        # Clear the entry and message label.
        self.guess_entry.delete(0, tk.END)
        self.message_label.config(text="")
        # Enable the NEXT button and show the entry field again.
        self.next_button.config(state=tk.NORMAL)
        self.guess_entry.config(state=tk.NORMAL)
        self.guess_entry.focus_set()
        # Hide the PLAY AGAIN button until after the guess.
        self.play_again_button.pack_forget()

    def check_guess(self) -> None:
        """Check the player's guess against the current shape."""
        guess = self.guess_entry.get().strip().lower()
        if not guess:
            messagebox.showinfo("No input", "Please enter your guess before proceeding.")
            return
        # Disable input during result display to prevent double submissions.
        self.next_button.config(state=tk.DISABLED)
        self.guess_entry.config(state=tk.DISABLED)
        # Determine if the guess was correct.
        if guess == self.current_shape:
            self.message_label.config(text="You won! 🎉", fg="green")
        else:
            correct = self.current_shape.capitalize()
            self.message_label.config(
                text=f"You lost! It was a {correct}.", fg="red"
            )
        # Show the PLAY AGAIN button.
        self.play_again_button.pack(pady=10)


def main() -> None:
    """Entry point for running the game application."""
    app = GuessGameApp()
    app.mainloop()


if __name__ == "__main__":
    main()
