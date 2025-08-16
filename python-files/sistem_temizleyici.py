import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import glob
import ctypes
import sys
import threading
import winshell

def is_admin():
    """Programın yönetici olarak çalışıp çalışmadığını kontrol eder."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Programı yönetici yetkileriyle yeniden başlatır."""
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        except Exception as e:
            messagebox.showerror("Hata", f"Yönetici olarak başlatılamadı: {e}")
            sys.exit()

class CleanerApp:
    def __init__(self, master):
        self.master = master
        master.title("Bilgisayar Temizleme Aracı")
        master.geometry("450x250")
        master.resizable(False, False)
        
        self.is_cleaning = False
        self.cancel_event = threading.Event()
        
        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(main_frame, text="Temizleme işlemi için hazırsınız.", font=("Helvetica", 12))
        self.label.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.status_label = ttk.Label(main_frame, text="", font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.clean_button = ttk.Button(button_frame, text="Temizlemeyi Başlat", command=self.ask_and_clean)
        self.clean_button.pack(side=tk.LEFT, padx=10)
        
        self.cancel_button = ttk.Button(button_frame, text="İptal", command=self.ask_cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button.config(state=tk.DISABLED)
        
    def ask_and_clean(self):
        answer = messagebox.askyesno(
            "Onay",
            "Bilgisayarınızdaki gereksiz dosyalar ve loglar temizlenecek. Devam etmek istiyor musunuz?",
            icon='question'
        )
        if answer:
            self.clean_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.NORMAL)
            self.is_cleaning = True
            self.cancel_event.clear()
            self.status_label.config(text="Temizleme işlemi başladı...")
            
            clean_thread = threading.Thread(target=self.clean_in_thread)
            clean_thread.daemon = True
            clean_thread.start()

    def ask_cancel(self):
        if self.is_cleaning:
            answer = messagebox.askyesno(
                "İşlemi İptal Et",
                "Temizleme işlemini iptal etmek istediğinize emin misiniz?",
                icon='warning'
            )
            if answer:
                self.cancel_event.set()
                self.status_label.config(text="Temizleme iptal ediliyor...")

    def clean_in_thread(self):
        total_deleted_size = 0
        total_deleted_items = 0
        
        # Temizlenecek ana klasörlerin yollarını belirle
        paths_to_clean = [
            os.path.join(os.getenv('TEMP')),
            os.path.join(os.getenv('TMP')),
            os.path.join(os.getenv('WINDIR'), 'Prefetch'),
            os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Recent'),
            os.path.expanduser('~')
        ]
        
        # Tüm temizlenecek öğeleri bul
        all_items = []
        for path in paths_to_clean:
            if not os.path.exists(path):
                continue
            
            try:
                # Klasörlerin içindeki her şeyi ekle
                if path in [os.getenv('TEMP'), os.getenv('TMP'), os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Recent')]:
                    for item in os.listdir(path):
                        all_items.append(os.path.join(path, item))
                
                # Log dosyalarını bul
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.log'):
                            all_items.append(os.path.join(root, file))
            except PermissionError:
                continue
            except Exception:
                continue
        
        total_items_to_clean = len(all_items) + 1 # Geri dönüşüm kutusu için +1

        if total_items_to_clean == 1:
            total_items_to_clean = 2 # Bölme hatasını önle

        # Temizleme işlemine başla ve ilerleme çubuğunu güncelle
        items_cleaned = 0
        for item_path in all_items:
            if self.cancel_event.is_set():
                break
            
            try:
                if os.path.isfile(item_path):
                    total_deleted_size += os.path.getsize(item_path)
                    os.remove(item_path)
                    total_deleted_items += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception:
                pass # Hata olursa devam et
            
            items_cleaned += 1
            progress_percent = (items_cleaned / total_items_to_clean) * 100
            self.master.after(0, self.update_progress, progress_percent, item_path)
        
        # Geri Dönüşüm Kutusunu boşalt
        if not self.cancel_event.is_set():
            try:
                self.status_label.config(text="Geri Dönüşüm Kutusu boşaltılıyor...")
                self.progress_bar['value'] = 99
                self.master.update_idletasks()
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            except (ImportError, Exception):
                pass
        
        # İşlem tamamlandığında veya iptal edildiğinde GUI'yi güncelle
        self.master.after(0, self.finish_cleaning, total_deleted_size, total_deleted_items)

    def update_progress(self, value, path):
        """İlerleme çubuğu ve durumu günceller."""
        self.progress_bar['value'] = value
        self.status_label.config(text=f"Siliniyor: {os.path.basename(path)}")
        self.master.update_idletasks()

    def finish_cleaning(self, size, files):
        self.is_cleaning = False
        self.clean_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.status_label.config(text="")

        if self.cancel_event.is_set():
            messagebox.showinfo("İşlem İptal Edildi", "Temizleme işlemi kullanıcı tarafından iptal edildi.")
        else:
            size_mb = size / (1024 * 1024)
            messagebox.showinfo(
                "Temizleme Tamamlandı",
                f"Bilgisayar temizleme işlemi tamamlandı.\n\n"
                f"Toplam {files} dosya silindi.\n"
                f"Yaklaşık {size_mb:.2f} MB disk alanı boşaltıldı.",
                icon='info'
            )
        self.master.destroy()

def main():
    run_as_admin()
    root = tk.Tk()
    app = CleanerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()