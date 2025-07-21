import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys

class WaterReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Reminder")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        # System tray icon setup
        self.root.withdraw()  # Hide main window initially
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Reminder settings
        self.reminder_interval_minutes = 60  # Default: 60 minutes
        self.display_duration = 10           # Show icon for 10 seconds
        
        # Create reminder window
        self.create_reminder_window()
        
        # Start reminder thread
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()

    def create_tray_icon(self):
        from pystray import Icon, Menu, MenuItem
        from PIL import Image, ImageDraw
        
        # Create tray icon image
        image = Image.new('RGB', (64, 64), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], fill='blue', outline='lightblue')
        
        # Tray menu
        menu = Menu(
            MenuItem('Show Reminder', self.show_reminder),
            MenuItem('Set Interval', self.set_interval),
            MenuItem('Exit', self.exit_app)
        )
        
        self.tray_icon = Icon("water_reminder", image, "Water Reminder", menu)
        
        # Run tray icon in separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def create_reminder_window(self):
        self.reminder_window = tk.Toplevel(self.root)
        self.reminder_window.overrideredirect(True)  # Remove window decorations
        self.reminder_window.attributes("-topmost", True)  # Always on top
        self.reminder_window.attributes("-alpha", 0.9)  # Slightly transparent
        
        # Create water drop symbol
        self.canvas = tk.Canvas(
            self.reminder_window, 
            width=100, 
            height=100, 
            bg='white',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Draw water drop shape
        self.draw_water_drop()
        
        # Position window at bottom-right corner
        self.position_window()
        
        # Initially hide the window
        self.reminder_window.withdraw()

    def draw_water_drop(self):
        # Draw a blue water drop shape
        self.canvas.create_oval(20, 10, 80, 70, fill='#00BFFF', outline='')
        self.canvas.create_polygon(50, 70, 30, 90, 70, 90, fill='#00BFFF', outline='')

    def position_window(self):
        # Get screen dimensions
        screen_width = self.reminder_window.winfo_screenwidth()
        screen_height = self.reminder_window.winfo_screenheight()
        
        # Set position (bottom-right corner with some margin)
        x = screen_width - 120
        y = screen_height - 120
        
        self.reminder_window.geometry(f"100x100+{x}+{y}")

    def show_reminder(self):
        # Show the reminder window
        self.reminder_window.deiconify()
        
        # Hide after display duration
        self.root.after(self.display_duration * 1000, self.reminder_window.withdraw)

    def reminder_loop(self):
        while True:
            time.sleep(self.reminder_interval_minutes * 60)
            self.root.after(0, self.show_reminder)

    def set_interval(self):
        # Create dialog to set interval
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Reminder Interval")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Reminder Interval (minutes):").pack(pady=10)
        
        entry = tk.Entry(dialog)
        entry.pack(pady=5)
        entry.insert(0, str(self.reminder_interval_minutes))
        
        def save_interval():
            try:
                minutes = int(entry.get())
                if minutes > 0:
                    self.reminder_interval_minutes = minutes
                    dialog.destroy()
                else:
                    messagebox.showerror("Invalid Input", "Please enter a positive number")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number")
        
        tk.Button(dialog, text="Save", command=save_interval).pack(pady=10)

    def exit_app(self):
        self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterReminderApp(root)
    root.mainloop()