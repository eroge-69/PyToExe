
import tkinter as tk
from tkinter import filedialog, messagebox
import random

DELTA = 0.015

def format_coord(value):
    return f"{value:11.3f}"

def process_file(filepath):
    with open(filepath, 'r') as infile:
        lines = [line.strip() for line in infile if line.strip()]

    output_lines = []
    for i, line in enumerate(lines, 1):
        output_lines.append(line)
        if i % 20 == 0:
            parts = line.split('\t')
            if len(parts) != 4:
                continue
            name = parts[0] + 'k'
            try:
                x = float(parts[1]) + random.uniform(-DELTA, DELTA)
                y = float(parts[2]) + random.uniform(-DELTA, DELTA)
                z = float(parts[3]) + random.uniform(-DELTA, DELTA)
            except ValueError:
                continue
            new_line = f"{name}\t{format_coord(x)}\t{format_coord(y)}\t{format_coord(z)}"
            output_lines.append(new_line)

    output_path = filepath.rsplit('.', 1)[0] + '_izlaz.txt'
    with open(output_path, 'w') as outfile:
        outfile.write('\n'.join(output_lines))

    return output_path

def run_app():
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title="Izaberi ulazni TXT fajl", filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return

    try:
        output_path = process_file(filepath)
        messagebox.showinfo("Uspešno", f"Obrađen fajl je sačuvan kao:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Greška", f"Desila se greška:\n{e}")

run_app()
