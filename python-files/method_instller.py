import tkinter as tk
from tkinter import ttk, messagebox
import random

class InstallerForm:
    def __init__(self, root):
        self.root = root
        self.current_progress = 0.0
        
        # --- Configuration ---
        # Total time for 100% would be 12 minutes (720 seconds).
        # We fail at 73%, which will happen at around the 8.7 minute mark.
        total_duration_seconds = 720
        self.timer_interval_ms = 100
        total_ticks = (total_duration_seconds * 1000) / self.timer_interval_ms
        self.progress_increment = 100.0 / total_ticks

        self.initialize_status_messages()
        self.initialize_components()

    def initialize_status_messages(self):
        # A list of believable installation status messages.
        self.status_messages = [
            "Initializing setup...",
            "Checking system requirements...",
            "Unpacking files: core_engine.dat",
            "Unpacking files: assets_01.pak",
            "Configuring environment variables...",
            "Writing to registry: HKLM\\Software\\Venv\\",
            "Installing DirectX components...",
            "Decompressing krak pack...",
            "Copying files to installation directory...",
            "Creating program shortcuts...",
            "Registering components...",
            "Verifying file integrity...",
            "Installing dependencies...",
            "Unpacking files: level_data.bin",
            "Finalizing installation..."
        ]

    def initialize_components(self):
        # --- Form Setup ---
        self.root.title("Venv Puzzle Game - Installation")
        self.root.geometry("500x190") # Slightly adjusted height for better fit
        self.root.resizable(False, False)
        self.root.configure(bg="#F0F0F0")

        # Center the window on the screen
        window_width = 500
        window_height = 190
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(
            self.root, 
            orient="horizontal", 
            length=420, 
            mode="determinate"
        )
        self.progress_bar.place(x=30, y=40, height=30)

        # --- Status Label (e.g., "Unpacking files...") ---
        self.status_label_var = tk.StringVar(value="Starting installation...")
        self.status_label = tk.Label(
            self.root, 
            textvariable=self.status_label_var, 
            anchor="w", 
            bg="#F0F0F0",
            font=("Segoe UI", 9)
        )
        self.status_label.place(x=30, y=80, width=380, height=20)
        
        # --- Percentage Label (e.g., "0%") ---
        self.percentage_label_var = tk.StringVar(value="0%")
        self.percentage_label = tk.Label(
            self.root, 
            textvariable=self.percentage_label_var, 
            anchor="e", 
            bg="#F0F0F0",
            font=("Segoe UI", 9, "bold")
        )
        self.percentage_label.place(x=410, y=80, width=40, height=20)

        # --- Cancel Button ---
        self.cancel_button = tk.Button(
            self.root, 
            text="Cancel", 
            command=self.root.destroy,
            font=("Segoe UI", 9)
        )
        self.cancel_button.place(x=370, y=120, width=80, height=30)

        # --- Start the timer loop ---
        self.root.after(self.timer_interval_ms, self.update_progress)

    def update_progress(self):
        self.current_progress += self.progress_increment
        
        if int(self.current_progress) >= 73:
            # --- Failure Condition ---
            self.progress_bar["value"] = 73
            self.percentage_label_var.set("73%")
            self.status_label_var.set("A critical error occurred.")
            self.cancel_button.config(state="disabled")

            # Display the metaphorical runtime error message
            error_title = "Runtime Error"
            error_message = (
                "Program: C:\\Program Files (x86)\\Venv\\PuzzleGame\\launch.exe\n\n"
                "R6025\n"
                "- pure virtual function call"
            )
            messagebox.showerror(error_title, error_message)
            
            # After the user clicks OK, close the installer.
            self.root.destroy()
        else:
            # --- Normal Progress Update ---
            progress_int = int(self.current_progress)
            self.progress_bar["value"] = progress_int
            self.percentage_label_var.set(f"{progress_int}%")
            
            # Update the status message every so often to look realistic
            if random.randint(0, 14) == 1: # 1 in 15 chance each tick
                new_status = random.choice(self.status_messages)
                self.status_label_var.set(new_status)
            
            # Schedule the next update
            self.root.after(self.timer_interval_ms, self.update_progress)


if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerForm(root)
    root.mainloop()