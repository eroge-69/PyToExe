import tkinter as tk
from tkinter import ttk, messagebox
import random
import sys

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Venv Puzzle Game - Installation")
        self.root.geometry("500x190")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.configure(bg='#F0F0F0')

        # --- Configuration ---
        # Using a shorter duration for faster testing
        # Total time for 100% would be 12 minutes (720 seconds).
        # We fail at 73%, which will happen at around the 8.7 minute mark.
        total_duration_seconds = 720
        self.timer_interval_milliseconds = 100
        total_ticks = (total_duration_seconds * 1000) / self.timer_interval_milliseconds
        self.progress_increment = 100.0 / total_ticks
        self.current_progress = 0.0
        
        # This will hold the .after() job id
        self.update_job = None

        self.initialize_status_messages()
        self.create_widgets()
        self.update_progress()

    def initialize_status_messages(self):
        """A list of believable installation status messages."""
        self.status_messages = [
            "Initializing setup...",
            "Checking system requirements...",
            "Unpacking files: core_engine.dat",
            "Unpacking files: assets_01.pak",
            "Configuring environment variables...",
            "Writing to registry: HKLM\\Software\\Venv\\PuzzleGame",
            "Installing DirectX components...",
            "Decompressing texture pack (high_res)...",
            "Copying game files to installation directory...",
            "Creating program shortcuts...",
            "Registering components...",
            "Verifying file integrity...",
            "Installing audio drivers...",
            "Unpacking files: level_data.bin",
            "Finalizing installation..."
        ]

    def create_widgets(self):
        """Create and layout the GUI elements."""
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=420, mode='determinate')
        self.progress_bar.pack(pady=10)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, expand=True)

        self.status_label = ttk.Label(status_frame, text="Starting installation...")
        self.status_label.pack(side=tk.LEFT, pady=5)
        
        self.percentage_label = ttk.Label(status_frame, text="0%")
        self.percentage_label.pack(side=tk.RIGHT, pady=5)

        self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self.on_closing)
        self.cancel_button.place(x=380, y=110, width=80, height=30)
        
    def update_progress(self):
        """Periodically updates the progress bar and checks for failure."""
        self.current_progress += self.progress_increment
        
        if int(self.current_progress) >= 73:
            self.progress_bar['value'] = 73
            self.percentage_label.config(text="73%")
            self.status_label.config(text="A critical error occurred.")
            self.cancel_button.config(state=tk.DISABLED)

            error_message = ("Program: C:\\Program Files (x86)\\Venv\\PuzzleGame\\launch.exe\n\n"
                             "R6025\n"
                             "- pure virtual function call")
            messagebox.showerror("Runtime Error", error_message)
            self.on_closing()
        else:
            self.progress_bar['value'] = self.current_progress
            self.percentage_label.config(text=f"{int(self.current_progress)}%")

            if random.randint(0, 14) == 1:
                self.status_label.config(text=random.choice(self.status_messages))
            
            # Schedule the next update
            self.update_job = self.root.after(self.timer_interval_milliseconds, self.update_progress)

    def on_closing(self):
        """Handle the window closing event."""
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.root.destroy()


def main():
    """Main function to run the application."""
    try:
        root = tk.Tk()
        # --- KEY CHANGE ---
        # Hide the window until the app is fully initialized
        root.withdraw() 
        app = InstallerApp(root)
        # Show the window now that everything is set up
        root.deiconify() 
        root.mainloop()
    except Exception as e:
        # If there's an error, write it to a file for debugging
        with open("error_log.txt", "w") as f:
            f.write(f"An error occurred: {str(e)}\n")
            import traceback
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()

