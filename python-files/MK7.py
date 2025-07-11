# -*- coding: utf-8 -*-

"""
Created on Thu Jul 10 14:23:04 2025
@author: VikramVinod
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from pybaselines import Baseline

def advanced_smooth_and_correct(X, Y, pixel_data, window_size=10, polyorder=1):
    # Savitzky-Golay smoothing
    filtered_X = savgol_filter(X, window_size, polyorder=polyorder)
    filtered_Y = savgol_filter(Y, window_size, polyorder=polyorder)
    
    # Baseline correction using SNIP
    baseline_fitter = Baseline(x_data=pixel_data)
    bkg_X, _ = baseline_fitter.snip(filtered_X, max_half_window=40, decreasing=True, smooth_half_window=3)
    bkg_Y, _ = baseline_fitter.snip(filtered_Y, max_half_window=40, decreasing=True, smooth_half_window=3)
    
    X_corr = filtered_X - bkg_X
    Y_corr = filtered_Y - bkg_Y
    
    # Normalization (max = 1)
    normalized_X = X_corr / np.max(X_corr)
    normalized_Y = Y_corr / np.max(Y_corr)
    
    return normalized_X, normalized_Y

def analyze_csv(filepath):
    try:
        df = pd.read_csv(filepath, header=None)
        n_pixels = 256

        # Assume first 256 columns are X, next 256 are Y
        X = df.iloc[0, :n_pixels].astype(float).values
        Y = df.iloc[0, n_pixels:2*n_pixels].astype(float).values

        # Advanced smoothing, baseline correction, normalization
        pixel_data = np.arange(n_pixels)
        X_norm, Y_norm = advanced_smooth_and_correct(X, Y, pixel_data)

        # Intensity map
        Z = np.outer(X_norm, Y_norm)

        # Indices for calculation
        x_indices = np.arange(n_pixels)
        y_indices = np.arange(n_pixels)
        Z_sum = Z.sum()
        x_bar = (Z.sum(axis=1) @ x_indices) / Z_sum
        y_bar = (Z.sum(axis=0) @ y_indices) / Z_sum
        sigma_x2 = (Z.sum(axis=1) @ (x_indices - x_bar)**2) / Z_sum
        sigma_y2 = (Z.sum(axis=0) @ (y_indices - y_bar)**2) / Z_sum
        sigma_x = np.sqrt(sigma_x2)
        sigma_y = np.sqrt(sigma_y2)
        d4x = 4 * sigma_x
        d4y = 4 * sigma_y

        # Prepare results
        results = {
            'Centroid X': f'{x_bar:.4f}',
            'Centroid Y': f'{y_bar:.4f}',
            'Variance X': f'{sigma_x2:.4f}',
            'Variance Y': f'{sigma_y2:.4f}',
            'Std Dev X': f'{sigma_x:.4f}',
            'Std Dev Y': f'{sigma_y:.4f}',
            'D4-Sigma X': f'{d4x:.4f}',
            'D4-Sigma Y': f'{d4y:.4f}',
        }

        # Plot
        plt.figure(figsize=(10,5))
        plt.plot(X_norm, label='X (smoothed, baseline-corrected, normalized)')
        plt.plot(Y_norm, label='Y (smoothed, baseline-corrected, normalized)')
        plt.xlabel('Pixel Index')
        plt.ylabel('Normalized Value')
        plt.title('Smoothed, Baseline-Corrected & Normalized X/Y Sensor Readings')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        return results

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{e}")
        return None

def drop_file(event):
    filepath = event.data
    if filepath.startswith('{') and filepath.endswith('}'):
        filepath = filepath[1:-1]
    results = analyze_csv(filepath)
    if results:
        for k, v in results.items():
            result_tree.insert('', 'end', values=(k, v))

def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if filepath:
        result_tree.delete(*result_tree.get_children())
        results = analyze_csv(filepath)
        if results:
            for k, v in results.items():
                result_tree.insert('', 'end', values=(k, v))

# GUI setup
root = tk.Tk()
root.title("CSV Beam Profile Analyzer")
root.geometry("500x400")
frame = tk.Frame(root)
frame.pack(pady=10)

label = tk.Label(frame, text="Drop your CSV file here or click 'Open File'", font=('Arial', 14))
label.pack(pady=10)

open_btn = tk.Button(frame, text="Open File", command=open_file)
open_btn.pack(pady=5)

# Results table
result_tree = ttk.Treeview(root, columns=('Parameter', 'Value'), show='headings', height=8)
result_tree.heading('Parameter', text='Parameter')
result_tree.heading('Value', text='Value')
result_tree.pack(pady=10, fill='x', expand=True)

# Enable drag-and-drop (for Windows, needs tkdnd)
try:
    import tkinterdnd2
    root = tkinterdnd2.TkinterDnD.Tk()
    label.drop_target_register(tkinterdnd2.DND_FILES)
    label.dnd_bind('<Drop>', drop_file)
except ImportError:
    pass # Drag-and-drop won't work, but Open File will

root.mainloop()
