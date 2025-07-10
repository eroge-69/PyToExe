
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pandastable import Table
import matplotlib.pyplot as plt

class ExcelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VALCOM Report Editor")
        self.root.geometry("1200x700")

        self.file_path = "VALCOM Template-2025.xlsx"
        self.dfs = {}
        self.current_sheet = None
        self.table_frame = None

        self.make_widgets()
        self.load_excel()

    def make_widgets(self):
        aframe = tk.Frame(self.root); aframe.pack(fill=tk.X, pady=5)
        self.sheet_sel = ttk.Combobox(aframe, state="readonly", width=30)
        self.sheet_sel.pack(side=tk.LEFT, padx=5)
        self.sheet_sel.bind("<<ComboboxSelected>>", self.on_sheet)

        tk.Button(aframe, text="Salva Excel", command=self.save_excel).pack(side=tk.RIGHT, padx=5)
        tk.Button(aframe, text="Genera Report", command=self.gen_report).pack(side=tk.RIGHT)
        tk.Button(aframe, text="Crea Grafico", command=self.make_plot).pack(side=tk.RIGHT, padx=5)

    def load_excel(self):
        try:
            xls = pd.ExcelFile(self.file_path)
            self.sheet_sel["values"] = xls.sheet_names
            for s in xls.sheet_names:
                self.dfs[s] = xls.parse(s)
            if xls.sheet_names:
                self.sheet_sel.current(0)
                self.on_sheet()
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def on_sheet(self, event=None):
        s = self.sheet_sel.get()
        self.current_sheet = s
        df = self.dfs[s]

        if self.table_frame:
            self.table_frame.destroy()
        self.table_frame = tk.Frame(self.root); self.table_frame.pack(fill=tk.BOTH, expand=True)
        pt = Table(self.table_frame, dataframe=df, showtoolbar=True, showstatusbar=True)
        pt.show()
        self.current_table = pt

    def save_excel(self):
        try:
            self.dfs[self.current_sheet] = self.current_table.model.df
            out = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                               filetypes=[("Excel file","*.xlsx")],
                                               initialfile="VALCOM_report_modificato.xlsx")
            if not out: return
            writer = pd.ExcelWriter(out, engine="openpyxl")
            for s, df in self.dfs.items():
                df.to_excel(writer, sheet_name=s, index=False)
            writer.save()
            messagebox.showinfo("Salvataggio", f"File salvato in: {out}")
        except Exception as e:
            messagebox.showerror("Errore salvataggio", str(e))

    def gen_report(self):
        out = ""
        for name, df in self.dfs.items():
            nums = df.select_dtypes(include='number')
            if not nums.empty:
                tot = nums.sum().sum()
                out += f"{name}: totale numerico = € {tot:,.2f}\n"
        messagebox.showinfo("Report Economico", out or "Nessun valore numerico rilevato.")

    def make_plot(self):
        sheet = self.current_sheet
        df = self.dfs[sheet]
        nums = df.select_dtypes(include='number')
        if nums.empty:
            messagebox.showwarning("Grafico", "Sheet senza dati numerici.")
            return

        col = tk.simpledialog.askstring("Colonna", f"Seleziona colonna numerica in '{sheet}':\n{', '.join(nums.columns)}")
        if col not in nums.columns:
            messagebox.showerror("Errore", "Colonna non valida.")
            return

        plt.figure(figsize=(8,5))
        plt.plot(df[col], marker='o')
        plt.title(f"{sheet}: {col}")
        plt.xlabel("Riga")
        plt.ylabel(col)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    import sys
    try:
        from pandastable import Table
    except ImportError:
        messagebox.showerror("Dipendenza mancante", "Installa pandastable via: pip install pandastable")
        sys.exit(1)
    app = ExcelApp(root)
    root.mainloop()
