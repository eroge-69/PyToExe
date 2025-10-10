import tkinter as tk
from tkinter import scrolledtext
import sys
import threading

# Import your game
from Main import Game


class ConsoleGUI:


    def __init__(self, root):

        self.root = root
        self.root.title("⚔️ One Piece Text RPG")
        self.root.geometry("1000x650")

        # THEME: One Piece (Gold and Blue)
        self.colors = {
            "bg_main": "#0a1e3d",  # Navy blue (ocean)
            "bg_console": "#051429",  # Darker blue
            "text": "#ffd700",  # Gold (treasure!)
            "bg_title": "#061b33",  # Title bar
            "bg_input": "#051429",  # Input background
            "button_bg": "#d4af37",  # Gold button
            "button_fg": "#000000",  # Black text on button
            "button_hover": "#ffd700",  # Brighter gold on hover
            "cursor": "#ffd700",  # Gold cursor
            "selection": "#1a3a5c",  # Selection highlight
        }

        self.root.configure(bg=self.colors["bg_main"])

        # Game instance (will store your Game object)
        self.game = None

        # Input handling variables
        self.waiting_for_input = False  # Is the game waiting for user input?
        self.input_callback = None  # Not used in this version
        self.current_input = None  # Stores what the user typed

        # Setup UI
        self.setup_ui()

        # Redirect output (make print() go to GUI)
        self.redirect_output()

    def setup_ui(self):

        # ===== TITLE BAR =====

        title_frame = tk.Frame(self.root, bg=self.colors["bg_title"], height=50)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)  # Don't let contents resize it

        tk.Label(
            title_frame,
            text="⚔️ ONE PIECE TEXT RPG ⚔️",
            font=("Courier New", 16, "bold"),
            bg=self.colors["bg_title"],
            fg=self.colors["text"]
        ).pack(expand=True)

        # ===== CONSOLE DISPLAY AREA =====
        console_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ScrolledText = text area with automatic scrollbar
        self.console = scrolledtext.ScrolledText(
            console_frame,
            font=("Courier New", 10),
            bg=self.colors["bg_console"],  # Console background
            fg=self.colors["text"],  # Text color
            insertbackground=self.colors["cursor"],  # Cursor color
            selectbackground=self.colors["selection"],  # Selection highlight
            wrap=tk.WORD,  # Wrap at word boundaries
            padx=15,
            pady=10
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)  # Read-only (user can't type here)

        # ===== INPUT AREA =====
        input_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Prompt symbol ">"
        tk.Label(
            input_frame,
            text=">",
            font=("Courier New", 12, "bold"),
            bg=self.colors["bg_main"],
            fg=self.colors["text"]
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Text entry box (where user types)
        self.input_entry = tk.Entry(
            input_frame,
            font=("Courier New", 11),
            bg=self.colors["bg_input"],
            fg=self.colors["text"],
            insertbackground=self.colors["cursor"],
            relief=tk.FLAT,
            borderwidth=2
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bind Enter key to submit input
        self.input_entry.bind("<Return>", self.on_enter_pressed)

        # Submit button
        self.submit_btn = tk.Button(
            input_frame,
            text="ENTER",
            font=("Courier New", 10, "bold"),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            activebackground=self.colors["button_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            width=10,
            command=self.on_enter_pressed  # Call this function when clicked
        )
        self.submit_btn.pack(side=tk.LEFT, padx=(8, 0))

        # ===== STATUS BAR =====
        status_frame = tk.Frame(self.root, bg=self.colors["bg_title"], height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Ready to start...",
            font=("Courier New", 9),
            bg=self.colors["bg_title"],
            fg=self.colors["text"],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

    def redirect_output(self):

        sys.stdout = TextRedirector(self)
        sys.stderr = TextRedirector(self)  # Errors too

    def write_to_console(self, text):

        self.console.config(state=tk.NORMAL)  # Allow editing
        if text and not text.endswith('\n'):
            text += '\n'
        self.console.insert(tk.END, text)  # Add text at end
        self.console.see(tk.END)  # Scroll to bottom
        self.console.config(state=tk.DISABLED)  # Make read-only again
        self.root.update_idletasks()  # Force GUI to update now

    def get_input_from_user(self, prompt=""):

        if prompt:
            self.write_to_console(prompt)

        self.waiting_for_input = True
        self.current_input = None
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus()  # Put cursor in input box
        self.status_label.config(text="Waiting for input...")

        # BLOCKING LOOP - waits for user input
        while self.waiting_for_input:
            self.root.update()  # Process GUI events (clicks, typing, etc)

        return self.current_input

    def on_enter_pressed(self, event=None):

        if not self.waiting_for_input:
            return  # Not waiting for input, ignore

        user_input = self.input_entry.get()  # Get text from entry box
        self.input_entry.delete(0, tk.END)  # Clear the box

        # Echo input to console (with newline for spacing!)
        self.write_to_console(user_input + "\n")

        # Store input and stop waiting
        self.current_input = user_input
        self.waiting_for_input = False  # This exits the loop!
        self.status_label.config(text="Processing...")

    def start_game(self):


        def run_game():
            """This runs in a separate thread"""
            try:
                # Create and run your game
                self.game = Game()
                self.game.create_player()
                self.game.start_journey()
                self.game.sailing()
            except Exception as e:
                # If game crashes, show error in GUI
                self.write_to_console(f"\n\nError: {e}\n")
                self.status_label.config(text="Game ended with error")
            else:
                # Game ended normally
                self.write_to_console("\n\nGame ended. Close window to exit.\n")
                self.status_label.config(text="Game ended")


        import builtins
        builtins.input = self.get_input_from_user


        game_thread = threading.Thread(target=run_game, daemon=True)
        game_thread.start()

        self.status_label.config(text="Game running...")


class TextRedirector:

    def __init__(self, gui):
        self.gui = gui

    def write(self, text):
        """
        Called by print() - redirects to GUI.


        """
        if text.strip():  # Only write if not just whitespace
            self.gui.write_to_console(text)

    def flush(self):

        pass


def main():

    root = tk.Tk()
    gui = ConsoleGUI(root)

    # Start game after GUI is ready (100ms delay)
    root.after(100, gui.start_game)

    # Enter the event loop (keeps window open)
    root.mainloop()


if __name__ == "__main__":
    main()

