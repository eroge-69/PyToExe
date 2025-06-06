import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DATA_FILE = "gelir_gider_kayitlari.csv"

class GelirGiderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gelir Gider Takip")
        self.geometry("700x600")

        self.transactions = self.load_transactions()

        # Giriş alanları
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Tutar")
        self.amount_entry.pack(pady=5)

        self.description_entry = ctk.CTkEntry(self, placeholder_text="Açıklama")
        self.description_entry.pack(pady=5)

        self.type_var = ctk.StringVar(value="Gelir")
        self.type_option = ctk.CTkOptionMenu(self, values=["Gelir", "Gider"], variable=self.type_var)
        self.type_option.pack(pady=5)

        self.method_var = ctk.StringVar(value="Nakit")
        self.method_option = ctk.CTkOptionMenu(self, values=["Nakit", "Kredi Kartı"], variable=self.method_var)
        self.method_option.pack(pady=5)

        self.date_entry = ctk.CTkEntry(self, placeholder_text="Tarih (GG.AA.YYYY) - boş bırak güncel tarih")
        self.date_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Ekle", command=self.add_transaction)
        self.add_button.pack(pady=10)

        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(pady=10)

        self.start_date_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Başlangıç Tarihi (GG.AA.YYYY)")
        self.start_date_entry.pack(side="left", padx=5)

        self.end_date_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Bitiş Tarihi (GG.AA.YYYY)")
        self.end_date_entry.pack(side="left", padx=5)

        self.filter_button = ctk.CTkButton(self.filter_frame, text="Filtrele", command=self.filter_transactions)
        self.filter_button.pack(side="left", padx=5)

        self.show_all_button = ctk.CTkButton(self.filter_frame, text="Tümünü Göster", command=self.update_listbox)
        self.show_all_button.pack(side="left", padx=5)

        self.listbox = ctk.CTkTextbox(self, height=200)
        self.listbox.pack(pady=10, fill="both", expand=True)

        self.summary_label = ctk.CTkLabel(self, text="")
        self.summary_label.pack(pady=5)

        self.graph_button = ctk.CTkButton(self, text="Aylık Grafik", command=self.plot_monthly_summary)
        self.graph_button.pack(pady=5)

        self.save_button = ctk.CTkButton(self, text="Excel Olarak Kaydet", command=self.export_to_excel)
        self.save_button.pack(pady=5)

        self.update_listbox()

    def load_transactions(self):
        transactions = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    transactions.append(row)
        return transactions

    def save_transactions(self):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["Tutar", "Açıklama", "Tür", "Yöntem", "Tarih"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in self.transactions:
                writer.writerow(t)

    def add_transaction(self):
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        t_type = self.type_var.get()
        method = self.method_var.get()
        date_str = self.date_entry.get()

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir tutar girin.")
            return

        if not date_str:
            date = datetime.today().strftime("%d.%m.%Y")
        else:
            try:
                datetime.strptime(date_str, "%d.%m.%Y")
                date = date_str
            except ValueError:
                messagebox.showerror("Hata", "Tarih formatı geçersiz. GG.AA.YYYY")
                return

        transaction = {
            "Tutar": amount,
            "Açıklama": description,
            "Tür": t_type,
            "Yöntem": method,
            "Tarih": date
        }
        self.transactions.append(transaction)
        self.save_transactions()
        self.update_listbox()

        self.amount_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        self.date_entry.delete(0, "end")

    def update_listbox(self, data=None):
        self.listbox.delete("0.0", "end")
        data = data or self.transactions
        gelir = gider = 0
        for i, t in enumerate(data, 1):
            self.listbox.insert("end", f"{i}. {t['Tarih']} - {t['Açıklama']} - {t['Tür']} - {t['Tutar']} ₺ - {t['Yöntem']}\n")
            if t["Tür"] == "Gelir":
                gelir += float(t["Tutar"])
            else:
                gider += float(t["Tutar"])
        bakiye = gelir - gider
        self.summary_label.configure(text=f"Toplam Gelir: {gelir:.2f} ₺ | Gider: {gider:.2f} ₺ | Bakiye: {bakiye:.2f} ₺")

    def filter_transactions(self):
        start = self.start_date_entry.get()
        end = self.end_date_entry.get()

        try:
            start_date = datetime.strptime(start, "%d.%m.%Y") if start else None
            end_date = datetime.strptime(end, "%d.%m.%Y") if end else None
        except ValueError:
            messagebox.showerror("Hata", "Tarih formatı hatalı.")
            return

        filtered = []
        for t in self.transactions:
            t_date = datetime.strptime(t["Tarih"], "%d.%m.%Y")
            if (not start_date or t_date >= start_date) and (not end_date or t_date <= end_date):
                filtered.append(t)
        self.update_listbox(filtered)

    def plot_monthly_summary(self):
        df = pd.DataFrame(self.transactions)
        df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
        df["Tutar"] = pd.to_numeric(df["Tutar"])
        df["Ay"] = df["Tarih"].dt.to_period("M").astype(str)
        summary = df.groupby(["Ay", "Tür"])["Tutar"].sum().unstack().fillna(0)
        summary.plot(kind="bar", stacked=False)
        plt.title("Aylık Gelir Gider Özeti")
        plt.ylabel("Tutar (₺)")
        plt.xlabel("Ay")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def export_to_excel(self):
        df = pd.DataFrame(self.transactions)
        if df.empty:
            messagebox.showinfo("Bilgi", "Veri yok.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Başarılı", "Excel dosyası kaydedildi.")

if __name__ == "__main__":
    app = GelirGiderApp()
    app.mainloop()
