import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import openpyxl

class StudentIDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Öğrenci Kimlik Programı")
        
        tk.Label(root, text="Adı:").grid(row=0, column=0)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1)
        
        tk.Label(root, text="Soyadı:").grid(row=1, column=0)
        self.surname_entry = tk.Entry(root)
        self.surname_entry.grid(row=1, column=1)
        
        tk.Label(root, text="Sınıfı:").grid(row=2, column=0)
        self.class_entry = tk.Entry(root)
        self.class_entry.grid(row=2, column=1)
        
        tk.Label(root, text="Numarası:").grid(row=3, column=0)
        self.number_entry = tk.Entry(root)
        self.number_entry.grid(row=3, column=1)
        
        self.photo_path = None
        tk.Button(root, text="Fotoğraf Seç", command=self.select_photo).grid(row=4, column=0, columnspan=2)
        
        self.preview_label = tk.Label(root, text="Kimlik Önizleme", width=30, height=10, relief="sunken")
        self.preview_label.grid(row=0, column=2, rowspan=6, padx=10)
        
        tk.Button(root, text="Kimliği Kaydet", command=self.save_student).grid(row=5, column=0, columnspan=2)
        tk.Button(root, text="Excel'e Dışa Aktar", command=lambda: export_to_excel(self.students)).grid(row=6, column=0, columnspan=2)
        
        self.students = []
    
    def select_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if path:
            self.photo_path = path
            img = Image.open(path)
            img = img.resize((120, 120))
            self.photo_img = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.photo_img, text="")
    
    def save_student(self):
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        class_ = self.class_entry.get().strip()
        number = self.number_entry.get().strip()
        photo = self.photo_path
        
        if not (name and surname and class_ and number and photo):
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun ve fotoğraf seçin.")
            return
        
        student = {
            "Ad": name,
            "Soyad": surname,
            "Sınıf": class_,
            "Numara": number,
            "Fotoğraf": photo
        }
        self.students.append(student)
        messagebox.showinfo("Başarılı", f"{name} {surname} kaydedildi.")
        
        self.name_entry.delete(0, tk.END)
        self.surname_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        self.number_entry.delete(0, tk.END)
        self.preview_label.config(image="", text="Kimlik Önizleme")
        self.photo_path = None

def export_to_excel(students):
    if not students:
        messagebox.showwarning("Uyarı", "Kaydedilmiş öğrenci yok.")
        return
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Öğrenciler"
    
    headers = ["Ad", "Soyad", "Sınıf", "Numara", "Fotoğraf Yolu"]
    ws.append(headers)
    
    for s in students:
        ws.append([s["Ad"], s["Soyad"], s["Sınıf"], s["Numara"], s["Fotoğraf"]])
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Dosyaları", "*.xlsx")],
        title="Excel dosyasını kaydet"
    )
    if file_path:
        wb.save(file_path)
        messagebox.showinfo("Başarılı", f"Öğrenciler Excel dosyasına kaydedildi:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentIDApp(root)
    root.mainloop()
