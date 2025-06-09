import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import json

SAVE_FILE = "strips.json"

class FlightStripApp:
    def __init__(self, root):
        self.root = root
        root.title("Flight Strip App")
        root.geometry("800x600")

        self.left_list = tk.Listbox(root, width=40, height=25)
        self.right_list = tk.Listbox(root, width=40, height=25)
        self.left_list.grid(row=1, column=0, padx=10, pady=10)
        self.right_list.grid(row=1, column=1, padx=10, pady=10)

        self.left_list.bind('<ButtonPress-1>', self.start_drag)
        self.left_list.bind('<B1-Motion>', self.do_drag)
        self.left_list.bind('<ButtonRelease-1>', self.drop_item)

        self.right_list.bind('<ButtonPress-1>', self.start_drag)
        self.right_list.bind('<B1-Motion>', self.do_drag)
        self.right_list.bind('<ButtonRelease-1>', self.drop_item)

        entry_frame = tk.Frame(root)
        entry_frame.grid(row=0, column=0, columnspan=2, pady=5)

        self.entry = tk.Entry(entry_frame, width=80)
        self.entry.pack(side=tk.LEFT, padx=5)
        tk.Button(entry_frame, text="Hinzufügen", command=self.add_item).pack(side=tk.LEFT)

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=2, column=0, columnspan=2)

        tk.Button(btn_frame, text="Bearbeiten", command=self.edit_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Löschen", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Speichern", command=self.save_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Laden", command=self.load_data).pack(side=tk.LEFT, padx=5)

        self.drag_data = {"widget": None, "index": None}
        self.load_data()

    def get_selected_list(self):
        if self.left_list.curselection():
            return self.left_list
        elif self.right_list.curselection():
            return self.right_list
        return None

    def add_item(self):
        text = self.entry.get().strip()
        if not text:
            return
        text = text[:100]
        self.left_list.insert(tk.END, text)
        self.entry.delete(0, tk.END)

    def delete_item(self):
        lst = self.get_selected_list()
        if lst:
            index = lst.curselection()
            if index:
                lst.delete(index)

    def edit_item(self):
        lst = self.get_selected_list()
        if lst:
            index = lst.curselection()
            if index:
                old = lst.get(index)
                new = simpledialog.askstring("Bearbeiten", "Neuer Text:", initialvalue=old)
                if new:
                    lst.delete(index)
                    lst.insert(index, new[:100])

    def save_data(self):
        data = {
            "left": list(self.left_list.get(0, tk.END)),
            "right": list(self.right_list.get(0, tk.END)),
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        messagebox.showinfo("Gespeichert", "Strips wurden gespeichert.")

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.left_list.delete(0, tk.END)
            self.right_list.delete(0, tk.END)
            for item in data.get("left", []):
                self.left_list.insert(tk.END, item)
            for item in data.get("right", []):
                self.right_list.insert(tk.END, item)

    def start_drag(self, event):
        widget = event.widget
        index = widget.nearest(event.y)
        self.drag_data["widget"] = widget
        self.drag_data["index"] = index

    def do_drag(self, event):
        # Optional: visual feedback could be added here
        pass

    def drop_item(self, event):
        widget = event.widget
        data_widget = self.drag_data["widget"]
        index = self.drag_data["index"]
        if data_widget and index is not None:
            item_text = data_widget.get(index)
            data_widget.delete(index)
            widget.insert(tk.END, item_text)
        self.drag_data = {"widget": None, "index": None}

if __name__ == "__main__":
    root = tk.Tk()
    app = FlightStripApp(root)
    root.mainloop()

