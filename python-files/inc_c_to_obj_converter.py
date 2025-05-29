import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

def parse_vertex_data(lines):
    vertices = []
    for line in lines:
        match = re.search(r'VTX\(([^)]+)\)', line)
        if match:
            values = list(map(int, match.group(1).split(',')))
            x, y, z = values[:3]
            vertices.append((x / 32.0, y / 32.0, z / 32.0))
    return vertices

def parse_triangles(lines):
    triangles = []
    for line in lines:
        match = re.search(r'gsSP2Triangles\(([^)]+)\)', line)
        if match:
            values = list(map(int, re.findall(r'\d+', match.group(1))))
            if len(values) >= 6:
                triangles.append((values[0], values[1], values[2]))
                triangles.append((values[3], values[4], values[5]))
    return triangles

def write_obj_file(name, vertices, triangles, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, name + ".obj")
    with open(filepath, "w") as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for t in triangles:
            f.write(f"f {t[0]+1} {t[1]+1} {t[2]+1}\n")
    return filepath

def convert_file():
    file_path = filedialog.askopenfilename(title="Wähle eine .inc.c Datei", filetypes=[("C Include-Dateien", "*.inc.c")])
    if not file_path:
        return

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        vertices = parse_vertex_data(lines)
        triangles = parse_triangles(lines)
        if not vertices or not triangles:
            messagebox.showerror("Fehler", "Keine gültigen Daten gefunden.")
            return

        name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = write_obj_file(name, vertices, triangles)
        messagebox.showinfo("Erfolg", f"Datei exportiert nach:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

def main():
    root = tk.Tk()
    root.withdraw()
    convert_file()

if __name__ == "__main__":
    main()
