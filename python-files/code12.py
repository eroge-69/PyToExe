import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import csv
import math
import os

class CSVComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparison of Pick and Place CSV Data (Angle Comparison)")

        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        self.load_start_button = tk.Button(root, text="Load Start-Data", command=self.load_start_file)
        self.load_start_button.pack(pady=5)

        self.load_import_button = tk.Button(root, text="Load import-Data", command=self.load_import_file)
        self.load_import_button.pack(pady=5)

        self.compare_button = tk.Button(root, text="Compare", command=self.compare_angles)
        self.compare_button.pack(pady=5)

        self.save_button = tk.Button(root, text="Save modified Start Data", command=self.save_modified_start_file)
        self.save_button.pack(pady=5)

        self.start_file_path = None
        self.import_file_path = None
        self.start_angles = {}
        self.import_angles = {}

    def calculate_angle(self, cx, cy, px, py):
        try:
            dx = float(px) - float(cx)
            dy = float(py) - float(cy)
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            return round(angle_deg, 2)
        except:
            return None

    def parse_csv(self, file_path):
        designator_angle_map = {}
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                lines = csvfile.readlines()

            header_index = None
            for i, line in enumerate(lines):
                if line.strip().startswith('"Designator"'):
                    header_index = i
                    break

            if header_index is None:
                return {}, lines, None

            reader = csv.reader(lines[header_index:])
            headers = next(reader)

            for row in reader:
                if len(row) >= 10:
                    designator = row[0].strip('"')
                    angle = self.calculate_angle(row[3], row[4], row[8], row[9])
                    if angle is not None:
                        designator_angle_map[designator] = angle
            return designator_angle_map, lines, header_index
        except Exception as e:
            messagebox.showerror("Error reading the Data", str(e))
            return {}, [], None

    def load_start_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")], title="Choose Start")
        if not file_path:
            return
        self.start_file_path = file_path
        self.start_angles, self.start_lines, self.start_header_index = self.parse_csv(file_path)
        messagebox.showinfo("Startdatei geladen", f"Startdatei erfolgreich geladen:\n{os.path.basename(file_path)}")

    def load_import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")], title="Wähle Importdatei")
        if not file_path:
            return
        self.import_file_path = file_path
        self.import_angles, _, _ = self.parse_csv(file_path)
        messagebox.showinfo("Importdatei geladen", f"Importdatei erfolgreich geladen:\n{os.path.basename(file_path)}")

    def compare_angles(self):
        if not self.start_file_path or not self.import_file_path:
            messagebox.showerror("Fehler", "Bitte zuerst Start- und Importdatei laden.")
            return

        all_designators = sorted(set(self.start_angles.keys()).union(self.import_angles.keys()))

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("Designator", os.path.basename(self.start_file_path), os.path.basename(self.import_file_path))
        self.tree["show"] = "headings"

        self.tree.heading("Designator", text="Designator")
        self.tree.heading(os.path.basename(self.start_file_path), text=f"Winkel {os.path.basename(self.start_file_path)} (°)")
        self.tree.heading(os.path.basename(self.import_file_path), text=f"Winkel {os.path.basename(self.import_file_path)} (°)")

        self.tree.column("Designator", width=120)
        self.tree.column(os.path.basename(self.start_file_path), width=150)
        self.tree.column(os.path.basename(self.import_file_path), width=150)

        for des in all_designators:
            angle1 = self.start_angles.get(des, "")
            angle2 = self.import_angles.get(des, "")
            item_id = self.tree.insert("", "end", values=(des, angle1, angle2))
            if angle1 != "" and angle2 != "" and angle1 != angle2:
                self.tree.item(item_id, tags=("changed",))

        self.tree.tag_configure("changed", background="#ffcccc")

    def save_modified_start_file(self):
        if not self.start_file_path or not self.import_file_path:
            messagebox.showerror("Fehler", "Bitte zuerst Start- und Importdatei laden.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")], title="Speichere modifizierte Startdatei")
        if not save_path:
            return

        try:
            with open(save_path, 'w', newline='', encoding='utf-8') as outfile:
                for i, line in enumerate(self.start_lines):
                    if i <= self.start_header_index:
                        outfile.write(line)
                    else:
                        row = next(csv.reader([line]))
                        if len(row) >= 10:
                            designator = row[0].strip('"')
                            original_rotation = row[5]
                            try:
                                original_rotation_val = float(original_rotation)
                                angle_start = self.start_angles.get(designator)
                                angle_import = self.import_angles.get(designator)
                                if angle_start is not None and angle_import is not None:
                                    delta = angle_import - angle_start
                                    new_rotation = int(round(original_rotation_val - delta))
                                    row[5] = str(new_rotation)
                            except:
                                pass
                        quoted_row = ['"{}"'.format(cell.strip('"')) for cell in row]
                        outfile.write(','.join(quoted_row) + '\n')

            messagebox.showinfo("Datei gespeichert", f"Modifizierte Startdatei gespeichert:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))

# GUI starten
root = tk.Tk()
app = CSVComparatorApp(root)
root.mainloop()

