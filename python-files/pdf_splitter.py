# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pathlib import Path

# PyPDF2/pypdf import kontrolü
try:
    import PyPDF2
    print("PyPDF2 yüklendi")
except ImportError:
    try:
        import pypdf as PyPDF2
        print("pypdf (yeni sürüm) yüklendi")
    except ImportError:
        print("HATA: PyPDF2 veya pypdf kütüphanesi yüklü değil!")
        print("Lütfen şu komutu çalıştırın: pip install pypdf")
        exit(1)

class PDFSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Bölme Programı")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Değişkenler
        self.pdf_path = ""
        self.total_pages = 0
        
        # Stil ayarları
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ana çerçeve
        main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = tk.Label(main_frame, text="PDF BÖLME PROGRAMI", 
                              font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # PDF seçim bölümü
        select_frame = tk.Frame(main_frame, bg='#f0f0f0')
        select_frame.pack(fill=tk.X, pady=10)
        
        self.select_btn = tk.Button(select_frame, text="PDF Dosyası Seç", 
                                    command=self.select_pdf,
                                    bg='#3498db', fg='white', font=("Arial", 10, "bold"),
                                    padx=20, pady=10, cursor="hand2")
        self.select_btn.pack(side=tk.LEFT)
        
        self.file_label = tk.Label(select_frame, text="Dosya seçilmedi", 
                                   bg='#f0f0f0', fg='#7f8c8d', font=("Arial", 9))
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Sayfa bilgisi
        self.info_label = tk.Label(main_frame, text="", bg='#f0f0f0', fg='#2c3e50', 
                                   font=("Arial", 10))
        self.info_label.pack(pady=10)
        
        # Sayfa aralığı bölümü
        range_frame = tk.LabelFrame(main_frame, text="Sayfa Aralığı", 
                                   bg='#f0f0f0', fg='#2c3e50', 
                                   font=("Arial", 11, "bold"), padx=15, pady=15)
        range_frame.pack(fill=tk.X, pady=20)
        
        # Başlangıç sayfası
        start_frame = tk.Frame(range_frame, bg='#f0f0f0')
        start_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(start_frame, text="Başlangıç Sayfası:", bg='#f0f0f0', 
                fg='#2c3e50', width=15, anchor='w').pack(side=tk.LEFT)
        
        self.start_var = tk.StringVar(value="1")
        self.start_entry = tk.Entry(start_frame, textvariable=self.start_var, 
                                   width=10, font=("Arial", 10))
        self.start_entry.pack(side=tk.LEFT)
        
        # Bitiş sayfası
        end_frame = tk.Frame(range_frame, bg='#f0f0f0')
        end_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(end_frame, text="Bitiş Sayfası:", bg='#f0f0f0', 
                fg='#2c3e50', width=15, anchor='w').pack(side=tk.LEFT)
        
        self.end_var = tk.StringVar(value="1")
        self.end_entry = tk.Entry(end_frame, textvariable=self.end_var, 
                                 width=10, font=("Arial", 10))
        self.end_entry.pack(side=tk.LEFT)
        
        # Kayıt ismi
        name_frame = tk.Frame(main_frame, bg='#f0f0f0')
        name_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(name_frame, text="Yeni Dosya Adı:", bg='#f0f0f0', 
                fg='#2c3e50', font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.name_var = tk.StringVar(value="bolunmus_pdf")
        self.name_entry = tk.Entry(name_frame, textvariable=self.name_var, 
                                  width=30, font=("Arial", 10))
        self.name_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(name_frame, text=".pdf", bg='#f0f0f0', 
                fg='#2c3e50', font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Bölme butonu
        self.split_btn = tk.Button(main_frame, text="PDF'i Böl", 
                                  command=self.split_pdf,
                                  bg='#27ae60', fg='white', font=("Arial", 12, "bold"),
                                  padx=30, pady=12, cursor="hand2", state=tk.DISABLED)
        self.split_btn.pack(pady=20)
        
        # Durum çubuğu
        self.status_label = tk.Label(main_frame, text="PDF dosyası seçerek başlayın", 
                                    bg='#ecf0f1', fg='#34495e', 
                                    font=("Arial", 9), relief=tk.SUNKEN, anchor='w')
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
    def select_pdf(self):
        """PDF dosyası seçme işlemi"""
        self.pdf_path = filedialog.askopenfilename(
            title="PDF Dosyası Seç",
            filetypes=[("PDF Dosyaları", "*.pdf")]
        )
        
        if self.pdf_path:
            try:
                # PDF'i oku ve sayfa sayısını al
                with open(self.pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    self.total_pages = len(pdf_reader.pages)
                
                # Dosya adını göster
                filename = os.path.basename(self.pdf_path)
                self.file_label.config(text=f"✓ {filename}", fg='#27ae60')
                
                # Sayfa bilgisini göster
                self.info_label.config(text=f"Toplam Sayfa Sayısı: {self.total_pages}")
                
                # Varsayılan değerleri ayarla
                self.end_var.set(str(self.total_pages))
                
                # Bölme butonunu aktif et
                self.split_btn.config(state=tk.NORMAL)
                
                # Durum güncelle
                self.status_label.config(text="PDF başarıyla yüklendi. Sayfa aralığını belirleyin.")
                
            except Exception as e:
                messagebox.showerror("Hata", f"PDF dosyası okunamadı:\n{str(e)}")
                self.reset_fields()
    
    def split_pdf(self):
        """PDF bölme işlemi"""
        try:
            # Girdi kontrolü
            start_page = int(self.start_var.get())
            end_page = int(self.end_var.get())
            
            # Sayfa numarası kontrolleri
            if start_page < 1 or start_page > self.total_pages:
                raise ValueError(f"Başlangıç sayfası 1 ile {self.total_pages} arasında olmalıdır.")
            
            if end_page < 1 or end_page > self.total_pages:
                raise ValueError(f"Bitiş sayfası 1 ile {self.total_pages} arasında olmalıdır.")
            
            if start_page > end_page:
                raise ValueError("Başlangıç sayfası bitiş sayfasından büyük olamaz.")
            
            # Durum güncelle
            self.status_label.config(text="PDF bölünüyor...")
            self.root.update()
            
            # PDF'i oku
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Belirtilen sayfaları ekle (0 indeksli olduğu için -1)
                for page_num in range(start_page - 1, end_page):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Kaydetme yolunu belirle
                output_name = self.name_var.get().strip()
                if not output_name:
                    output_name = "bolunmus_pdf"
                
                # .pdf uzantısını kontrol et
                if not output_name.endswith('.pdf'):
                    output_name += '.pdf'
                
                # Masaüstü yolu
                desktop_path = Path.home() / "Desktop"
                output_path = desktop_path / output_name
                
                # Dosya varsa numaralandır
                counter = 1
                original_path = output_path
                while output_path.exists():
                    name_without_ext = original_path.stem
                    output_path = desktop_path / f"{name_without_ext}_{counter}.pdf"
                    counter += 1
                
                # PDF'i kaydet
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                # Başarı mesajı
                selected_pages = end_page - start_page + 1
                messagebox.showinfo("Başarılı", 
                    f"PDF başarıyla bölündü!\n\n"
                    f"Seçilen sayfalar: {start_page}-{end_page} ({selected_pages} sayfa)\n"
                    f"Kaydedildi: {output_path.name}\n"
                    f"Konum: Masaüstü")
                
                self.status_label.config(text=f"✓ PDF başarıyla kaydedildi: {output_path.name}")
                
        except FileNotFoundError:
            messagebox.showerror("Hata", "Masaüstü klasörü bulunamadı. Lütfen manuel olarak kaydedin.")
            
            # Manuel kaydetme
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Dosyaları", "*.pdf")],
                initialfile=output_name
            )
            
            if save_path:
                with open(self.pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    pdf_writer = PyPDF2.PdfWriter()
                    
                    for page_num in range(start_page - 1, end_page):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    with open(save_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                
                messagebox.showinfo("Başarılı", f"PDF başarıyla kaydedildi:\n{save_path}")
                self.status_label.config(text=f"✓ PDF kaydedildi")
                
        except ValueError as ve:
            messagebox.showerror("Hata", str(ve))
            self.status_label.config(text="Hata: Geçersiz sayfa aralığı")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF bölünürken hata oluştu:\n{str(e)}")
            self.status_label.config(text="Hata oluştu")
    
    def reset_fields(self):
        """Alanları sıfırla"""
        self.pdf_path = ""
        self.total_pages = 0
        self.file_label.config(text="Dosya seçilmedi", fg='#7f8c8d')
        self.info_label.config(text="")
        self.start_var.set("1")
        self.end_var.set("1")
        self.split_btn.config(state=tk.DISABLED)
        self.status_label.config(text="PDF dosyası seçerek başlayın")

def main():
    print("PDF Bölme Programı başlatılıyor...")
    try:
        root = tk.Tk()
        app = PDFSplitter(root)
        print("GUI başarıyla oluşturuldu")
        root.mainloop()
    except Exception as e:
        print(f"Program başlatılırken hata oluştu: {e}")

if __name__ == "__main__":
    main()