
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import pandas as pd
import os

def load_json():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        app.data = data
        label_file.config(text=f"Loaded: {os.path.basename(file_path)}")
        btn_export.config(state=tk.NORMAL)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON:\n{e}")

def export_excel():
    if not hasattr(app, 'data'):
        messagebox.showwarning("No Data", "Please load a JSON file first.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                             filetypes=[("Excel files", "*.xlsx")])
    if not save_path:
        return

    try:
        if isinstance(app.data, dict):
            df = pd.DataFrame([app.data])
        elif isinstance(app.data, list):
            df = pd.DataFrame(app.data)
        else:
            raise ValueError("Unsupported JSON format.")

        df.to_excel(save_path, index=False)
        messagebox.showinfo("Success", f"Excel file saved to:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to export Excel:\n{e}")

app = tk.Tk()
app.title("JSON to Excel Converter")
app.geometry("400x200")
app.resizable(False, False)

frame = tk.Frame(app, padx=20, pady=20)
frame.pack(fill="both", expand=True)

label_title = tk.Label(frame, text="JSON to Excel Converter", font=("Arial", 16))
label_title.pack(pady=10)

btn_load = tk.Button(frame, text="Load JSON File", command=load_json)
btn_load.pack(pady=5)

label_file = tk.Label(frame, text="No file loaded", fg="gray")
label_file.pack(pady=5)

btn_export = tk.Button(frame, text="Export to Excel", command=export_excel, state=tk.DISABLED)
btn_export.pack(pady=10)

app.mainloop()
