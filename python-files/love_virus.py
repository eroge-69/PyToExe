import tkinter as tk
from tkinter import messagebox
import time
import os

class LoveVirus:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

    def show_error(self, title, message, icon=messagebox.ERROR):
        return messagebox.askyesno(title, message, icon=icon)

    def show_message(self, title, message, icon=messagebox.INFO):
        messagebox.showinfo(title, message, icon=icon)

    def run(self):
        no_messages = [
            "Are you sure? You'll break my heart! <3",
            "Please? I promise to be good! :D",
            "Don't you want to see what happens if you click Yes? ^_^",
            "The No button is just for decoration! :3",
            "You're really going to say No? (T_T)",
            "Fine, be that way! But you'll miss out on the fun! :P",
            "Last chance to click Yes! <3",
            "You're breaking my virtual heart! :(",
            "The Yes button is much more fun! :D",
            "Are you really sure? Think about it! ^_^"
        ]
        
        message = "Do you want to continue spreading love? <3"
        no_count = 0
        
        while True:
            if self.show_error("System Error", message):
                # If they click Yes, show a happy message and exit
                self.show_message("System Error", "Yay! You're the best! <3", messagebox.ERROR)
                time.sleep(1)
                self.show_message("Goodbye", "Thanks for playing! <3", messagebox.INFO)
                self.root.quit()
                os._exit(0)
            else:
                # If they click No, show a convincing message
                if no_count < len(no_messages):
                    message = no_messages[no_count]
                    no_count += 1
                else:
                    # If we've shown all messages, start over
                    no_count = 0
                    message = no_messages[0]
            
            time.sleep(0.5)

if __name__ == "__main__":
    virus = LoveVirus()
    virus.run() 