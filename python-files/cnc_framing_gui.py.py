import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

def extract_max_dimensions(lines):
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    for line in lines:
        x_match = re.search(r'X(-?\d+\.?\d*)', line.upper())
        y_match = re.search(r'Y(-?\d+\.?\d*)', line.upper())

        if x_match:
            x_val = float(x_match.group(1))
            min_x = min(min_x, x_val)
            max_x = max(max_x, x_val)

        if y_match:
            y_val = float(y_match.group(1))
            min_y = min(min_y, y_val)
            max_y = max(max_y, y_val)

    width = round(max_x - min_x, 3)
    height = round(max_y - min_y, 3)
    origin_x = round(min_x, 3)
    origin_y = round(min_y, 3)

    return width, height, origin_x, origin_y

def insert_framing(lines, width, height, z_safe, z_work, feed, origin_x, origin_y):
    framing = [
        "(--- Begin Framing ---)",
        f"G0 Z{z_safe:.3f}",
        f"G0 X{origin_x} Y{origin_y}",
        f"G1 Z{z_work:.3f} F{feed}",
        f"G1 X{origin_x + width} Y{origin_y} F{feed}",
        f"G1 X{origin_x + width} Y{origin_y + height}",
        f"G1 X{origin_x} Y{origin_y + height}",
        f"G1 X{origin_x} Y{origin_y}",
        f"G0 Z{z_safe:.3f}",
        "(--- End Framing ---)"
    ]

    return lines[:2] + framing + lines[2:]

def process_file():
    filepath = filedialog.askopenfilename(
        filetypes=[("G-code files", "*.nc *.txt *.tap"), ("All files", "*.*")]
    )

    if not filepath:
        return

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file:\n{e}")
        return

    width, height, origin_x, origin_y = extract_max_dimensions(lines)
    entry_width.config(state='normal')
    entry_height.config(state='normal')
    entry_width.delete(0, tk.END)
    entry_height.delete(0, tk.END)
    entry_width.insert(0, str(width))
    entry_height.insert(0, str(height))
    entry_width.config(state='readonly')
    entry_height.config(state='readonly')

    def save_framed_file():
        try:
            z_safe = float(entry_zsafe.get())
            z_work = float(entry_zwork.get())
            feed = int(entry_feed.get())

            modified = insert_framing(lines, width, height, z_safe, z_work, feed, origin_x, origin_y)

            base, ext = os.path.splitext(filepath)
            outpath = f"{base}_framed{ext}"

            with open(outpath, 'w') as f:
                f.write("\n".join(modified))

            messagebox.showinfo("Success", f"✅ Framed file saved:\n{outpath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    btn_generate.config(command=save_framed_file)

# GUI setup
root = tk.Tk()
root.title("CNC G-code Framing Tool")

tk.Button(root, text="Select G-code File", command=process_file).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(root, text="Detected Width (X):").grid(row=1, column=0, sticky="e")
entry_width = tk.Entry(root, state='readonly')
entry_width.grid(row=1, column=1)

tk.Label(root, text="Detected Height (Y):").grid(row=2, column=0, sticky="e")
entry_height = tk.Entry(root, state='readonly')
entry_height.grid(row=2, column=1)

tk.Label(root, text="Safe Z Height:").grid(row=3, column=0, sticky="e")
entry_zsafe = tk.Entry(root)
entry_zsafe.insert(0, "5")
entry_zsafe.grid(row=3, column=1)

tk.Label(root, text="Framing Z Height:").grid(row=4, column=0, sticky="e")
entry_zwork = tk.Entry(root)
entry_zwork.insert(0, "2")
entry_zwork.grid(row=4, column=1)

tk.Label(root, text="Framing Feedrate:").grid(row=5, column=0, sticky="e")
entry_feed = tk.Entry(root)
entry_feed.insert(0, "2000")
entry_feed.grid(row=5, column=1)

btn_generate = tk.Button(root, text="Generate Framed G-code")
btn_generate.grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()
