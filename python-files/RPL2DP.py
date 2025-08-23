import os
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox


# Function to calculate angle between three points
def calculate_angle(p1, p2, p3):
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = p3[0] - p2[0], p3[1] - p2[1]
    dot_product = dx1 * dx2 + dy1 * dy2
    magnitude1 = np.hypot(dx1, dy1)
    magnitude2 = np.hypot(dx2, dy2)
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    cos_theta = dot_product / (magnitude1 * magnitude2)
    angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
    return angle


# Simplify line using weed factor (angle threshold)
def simplify_line_with_weed_factor(df, weed_factor=2.0):
    simplified_df = df.iloc[:1]
    for i in range(1, len(df) - 1):
        p1 = df.iloc[i - 1][["Easting", "Northing"]].values
        p2 = df.iloc[i][["Easting", "Northing"]].values
        p3 = df.iloc[i + 1][["Easting", "Northing"]].values
        angle = calculate_angle(p1, p2, p3)
        if angle > weed_factor:
            simplified_df = pd.concat([simplified_df, df.iloc[i:i + 1]], ignore_index=True)
    simplified_df = pd.concat([simplified_df, df.iloc[[-1]]], ignore_index=True)
    return simplified_df


# Compute vessel positions based on layback and heading
def compute_vessel_positions_by_heading(df, layback, direction="increasing"):
    if direction == "decreasing":
        df = df[::-1].reset_index(drop=True)

    easting = df["Easting"].values
    northing = df["Northing"].values

    vessel_eastings = []
    vessel_northings = []

    for i in range(len(df)):
        if i == len(df) - 1:
            dx = easting[i] - easting[i - 1]
            dy = northing[i] - northing[i - 1]
        else:
            dx = easting[i + 1] - easting[i]
            dy = northing[i + 1] - northing[i]

        heading = np.arctan2(dy, dx)
        vessel_e = easting[i] - layback * np.cos(heading)
        vessel_n = northing[i] - layback * np.sin(heading)

        vessel_eastings.append(vessel_e)
        vessel_northings.append(vessel_n)

    vessel_df = pd.DataFrame({
        "Vessel_Easting": vessel_eastings,
        "Vessel_Northing": vessel_northings
    })

    vessel_df['Easting_MA'] = vessel_df['Vessel_Easting'].rolling(window=21, center=True, min_periods=1).mean().round(2)
    vessel_df['Northing_MA'] = vessel_df['Vessel_Northing'].rolling(window=21, center=True, min_periods=1).mean().round(2)

    return vessel_df


# Main processing function
def process_all_files(input_dir, output_dir, layback, simplify=False, angle_threshold=2.0, create_combined_file=False):
    all_simplified_data = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_dir, filename)
            try:
                df = pd.read_csv(filepath, sep=",", header=None)
                if df.shape[1] < 3:
                    print(f"Skipping {filename}: not enough columns.")
                    continue

                df.columns = ["KP", "Easting", "Northing"]
                df["Easting"] = pd.to_numeric(df["Easting"], errors="coerce")
                df["Northing"] = pd.to_numeric(df["Northing"], errors="coerce")
                df.dropna(subset=["Easting", "Northing"], inplace=True)

                base_filename = os.path.splitext(filename)[0]
                layback_str = f"{int(layback)}m"

                if simplify:
                    simplified_df = simplify_line_with_weed_factor(df, weed_factor=angle_threshold)
                    simplified_path = os.path.join(output_dir, f"Simplified_{base_filename}.txt")
                    simplified_df[["Easting", "Northing"]].to_csv(simplified_path, index=False, header=False, sep=",", float_format="%.2f")
                    print(f"Simplified: {filename}")

                    if create_combined_file:
                        all_simplified_data.append(simplified_df[["Easting", "Northing"]])
                else:
                    # ⚠ Corrected: assign based on actual logic
                    vessel_inc = compute_vessel_positions_by_heading(df, layback, direction="decreasing")
                    vessel_dec = compute_vessel_positions_by_heading(df, layback, direction="increasing")

                    output_file_inc = os.path.join(output_dir, f"DP_{base_filename}_IncreasingKPs_{layback_str}.txt")
                    output_file_dec = os.path.join(output_dir, f"DP_{base_filename}_DecreasingKPs_{layback_str}.txt")

                    vessel_inc[['Easting_MA', 'Northing_MA']].to_csv(
                        output_file_inc, index=False, header=False, sep=",", float_format="%.2f"
                    )
                    vessel_dec[['Easting_MA', 'Northing_MA']].to_csv(
                        output_file_dec, index=False, header=False, sep=",", float_format="%.2f"
                    )

                    print(f"Processed: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if create_combined_file and all_simplified_data:
        combined_df = pd.concat(all_simplified_data, ignore_index=True)
        combined_file_path = os.path.join(output_dir, "Combined_Simplified_Lines.txt")
        combined_df.to_csv(combined_file_path, index=False, header=False, sep=",", float_format="%.2f")
        print("Combined simplified lines saved.")


# GUI interface
def run_gui():
    def select_input():
        folder = filedialog.askdirectory()
        input_var.set(folder)

    def select_output():
        folder = filedialog.askdirectory()
        output_var.set(folder)

    def toggle_method():
        if dp_with_layback_var.get():
            simplify_check_var.set(False)
            layback_label.grid(row=4, column=0)
            layback_entry.grid(row=4, column=1)
            angle_threshold_label.grid_forget()
            angle_threshold_entry.grid_forget()
            combined_file_check.grid_forget()
        elif simplify_check_var.get():
            dp_with_layback_var.set(False)
            layback_label.grid_forget()
            layback_entry.grid_forget()
            angle_threshold_label.grid(row=5, column=0)
            angle_threshold_entry.grid(row=5, column=1)
            combined_file_check.grid(row=6, column=0)
        else:
            layback_label.grid_forget()
            layback_entry.grid_forget()
            angle_threshold_label.grid_forget()
            angle_threshold_entry.grid_forget()
            combined_file_check.grid_forget()

    def run_processing():
        input_dir = input_var.get()
        output_dir = output_var.get()
        layback = float(layback_var.get()) if layback_var.get() else 0
        simplify = simplify_check_var.get()
        angle_threshold = float(angle_threshold_var.get()) if angle_threshold_var.get() else 0.2
        create_combined_file = combined_file_var.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output directories.")
            return

        process_all_files(input_dir, output_dir, layback, simplify=simplify,
                          angle_threshold=angle_threshold, create_combined_file=create_combined_file)

        messagebox.showinfo("Done", "Processing complete.")

    window = tk.Tk()
    window.title("Cable Layback and Line Simplification")

    input_var = tk.StringVar()
    output_var = tk.StringVar()

    tk.Button(window, text="Select Input Directory", command=select_input).grid(row=0, column=0)
    tk.Entry(window, textvariable=input_var, width=40).grid(row=0, column=1)

    tk.Button(window, text="Select Output Directory", command=select_output).grid(row=1, column=0)
    tk.Entry(window, textvariable=output_var, width=40).grid(row=1, column=1)

    dp_with_layback_var = tk.BooleanVar()
    simplify_check_var = tk.BooleanVar()

    tk.Checkbutton(window, text="DP with Layback", variable=dp_with_layback_var, command=toggle_method).grid(row=2, column=0)
    tk.Checkbutton(window, text="Simplify Line", variable=simplify_check_var, command=toggle_method).grid(row=2, column=1)

    layback_label = tk.Label(window, text="Layback (m):")
    layback_var = tk.StringVar(value="0")
    layback_entry = tk.Entry(window, textvariable=layback_var)

    angle_threshold_label = tk.Label(window, text="Weeding Angle Threshold (degrees):")
    angle_threshold_var = tk.StringVar(value="2.0")
    angle_threshold_entry = tk.Entry(window, textvariable=angle_threshold_var)

    combined_file_var = tk.BooleanVar()
    combined_file_check = tk.Checkbutton(window, text="Create Combined Simplified File", variable=combined_file_var)

    tk.Button(window, text="Run", command=run_processing).grid(row=7, column=0, columnspan=2)

    window.mainloop()


if __name__ == "__main__":
    run_gui()
