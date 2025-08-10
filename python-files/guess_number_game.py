import tkinter as tk
import random


class GuessingGame:
    """A simple hot‑or‑cold number guessing game using Tkinter for the GUI.

    The game chooses a random number between 1 and 100. The user guesses
    numbers and receives feedback based on how close their guess is to the
    secret number. When the correct number is guessed, the user is given
    the option to play again.
    """

    def __init__(self, master: tk.Tk) -> None:
        """Initialize the game UI and variables.

        Args:
            master: The root Tk widget.
        """
        self.master = master
        master.title("Guess the Number Game")
        # Set a reasonable window size for desktop use
        master.geometry("400x300")

        # Initialize the secret number and attempt counter
        self.secret_number = random.randint(1, 100)
        self.attempts = 0

        # Instruction label
        self.label = tk.Label(
            master,
            text="I'm thinking of a number between 1 and 100.\n"
                 "Enter your guess below:",
            justify="center"
        )
        self.label.pack(pady=10)

        # Entry field for the user's guess
        self.entry = tk.Entry(master, font=("Helvetica", 14), justify="center")
        self.entry.pack(pady=10)

        # Button to submit the guess
        self.button = tk.Button(
            master,
            text="Submit Guess",
            command=self.check_guess,
            width=20
        )
        self.button.pack(pady=10)

        # Label to display feedback (hot/cold or success message)
        self.feedback = tk.Label(master, text="", font=("Helvetica", 12))
        self.feedback.pack(pady=10)

        # Button to reset the game; initially disabled until user wins
        self.reset_button = tk.Button(
            master,
            text="Play Again",
            command=self.reset_game,
            state=tk.DISABLED,
            width=20
        )
        self.reset_button.pack(pady=10)

    def hot_cold(self, guess: int) -> str:
        """Determine a temperature hint based on how close the guess is.

        Args:
            guess: The user's guessed number.

        Returns:
            A string representing the hot/cold hint.
        """
        diff = abs(self.secret_number - guess)
        if diff == 0:
            return "correct"
        elif diff <= 2:
            return "boiling hot"
        elif diff <= 5:
            return "very hot"
        elif diff <= 10:
            return "hot"
        elif diff <= 20:
            return "warm"
        elif diff <= 30:
            return "cold"
        else:
            return "very cold"

    def check_guess(self) -> None:
        """Handle the logic when the user submits a guess.

        Validates input, compares it to the secret number, updates feedback,
        and manages the state of the UI controls.
        """
        # Retrieve the value from the entry field
        guess_str = self.entry.get()
        try:
            guess = int(guess_str)
        except ValueError:
            self.feedback.config(text="Please enter a valid integer.")
            # Clear the entry field for the next attempt
            self.entry.delete(0, tk.END)
            return

        # Ensure the guess is within the expected range
        if not 1 <= guess <= 100:
            self.feedback.config(text="Your guess must be between 1 and 100.")
            self.entry.delete(0, tk.END)
            return

        # Valid guess; increment attempt counter
        self.attempts += 1

        # Determine hint or success
        hint = self.hot_cold(guess)
        if hint == "correct":
            self.feedback.config(
                text=f"Congratulations! {guess} is correct. You guessed it in {self.attempts} attempts.")
            # Disable guessing controls
            self.entry.config(state=tk.DISABLED)
            self.button.config(state=tk.DISABLED)
            # Enable the reset button so the user can play again
            self.reset_button.config(state=tk.NORMAL)
        else:
            # Provide a hint based on the difference
            self.feedback.config(text=f"{hint.capitalize()}! Try again.")
        # Clear the entry field after each guess to make the next guess easier
        self.entry.delete(0, tk.END)

    def reset_game(self) -> None:
        """Reset the game state to allow the user to play another round."""
        # Select a new secret number and reset attempts
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        # Clear feedback and re-enable controls
        self.feedback.config(text="")
        self.entry.config(state=tk.NORMAL)
        self.button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)


def main() -> None:
    """Run the guessing game application."""
    root = tk.Tk()
    game = GuessingGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()