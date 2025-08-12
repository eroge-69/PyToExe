import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

def load_csv(filename):
    try:
        df = pd.read_csv(filename, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        messagebox.showerror("File Error", f"File '{filename}' not found.")
    except pd.errors.ParserError as e:
        messagebox.showerror("Parse Error", f"Error parsing '{filename}': {e}")
    return None

def validate_columns(df, required_cols, filename):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        messagebox.showerror("Column Error", f"Missing columns in '{filename}': {missing}")
        return False
    return True

def filter_active_rows(df, col_name='Outlet Mapping', active_value='active'):
    df[col_name + '_clean'] = df[col_name].astype(str).str.strip().str.lower()
    filtered = df[df[col_name + '_clean'] == active_value].copy()
    return filtered

def create_concat_key(df, cols):
    key = df[cols[0]].astype(str).str.strip()
    for col in cols[1:]:
        key += '-' + df[col].astype(str).str.strip()
    return key.str.lower()

def compare_files(file1, file2):
    active_col = 'Outlet Mapping'
    concat_cols = ['Service Id', 'Program Id', 'Outlet Id Long']

    df1 = load_csv(file1)
    if df1 is None: return None

    df2 = load_csv(file2)
    if df2 is None: return None

    if not validate_columns(df1, concat_cols + [active_col], file1): return None
    if not validate_columns(df2, concat_cols + [active_col], file2): return None

    df1_active = filter_active_rows(df1, active_col)
    df2_active = filter_active_rows(df2, active_col)

    if df1_active.empty or df2_active.empty:
        messagebox.showwarning("Warning", "One or both files have no rows where 'Outlet Mapping' == 'active'.")

    df1_active['concat_key'] = create_concat_key(df1_active, concat_cols)
    df2_active['concat_key'] = create_concat_key(df2_active, concat_cols)

    keys1 = set(df1_active['concat_key'])
    keys2 = set(df2_active['concat_key'])

    unique1 = df1_active[df1_active['concat_key'].isin(keys1 - keys2)].copy()
    unique2 = df2_active[df2_active['concat_key'].isin(keys2 - keys1)].copy()

    if unique1.empty and unique2.empty:
        messagebox.showinfo("Result", "No unique rows found between the two files.")
        return None

    unique1['Source'] = 'Removed'
    unique2['Source'] = 'Added'

    result = pd.concat([unique1, unique2], ignore_index=True)
    result.drop(columns=['concat_key', active_col + '_clean'], inplace=True)

    return result

def save_result(result):
    output_file = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Workbook", "*.xlsx"), ("CSV file", "*.csv")],
        title="Save output file as"
    )
    if output_file:
        try:
            if output_file.endswith('.xlsx'):
                result.to_excel(output_file, index=False, engine='openpyxl')
            else:
                result.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"Saved {len(result)} rows to '{os.path.basename(output_file)}'.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving file: {e}")

def on_compare_click():
    file1 = filedialog.askopenfilename(title="Select New LDR file", filetypes=[("CSV files", "*.csv")])
    if not file1:
        return
    file2 = filedialog.askopenfilename(title="Select Old LDR file", filetypes=[("CSV files", "*.csv")])
    if not file2:
        return

    result = compare_files(file1, file2)
    if result is not None:
        save_result(result)

# Build the GUI with background image
root = tk.Tk()
root.title("LDR Comparison Tool")
root.geometry("550x200")

# Load and set background image
bg_image_path = r"C:\Users\VishalKumar\OneDrive - DreamFolks Services Ltd\Desktop\Automated Scripts\Logo.png"
try:
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((550, 200), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
except Exception as e:
    messagebox.showerror("Image Error", f"Error loading background image: {e}")
    bg_photo = None

if bg_photo:
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Put widgets on top, set bg color for label for readability
label = tk.Label(root, text="LDR Comparison Tool", font=("Arial", 15,"bold"), bg="#000000", fg="#FCFCFC")
label.pack(pady=(25, 90))

btn_compare = tk.Button(root, text="Select Latest LDR", command=on_compare_click, width=25, height=2)
btn_compare.pack()

root.mainloop()
