import tkinter as tk
import time
import collections

class FPSCounter:
    """
    Measures "frames" (dummy operations/ticks) over a rolling 1-second window.
    This aims to show a fluctuating number representing system responsiveness.
    """
    def __init__(self):
        self.timestamps = collections.deque()
        self.current_fps = 0
        self.is_running = True # Control the internal fast loop

    def run_dummy_loop(self):
        """
        Runs a very fast loop to generate 'ticks' for FPS calculation.
        This method will run in the background.
        """
        while self.is_running:
            now = time.perf_counter()
            self.timestamps.append(now)

            # Remove timestamps older than 1 second
            while self.timestamps and self.timestamps[0] < now - 1.0:
                self.timestamps.popleft()

            self.current_fps = len(self.timestamps) # Number of ticks in the last second

            # Small sleep to prevent 100% CPU usage for the dummy loop
            # Adjust as needed; too low might still use significant CPU.
            # too high, and the FPS will drop significantly.
            time.sleep(0.001) # Sleep for 1 millisecond

    def get_fps(self):
        """
        Returns the calculated FPS.
        """
        return self.current_fps

    def stop(self):
        """
        Stops the internal dummy loop.
        """
        self.is_running = False

def create_overlay_window():
    """
    Creates and configures the Tkinter window for the FPS overlay.
    """
    root = tk.Tk()

    # --- Window Configuration ---
    root.overrideredirect(True)  # Remove window decorations (title bar, borders)
    root.attributes("-topmost", True)  # Keep window on top of others

    # Set a specific background color that will be made transparent on Windows
    transparent_color = 'grey15' # A dark grey
    root.config(bg=transparent_color)
    root.wm_attributes("-transparentcolor", transparent_color)

    # --- Label Configuration ---
    # Changed font size to 12
    fps_label = tk.Label(root,
                         text="FPS: ---", # Use three dashes for higher possible values
                         fg="white",
                         bg=transparent_color,
                         font=("Consolas", 12, "bold"))
    fps_label.pack(expand=True, fill="both", padx=5, pady=2)

    # --- Window Positioning ---
    screen_width = root.winfo_screenwidth()
    window_width = 85 # Adjusted for potentially larger numbers (e.g., 3 digits)
    window_height = 28
    margin = 10
    x_position = screen_width - window_width - margin
    y_position = margin
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    return root, fps_label

def update_display(root, fps_label, fps_counter):
    """
    Updates the FPS display on the label and schedules the next display update.
    The actual FPS calculation is now happening in the background loop.
    """
    # Simply retrieve the current FPS from the background counter
    # Format to an integer. We no longer force two digits as values can be higher.
    fps_label.config(text=f"FPS: {int(fps_counter.get_fps()):d}")

    # Schedule this display update function to run again after 1000 milliseconds (1 second)
    # This is purely for updating the label text, not for running the FPS logic.
    root.after(1000, lambda: update_display(root, fps_label, fps_counter))

# --- Main execution block ---
if __name__ == "__main__":
    import threading # We need threading for the background loop

    # 1. Create the overlay window and get the label object
    root_window, fps_display_label = create_overlay_window()

    # 2. Initialize the FPS counter
    my_fps_counter = FPSCounter()

    # 3. Start the dummy loop in a separate thread
    # This loop will continuously generate 'ticks'
    fps_thread = threading.Thread(target=my_fps_counter.run_dummy_loop, daemon=True)
    fps_thread.start()

    # 4. Start the display update loop for the FPS display
    # This will read the FPS from the counter and update the label every second.
    update_display(root_window, fps_display_label, my_fps_counter)

    # 5. When the Tkinter window closes, tell the background thread to stop
    def on_closing():
        my_fps_counter.stop()
        root_window.destroy()

    root_window.protocol("WM_DELETE_WINDOW", on_closing)

    # 6. Start the Tkinter event loop
    root_window.mainloop()