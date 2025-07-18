import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import csv
import os

DATA_FILE = "storage_data_Original.json"

class StorageMatrix:
    def __init__(self):
        self.locations = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        self.locations += [chr(letter) for letter in range(ord('D'), ord('S'))]  # D to R
        self.storage = self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {loc: {"part": None, "qty": 0} for loc in self.locations}

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.storage, f)

    def place_part(self, part, qty):
        for loc in self.locations:
            if self.storage[loc]["part"] is None:
                self.storage[loc] = {"part": part, "qty": qty}
                return loc
            elif self.storage[loc]["part"] == part:
                self.storage[loc]["qty"] += qty
                return loc
        return None

    def take_part(self, part, qty):
        for loc in self.locations:
            if self.storage[loc]["part"] == part:
                if self.storage[loc]["qty"] > qty:
                    self.storage[loc]["qty"] -= qty
                    return loc
                elif self.storage[loc]["qty"] == qty:
                    self.storage[loc] = {"part": None, "qty": 0}
                    return loc
                else:
                    return "not_enough"
        return None

    def get_data(self):
        return self.storage.copy()

class LeftoverApp:
    def __init__(self, root):
        self.export_filename = "parts_export.csv"
        self.root = root
        self.root.title("Leftover Material Management")
        self.root.attributes('-fullscreen', True)

        self.matrix = StorageMatrix()

        tk.Label(root, text="Leftover Materials", font=("Arial", 24)).pack(pady=20)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Place Part", font=("Arial", 14), width=15, command=self.open_place_popup, bg="lightgreen").pack(side=tk.LEFT, padx=50)
        tk.Button(btn_frame, text="Take Away", font=("Arial", 14), width=15, command=self.open_take_popup, bg="tomato").pack(side=tk.RIGHT, padx=50)
        
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)

        self.slot_labels = {}
        self.build_matrix()

    def build_matrix(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        idx = 0
        # First row: 3 cells each with 2 sections (A1, A2), (B1, B2), (C1, C2)
        for col in range(3):
            cell_frame = tk.Frame(self.grid_frame, bg="black", bd=1, relief="solid")
            cell_frame.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
            self.grid_frame.grid_rowconfigure(0, weight=1)
            self.grid_frame.grid_columnconfigure(col, weight=1)

            left_slot = self.matrix.locations[idx]
            right_slot = self.matrix.locations[idx+1]

            left_label = tk.Frame(cell_frame, bg="lightblue", bd=1, relief="ridge")
            left_content = tk.Label(left_label, text="", bg="lightblue", font=("Arial", 12))
            left_content.pack(expand=True, fill=tk.BOTH)
            left_footer = tk.Label(left_label, text=left_slot, bg="black", fg="white", font=("Arial", 10))
            left_footer.pack(side=tk.BOTTOM, fill=tk.X)
            left_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            right_label = tk.Frame(cell_frame, bg="lightblue", bd=1, relief="ridge")
            right_content = tk.Label(right_label, text="", bg="lightblue", font=("Arial", 12))
            right_content.pack(expand=True, fill=tk.BOTH)
            right_footer = tk.Label(right_label, text=right_slot, bg="black", fg="white", font=("Arial", 10))
            right_footer.pack(side=tk.BOTTOM, fill=tk.X)
            right_label.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            self.slot_labels[left_slot] = left_content
            self.slot_labels[right_slot] = right_content
            idx += 2

        # Remaining rows: single sections D to R
        row = 1
        col = 0
        while idx < len(self.matrix.locations):
            slot = self.matrix.locations[idx]
            label = tk.Frame(self.grid_frame, bg="lightblue", bd=1, relief="solid")
            content_label = tk.Label(label, text="", bg="lightblue", font=("Arial", 14))
            content_label.pack(expand=True, fill=tk.BOTH)
            loc_label = tk.Label(label, text=slot, bg="black", fg="white", font=("Arial", 10))
            loc_label.pack(side=tk.BOTTOM, fill=tk.X)
            label.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            self.slot_labels[slot] = content_label
            self.grid_frame.grid_rowconfigure(row, weight=1)
            self.grid_frame.grid_columnconfigure(col, weight=1)
            # removed duplicate assignment of label to slot_labels

            col += 1
            if col >= 3:
                col = 0
                row += 1
            idx += 1

        self.update_matrix()

    from tkinter import filedialog

    def export_to_excel(self):
        file_path = r"\\BOSCH.COM\DfsRB\DfsIN\LOC\Ja\DS\MFN\01_JaP_MFN\04_mfh1_common\Devanshu Sharma\Leftover App\parts_export_original.csv"  # <-- Change this path to your desired location
    
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Part Number", "Quantity"])
            for item in self.matrix.get_data().values():
                if item['part']:
                    writer.writerow([item['part'], item['qty']])
        messagebox.showinfo("Exported", f"Data exported to {file_path}")

    def update_matrix(self):
        self.export_to_excel()
        self.matrix.save_data()
        data = self.matrix.get_data()
        for loc, label in self.slot_labels.items():
            content = data[loc]
            if content["part"]:
                label.config(text=f"{content['part']} ({content['qty']})", bg="lightgreen")
            else:
                label.config(text="", bg="lightblue")

    def open_place_popup(self):
        self.open_popup("place")

    def open_take_popup(self):
        self.open_popup("take")

    def open_popup(self, action):
        location_var = tk.StringVar()
        popup = tk.Toplevel(self.root)
        popup.title("Enter Part Info")
        popup.geometry("350x280")

        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

        if action == "place":
            tk.Label(popup, text="Select Location:", font=("Arial", 12)).pack(pady=3)
            loc_menu = tk.OptionMenu(popup, location_var, *self.matrix.locations)
            loc_menu.pack(pady=3)

        tk.Label(popup, text="Part Number:", font=("Arial", 12)).pack(pady=5)
        part_entry = tk.Entry(popup, font=("Arial", 12))
        part_entry.pack(pady=5)

        if action == "take":
            def on_keyrelease(event):
                typed = part_entry.get().strip().lower()
                if len(typed) >= 3:
                    matches = [p for p in {v['part'] for v in self.matrix.get_data().values() if v['part']} if p.lower().endswith(typed)]
                    if hasattr(popup, 'dropdown'):
                        popup.dropdown.destroy()
                    if matches:
                        popup.dropdown = tk.Listbox(popup, height=min(len(matches), 5))
                        for m in matches:
                            popup.dropdown.insert(tk.END, m)
                        popup.dropdown.place(x=part_entry.winfo_x(), y=part_entry.winfo_y() + part_entry.winfo_height() + 5)

                        def on_select(evt):
                            selection = popup.dropdown.get(popup.dropdown.curselection())
                            part_entry.delete(0, tk.END)
                            part_entry.insert(0, selection)
                            popup.dropdown.destroy()

                        popup.dropdown.bind("<Double-Button-1>", on_select)
                else:
                    if hasattr(popup, 'dropdown'):
                        popup.dropdown.destroy()

            part_entry.bind("<KeyRelease>", on_keyrelease)

        tk.Label(popup, text="Quantity:", font=("Arial", 12)).pack(pady=5)
        qty_entry = tk.Entry(popup, font=("Arial", 12))
        qty_entry.pack(pady=5)

        def submit():
            part = part_entry.get().strip()
            try:
                qty = int(qty_entry.get().strip())
            except:
                messagebox.showerror("Error", "Quantity must be a number.")
                return

            if not part:
                messagebox.showerror("Error", "Part number required.")
                return

            if action == "place":
                loc_choice = location_var.get()
                if loc_choice != "Auto":
                    if self.matrix.storage[loc_choice]["part"] is None:
                        self.matrix.storage[loc_choice] = {"part": part, "qty": qty}
                        slot = loc_choice
                    elif self.matrix.storage[loc_choice]["part"] == part:
                        self.matrix.storage[loc_choice]["qty"] += qty
                        slot = loc_choice
                    else:
                        messagebox.showerror("Error", f"{loc_choice} already has a different part.")
                        return
                else:
                    slot = self.matrix.place_part(part, qty)
                if slot:
                    messagebox.showinfo("Success", f"Placed in {slot.upper()}")
                else:
                    messagebox.showwarning("Full", "No empty slot available.")
            else:
                result = self.matrix.take_part(part, qty)
                if result == "not_enough":
                    messagebox.showwarning("Not Enough", "Not enough quantity to remove.")
                elif result:
                    messagebox.showinfo("Removed", f"Removed from {result.upper()}")
                else:
                    messagebox.showerror("Not Found", "Part not found.")

            popup.destroy()
            self.update_matrix()

        tk.Button(popup, text="Submit", command=submit, bg="skyblue", font=("Arial", 12)).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LeftoverApp(root)
    root.mainloop()


