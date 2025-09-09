import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import csv
import os
import sys
import schedule
import time

try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

class LockScreenApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the window initially
        self.lock_file = 'lock_screen.lock'

        # Check for lock file to prevent multiple instances
        if os.path.exists(self.lock_file):
            print("Lock screen is already running.")
            sys.exit(0)
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))

        self.is_locked = False
        self.screen_width = None
        self.screen_height = None
        self.bg_image = None
        self.canvas = None
        self.label = None
        self.id_entry = None
        self.error_label = None
        self.submit_button = None

        # Schedule the lock screen to run every 10 minutes
        schedule.every(0.1).minutes.do(self.show_lock_screen)

        # Run the lock screen immediately on startup
        self.show_lock_screen()

        # Start the scheduling loop
        self.run_scheduler()

    def show_lock_screen(self):
        if self.is_locked:
            return  # Skip if already locked
        self.is_locked = True

        # Configure root window for lock screen
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.root.bind('<Return>', lambda event: self.unlock())
        self.root.deiconify()  # Show the window

        # Create canvas for background image and widgets
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Resolve path to background.png
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_path, 'background.jpeg')

        # Load and set background image
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        try:
            if PILLOW_AVAILABLE:
                image = Image.open(image_path)
                image = image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(image)
            else:
                self.bg_image = tk.PhotoImage(file=image_path)
            self.canvas.create_image(self.screen_width//2, self.screen_height//2, image=self.bg_image, anchor='center')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background.png: {str(e)}\nUsing plain background.")
            self.canvas.configure(bg='black')

        # Create semi-transparent rectangle
        self.canvas.create_rectangle(
            self.screen_width//2 - 200, self.screen_height//2 - 150,
            self.screen_width//2 + 200, self.screen_height//2 + 150,
            fill='white',
            outline=''
        )

        # Widgets
        self.label = tk.Label(self.root, text="Enter your 6 or 9-digit ID:", font=("Arial", 20), bg='white', fg='black')
        self.canvas.create_window(self.screen_width//2, self.screen_height//2 - 60, window=self.label)

        self.id_entry = tk.Entry(self.root, font=("Arial", 16), width=20, bg='white', fg='black', insertbackground='black')
        self.canvas.create_window(self.screen_width//2, self.screen_height//2, window=self.id_entry)
        self.id_entry.focus_set()

        self.error_label = tk.Label(self.root, text="", font=("Arial", 14), bg='white', fg='red')
        self.canvas.create_window(self.screen_width//2, self.screen_height//2 + 40, window=self.error_label)

        self.submit_button = tk.Button(self.root, text="Submit", font=("Arial", 16), bg='white', fg='black', command=self.unlock)
        self.canvas.create_window(self.screen_width//2, self.screen_height//2 + 80, window=self.submit_button)

    def disable_event(self):
        pass

    def unlock(self):
        user_id = self.id_entry.get().strip()
        if self.validate_id(user_id):
            self.log_id(user_id)
            # Clean up widgets and hide window
            self.canvas.destroy()
            self.label.destroy()
            self.id_entry.destroy()
            self.error_label.destroy()
            self.submit_button.destroy()
            self.root.withdraw()
            self.is_locked = False
        else:
            self.error_label.config(text="Invalid ID! Must be 6 or 9 digits.")

    def validate_id(self, user_id):
        return user_id.isdigit() and len(user_id) in (6, 9)

    def log_id(self, user_id):
        file_exists = os.path.isfile('id_log.csv')
        with open('id_log.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['Timestamp', 'ID'])
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id])

    def run_scheduler(self):
        # Run scheduler tasks and recheck every 1000ms
        schedule.run_pending()
        self.root.after(1000, self.run_scheduler)

    def cleanup(self):
        # Remove lock file on exit
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)

def main():
    root = tk.Tk()
    app = LockScreenApp(root)
    try:
        root.mainloop()
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()