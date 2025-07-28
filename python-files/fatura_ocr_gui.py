
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import pandas as pd

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fatura OCR Okuyucu")
        self.root.geometry("1000x700")
        self.data = []
        self.index = 0
        self.image_list = []
        self.folder_path = ""

        self.build_gui()

    def build_gui(self):
        self.img_label = tk.Label(self.root)
        self.img_label.pack(pady=10)

        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack()

        self.fields = ["Ad Soyad", "T.C. No", "Fatura No", "Tarih", "Miktar", "Fiyat", "Tutar"]
        self.entries = {}

        for i, field in enumerate(self.fields):
            tk.Label(self.form_frame, text=field).grid(row=i, column=0, sticky="e")
            entry = tk.Entry(self.form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.entries[field] = entry

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Klasör Seç", command=self.select_folder).grid(row=0, column=0, padx=5)
        tk.Button(self.button_frame, text="Kaydet ve Geç", command=self.save_and_next).grid(row=0, column=1, padx=5)
        tk.Button(self.button_frame, text="Excel'e Aktar", command=self.export_excel).grid(row=0, column=2, padx=5)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.image_list = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path)
                           if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        self.index = 0
        if self.image_list:
            self.load_image()
        else:
            messagebox.showerror("Hata", "Klasörde geçerli resim dosyası bulunamadı.")

    def load_image(self):
        if self.index < len(self.image_list):
            img_path = self.image_list[self.index]
            img = Image.open(img_path)
            img.thumbnail((800, 600))
            img_tk = ImageTk.PhotoImage(img)
            self.img_label.configure(image=img_tk)
            self.img_label.image = img_tk

            text = pytesseract.image_to_string(img)
            self.fill_entries(text)
        else:
            messagebox.showinfo("Bitti", "Tüm resimler işlendi.")

    def fill_entries(self, text):
        self.entries["Ad Soyad"].delete(0, tk.END)
        self.entries["T.C. No"].delete(0, tk.END)
        self.entries["Fatura No"].delete(0, tk.END)
        self.entries["Tarih"].delete(0, tk.END)
        self.entries["Miktar"].delete(0, tk.END)
        self.entries["Fiyat"].delete(0, tk.END)
        self.entries["Tutar"].delete(0, tk.END)

        import re
        tc = re.search(r'\b(\d{11})\b', text)
        tarih = re.search(r'(\d{2}[./-]\d{2}[./-]\d{4})', text)
        miktar = re.search(r'Miktar.*?([\d.,]+)', text)
        fiyat = re.search(r'Birim Fiyat.*?([\d.,]+)', text)
        tutar = re.search(r'Tutar.*?([\d.,]+)', text)

        if tc: self.entries["T.C. No"].insert(0, tc.group(1))
        if tarih: self.entries["Tarih"].insert(0, tarih.group(1))
        if miktar: self.entries["Miktar"].insert(0, miktar.group(1).replace(",", "."))
        if fiyat: self.entries["Fiyat"].insert(0, fiyat.group(1).replace(",", "."))
        if tutar: self.entries["Tutar"].insert(0, tutar.group(1).replace(",", "."))

    def save_and_next(self):
        entry_data = {field: self.entries[field].get() for field in self.fields}
        self.data.append(entry_data)
        self.index += 1
        self.load_image()

    def export_excel(self):
        if not self.data:
            messagebox.showerror("Hata", "Kaydedilmiş veri yok.")
            return
        df = pd.DataFrame(self.data)
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel Dosyası", "*.xlsx")])
        if save_path:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("Başarılı", "Excel dosyası kaydedildi.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
