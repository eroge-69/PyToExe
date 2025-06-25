
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import pyodbc

def run_app():
    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            entry_file.delete(0, tk.END)
            entry_file.insert(0, file_path)

    def upload_data():
        excel_path = entry_file.get()
        if not excel_path:
            messagebox.showerror("Hata", "Lütfen bir Excel dosyası seçin.")
            return

        username = simpledialog.askstring("SQL Giriş", "Kullanıcı Adı:")
        password = simpledialog.askstring("SQL Giriş", "Şifre:", show='*')
        if not username or not password:
            messagebox.showerror("Hata", "Kullanıcı adı ve şifre gereklidir.")
            return

        try:
            df = pd.read_excel(excel_path)
            df["ISEGIRISTRH"] = pd.to_datetime(df["İŞE GİRİŞ"], errors='coerce')

            conn_str = (
                "DRIVER={SQL Server};"
                "SERVER=192.168.207.11;"
                "DATABASE=CMDIHALE_KAMPOTU;"
                f"UID={username};PWD={password};"
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO dbo.TBL_BRICK_TEMSILCI
                    (BRICK, TEMSILCIADI, YIL, AY, BRICKID, BOLGE, ISEGIRISTRH, HEDEFTL, PAYDASIL)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row["BRICK"],
                row["TEMSILCIADI"],
                int(row["YIL"]),
                int(row["AY"]),
                int(row["BRICKID"]),
                row["BOLGE"],
                row["ISEGIRISTRH"] if pd.notna(row["ISEGIRISTRH"]) else None,
                int(row["HEDEFTL"]),
                None if pd.isna(row["PAYDASIL"]) else row["PAYDASIL"]
                )

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Veriler başarıyla aktarıldı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu:\n{str(e)}")

    root = tk.Tk()
    root.title("Excel'den SQL Server'a Veri Aktarma")
    root.geometry("500x150")

    tk.Label(root, text="Excel Dosyası Seç:").pack(pady=5)
    entry_file = tk.Entry(root, width=50)
    entry_file.pack(pady=5)
    tk.Button(root, text="Gözat", command=select_file).pack()

    tk.Button(root, text="Veriyi Yükle", command=upload_data, bg="green", fg="white").pack(pady=10)

    root.mainloop()

run_app()
