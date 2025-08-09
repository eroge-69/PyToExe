import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from scipy.stats import linregress
from sklearn.metrics import r2_score
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

# Function to load CSV data
def load_data(file_path, relevant_columns):
    for encoding in ['utf-8', 'utf-16']:
        try:
            # Skip first 14 rows, use row 15 as header, and set tab as separator
            data = pd.read_csv(file_path, encoding=encoding, skiprows=14, header=0, sep='\t')
            # Lowercase columns for matching
            data.columns = [col.lower().strip() for col in data.columns]
            lower_relevant = [col.lower() for col in relevant_columns]
            if all(col in data.columns for col in lower_relevant):
                data_filtered = data[lower_relevant]
                data_filtered.columns = relevant_columns
                return data_filtered
        except Exception:
            continue
    raise ValueError(
        f"Could not find columns {relevant_columns} in {file_path}. "
        f"Found columns: {data.columns.tolist()}"
    )

# Function to preprocess data with basic noise filtering
def preprocess_filtered_data(data):
    if len(data) < 1:
        raise ValueError("Not enough data")
    data_cleaned = data.copy()  # No slicing, keep all rows
    data_cleaned['extensional strain'] = pd.to_numeric(data_cleaned['extensional strain'], errors='coerce')
    data_cleaned['extensional stress'] = pd.to_numeric(data_cleaned['extensional stress'], errors='coerce')
    data_cleaned = data_cleaned.dropna(subset=['extensional strain', 'extensional stress'])
    print(data_cleaned.head())
    return data_cleaned

# Function to find the best linear segment within 0 to 0.5 strain
def find_best_linear_segment(strain, stress, window_size=0.1, window_step=0.05):
    """
    window_size: width of the strain window to fit (e.g., 0.1 means 0.2–0.3)
    window_step: how much to move the window each time (e.g., 0.05)
    To loosen (widen) the linear range, increase window_size.
    To tighten (narrow) the linear range, decrease window_size.
    """
    best_r2 = -1
    best_range = (0, 0)
    best_slope = 0

    # Iterate through possible strain ranges
    for start in np.arange(0 + window_step, 0.5, window_step):
        end = start + window_size

        if end > 0.5:
            break

        mask = (strain >= start) & (strain <= end)
        strain_segment = strain[mask]
        stress_segment = stress[mask]

        if len(strain_segment) == 0:
            continue

        # Fit a linear regression to the segment
        slope, intercept, _, _, _ = linregress(strain_segment, stress_segment)
        predictions = slope * strain_segment + intercept
        r2 = r2_score(stress_segment, predictions)

        # Keep the best-fit segment with the highest R-squared value
        if r2 > best_r2:
            best_r2 = r2
            best_range = (start, end)
            best_slope = slope

    return best_range, best_slope

def min_strain(replicates_data):
    min_strains = []
    for df in replicates_data:
        min_strains.append(df['extensional strain'].min())
    return min(min_strains) if min_strains else None

def calculate_moduli_across_replicates(replicates_data, window_size=0.1, window_step=0.05, x_min=0, x_max=0.5):
    best_ranges = []
    slopes = []
    minstrain = min_strain(replicates_data)
    threshold = 0.0 if minstrain is None else minstrain
    results = []

    # 1. Find best range for each replicate
    for n, replicate in enumerate(replicates_data):
        strain = replicate['extensional strain']
        stress = replicate['extensional stress']
        mask = strain > threshold
        strain = strain[mask]
        stress = stress[mask]
        best_range, _ = find_best_linear_segment(strain, stress, window_size, window_step)
        best_ranges.append(best_range)
        results.append(f"Best linear range for replicate {n + 1}: {best_range}")

    # 2. Choose the most common range (mode)
    range_counts = Counter(best_ranges)
    common_range = range_counts.most_common(1)[0][0]
    results.append(f"\nUsing common linear range for all replicates: {common_range}\n")

    # 3. Recalculate modulus for each replicate using the common range
    for n, replicate in enumerate(replicates_data):
        strain = replicate['extensional strain']
        stress = replicate['extensional stress']
        mask = (strain >= common_range[0]) & (strain <= common_range[1])
        strain_segment = strain[mask]
        stress_segment = stress[mask]
        if len(strain_segment) < 2:
            results.append(f"Replicate {n + 1}: Not enough data in common range.")
            slopes.append(np.nan)
            continue
        slope, intercept, _, _, _ = linregress(strain_segment, stress_segment)
        slopes.append(slope)
        results.append(f"Replicate {n + 1} modulus in common range: {slope:.2f} MPa")

    # 4. Compute and print average modulus (ignoring NaN)
    valid_slopes = [s for s in slopes if not np.isnan(s)]
    if valid_slopes:
        average_slope = np.mean(valid_slopes)
        results.append(f'\nAverage Young Modulus across all replicates (common range): {average_slope:.2f} MPa')
    else:
        results.append("No valid slopes calculated.")

    # Show results in the GUI text box
    if 'results_text' in globals():
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, "\n".join(results))

    # 5. Plot everything
    plot_replicates_with_fits(replicates_data, best_ranges, common_range, x_min, x_max)

    # After plotting, store results for export
    global latest_export_data
    latest_export_data = {
        "replicates_data": replicates_data,
        "best_ranges": best_ranges,
        "common_range": common_range,
        "slopes": slopes,
        "x_min": x_min,
        "x_max": x_max
    }

def plot_replicates_with_fits(replicates_data, best_ranges, common_range, x_min, x_max):
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']
    markers = ['o', 's', '^', 'D', 'v', 'P']
    plt.figure(figsize=(10, 6))

    # Plot each replicate and its best-fit line
    for i, replicate in enumerate(replicates_data):
        # Only plot data within x_min to x_max
        mask_plot = (replicate['extensional strain'] >= x_min) & (replicate['extensional strain'] <= x_max)
        strain = replicate['extensional strain'][mask_plot]
        stress = replicate['extensional stress'][mask_plot]
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        plt.scatter(strain, stress, label=f'Replicate {i+1}', color=color, marker=marker, alpha=0.7)

        # Plot individual best-fit line (within best linear segment, but also limited to x_max)
        best_range = best_ranges[i]
        mask_fit = (strain >= best_range[0]) & (strain <= min(best_range[1], x_max))
        if mask_fit.sum() >= 2:
            x_fit = strain[mask_fit]
            y_fit = stress[mask_fit]
            slope, intercept, _, _, _ = linregress(x_fit, y_fit)
            x_line = np.linspace(best_range[0], min(best_range[1], x_max), 100)
            y_line = slope * x_line + intercept
            plt.plot(x_line, y_line, color=color, linestyle='--', alpha=0.7, label=f'Rep {i+1} best fit')

    # Plot common best-fit line (only within x_min to x_max)
    all_strain = []
    all_stress = []
    for replicate in replicates_data:
        mask_common = (replicate['extensional strain'] >= common_range[0]) & (replicate['extensional strain'] <= min(common_range[1], x_max))
        all_strain.extend(replicate['extensional strain'][mask_common])
        all_stress.extend(replicate['extensional stress'][mask_common])
    if len(all_strain) >= 2:
        slope, intercept, _, _, _ = linregress(all_strain, all_stress)
        x_common = np.linspace(common_range[0], min(common_range[1], x_max), 100)
        y_common = slope * x_common + intercept
        plt.plot(x_common, y_common, color='black', linewidth=2, label='Common best fit')

    plt.xlim(x_min, x_max)
    max_stress = max([df[(df['extensional strain'] >= x_min) & (df['extensional strain'] <= x_max)]['extensional stress'].max() for df in replicates_data])
    plt.ylim(0, max_stress * 1.1)

    # Box in the common best linear range using the set y-limits
    y_min, y_max = plt.ylim()
    plt.axvline(common_range[0], color='grey', linestyle=':', linewidth=2)
    plt.axvline(min(common_range[1], x_max), color='grey', linestyle=':', linewidth=2)
    plt.fill_betweenx([y_min, y_max], common_range[0], min(common_range[1], x_max), color='grey', alpha=0.1)

    plt.xlabel('Extensional Strain')
    plt.ylabel('Extensional Stress (MPa)')
    plt.title('Replicates with Individual and Common Best Linear Fits')
    plt.legend()
    plt.tight_layout()
    plt.show()

# Function to open file dialog and select CSV files
def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
    if file_paths:
        file_paths_var.set("\n".join(file_paths))
        try:
            window_size = float(window_size_var.get())
            window_step = float(window_step_var.get())
            x_min = float(x_min_var.get())
            x_max = float(x_max_var.get())
        except ValueError:
            print("Invalid input for window or axis limits. Using defaults.")
            window_size = 0.1
            window_step = 0.05
            x_min, x_max = 0, 0.5
        analyze_files(file_paths, window_size, window_step, x_min, x_max)

def analyze_files(file_paths, window_size, window_step, x_min, x_max):
    relevant_columns = ['extensional strain', 'extensional stress']
    replicates_data = []
    for file in file_paths:
        try:
            data = load_data(file, relevant_columns)
            df_cleaned = preprocess_filtered_data(data)
            replicates_data.append(df_cleaned)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
    if replicates_data:
        calculate_moduli_across_replicates(replicates_data, window_size, window_step, x_min, x_max)

# Function to setup and run the GUI
def setup_gui():
    global file_paths_var, window_size_var, window_step_var, x_min_var, x_max_var, results_text
    root = tk.Tk()
    root.title("Compression Test Analysis")

    # Label and entry for file paths
    file_paths_var = tk.StringVar()
    file_paths_label = tk.Label(root, text="Selected Files:")
    file_paths_label.pack()
    file_paths_entry = tk.Entry(root, textvariable=file_paths_var, width=80)
    file_paths_entry.pack()

    # Window size input
    window_size_var = tk.StringVar(value="0.1")
    window_size_label = tk.Label(root, text="Linear Range Window Size (e.g., 0.1):")
    window_size_label.pack()
    window_size_entry = tk.Entry(root, textvariable=window_size_var, width=10)
    window_size_entry.pack()

    # Window step input
    window_step_var = tk.StringVar(value="0.05")
    window_step_label = tk.Label(root, text="Linear Range Window Step (e.g., 0.05):")
    window_step_label.pack()
    window_step_entry = tk.Entry(root, textvariable=window_step_var, width=10)
    window_step_entry.pack()

    # X-axis (strain) limits
    x_min_var = tk.StringVar(value="0")
    x_max_var = tk.StringVar(value="0.5")
    x_min_label = tk.Label(root, text="Strain Min (x-axis):")
    x_min_label.pack()
    x_min_entry = tk.Entry(root, textvariable=x_min_var, width=10)
    x_min_entry.pack()
    x_max_label = tk.Label(root, text="Strain Max (x-axis):")
    x_max_label.pack()
    x_max_entry = tk.Entry(root, textvariable=x_max_var, width=10)
    x_max_entry.pack()

    # Button to open file dialog
    select_files_button = tk.Button(root, text="Select CSV Files", command=select_files)
    select_files_button.pack(pady=10)

    # Results text box
    results_text = tk.Text(root, height=15, width=100, wrap='word')
    results_text.pack(pady=10)

    # Export to Excel button
    export_button = tk.Button(root, text="Export Results to Excel", command=export_results_gui)
    export_button.pack(pady=5)

    root.mainloop()


def export_results_gui():
    if not latest_export_data["replicates_data"]:
        messagebox.showerror("Export Error", "No results to export. Please run an analysis first.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save Results As"
    )
    if file_path:
        export_results_to_excel(
            latest_export_data["replicates_data"],
            latest_export_data["best_ranges"],
            latest_export_data["common_range"],
            latest_export_data["slopes"],
            latest_export_data["x_min"],
            latest_export_data["x_max"],
            filename=file_path
        )
        messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")


def export_results_to_excel(replicates_data, best_ranges, common_range, slopes, x_min, x_max, filename="results.xlsx"):
    import os
    from pandas import ExcelWriter

    # Prepare summary DataFrame
    summary = []
    for i, (br, s) in enumerate(zip(best_ranges, slopes)):
        summary.append({
            "Replicate": i+1,
            "Best Linear Range Start": br[0],
            "Best Linear Range End": br[1],
            "Modulus (MPa)": s
        })
    summary_df = pd.DataFrame(summary)
    summary_df["Common Range Start"] = common_range[0]
    summary_df["Common Range End"] = common_range[1]

    # Save plot to file
    plot_filename = "plot.png"
    plt.savefig(plot_filename)

    # Write to Excel
    with ExcelWriter(filename) as writer:
        summary_df.to_excel(writer, index=False, sheet_name="Summary")
        # Optionally, save raw data for each replicate
        for i, df in enumerate(replicates_data):
            df.to_excel(writer, index=False, sheet_name=f"Replicate_{i+1}")

    # Add plot image to Excel (optional, requires openpyxl)
    try:
        from openpyxl import load_workbook
        from openpyxl.drawing.image import Image as XLImage
        wb = load_workbook(filename)
        ws = wb["Summary"]
        img = XLImage(plot_filename)
        ws.add_image(img, "G2")
        wb.save(filename)
    except Exception as e:
        print("Could not add plot image to Excel:", e)

    # Clean up plot image file
    if os.path.exists(plot_filename):
        os.remove(plot_filename)

latest_export_data = {
    "replicates_data": None,
    "best_ranges": None,
    "common_range": None,
    "slopes": None,
    "x_min": None,
    "x_max": None
}


# Execute the following
setup_gui()

