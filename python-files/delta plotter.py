import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.stats import linregress
import time
import threading

class CorrelationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Correlation Plot Tool")

        self.baseline_file = tk.StringVar(value="")
        self.current_file = tk.StringVar(value="")

        self.measurements = {label: tk.BooleanVar(value=False) for label in
                             ["M1X", "M2X", "M3X", "M4X", "M5X",
                              "M1Y", "M2Y", "M3Y", "M4Y", "M5Y"]}

        self.tolerance = tk.IntVar(value=1)

        # Spinner
        self.spinner_label = ttk.Label(self.root, text="", foreground="green", font=("Courier", 12))
        self.spinner_running = False
        self.spinner_frames = ["|", "/", "-", "\\"]
        self.spinner_index = 0

        self.create_widgets()

    def create_widgets(self):
        frame1 = ttk.LabelFrame(self.root, text="Baseline Excel")
        frame1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        frame1.columnconfigure(1, weight=1)
        ttk.Button(frame1, text="Browse", command=self.load_baseline).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame1, textvariable=self.baseline_file, width=50, anchor="w").grid(row=0, column=1, padx=5, sticky="ew")

        frame2 = ttk.LabelFrame(self.root, text="Current Excel")
        frame2.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        frame2.columnconfigure(1, weight=1)
        ttk.Button(frame2, text="Browse", command=self.load_current).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame2, textvariable=self.current_file, width=50, anchor="w").grid(row=0, column=1, padx=5, sticky="ew")

        frame3 = ttk.LabelFrame(self.root, text="Measurements")
        frame3.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        labels_top = ["M1X", "M2X", "M3X", "M4X", "M5X"]
        labels_bottom = ["M1Y", "M2Y", "M3Y", "M4Y", "M5Y"]

        for col, label in enumerate(labels_top):
            ttk.Checkbutton(frame3, text=label, variable=self.measurements[label]).grid(row=0, column=col, padx=5, pady=2)
        for col, label in enumerate(labels_bottom):
            ttk.Checkbutton(frame3, text=label, variable=self.measurements[label]).grid(row=1, column=col, padx=5, pady=2)

        frame4 = ttk.LabelFrame(self.root, text="Matching Tolerance (±)")
        frame4.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        tol_spin = ttk.Spinbox(frame4, from_=0, to=3, increment=1, textvariable=self.tolerance, width=5)
        tol_spin.grid(row=0, column=0, padx=5, pady=5)
        tol_label = ttk.Label(frame4, text="units for X2 & Y2 matching")
        tol_label.grid(row=0, column=1, padx=5, pady=5)

        instructions = ("Name col1, col2, col3, up to col14 in both the baseline Excel "
                        "and current data Excel files.")
        ttk.Label(self.root, text=instructions, wraplength=600, foreground="blue").grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        ttk.Button(self.root, text="Plot", command=self.start_plot_with_spinner).grid(row=5, column=0, pady=5)

        self.spinner_label.grid(row=5, column=1, padx=10)

        container = ttk.Frame(self.root)
        container.grid(row=6, column=0, sticky="nsew", padx=5, pady=5)
        self.canvas = tk.Canvas(container, height=700, width=1000)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(6, weight=1)

    def start_spinner(self):
        if self.spinner_running:
            self.spinner_label.config(text=self.spinner_frames[self.spinner_index])
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)
            self.root.after(100, self.start_spinner)

    def start_plot_with_spinner(self):
        self.spinner_running = True
        self.spinner_index = 0
        self.start_time = time.time()
        self.spinner_label.config(text="")
        self.start_spinner()

        threading.Thread(target=self.run_plot_with_timing).start()

    def run_plot_with_timing(self):
        start_calc = time.time()
        self.plot_data()
        elapsed_calc = time.time() - start_calc
        total_wait = max(3, elapsed_calc)

        while time.time() - self.start_time < total_wait:
            time.sleep(0.1)

        self.spinner_running = False
        self.spinner_label.config(text="Done ✅")

    def load_baseline(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.baseline_file.set(filename)

    def load_current(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.current_file.set(filename)

    def match_rows(self, df_base, df_curr):
        matched_pairs = []
        tol = self.tolerance.get()
        for _, row_b in df_base.iterrows():
            candidates = df_curr[(df_curr["X1"] == row_b["X1"]) & (df_curr["Y1"] == row_b["Y1"])]
            if candidates.empty:
                continue
            candidates = candidates[(abs(candidates["X2"] - row_b["X2"]) <= tol) &
                                    (abs(candidates["Y2"] - row_b["Y2"]) <= tol)]
            if candidates.empty:
                continue
            candidates = candidates.copy()
            candidates["dist"] = np.sqrt((candidates["X2"] - row_b["X2"])**2 +
                                         (candidates["Y2"] - row_b["Y2"])**2)
            best_match = candidates.loc[candidates["dist"].idxmin()]
            matched_pairs.append((row_b, best_match))
        return matched_pairs

    def plot_data(self):
        if not self.baseline_file.get() or not self.current_file.get():
            return
        df_base = pd.read_excel(self.baseline_file.get())
        df_curr = pd.read_excel(self.current_file.get())
        matches = self.match_rows(df_base, df_curr)
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        selected_measures = [m for m in self.measurements if self.measurements[m].get()]
        for measure in selected_measures:
            base_vals = [m[0][measure] for m in matches]
            curr_vals = [m[1][measure] for m in matches]
            if not base_vals or not curr_vals:
                continue
            fig, axes = plt.subplots(1, 4, figsize=(24, 4), constrained_layout=True)
            slope, intercept, r_value, _, _ = linregress(base_vals, curr_vals)
            fit_line = [slope * x + intercept for x in base_vals]
            ax = axes[0]
            ax.scatter(base_vals, curr_vals, color="blue", label="Data points")
            ax.plot(base_vals, fit_line, color="red", label=f"Fit: y={slope:.3f}x+{intercept:.3f}\nR²={r_value**2:.4f}")
            ax.set_xlabel("Baseline")
            ax.set_ylabel("Current")
            ax.set_title(f"Correlation Plot - {measure}")
            ax.legend()
            ax = axes[1]
            indices = np.arange(1, len(curr_vals) + 1)
            ax.scatter(indices, curr_vals, color="green", s=10)
            ax.axhline(0, color="black", linestyle="--", linewidth=1)
            ax.set_xlabel("Index")
            ax.set_ylabel("Current Values")
            ax.set_title(f"Extension Plot - {measure}")
            mean_val = np.mean(curr_vals)
            min_val = np.min(curr_vals)
            max_val = np.max(curr_vals)
            std_val = np.std(curr_vals)
            three_sigma = 3 * std_val
            stats_text = f"Mean: {mean_val:.3f}\nMin: {min_val:.3f}\nMax: {max_val:.3f}\n±3σ: {three_sigma:.3f}"
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
                    verticalalignment='top', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="wheat", alpha=0.5))
            ax = axes[2]
            differences = np.array(base_vals) - np.array(curr_vals)
            ax.scatter(indices, differences, color="purple", s=10)
            ax.axhline(0, color="black", linestyle="--", linewidth=1)
            ax.axhline(0.25, color="red", linestyle="--", linewidth=1)
            ax.axhline(-0.25, color="red", linestyle="--", linewidth=1)
            ax.set_xlabel("Index")
            ax.set_ylabel("Baseline - Current")
            ax.set_title(f"Difference Plot - {measure}")
            above_threshold = np.sum(differences > 0.25)
            below_threshold = np.sum(differences < -0.25)
            diff_stats_text = f"Above +0.25: {above_threshold}\nBelow -0.25: {below_threshold}"
            ax.text(0.05, 0.95, diff_stats_text, transform=ax.transAxes,
                    verticalalignment='top', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="mistyrose", alpha=0.7))
            ax = axes[3]
            ax.axis('off')
            unique_baseline = len(df_base.drop_duplicates())
            unique_current = len(df_curr.drop_duplicates())
            matched_count = len(matches)
            summary_text = (f"Summary - {measure}\n\n"
                            f"Baseline rows: {unique_baseline}\n"
                            f"Current rows: {unique_current}\n"
                            f"Matched rows: {matched_count}")
            ax.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center')
            canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = CorrelationApp(root)
    root.mainloop()
