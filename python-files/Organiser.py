import tkinter as tk
from tkinter import simpledialog, colorchooser

class CalendarApp:
    def __init__(self, root):
        self.root = root
    
        for i, day in enumerate(self.days):
            label = tk.Label(root, text=day)
            label.grid(row=0, column=i+1)

        self.add_button = tk.Button(root, text="+", command=self.add_entry)
        self.add_button.grid(row=1, column=0)

        self.entries = {}

    def add_entry(self):
        name = simpledialog.askstring("Person hinzufügen", "Name der Person:")
        if not name:
            return
        
        color = colorchooser.askcolor()[1]
        if not color:
            return

        new_row = len(self.entries) + 1
        for i, day in enumerate(self.days):
            self.entries[(new_row, i+1)] = tk.Text(self.root, width=10, height=2, bg=color)
            self.entries[(new_row, i+1)].grid(row=new_row, column=i+1)

        label = tk.Label(self.root, text=name, bg=color)
        label.grid(row=new_row, column=0)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
