import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

class NCEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("NC Post Düzenleyici")
        master.geometry("400x200")
        master.resizable(False, False)

        # Arayüz elemanlarını oluşturma
        self.label = tk.Label(master, text="Düzenlemek için NC dosyasını seçin:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(master, text="Dosya Seç", command=self.select_file)
        self.select_button.pack(pady=5)

        self.file_path_label = tk.Label(master, text="Seçilen Dosya: Yok")
        self.file_path_label.pack(pady=5)

        self.process_button = tk.Button(master, text="Düzenle ve Kaydet", command=self.process_file, state=tk.DISABLED)
        self.process_button.pack(pady=5)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

        self.selected_file = None

    def select_file(self):
        """Kullanıcının dosya seçmesini sağlar ve arayüzü günceller."""
        file_path = filedialog.askopenfilename(defaultextension=".nc",
                                               filetypes=[("NC Dosyaları", "*.nc"), ("Tüm Dosyalar", "*.*")])
        if file_path:
            self.selected_file = file_path
            self.file_path_label.config(text=f"Seçilen Dosya: {os.path.basename(file_path)}")
            self.process_button.config(state=tk.NORMAL)
            self.status_label.config(text="")

    def process_file(self):
        """Seçilen dosyayı belirtilen kurallara göre düzenler."""
        if not self.selected_file:
            messagebox.showerror("Hata", "Lütfen önce bir dosya seçin.")
            return

        try:
            with open(self.selected_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunamadı: {e}")
            return

        new_lines = []
        first_percent_found = False
        
        # 1. İlk % işaretinden önceki satırları sil
        for line in lines:
            if line.strip() == '%' and not first_percent_found:
                new_lines.append(line.strip() + '\n')
                first_percent_found = True
            elif first_percent_found:
                new_lines.append(line)

        if not first_percent_found:
            messagebox.showerror("Hata", "Dosyada '%' işareti bulunamadı. Lütfen doğru bir NC dosyası seçin.")
            return

        final_lines = []
        i = 0
        while i < len(new_lines):
            line = new_lines[i].strip()
            
            # 4. M30'dan önceki G91 G28 Y0. satırını sil
            # M30 satırı kontrolü
            if "M30" in line:
                # Bir önceki satır 'G91 G28 Y0.' ise onu atla
                if i > 0 and 'G91 G28 Y0.' in new_lines[i-1]:
                    # 'G91 G28 Y0.' satırını silmek için son eklenen satırı kaldır
                    if final_lines and final_lines[-1].strip() == new_lines[i-1].strip():
                         final_lines.pop()
                # 5. M30'u M02'ye dönüştür
                final_lines.append("M02\n")
            # 2. S... M03'ten sonra G5.1 Q1 ekle
            elif re.search(r'S\d+ M03$', line):
                final_lines.append(line + '\n')
                final_lines.append("G5.1 Q1\n")
            # 3. M09'dan sonra G5.1 Q0 ekle
            elif re.search(r'M09$', line):
                final_lines.append(line + '\n')
                final_lines.append("G5.1 Q0\n")
            else:
                final_lines.append(line + '\n')
            
            i += 1
        
        # 6. Program sonuna % işareti ekle (eğer yoksa)
        if final_lines and final_lines[-1].strip() != '%':
            final_lines.append('%\n')
        
        # 1. Dosya adını "_duzenlenmis" ekiyle değiştir
        file_dir, file_name = os.path.split(self.selected_file)
        file_base, file_ext = os.path.splitext(file_name)
        new_file_path = os.path.join(file_dir, f"{file_base}_duzenlenmis{file_ext}")

        # 2. Yeni dosyaya yaz
        try:
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.writelines(final_lines)
            
            self.status_label.config(text=f"Dosya başarıyla güncellendi ve kaydedildi:\n{os.path.basename(new_file_path)}")
            messagebox.showinfo("Başarılı", "Dosya başarıyla düzenlendi ve kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NCEditorApp(root)
    root.mainloop()