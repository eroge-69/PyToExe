#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import sys

class MultiPopupApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.running = True
        self.popup_count = 0
        self.max_popups = 5  # Number of popups to show simultaneously
        
    def create_popup(self, message, x_pos, y_pos):
        """Create a single popup window at specified position"""
        popup = tk.Toplevel(self.root)
        popup.title("Notification")
        popup.geometry(f"+{x_pos}+{y_pos}")
        popup.attributes('-topmost', True)
        
        label = tk.Label(popup, text=message, padx=20, pady=20)
        label.pack()
        
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)
        
        # Auto-close after 3 seconds
        popup.after(3000, popup.destroy)
        return popup
    
    def show_multiple_popups(self):
        """Show multiple popups at random positions"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        messages = [
            "Fuck you Clark",
            "Small Dick ahhh",
            "You've been poop cupped",
            "Fuck youuuuuuuuuu",
            "Messed with the wrong person",
            "Good Luck stopping this",
	    "Bitch made boy",
	    "Suckaaaaaaa",
	    "Stay Tf out my room bitch"
        ]
        
        for i in range(self.max_popups):
            if not self.running:
                break
                
            x_pos = random.randint(50, screen_width - 300)
            y_pos = random.randint(50, screen_height - 200)
            message = random.choice(messages)
            
            self.create_popup(message, x_pos, y_pos)
            self.popup_count += 1
            time.sleep(0.1)  # Small delay between creating popups
    
    def start_popup_loop(self, interval=500):
        """Start the popup loop"""
        def popup_loop():
            while self.running:
                self.show_multiple_popups()
                time.sleep(interval / 1000)  # Convert ms to seconds
        
        thread = threading.Thread(target=popup_loop, daemon=True)
        thread.start()
        
        print(f"Showing {self.max_popups} popups every {interval}ms")
        print("Press Ctrl+C to stop...")
        
        self.root.mainloop()
    
    def stop(self):
        """Stop the application"""
        self.running = False
        self.root.quit()
        self.root.destroy()

def main():
    app = MultiPopupApp()
    
    try:
        # Start showing multiple popups every 500ms
        app.start_popup_loop(interval=500)
    except KeyboardInterrupt:
        print("\nStopping popups...")
        app.stop()
    except Exception as e:
        print(f"Error: {e}")
        app.stop()

if __name__ == "__main__":
    main()
