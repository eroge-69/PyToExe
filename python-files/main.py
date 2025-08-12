import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# -------------------- Existing functions --------------------
def read_cv_data(file_path):
    """Read and preprocess cyclic voltammetry data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find header line index
    header_idx = next((i for i, line in enumerate(lines) if "T(usec)" in line), None)
    if header_idx is None:
        raise ValueError(f"Could not find data header in file: {file_path}")

    # Keep only header + data lines
    lines = lines[header_idx:]


    cleaned_lines = []
    for line in lines:
        # Remove '+' signs
        line = line.replace("+", "")
        # Replace decimal commas with decimal points
        line = line.replace(",", ".")
        # Split by whitespace and join with commas for CSV format
        parts = line.strip().split()
        if parts:  # skip empty lines
            cleaned_lines.append(",".join(parts))

    # Read into DataFrame
    from io import StringIO
    csv_data = "\n".join(cleaned_lines)
    df = pd.read_csv(StringIO(csv_data))

    return df

def plot_iv_curves(data_files, labels=None, title=None):
    """Plot I-V curves with improved styling"""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150, constrained_layout=True)  # smaller size, better scaling

    # Sort files and labels together
    if labels:
        sorted_pairs = sorted(zip(data_files, labels), key=lambda x: Path(x[0]).stem)
        data_files, labels = zip(*sorted_pairs)
    else:
        data_files = sorted(data_files, key=lambda f: Path(f).stem)
        labels = [Path(f).stem for f in data_files]

    # Better color palette (Tableau)
    colors = plt.cm.tab10.colors

    for i, (data_file, label) in enumerate(zip(data_files, labels)):
        df = read_cv_data(data_file)
        voltage = df['E(V)'].values
        current = df['I(mA)'].values * 1000  # µA

        ax.plot(voltage, current,
                color=colors[i % len(colors)],
                linewidth=1,
                label=label,
                markersize=3,
                markerfacecolor='white')

    ax.set_xlabel('Voltage [V]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Current [µA]', fontsize=12, fontweight='bold')
    ax.set_title(title or "I-V Curves", fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=9, frameon=True, shadow=True, loc='best')

    plt.show()

# -------------------- Tkinter GUI --------------------
class CVPlotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cyclic Voltammetry Plotter")
        self.master.geometry("500x300")

        self.file_paths = []

        self.select_btn = tk.Button(master, text="Select Data Files", command=self.select_files)
        self.select_btn.pack(pady=10)

        self.files_label = tk.Label(master, text="No files selected", wraplength=450, justify="left")
        self.files_label.pack(pady=5)

        self.plot_btn = tk.Button(master, text="Plot I-V Curves", command=self.plot_files, state=tk.DISABLED)
        self.plot_btn.pack(pady=20)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select CV Data Files",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if files:
            # Sort file paths by file name
            self.file_paths = sorted(files, key=lambda f: Path(f).stem)
            self.files_label.config(text="\n".join([Path(f).name for f in self.file_paths]))
            self.plot_btn.config(state=tk.NORMAL)
        else:
            self.file_paths = []
            self.files_label.config(text="No files selected")
            self.plot_btn.config(state=tk.DISABLED)

    def plot_files(self):
        if not self.file_paths:
            messagebox.showerror("Error", "Please select at least one file first.")
            return
        try:
            plot_iv_curves(self.file_paths)  # No labels passed → uses sorted file names
        except Exception as e:
            messagebox.showerror("Error", str(e))

# -------------------- Run the app --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CVPlotApp(root)
    root.mainloop()
