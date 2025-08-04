import tkinter as tk
from tkinter import messagebox, filedialog
import pyautogui
import time
import threading
import keyboard


class AutoTypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CKBsolution")
        
        # Set icon (optional)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Create widgets for the GUI
        self.create_widgets()


        # To control whether typing is running
        self.typing_in_progress = False


    def create_widgets(self):
        # Speed control label and entry
        self.speed_label = tk.Label(self.root, text="Typing Speed (ms per character):")
        self.speed_label.pack(pady=5)
        
        self.speed_entry = tk.Entry(self.root)
        self.speed_entry.insert(0, "100") # Default speed
        self.speed_entry.pack(pady=5)


        # Delay before start label and entry
        self.delay_label = tk.Label(self.root, text="Delay Before Start (seconds):")
        self.delay_label.pack(pady=5)
        
        self.delay_entry = tk.Entry(self.root)
        self.delay_entry.insert(0, "2") # Default delay
        self.delay_entry.pack(pady=5)


        # File input (Upload file)
        self.upload_button = tk.Button(self.root, text="Upload Text File", command=self.upload_file)
        self.upload_button.pack(pady=10)


        # Start button
        self.start_button = tk.Button(self.root, text="Start Typing", command=self.start_typing)
        self.start_button.pack(pady=10)


        # Emergency Stop button
        self.stop_button = tk.Button(self.root, text="Stop Typing", command=self.stop_typing)
        self.stop_button.pack(pady=10)


    def upload_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.filepath:
            with open(self.filepath, "r") as file:
                self.text_to_type = file.read()


    def start_typing(self):
        if not hasattr(self, 'text_to_type'):
            messagebox.showerror("Error", "Please upload a text file first.")
            return
        
        # Validate the speed and delay inputs
        try:
            self.speed = int(self.speed_entry.get())
            self.delay = int(self.delay_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Speed and Delay must be valid integers.")
            return


        if self.speed <= 0:
            messagebox.showerror("Input Error", "Speed must be greater than 0.")
            return


        # Prevent typing if already typing
        if self.typing_in_progress:
            return
        
        # Start typing in a new thread to prevent freezing the GUI
        self.typing_in_progress = True
        threading.Thread(target=self.type_text).start()


    def type_text(self):
        time.sleep(self.delay)
        for char in self.text_to_type:
            if self.typing_in_progress:
                pyautogui.write(char, interval=self.speed / 1000) # Convert to seconds
                time.sleep(0.1) # Small pause to simulate human typing
                if keyboard.is_pressed("esc"):
                    self.stop_typing()
                    break
            else:
                break


    def stop_typing(self):
        self.typing_in_progress = False


# Initialize the GUI window
root = tk.Tk()
app = AutoTypingApp(root)


# Run the GUI main loop
root.mainloop()

