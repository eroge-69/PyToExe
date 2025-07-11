import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
import os
from itertools import groupby
import re
import sys
import datetime
from matplotlib.colors import Normalize

# === Choose whether to compare two files or two folders === #
def pick_mode():
    mode_win = tk.Tk()
    mode_win.title("Select Comparison Mode")
    mode_win.geometry("300x150")
    selection = tk.StringVar(value="files")

    tk.Label(mode_win, text="Choose comparison mode:", font=("Arial", 12)).pack(pady=10)
    tk.Radiobutton(mode_win, text="Compare two files", variable=selection, value="files").pack(anchor="w", padx=20)
    tk.Radiobutton(mode_win, text="Compare two folders", variable=selection, value="folders").pack(anchor="w", padx=20)

    def submit():
        mode_win.quit()
        mode_win.destroy()

    tk.Button(mode_win, text="OK", command=submit).pack(pady=10)
    mode_win.mainloop()
    return selection.get()

# === Snuff out any abnormally formatted PSID files === #
def validate_against_old(new_path, old_df):

    try: 
        new_df = pd.read_csv(new_path, index_col = 0)
    except Exception as e:
        messagebox.showerror("Invalid CSV", f"Could not read new CSV:\n{new_path}\n\n{e}")
        return None


    # Check whether the headers match (PS/ID, IID0001...)
    if not new_df.columns.equals(old_df.columns):
        messagebox.showerror("Invalid CSV", "Column headers of the new CSV do not exactly match the old CSV.")
        return None


    # Check whether the values in the first column match
    if not new_df.index.equals(old_df.index):
        messagebox.showerror("Invalid CSV", "The PS names of the new CSV do not match the old CSV.")
        return None


    # Make sure all values apart from those in the first row and column are numbers
    # This is accomplished by attempting to coerce every value to float and looking for failures

    coerced = new_df.apply(pd.to_numeric, errors='coerce')
    # Any NaN in 'coerced' signals an original bad cell

    if coerced.isna().any().any():

        # Locate the first offending cell
        mask = coerced.isna()
        row_label, col_label = next(((r, c) for r, c in zip(*mask.to_numpy().nonzero()) ), (None, None))
        # Get the actual labels
        ps_name = coerced.index[row_label]
        eid = coerced.columns[col_label]
        bad_val = new_df.iat[row_label, col_label]
        messagebox.showerror("Invalid CSV", f"Non-numeric or empty value at PS '{ps_name}', ID '{eid}':\n  {bad_val}")

        return None



    return new_df







# === Compute differences === #
def compute_diffs(mode):
    root = tk.Tk()
    root.withdraw()
    diffs = {}
    label_map = {}

    def common_prefix(a, b):
        return a[:9] if a[:9] == b[:9] else None

    try:
        if mode == "files":
            old_file = filedialog.askopenfilename(title="Select OLD PSID CSV", filetypes=[("CSV files", "*.csv")])
            new_file = filedialog.askopenfilename(title="Select NEW PSID CSV", filetypes=[("CSV files", "*.csv")])
            if not old_file or not new_file:
                return {}, {}

            # Load old as template
            df_old = pd.read_csv(old_file, index_col=0)

            # Validate new against old
            df_new = validate_against_old(new_file, df_old)
            if df_new is None:
                # validation failed → abort entire comparison
                return {}, {}

            # Compute diff
            diff = (df_new - df_old).fillna(0)
            if diff.shape[1] > 600:
                diff = diff.iloc[:, :600]

            prefix = common_prefix(os.path.basename(old_file), os.path.basename(new_file))
            if not prefix:
                messagebox.showerror("Error",
                                     f"File name mismatch:\n{os.path.basename(old_file)}\n{os.path.basename(new_file)}")
                return {}, {}

            diffs[prefix]     = diff
            label_map[prefix] = (old_file, new_file)

        else:  # folders
            old_folder = filedialog.askdirectory(title="Select folder containing OLD CSV files")
            new_folder = filedialog.askdirectory(title="Select folder containing NEW CSV files")
            if not old_folder or not new_folder:
                return {}, {}

            old_files = {f for f in os.listdir(old_folder) if f.lower().endswith('.csv')}
            new_files = {f for f in os.listdir(new_folder) if f.lower().endswith('.csv')}
            common_files = sorted(old_files & new_files)

            if not common_files:
                messagebox.showerror("Error", "No matching CSV files found in both folders.")
                return {}, {}

            for fname in common_files:
                old_path = os.path.join(old_folder, fname)
                new_path = os.path.join(new_folder, fname)
                try:
                    # Load old
                    df_old = pd.read_csv(old_path, index_col=0)

                    # Validate new against this old
                    df_new = validate_against_old(new_path, df_old)
                    if df_new is None:
                        # skip this pair
                        messagebox.showwarning(
                            "Skipping file",
                            f"'{fname}' skipped because new CSV did not match old CSV structure."
                        )
                        continue

                    # Compute diff
                    d = (df_new - df_old).fillna(0)
                    if d.shape[1] < 600:
                        # too few columns → skip
                        continue

                    diffs[fname]     = d.iloc[:, :600]
                    label_map[fname] = (old_path, new_path)

                except Exception as e:
                    messagebox.showwarning("Warning", f"Could not process {fname}:\n{e}")

        return diffs, label_map

    finally:
        root.destroy()



# === Single-PS Heatmap === #
def show_heatmap(diff_df, ps_name, title=""):
    if ps_name not in diff_df.index:
        messagebox.showerror("Error", f"PS '{ps_name}' not found.")
        return

    #arr = diff_df.loc[ps_name].to_numpy().reshape(6, 100)
    arr = np.abs(diff_df.loc[ps_name].to_numpy().reshape(6, 100))

    if arr.max() == 0:
        messagebox.showinfor("No changes", f"No non-zero changes for PS '{ps_name}")
        return

    # 1) Same window size as before…
    fig, ax = plt.subplots(figsize=(10, 4))

    # 2) Push the axes to the edges [left, bottom, width, height] (all fractions of the figure)
    ax.set_position([0.02, 0.05, 0.96, 0.90])

    # 3) Tell imshow to fill the axes (aspect='auto')
    vmin = arr[arr>0].min() if np.any(arr>0) else 1e-8

    cmap = plt.cm.Purples # Color for all non-zeros
    #cmap = plt.cm.Blues # Color for all non-zeros
    #cmap = plt.cm.Reds
    #cmap.set_under('lavender') # Color for all zeros
    cmap.set_under('lemonchiffon') # Color for all zeros

    heatmap = ax.imshow(arr, cmap = cmap, norm = Normalize(vmin = vmin, vmax = arr.max()), aspect = 'auto')

    #heatmap = ax.imshow(np.abs(arr), cmap='Blues', aspect='auto')

    # 4) Draw colorbar attached to the image
    cbar = fig.colorbar(heatmap, ax=ax, label='|new − old|')
    # Optional: shrink the colorbar so it doesn’t push into the image
    #cbar.ax.set_position([0.97, 0.05, 0.02, 0.90])

    # 5) Labels
    ax.set_title(f"{title} — PS: {ps_name}")
    ax.set_xlabel("EID (per 100)")
    ax.set_ylabel(f"{ps_name}")

    # 6) Hover‐tool
    cursor = mplcursors.cursor(heatmap, hover=True)
    @cursor.connect("add")
    def on_hover(sel):
        i, j = map(int, sel.index)
        val = arr[i, j]
        eid = i * 100 + j + 1
        sel.annotation.set_text(f"EID: {eid}\nΔ: {val:.3f}")

    plt.show()


# === Combined Heatmap  === #
def show_combined_heatmap(diff_df, title=""):
    # Identify PS with changes
    changed_ps = diff_df.index[(diff_df.fillna(0) != 0).any(axis=1)]
    if len(changed_ps) == 0:
        messagebox.showinfo("No changes", "There are no non-zero changes in this dataset.")
        return

    # Prepare data matrix
    mat = diff_df.loc[changed_ps].fillna(0).abs().to_numpy()
    eids = [int(re.search(r'\d+', col).group()) for col in diff_df.columns]

    # Plot
    fig, ax = plt.subplots(figsize=(12, max(4, 0.3 * len(changed_ps))))

    # Background banding for differentiation
    #for i in range(len(changed_ps)):
        #if i % 2 == 0:
            #ax.axhspan(i - 0.5, i + 0.5, color='gray', alpha=0.1)

    hm = ax.imshow(mat, aspect='auto', cmap='Blues')
    fig.colorbar(hm, ax=ax, label='|new − old|')

    ax.set_title(f"{title} — Combined PS Changes")
    ax.set_xlabel("EID")
    ax.set_ylabel("PS index")

    # Y-axis labels
    ax.set_yticks(range(len(changed_ps)))
    ax.set_yticklabels(changed_ps, fontsize=8)

    # X-axis ticks every ~10%
    step = max(1, len(eids) // 10)
    ax.set_xticks(np.arange(0, len(eids), step))
    ax.set_xticklabels([str(eids[i]) for i in range(0, len(eids), step)], rotation=45)

    # Horizontal grid lines between rows
    #for i in range(len(changed_ps) + 1):
        #ax.axhline(i - 0.5, color='white', linewidth=0.5)

    # Hover annotation
    cursor = mplcursors.cursor(hm, hover=True)

    @cursor.connect("add")
    def on_hover(sel):
        i, j = map(int, sel.index)
        ps = changed_ps[i]
        eid = eids[j]
        val = mat[i, j]
        sel.annotation.set_text(f"PS: {ps}\nEID: {eid}\nΔ: {val:.3f}")

    plt.tight_layout()
    plt.show()


# === Summary Text === #
def compress_ranges(indices):
    ranges = []
    for _, g in groupby(enumerate(sorted(indices)), lambda ix: ix[0] - ix[1]):
        group = list(map(lambda x: x[1], g))
        if len(group) == 1:
            ranges.append(str(group[0]))
        else:
            ranges.append(f"{group[0]}-{group[-1]}")
    return ", ".join(ranges)


def show_summary(diffs, label_map):
    summary_win = tk.Toplevel()
    summary_win.title("Summary of Changes")
    text = tk.Text(summary_win, wrap="word")
    text.pack(expand=True, fill='both')

    text.tag_configure("lvl1", lmargin1=0,   lmargin2=20, font=("Helvetica", 12, "bold"))
    text.tag_configure("lvl2", lmargin1=20,  lmargin2=40)
    text.tag_configure("lvl3", lmargin1=40,  lmargin2=60, foreground="gray20")
    text.tag_configure("lvl4", lmargin1=60,  lmargin2=80, foreground="gray40")
    text.tag_configure("spacer", spacing3=10)

    today = datetime.datetime.now().strftime("%Y.%m.%d")
    text.insert("end", f"{today}  SEQ 변경사항 확인\n\n", "lvl1")

    for seq_key, df in diffs.items():
        old_label, new_label = label_map[seq_key]
        base_old = os.path.basename(old_label)
        base_new = os.path.basename(new_label)

        text.insert("end", f"• {seq_key}\n", "lvl1")
        text.insert("end", f"• {base_old} → {base_new}\n", "lvl2")

        changed = df.index[(df.fillna(0) != 0).any(axis=1)]
        for ps in changed:
            text.insert("end", f"• {ps}:\n", "lvl3")
            nz = df.loc[ps][df.loc[ps] != 0]
            eids = [int(re.search(r'\d+', col).group()) for col in nz.index if re.search(r'\d+', col)]
            if not eids:
                continue
            eid_ranges = compress_ranges(eids)
            text.insert("end", f"• EID {eid_ranges}\n", "lvl4")

        text.insert("end", "\n", "spacer")

    summary_win.geometry("750x550")
    summary_win.mainloop()


# === GUI === #
def launch_gui(diffs, label_map):
    root = tk.Tk()
    root.title("PSID Comparison Tool")

    ttk.Label(root, text="Select file/key:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    file_cb = ttk.Combobox(root, values=list(diffs.keys()), state='readonly')
    file_cb.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(root, text="Select PS:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    ps_cb = ttk.Combobox(root, values=[], state='readonly')
    ps_cb.grid(row=1, column=1, padx=5, pady=5)

    def update_ps_list(event=None):
        key = file_cb.get()
        if key:
            df = diffs[key]
            ps_list = df.index[(df.fillna(0) != 0).any(axis=1)].tolist()
            ps_cb['values'] = ps_list
            if ps_list:
                ps_cb.current(0)

    file_cb.bind("<<ComboboxSelected>>", update_ps_list)

    ttk.Button(
        root,
        text="Show Combined Heatmap",
        command=lambda: show_combined_heatmap(diffs[file_cb.get()], title=file_cb.get())
    ).grid(row=2, column=0, columnspan=2, pady=10)
    ttk.Button(root, text="Show Heatmap", command=lambda: show_heatmap(diffs[file_cb.get()], ps_cb.get(), title=file_cb.get())).grid(row=3, column=0, columnspan=2, pady=5)
    ttk.Button(root, text="Show Summary", command=lambda: show_summary(diffs, label_map)).grid(row=4, column=0, columnspan=2, pady=5)
    ttk.Button(root, text="Return to Start", command=lambda: (root.quit(), root.destroy())).grid(row=5, column=0, columnspan=2, pady=10)

    root.geometry("450x300")
    root.mainloop()


# === Main Entry === #
def start_app():
    while True:
        mode = pick_mode()
        diffs, label_map = compute_diffs(mode) 
        if not diffs:
            break
        launch_gui(diffs, label_map)

if __name__ == "__main__":
    start_app()
