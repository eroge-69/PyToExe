# -*- coding: utf-8 -*-
"""
Wind CSV Combiner + 4 Plots (GUI)
- Loads all CSVs from a selected folder (optionally recursive)
- For each file, reads only columns 0 (timestamp), 2 (direction), 4 (speed)
- Parses timestamp: 'YYYYMMDDHhhmmssUTC' -> datetime
- Coerces numeric values (decimal comma supported)
- Combines and plots:
    1) Direction over time
    2) Speed over time (knots)
    3) Histogram of direction (5° bins)
    4) Histogram of speed (1-knot bins)
"""

import os
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


# ---------- CONFIG ----------
USECOLS = [0, 2, 4]  # Keep columns: 0=date/time, 2=angle, 4=speed
COLNAMES = ["raw_ts", "Direction", "Wind speed [knots]"]


# ---------- CORE LOADER ----------
def load_and_combine(folder: str, recursive: bool = False, log_cb=None) -> pd.DataFrame:
    """
    Load all CSVs from folder (and optionally subfolders) and combine them.
    Only keeps columns 0, 2, 4. Parses timestamps and coerces numeric fields.

    Returns: combined DataFrame with columns
             ['Timestamp', 'Direction', 'Wind speed [knots]', 'source_file']
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    if not folder or not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    pattern = "**/*.csv" if recursive else "*.csv"
    csv_paths = sorted(glob.glob(os.path.join(folder, pattern), recursive=recursive))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found under: {os.path.join(folder, pattern)}")

    frames = []
    for p in csv_paths:
        fname = os.path.basename(p)
        try:
            # Read required columns only, comma-separated
            try:
                df = pd.read_csv(
                    p,
                    header=None,
                    sep=",",
                    engine="python",
                    encoding="utf-8-sig",
                    usecols=USECOLS,
                    skipinitialspace=True,
                    on_bad_lines="skip",  # pandas >= 1.3
                )
            except Exception:
                df = pd.read_csv(
                    p,
                    header=None,
                    sep=",",
                    engine="python",
                    encoding="cp1252",
                    usecols=USECOLS,
                    skipinitialspace=True,
                    on_bad_lines="skip",
                )

            df.columns = COLNAMES

            # Parse timestamp: replace 'UTC', 'H' -> 'T'
            ts = (
                df["raw_ts"].astype(str).str.strip()
                  .str.replace("UTC", "", regex=False)
                  .str.replace("H", "T", regex=False)
            )
            df["Timestamp"] = pd.to_datetime(ts, format="%Y%m%dT%H%M%S", errors="coerce")

            # Coerce numerics (also handle comma decimals)
            df["Direction"] = pd.to_numeric(
                df["Direction"].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            )
            df["Wind speed [knots]"] = pd.to_numeric(
                df["Wind speed [knots]"].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            )

            # Keep only valid rows
            df = df[["Timestamp", "Direction", "Wind speed [knots]"]].dropna(subset=["Timestamp"])
            if df.empty:
                log(f"Skip {fname}: no valid rows after parsing.")
                continue

            df["source_file"] = fname
            frames.append(df)
            log(f"Loaded {fname}: {df.shape[0]} rows.")

        except Exception as e:
            log(f"ERROR {fname}: {e}")

    if not frames:
        raise RuntimeError("No valid rows found in any CSV. Check file format (comma CSV?)")

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined.sort_values(["Timestamp", "source_file"], inplace=True, kind="stable")
    combined.drop_duplicates(subset=["Timestamp", "source_file"], inplace=True)

    log(f"Combined total rows: {len(combined)} from {len(frames)} files.")
    return combined


# ---------- PLOTTING ----------
def create_figure_four_plots(df: pd.DataFrame) -> Figure:
    fig = Figure(figsize=(11.5, 8.0), dpi=100)
    axs = np.array([[fig.add_subplot(2, 2, 1), fig.add_subplot(2, 2, 2)],
                    [fig.add_subplot(2, 2, 3), fig.add_subplot(2, 2, 4)]])

    # Convert speed to m/s
    df["Wind speed [m/s]"] = df["Wind speed [knots]"] * 0.514444

    # 1) Wind Direction over Time
    mask_dir = df["Direction"].notna()
    ax = axs[0, 0]
    if mask_dir.any():
        ax.plot(df.loc[mask_dir, "Timestamp"], df.loc[mask_dir, "Direction"], color="tab:blue", lw=0.8)
        ax.set_title("Wind Direction Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Direction (degrees)")
        ax.grid(True, alpha=0.4)
    else:
        ax.text(0.5, 0.5, "No Direction data", ha="center", transform=ax.transAxes)

    # 2) Wind Speed over Time (m/s)
    mask_spd = df["Wind speed [m/s]"].notna()
    ax = axs[1, 0]
    if mask_spd.any():
        ax.plot(df.loc[mask_spd, "Timestamp"], df.loc[mask_spd, "Wind speed [m/s]"],
                color="tab:green", lw=0.8)
        ax.set_title("Wind Speed Over Time (m/s)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Wind Speed (m/s)")
        ax.grid(True, alpha=0.4)
    else:
        ax.text(0.5, 0.5, "No Wind speed data", ha="center", transform=ax.transAxes)

    # 3) Histogram of Wind speeds (1m/s bins)
    ax = axs[0, 1]
    dir_vals = df["Wind speed [m/s]"].dropna().values
    if dir_vals.size > 0:
        dir_vals = dir_vals[(dir_vals >= 0) & (dir_vals <= 360)]
        bins_dir = np.arange(0, 15, .5)
        ax.hist(dir_vals, bins=bins_dir, color="skyblue", edgecolor="black")
        ax.set_title("Histogram of Wind Speed (0.5 m/s bins)")
        ax.set_xlabel("Wind speed (m/s)")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.4)
    else:
        ax.text(0.5, 0.5, "No Direction data", ha="center", transform=ax.transAxes)

    # 4) Windrose plot
    ax = axs[1, 1]
    dir_vals = df["Direction"].dropna().values
    if dir_vals.size > 0:
        dir_rad = np.deg2rad(dir_vals)
        ax = fig.add_subplot(2, 2, 4, polar=True)
        ax.hist(dir_rad, bins=32, color='orange', edgecolor='black')
        ax.set_title("Windrose")
    else:
        ax.text(0.5, 0.5, "No Direction data", ha="center", transform=ax.transAxes)

    fig.tight_layout()
    return fig



# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wind CSV Combiner & Plots")
        self.geometry("1200x800")
        self._combined_df = None
        self._canvas = None
        self._toolbar = None
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=(10, 10))
        top.pack(side=tk.TOP, fill=tk.X)

        Filterline = ttk.Frame(self, padding=(10, 10))
        Filterline.pack(side=tk.TOP, fill=tk.X)

        # Folder line
        ttk.Label(top, text="Folder:").pack(side=tk.LEFT)
        self.var_folder = tk.StringVar(value="")
        self.entry_folder = ttk.Entry(top, textvariable=self.var_folder, width=100)
        self.entry_folder.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(top, text="Browse…", command=self.on_browse).pack(side=tk.LEFT, padx=5)

        # Include subfolders
        self.var_recursive = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Include subfolders", variable=self.var_recursive).pack(side=tk.LEFT, padx=10)

        # Action buttons
        ttk.Button(top, text="Load", command=self.on_load).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Plot", command=self.on_plot).pack(side=tk.LEFT, padx=5)
        #ttk.Button(top, text="Export Combined CSV", command=self.on_export_csv).pack(side=tk.LEFT, padx=5)



        # Date filter entries
        ttk.Label(Filterline, text="Start Date (YYYY-MM-DD-HH):").pack(side=tk.LEFT)
        self.entry_start = ttk.Entry(Filterline, width=18)
        self.entry_start.pack(side=tk.LEFT, padx=5)

        ttk.Label(Filterline, text="End Date (YYYY-MM-DD-HH):").pack(side=tk.LEFT)
        self.entry_end = ttk.Entry(Filterline, width=18)
        self.entry_end.pack(side=tk.LEFT, padx=5)

        # Plot area
        self.frame_plot = ttk.Frame(self, padding=(10, 5))
        self.frame_plot.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Status log
        self.txt_status = tk.Text(self, height=8)
        self.txt_status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self._log("Ready. Select a folder and click 'Load & Plot'.")


    def _log(self, msg: str):
        self.txt_status.insert(tk.END, msg + "\n")
        self.txt_status.see(tk.END)
        self.update_idletasks()

    def on_browse(self):
        initial = self.var_folder.get() or os.getcwd()
        folder = filedialog.askdirectory(initialdir=initial, title="Select folder with CSV files")
        if folder:
            self.var_folder.set(folder)

    def on_load(self):
        folder = self.var_folder.get().strip()
        recursive = self.var_recursive.get()
        self._log(f"Loading from: {folder}  (recursive={recursive})")

        try:
            combined = load_and_combine(folder, recursive, log_cb=self._log)
        except Exception as e:
            messagebox.showerror("Load error", str(e))
            self._log(f"ERROR: {e}")
            return

        self._combined_df = combined
        # Pre-fill date filters
        self.entry_start.delete(0, tk.END)
        self.entry_start.insert(0, str(combined["Timestamp"].min().date()))
        self.entry_end.delete(0, tk.END)
        self.entry_end.insert(0, str(combined["Timestamp"].max().date()))

        self._log(f"Data ready. Rows: {len(combined)} | Columns: {list(combined.columns)}")
    def on_plot(self):
        self._draw_plots(self._get_filtered_df())

    def _get_filtered_df(self) -> pd.DataFrame:
        try:
            start = pd.to_datetime(self.entry_start.get())
            end = pd.to_datetime(self.entry_end.get())
        except Exception:
            return self._combined_df.copy()
        return self._combined_df[
            (self._combined_df["Timestamp"] >= start) & (self._combined_df["Timestamp"] <= end)].copy()

    def _draw_plots(self, df: pd.DataFrame):
        # Clear all widgets inside the plot frame
        for widget in self.frame_plot.winfo_children():
            widget.destroy()

        self._toolbar = None
        self._canvas = None

        fig = create_figure_four_plots(df)

        # Embed in Tk
        self._canvas = FigureCanvasTkAgg(fig, master=self.frame_plot)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Toolbar
        self._toolbar = NavigationToolbar2Tk(self._canvas, self.frame_plot, pack_toolbar=False)
        self._toolbar.update()
        self._toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_export_csv(self):
        if self._combined_df is None or self._combined_df.empty:
            messagebox.showinfo("Export", "No data to export. Load data first.")
            return
        folder = self.var_folder.get() or os.getcwd()
        default_path = os.path.join(folder, "combined_wind_data.csv")
        path = filedialog.asksaveasfilename(
            title="Save combined CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=os.path.basename(default_path),
            initialdir=os.path.dirname(default_path),
        )
        if not path:
            return
        try:
            self._combined_df.to_csv(path, index=False, encoding="utf-8")
            self._log(f"Saved combined CSV to: {path}")
            messagebox.showinfo("Export", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))
            self._log(f"ERROR saving CSV: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
