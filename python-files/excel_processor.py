
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Aapka custom query yahan likhein
def custom_query(df):
    # Example: Column A ko Column K mein copy karna
    df['K'] = df['A']
    return df

def process_file(file_path):
    try:
        df = pd.read_excel(file_path, header=None)

        # Pehli 2 rows delete
        df = df.iloc[2:].reset_index(drop=True)

        # Row 3 ko header banao
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        # Custom logic apply karo
        df = custom_query(df)

        # Same file overwrite karo
        df.to_excel(file_path, index=False)
        return f"✅ Overwritten: {os.path.basename(file_path)}"
    except Exception as e:
        return f"❌ Error: {os.path.basename(file_path)} - {str(e)}"

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="Select Excel Files",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_paths:
        return

    results = []
    for file_path in file_paths:
        result = process_file(file_path)
        results.append(result)

    messagebox.showinfo("Processing Complete", "\n".join(results))

def create_ui():
    root = tk.Tk()
    root.title("Excel Processing Tool")

    label = tk.Label(root, text="Select Excel files to process", font=("Arial", 12))
    label.pack(padx=20, pady=10)

    button = tk.Button(root, text="Select Files", command=select_files, width=20)
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_ui()
