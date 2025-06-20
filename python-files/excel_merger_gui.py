import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def sloucit_data(cesta):
    try:
        df = pd.read_excel(cesta)
        df.columns = [col.strip() for col in df.columns]

        if not {'Název', 'Množství', 'MJ'}.issubset(df.columns):
            messagebox.showerror("Chyba", "Sloupce 'Název', 'Množství', 'MJ' nebyly nalezeny.")
            return

        df_skupina = df.groupby(['Název', 'MJ'], as_index=False)['Množství'].sum()

        vystup = os.path.join(os.path.dirname(cesta), "Souhrn_polozek.xlsx")
        df_skupina.to_excel(vystup, index=False)

        messagebox.showinfo("Hotovo", f"Soubor uložen jako:
{vystup}")
    except Exception as e:
        messagebox.showerror("Chyba", str(e))

def otevrit_okno():
    cesta = filedialog.askopenfilename(filetypes=[("Excel soubory", "*.xlsx")])
    if cesta:
        sloucit_data(cesta)

okno = tk.Tk()
okno.title("Excel Merger - Sloučení položek")
okno.geometry("300x150")

tlacitko = tk.Button(okno, text="Načíst Excel a sloučit", command=otevrit_okno, height=2, width=25)
tlacitko.pack(expand=True)

okno.mainloop()