import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def split_csv():
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not file_path:
        messagebox.showwarning("Warning", "No file was selected.")
        return

    try:
        save_dir = os.path.dirname(file_path)
        df = pd.read_csv(file_path)
        n = len(df)
        if n < 3:
            messagebox.showerror("Error", "Not enough rows in the dataset.")
            return
        
        part_size = n // 3
        bangla_df = df.iloc[:part_size]
        hindi_df = df.iloc[part_size:part_size*2]
        english_df = df.iloc[part_size*2:]

        bangla_df.to_csv(os.path.join(save_dir, "bangla.csv"), index=False)
        hindi_df.to_csv(os.path.join(save_dir, "hindi.csv"), index=False)
        english_df.to_csv(os.path.join(save_dir, "english.csv"), index=False)

        messagebox.showinfo(
            "Success",
            f"✅ Three files have been created:\n\n- bangla.csv\n- hindi.csv\n- english.csv\n\nSaved in:\n{save_dir}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process the file:\n{e}")

# === GUI setup ===
root = tk.Tk()
root.title("CSV Splitter Tool")
root.resizable(True, True)

# === Load and place background image ===
bg_image_path = r"D:\VS Code Project\Python\csv_splitter_app\kpop.png"

if not os.path.exists(bg_image_path):
    messagebox.showerror("Error", f"Background image not found:\n{bg_image_path}")
    root.destroy()
    exit()

bg_image = Image.open(bg_image_path)
width, height = bg_image.size
root.geometry(f"{width}x{height}")  # Match window to image size
bg_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

background_label = tk.Label(root, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# === Overlay Labels and Buttons ===
header = tk.Label(
    root, 
    text="📄 CSV Splitter Tool", 
    font=("Segoe UI", 16, "bold"),
    fg="white", 
    bg="#000000"  # Solid black background for contrast
)
header.place(relx=0.5, y=30, anchor="center")

label = tk.Label(
    root, 
    text="Select a CSV file to split into 3 parts.\nOutput will be saved in the same folder.",
    font=("Segoe UI", 10),
    fg="white", 
    bg="#000000",
    justify="center"
)
label.place(relx=0.5, y=80, anchor="center")

split_button = tk.Button(
    root, 
    text="📂 Select and Split CSV", 
    command=split_csv, 
    bg="#28a745", 
    fg="white",
    font=("Segoe UI", 11),
    padx=15,
    pady=7
)
split_button.place(relx=0.5, y=150, anchor="center")

exit_button = tk.Button(
    root, 
    text="❌ Exit", 
    command=root.quit, 
    bg="#dc3545", 
    fg="white",
    font=("Segoe UI", 10),
    padx=10,
    pady=5
)
exit_button.place(relx=0.5, y=200, anchor="center")

root.mainloop()
