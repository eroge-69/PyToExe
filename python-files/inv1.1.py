import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json

CONFIG_FILE = "config.json"

class TextBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Box Writer")
        self.root.geometry("800x600")  # bigger window on startup

        # Storage
        self.entries = []
        self.entry_limit = 20
        self.max_chars = 250
        self.current_index = -1
        self.save_path = os.getcwd()

        # Load config if exists
        self.box_counter = 1
        self.load_config()

        # --- Widgets ---

        # Foldername label (static text)
        self.foldername_label = tk.Label(root, text="Foldername", font=("Arial", 14, "bold"))
        self.foldername_label.pack(pady=5)

        # Text input field
        self.text_input = tk.Entry(root, width=60, font=("Arial", 16))
        self.text_input.pack(pady=10)
        self.text_input.bind("<Return>", self.add_or_update_entry)

        # Navigation buttons under text input
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=10)

        self.prev_button = tk.Button(nav_frame, text="Previous", command=self.show_previous, state=tk.DISABLED, font=("Arial", 12))
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(nav_frame, text="Next", command=self.show_next, state=tk.DISABLED, font=("Arial", 12))
        self.next_button.pack(side=tk.LEFT, padx=10)

        # Entry and Box labels
        self.entry_label = tk.Label(root, text=f"Current Entry: 0/{self.entry_limit}", font=("Arial", 12))
        self.entry_label.pack()

        self.box_label = tk.Label(root, text=f"Current Box: {self.box_counter}", font=("Arial", 12))
        self.box_label.pack()

        # Manual box number input
        box_frame = tk.Frame(root)
        box_frame.pack(pady=10)

        self.box_entry = tk.Entry(box_frame, width=10, font=("Arial", 12))
        self.box_entry.pack(side=tk.LEFT, padx=5)

        self.set_box_button = tk.Button(box_frame, text="Set Box Number", command=self.set_box_number, font=("Arial", 12))
        self.set_box_button.pack(side=tk.LEFT, padx=5)

        # Path label
        self.path_label = tk.Label(root, text=f"Save Path: {self.save_path}", wraplength=600, justify="left", font=("Arial", 10))
        self.path_label.pack(pady=10)

        # Bottom frame for left/right controls
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=20)

        # Left: Choose Save Folder
        self.path_button = tk.Button(bottom_frame, text="Choose Save Folder", command=self.choose_path, font=("Arial", 12))
        self.path_button.pack(side=tk.LEFT)

        # Right: Next Box
        self.next_box_button = tk.Button(bottom_frame, text="Next Box", command=self.save_box, font=("Arial", 14, "bold"))
        self.next_box_button.pack(side=tk.RIGHT)

        # Save config on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def choose_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.config(text=f"Save Path: {self.save_path}")
            self.save_config()

    def set_box_number(self):
        try:
            new_number = int(self.box_entry.get().strip())
            if new_number <= 0:
                raise ValueError
            self.box_counter = new_number
            self.box_label.config(text=f"Current Box: {self.box_counter}")
            self.save_config()
            messagebox.showinfo("Box Number Updated", f"Box number set to {self.box_counter}")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer.")

    def add_or_update_entry(self, event=None):
        text = self.text_input.get().strip()

        if len(text) == 0:
            messagebox.showwarning("Warning", "Cannot add empty text.")
            return

        if len(text) > self.max_chars:
            messagebox.showwarning("Warning", f"Text must be at most {self.max_chars} characters.")
            return

        if 0 <= self.current_index < len(self.entries):
            self.entries[self.current_index] = text
        else:
            if len(self.entries) >= self.entry_limit:
                messagebox.showinfo("Info", "Entry limit reached. Please save the box before adding more.")
                return
            self.entries.append(text)
            self.current_index = len(self.entries) - 1

        if self.current_index < len(self.entries) - 1:
            self.current_index += 1
            self.text_input.delete(0, tk.END)
            self.text_input.insert(0, self.entries[self.current_index])
        else:
            if len(self.entries) < self.entry_limit:
                self.current_index = len(self.entries)
                self.text_input.delete(0, tk.END)
            else:
                self.text_input.delete(0, tk.END)

        self.update_labels()
        self.update_nav_buttons()

    def save_box(self):
        if not self.entries:
            messagebox.showwarning("Warning", "No entries to save.")
            return

        filename = os.path.join(self.save_path, f"box{self.box_counter}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.entries))

        messagebox.showinfo("Saved", f"Saved {len(self.entries)} entries to {filename}")

        self.entries = []
        self.current_index = -1
        self.update_labels()
        self.box_counter += 1
        self.box_label.config(text=f"Current Box: {self.box_counter}")
        self.update_nav_buttons()
        self.text_input.delete(0, tk.END)

        self.save_config()

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.text_input.delete(0, tk.END)
            self.text_input.insert(0, self.entries[self.current_index])
        self.update_nav_buttons()

    def show_next(self):
        if self.current_index < len(self.entries) - 1:
            self.current_index += 1
            self.text_input.delete(0, tk.END)
            self.text_input.insert(0, self.entries[self.current_index])
        elif self.current_index == len(self.entries) - 1 and len(self.entries) < self.entry_limit:
            self.current_index += 1
            self.text_input.delete(0, tk.END)
        self.update_nav_buttons()

    def update_labels(self):
        self.entry_label.config(text=f"Current Entry: {len(self.entries)}/{self.entry_limit}")

    def update_nav_buttons(self):
        if self.entries:
            self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            if self.current_index < len(self.entries) - 1 or (self.current_index == len(self.entries) - 1 and len(self.entries) < self.entry_limit):
                self.next_button.config(state=tk.NORMAL)
            else:
                self.next_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)

    def save_config(self):
        config = {
            "save_path": self.save_path,
            "box_counter": self.box_counter
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.save_path = config.get("save_path", self.save_path)
                    self.box_counter = config.get("box_counter", self.box_counter)
            except Exception:
                pass

    def on_close(self):
        self.save_config()
        self.root.destroy()


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TextBoxApp(root)
    root.mainloop()
