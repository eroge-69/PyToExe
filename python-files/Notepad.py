import tkinter as tk
from tkinter import filedialog, messagebox
import os
import winsound

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Hacker's Notepad")
        self.root.configure(bg="#2b2b2b")  # Set the background color to dark gray
        self.text_area = tk.Text(self.root, bg="#2b2b2b", fg="#00ff00", insertbackground="#00ff00", font=("Courier New", 14))
        self.text_area.pack(fill=tk.BOTH, expand=1)
        self.file_name = None
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.file_name = None

    def open_file(self):
        self.file_name = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]
        )
        if self.file_name:
            self.text_area.delete(1.0, tk.END)
            with open(self.file_name, "r") as f:
                self.text_area.insert(1.0, f.read())

    def save_file(self):
        if self.file_name:
            with open(self.file_name, "w") as f:
                f.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_as_file()

    def save_as_file(self):
        self.file_name = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]
        )
        if self.file_name:
            with open(self.file_name, "w") as f:
                f.write(self.text_area.get(1.0, tk.END))

    def key_press(self, event):
        self.text_area.after(100, self.play_click_sound)

    def play_click_sound(self):
        winsound.Beep(2500, 100)  # Make a beep sound at 2500 Hz for 100 ms

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set the initial window size
    notepad = Notepad(root)
    notepad.text_area.bind("<Key>", notepad.key_press)
    root.mainloop()