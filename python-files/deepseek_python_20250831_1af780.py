import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import threading
import sys

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern MP3/MP4 İndirici")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Title.TLabel', background='#f0f0f0', font=('Arial', 16, 'bold'))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        # Ana çerçeve
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Modern MP3/MP4 İndirici", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Sekmeler
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # MP3 Manuel sekmesi
        mp3_manual_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mp3_manual_frame, text="MP3 İndir (Şarkı-Ad)")
        
        ttk.Label(mp3_manual_frame, text="Şarkı adı ve sanatçı:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.track_entry = ttk.Entry(mp3_manual_frame, width=50)
        self.track_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(mp3_manual_frame, text="İndir", command=self.download_mp3_manual).grid(row=1, column=1, pady=10, sticky=tk.E)
        
        # YouTube MP3 sekmesi
        yt_mp3_frame = ttk.Frame(notebook, padding="10")
        notebook.add(yt_mp3_frame, text="YouTube'dan MP3")
        
        ttk.Label(yt_mp3_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.yt_mp3_entry = ttk.Entry(yt_mp3_frame, width=50)
        self.yt_mp3_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(yt_mp3_frame, text="İndir", command=self.download_yt_mp3).grid(row=1, column=1, pady=10, sticky=tk.E)
        
        # SoundCloud sekmesi
        sc_frame = ttk.Frame(notebook, padding="10")
        notebook.add(sc_frame, text="SoundCloud'dan MP3")
        
        ttk.Label(sc_frame, text="SoundCloud URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sc_entry = ttk.Entry(sc_frame, width=50)
        self.sc_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(sc_frame, text="İndir", command=self.download_soundcloud).grid(row=1, column=1, pady=10, sticky=tk.E)
        
        # YouTube Video sekmesi
        yt_video_frame = ttk.Frame(notebook, padding="10")
        notebook.add(yt_video_frame, text="YouTube'dan Video")
        
        ttk.Label(yt_video_frame, text="YouTube URL veya arama:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.yt_video_entry = ttk.Entry(yt_video_frame, width=50)
        self.yt_video_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(yt_video_frame, text="Kalite:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(yt_video_frame, textvariable=self.quality_var, width=20)
        quality_combo['values'] = ('360p', '480p', '720p (HD)', '1080p (Full HD)', '1440p (2K)', '2160p (4K)')
        quality_combo.current(2)  # Varsayılan 720p
        quality_combo.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Button(yt_video_frame, text="İndir", command=self.download_yt_video).grid(row=2, column=1, pady=10, sticky=tk.E)
        
        # Toplu MP3 sekmesi
        bulk_mp3_frame = ttk.Frame(notebook, padding="10")
        notebook.add(bulk_mp3_frame, text="Toplu MP3 İndir")
        
        ttk.Label(bulk_mp3_frame, text="Şarkı listesi (her satıra bir şarkı):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bulk_text = scrolledtext.ScrolledText(bulk_mp3_frame, width=50, height=10)
        self.bulk_text.grid(row=1, column=0, columnspan=2, pady=5, padx=5)
        ttk.Button(bulk_mp3_frame, text="İndir", command=self.download_bulk_mp3).grid(row=2, column=1, pady=10, sticky=tk.E)
        
        # Durum çıktısı
        ttk.Label(main_frame, text="İşlem Durumu:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.status_text = scrolledtext.ScrolledText(main_frame, width=80, height=15, state='disabled')
        self.status_text.grid(row=3, column=0, columnspan=2, pady=5)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Batch dosyasının yolu
        self.batch_file = "MP3_MP4_indir_Qwen.bat"
        
        # Batch dosyasını kontrol et
        if not os.path.exists(self.batch_file):
            self.log_message("HATA: Batch dosyası bulunamadı!")
            messagebox.showerror("Hata", "Batch dosyası bulunamadı! Lütfen script ile aynı dizinde olduğundan emin olun.")
    
    def log_message(self, message):
        """Durum kısmına mesaj yaz"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def run_batch_command(self, command_index, parameter=""):
        """Batch scriptini çalıştır"""
        try:
            self.progress.start()
            self.log_message(f"İşlem başlatılıyor...")
            
            # Batch scriptini çalıştır
            cmd = [self.batch_file, str(command_index)]
            if parameter:
                cmd.append(parameter)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Çıktıyı gerçek zamanlı olarak al
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())
            
            return_code = process.poll()
            if return_code == 0:
                self.log_message("İşlem başarıyla tamamlandı!")
                messagebox.showinfo("Başarılı", "İndirme işlemi tamamlandı!")
            else:
                self.log_message(f"İşlem hata kodu ile sonlandı: {return_code}")
                messagebox.showerror("Hata", "İndirme işleminde hata oluştu!")
                
        except Exception as e:
            self.log_message(f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
        finally:
            self.progress.stop()
    
    def download_mp3_manual(self):
        """MP3 Manuel indirme"""
        track_info = self.track_entry.get().strip()
        if not track_info:
            messagebox.showwarning("Uyarı", "Lütfen şarkı adı ve sanatçı bilgisini girin!")
            return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(1, f'"{track_info}"'))
        thread.daemon = True
        thread.start()
    
    def download_yt_mp3(self):
        """YouTube'dan MP3 indirme"""
        url = self.yt_mp3_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen YouTube URL'sini girin!")
            return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(2, f'"{url}"'))
        thread.daemon = True
        thread.start()
    
    def download_soundcloud(self):
        """SoundCloud'dan MP3 indirme"""
        url = self.sc_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen SoundCloud URL'sini girin!")
            return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(3, f'"{url}"'))
        thread.daemon = True
        thread.start()
    
    def download_yt_video(self):
        """YouTube'dan video indirme"""
        url = self.yt_video_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen YouTube URL'sini veya arama terimini girin!")
            return
        
        # Kalite seçeneğini sayıya çevir
        quality_map = {
            '360p': '1',
            '480p': '2', 
            '720p (HD)': '3',
            '1080p (Full HD)': '4',
            '1440p (2K)': '5',
            '2160p (4K)': '6'
        }
        
        quality = self.quality_var.get()
        if quality not in quality_map:
            quality = '720p (HD)'
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(4, f'"{url}" {quality_map[quality]}'))
        thread.daemon = True
        thread.start()
    
    def download_bulk_mp3(self):
        """Toplu MP3 indirme"""
        tracks = self.bulk_text.get("1.0", tk.END).strip()
        if not tracks:
            messagebox.showwarning("Uyarı", "Lütfen şarkı listesini girin!")
            return
        
        # Geçici dosyaya yaz
        with open("temp_tracks.txt", "w", encoding="utf-8") as f:
            f.write(tracks)
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(5, '"temp_tracks.txt"'))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()