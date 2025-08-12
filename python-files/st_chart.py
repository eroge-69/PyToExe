# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === 1. Data Calculation Function ===
def df_calculated_cleaned(df):
    df_calculated = df.copy().to_frame()
    df_calculated['Calculated_Price'] = np.nan

    for i in range(0, len(df_calculated), 20):
        window = df_calculated['Straddle Price'].iloc[i:i+20]
        high_price = window.max()
        low_price = window.min()
        last_price = window.iloc[-1]
        calculated_value = (high_price + low_price + last_price) / 3
        df_calculated.loc[i+20:i+39, 'Calculated_Price'] = calculated_value

    df_calculated = df_calculated.dropna()
    return df_calculated

# === 2. Interactive Chart Plot Function with improved tooltip ===
def chart_plot(df_calculated):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8))  # Object-Oriented API

    line1, = ax.plot(df_calculated.index, df_calculated['Straddle Price'], label='Straddle Price', color='lime')
    line2, = ax.plot(df_calculated.index, df_calculated['Calculated_Price'], label='Calculated Price', color='red')

    ax.set_title('Straddle Price vs Calculated Price')
    ax.set_xlabel('Index')
    ax.set_ylabel('Price')
    ax.legend()

    # Hide grid completely; set True for grid
    ax.grid(False)

    plt.tight_layout()

    # Annotation box for hover � dark background, white text
    annot = ax.annotate(
        "", xy=(0,0), xytext=(20,20), textcoords="offset points",
        bbox=dict(boxstyle="round", fc="#222222", ec="white", lw=1, alpha=0.9),
        arrowprops=dict(arrowstyle="->", color="white")
    )
    annot.set_color("white")  # Text color white
    annot.set_visible(False)

    def update_annot(ind, line):
        x, y = line.get_data()
        idx = ind["ind"][0]
        annot.xy = (x[idx], y[idx])
        text = f"Index: {x[idx]}\nPrice: {y[idx]:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.9)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            for line in [line1, line2]:
                cont, ind = line.contains(event)
                if cont:
                    update_annot(ind, line)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
        if vis:
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()

# === 3. File Upload Handler ===
def upload_and_process():
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        if 'Straddle Price' not in df.columns:
            messagebox.showerror("Error", "CSV must contain 'Straddle Price' column.")
            return

        df_series = df['Straddle Price']
        df_cleaned = df_calculated_cleaned(df_series)
        chart_plot(df_cleaned)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file.\n\n{str(e)}")

# === 4. GUI Setup ===
root = tk.Tk()
root.title("?? Straddle Price Analyzer")
root.geometry("800x500")
root.configure(bg="#1e1e2f")
root.eval('tk::PlaceWindow . center')
root.resizable(False, False)

font_title = ("Helvetica", 18, "bold")
font_normal = ("Helvetica", 12)
btn_color = "#4CAF50"
btn_fg = "white"

label = tk.Label(
    root,
    text="?? Upload CSV with 'Straddle Price' column",
    font=font_title,
    fg="white",
    bg="#1e1e2f"
)
label.pack(pady=40)

upload_button = tk.Button(
    root,
    text="Upload CSV",
    command=upload_and_process,
    font=font_normal,
    bg=btn_color,
    fg=btn_fg,
    padx=20,
    pady=10
)
upload_button.pack(pady=20)

root.mainloop()
