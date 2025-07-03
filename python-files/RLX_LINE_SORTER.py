import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import re
import os

def process_rlx(file_path, site_no):
    with open(file_path, 'r') as file:
        data = file.read()

    pattern = r'^(?:"(.*?)"|""|"-?\d+\.\d*");\s*\d+;\s*[\d\.]+;\s*"(.*?)"\n([\d\.\-; ]+)$'
    matches = re.findall(pattern, data, re.MULTILINE)

    if not matches:
        raise ValueError("Invalid RLX format or no line data found.")

    headers, units, coords = zip(*matches)
    lines = [list(map(float, c.strip().split(';'))) for c in coords]
    df = pd.DataFrame(lines, columns=[
        'x1', 'y1', 'x2', 'y2', 'z1', 'z2', 'z3', 'col1', 'col2'
    ])

    # Compute angles
    dx = df['x2'] - df['x1']
    dy = df['y2'] - df['y1']
    angles = np.degrees(np.arctan2(dy, dx))
    reference_angle = angles.iloc[0]

    angle_diff = np.abs((angles - reference_angle + 180) % 360 - 180)
    PL = 'PL' + site_no
    XL = 'XL' + site_no

    df['angle'] = angles
    df['type'] = [XL if abs(diff - 90) < 1e-1 else PL for diff in angle_diff]

    # Center points for sorting
    df['cx'] = (df['x1'] + df['x2']) / 2
    df['cy'] = (df['y1'] + df['y2']) / 2

    # Split by type
    df_pl = df[df['type'] == PL].sort_values(by=['cx', 'cy']).reset_index(drop=True)
    df_xl = df[df['type'] == XL].sort_values(by=['cx', 'cy'], ascending=False).reset_index(drop=True)

    # Assign order
    df_pl['order'] = [f"{PL}{str(i+1).zfill(2)}" for i in range(len(df_pl))]
    df_xl['order'] = [f"{XL}{str(i+1).zfill(2)}" for i in range(len(df_xl))]

    df_final = pd.concat([df_pl, df_xl], ignore_index=True)

    # Build output
    header_lines = [f'"{row["order"]}"; 64; 0; "Meter"' for _, row in df_final.iterrows()]
    coord_lines = [
        f'{row["x1"]}; {row["y1"]}; {row["x2"]}; {row["y2"]}; {row["z1"]}; {row["z2"]}; {row["z3"]}; {int(row["col1"])}; {int(row["col2"])}'
        for _, row in df_final.iterrows()
    ]

    final_output = '\n'.join(f"{h}\n{c}" for h, c in zip(header_lines, coord_lines))
    return final_output

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("RLX files", "*.rlx"), ("All files", "*.*")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def save_output(text, original_path):
    output_path = filedialog.asksaveasfilename(defaultextension=".rlx", initialfile=f"Processed_{os.path.basename(original_path)}")
    if output_path:
        with open(output_path, 'w') as f:
            f.write(text)
        messagebox.showinfo("Done", f"File saved to:\n{output_path}")

def run_processing():
    file_path = entry_file.get()
    site_no = entry_site.get().strip()

    if not file_path or not os.path.exists(file_path):
        messagebox.showerror("Error", "Please select a valid .rlx file.")
        return

    if not site_no.isdigit():
        messagebox.showerror("Error", "Site number must be numeric.")
        return

    try:
        output_text = process_rlx(file_path, site_no)
        save_output(output_text, file_path)
    except Exception as e:
        messagebox.showerror("Processing Failed", str(e))

# GUI Setup
root = tk.Tk()
root.title("RLX Line Sorter by Azubuike Godswill (Intern GOSL)")

tk.Label(root, text="Select RLX File:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Enter Site Number:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
entry_site = tk.Entry(root)
entry_site.grid(row=1, column=1, padx=5, pady=5)

tk.Button(root, text="Process File", command=run_processing, bg="#4CAF50", fg="white", padx=10).grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()

