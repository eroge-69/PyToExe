
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def compare_excels():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Excel Karşılaştırıcı", "Karşılaştırmak istediğiniz Excel dosyasını seçin.")

    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)

        # Format düzeltme
        df['CBS WORKBENCH'] = pd.to_numeric(df['CBS WORKBENCH'], errors='coerce').dropna().astype('int64').astype(str)
        df['CBS BULK'] = pd.to_numeric(df['CBS BULK'], errors='coerce').dropna().astype('int64').astype(str)

        # Farkları bulma
        df['Only_in_Workbench'] = df['CBS WORKBENCH'].apply(lambda x: x if x not in df['CBS BULK'].values else "")
        df['Only_in_Bulk'] = df['CBS BULK'].apply(lambda x: x if x not in df['CBS WORKBENCH'].values else "")

        # Kayıt
        out_path = os.path.splitext(file_path)[0] + "_karsilastirma_sonuclari.xlsx"
        df.to_excel(out_path, index=False)

        messagebox.showinfo("İşlem Tamam", f"Karşılaştırma tamamlandı!\nKaydedilen dosya:\n{out_path}")

    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{str(e)}")

compare_excels()
