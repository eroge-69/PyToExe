# 2D Game Editor with Tkinter

import tkinter as tk
from tkinter import simpledialog, messagebox
import os

class GameEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("2D Game Editor")
        self.canvas = tk.Canvas(master, width=800, height=600, bg='white')
        self.canvas.pack()
        
        self.squares = []
        self.create_buttons()

    def create_buttons(self):
        button_frame = tk.Frame(self.master)
        button_frame.pack()

        add_square_btn = tk.Button(button_frame, text="Add Square", command=self.add_square)
        add_square_btn.pack(side=tk.LEFT)

        save_script_btn = tk.Button(button_frame, text="Save Script", command=self.save_script)
        save_script_btn.pack(side=tk.LEFT)

        open_editor_btn = tk.Button(button_frame, text="Open in VS Code", command=self.open_in_vscode)
        open_editor_btn.pack(side=tk.LEFT)

    def add_square(self):
        x = simpledialog.askinteger("Input", "Enter x coordinate:")
        y = simpledialog.askinteger("Input", "Enter y coordinate:")
        size = simpledialog.askinteger("Input", "Enter size:")
        square = self.canvas.create_rectangle(x, y, x + size, y + size, fill='blue')
        self.squares.append((x, y, size))

    def save_script(self):
        script_content = "import tkinter as tk\n\n"
        script_content += "def create_squares(canvas):\n"
        for (x, y, size) in self.squares:
            script_content += f"    canvas.create_rectangle({x}, {y}, {x + size}, {y + size}, fill='blue')\n"
        
        with open("game_script.py", "w") as script_file:
            script_file.write(script_content)
        messagebox.showinfo("Info", "Script saved as game_script.py")

    def open_in_vscode(self):
        os.system("code game_script.py")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameEditor(root)
    root.mainloop()
