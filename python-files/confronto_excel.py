
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def load_file(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)

def compare_excels(file1, file2):
    try:
        df1 = pd.read_excel(file1, engine='openpyxl' if file1.endswith('.xlsx') else 'xlrd')
        df2 = pd.read_excel(file2, engine='openpyxl' if file2.endswith('.xlsx') else 'xlrd')
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel caricamento dei file:\n{e}")
        return

    try:
        # Compare dataframes and find differences
        df_diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
        df_diff.to_excel("differenze.xlsx", index=False)
        messagebox.showinfo("Confronto completato", "Differenze salvate in 'differenze.xlsx'")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel confronto dei file:\n{e}")

def main():
    root = tk.Tk()
    root.title("Confronto Excel")
    root.geometry("400x200")

    tk.Label(root, text="File Excel 1:").pack(pady=5)
    entry1 = tk.Entry(root, width=50)
    entry1.pack()
    tk.Button(root, text="Carica File 1", command=lambda: load_file(entry1)).pack(pady=5)

    tk.Label(root, text="File Excel 2:").pack(pady=5)
    entry2 = tk.Entry(root, width=50)
    entry2.pack()
    tk.Button(root, text="Carica File 2", command=lambda: load_file(entry2)).pack(pady=5)

    tk.Button(root, text="Confronta", command=lambda: compare_excels(entry1.get(), entry2.get())).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
