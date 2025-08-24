import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyttsx3
import threading
import time
from datetime import datetime

# Tema warna
THEME = {
    "bg_main": "#2C3E50",
    "bg_secondary": "#34495E",
    "bg_widget": "#ECF0F1",
    "text_primary": "#FFFFFF",
    "text_secondary": "#BDC3C7",
    "accent_red": "#E74C3C",
    "accent_green": "#2ECC71",
    "accent_blue": "#3498DB",
    "accent_yellow": "#F1C40F"
}

class BahayaJudolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Edukasi Bahaya Judi Online dan Randa")
        self.root.geometry("1000x700")
        self.root.configure(bg=THEME["bg_main"])
        
        # Inisialisasi engine TTS
        self.engine = pyttsx3.init()
        self.set_voice_properties()
        
        # Variabel state
        self.is_speaking = False
        self.stop_requested = False
        
        self.setup_ui()
        
    def set_voice_properties(self):
        """Set properti suara default"""
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 0.9)
        
    def setup_ui(self):
        """Setup antarmuka pengguna"""
        # Main container
        main_frame = tk.Frame(self.root, bg=THEME["bg_main"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="⚠️ EDUKASI BAHAYA JUDI ONLINE & RANDA ⚠️", 
            font=("Arial", 18, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["accent_red"]
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook untuk tab berbeda
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab 1: Cerita Edukasi
        self.setup_education_tab()
        
        # Tab 2: Dampak Negatif
        self.setup_impact_tab()
        
        # Tab 3: Solusi & Bantuan
        self.setup_solution_tab()
        
        # Control buttons frame
        button_frame = tk.Frame(main_frame, bg=THEME["bg_main"])
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text="▶ DENGARKAN CERITA",
            font=("Arial", 12, "bold"),
            bg=THEME["accent_green"],
            fg=THEME["text_primary"],
            width=20,
            command=self.start_speech
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ BERHENTI",
            font=("Arial", 12, "bold"),
            bg=THEME["accent_red"],
            fg=THEME["text_primary"],
            width=15,
            command=self.stop_speech,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear logs button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ BERSIHKAN LOG",
            font=("Arial", 12, "bold"),
            bg=THEME["accent_blue"],
            fg=THEME["text_primary"],
            width=15,
            command=self.clear_logs
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=THEME["bg_main"])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="✅ SIAP MENDENGARKAN",
            font=("Arial", 10, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["accent_green"]
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Logs frame
        log_frame = tk.LabelFrame(
            main_frame, 
            text=" Catatan Sistem ", 
            font=("Arial", 10, "bold"),
            bg=THEME["bg_secondary"],
            fg=THEME["text_primary"],
            relief=tk.GROOVE
        )
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 9),
            bg=THEME["bg_widget"],
            fg="#2C3E50",
            relief=tk.FLAT
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)
        
        self.add_log("Sistem edukasi siap. Pilih tab untuk mempelajari bahaya judi online dan randa.")
        
    def setup_education_tab(self):
        """Setup tab edukasi"""
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="📖 Cerita Edukasi")
        
        content = """
BAHAYA JUDI ONLINE DAN RANDA

Judol (Judi Online) dan Randa (Judi Dadu) adalah dua bentuk perjudian yang sangat berbahaya dan merusak kehidupan. 

🎲 APA ITU JUDOL DAN RANDA?
Judol adalah judi yang dilakukan melalui platform online seperti website atau aplikasi. Randa adalah judi dadu tradisional yang sering dilakukan secara sembunyi-sembunyi.

💀 DAMPAK YANG SANGAT BERBAHAYA:

1. KERUGIAN FINANSIAL BESAR
• Menghabiskan tabungan dan gaji dalam sekejap
• Terjebak utang yang tidak bisa dibayar
• Kehilangan harta benda dan aset berharga

2. KEHANCURAN KELUARGA
• Pertengkaran terus-menerus dengan pasangan
• Anak-anak menjadi korban dan terlantar
• Perceraian dan broken home

3. MASUK PENJARA
• Judi adalah illegal di Indonesia
• Hukuman penjara menanti para pelaku
• Masa depan suram dengan catatan kriminal

4. KESEHATAN MENTAL RUSAK
• Stress, depresi, dan anxiety
• Gangguan kecemasan yang parah
• Potensi bunuh diri akibat tekanan

5. ISOLASI SOSIAL
• Dikucilkan dari masyarakat
• Kehilangan teman dan relasi
• Stigma negatif seumur hidup

🚫 INGAT! Tidak ada yang menang dalam judi. Hanya bandar yang untung!
"""
        
        text_area = scrolledtext.ScrolledText(
            tab1,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg=THEME["bg_widget"],
            fg="#2C3E50",
            padx=15,
            pady=15
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
        
    def setup_impact_tab(self):
        """Setup tab dampak negatif"""
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="💔 Dampak Negatif")
        
        content = """
DAMPAK NEGATIF JUDI ONLINE DAN RANDA:

🎯 DAMPAK EKONOMI:
• Kebangkrutan finansial total
• Utang menumpuk tanpa bisa dibayar
• Kehilangan pekerjaan karena kecanduan
• Tidak bisa memenuhi kebutuhan dasar

👨‍👩‍👧‍👦 DAMPAK KELUARGA:
• KDRT meningkat drastis
• Anak-anak putus sekolah
• Keluarga terpecah belah
• Warisan keluarga habis

🏥 DAMPAK KESEHATAN:
• Gangguan tidur dan insomnia
• Penyakit jantung dan tekanan darah tinggi
• Gangguan pencernaan akibat stress
• Kekurangan gizi karena uang habis untuk judi

🔒 DAMPAK HUKUM:
• Vonis penjara 5-10 tahun
• Denda ratusan juta rupiah
• Catatan kriminal seumur hidup
• Sulit dapat pekerjaan setelah bebas

🧠 DAMPAK PSIKOLOGIS:
• Rasa malu dan bersalah terus-menerus
• Kehilangan harga diri dan kepercayaan diri
• Paranoid dan gangguan kecemasan
• Potensi bunuh diri sangat tinggi

📉 STATISTIK MENGERIKAN:
• 95% penjudi online bangkrut total
• 80% keluarga penjudi bercerai
• 70% anak penjudi putus sekolah
• 60% penjudi akhirnya dipenjara
"""
        
        text_area = scrolledtext.ScrolledText(
            tab2,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg=THEME["bg_widget"],
            fg="#2C3E50",
            padx=15,
            pady=15
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
        
    def setup_solution_tab(self):
        """Setup tab solusi dan bantuan"""
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="🆘 Solusi & Bantuan")
        
        content = """
SOLUSI DAN BANTUAN UNTUK KORBAN JUDI:

🆘 JIKA ANDA KECANDUAN JUDI:
1. AKUI MASALAHNYA
   • Sadari bahwa anda punya masalah
   • Berhenti menyangkal dan mencari alasan

2. CARI BANTUAN PROFESIONAL
   • Psikolog atau psikiater
   • Terapi perilaku kognitif
   • Konseling kecanduan

3. KELOLA KEUANGAN
   • Serahkan pengelolaan uang pada orang terpercaya
   • Blokir akses ke situs judi
   • Buat anggaran ketat

4. SUPPORT SYSTEM
   • Bergabung dengan support group
   • Cerita pada keluarga dan teman
   • Hindari teman-teman judi

📞 HOTLINE BANTUAN:
• Kementerian Sosial: 1500-771
• Lembaga Bantuan Hukum: 0811-8888-110
• Konseling Psikologi: 1198
• BNP2TKI: 1500-255

🏛️ LEMBAGA BANTUAN:
1. PANTI REHABILITASI
   • Program detoksifikasi judi
   • Terapi intensif 3-6 bulan
   • Pendampingan pasca rehab

2. BANTUAN HUKUM
   • Konsultasi hukum gratis
   • Pendampingan pengadilan
   • Bantuan pengurangan hukuman

3. BANTUAN EKONOMI
   • Pelatihan keterampilan
   • Bantuan modal usaha
   • Program reintegrasi sosial

🎯 PENCEGAHAN:
• Edukasi sejak dini tentang bahaya judi
• Pengawasan orang tua terhadap aktivitas online
• Blokir situs-situs judi melalui internet positif
• Laporkan bandar judi pada polisi

💪 INGAT! Masih ada harapan untuk berubah. Mulai dari sekarang juga!
"""
        
        text_area = scrolledtext.ScrolledText(
            tab3,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg=THEME["bg_widget"],
            fg="#2C3E50",
            padx=15,
            pady=15
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
        
    def add_log(self, message):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, log_message)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        
    def clear_logs(self):
        """Clear all logs"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.add_log("Log sistem telah dibersihkan.")
        
    def start_speech(self):
        """Start text to speech conversion"""
        current_tab = self.notebook.index(self.notebook.select())
        text_content = ""
        
        # Get content based on selected tab
        if current_tab == 0:  # Cerita Edukasi
            text_content = """
            BAHAYA JUDI ONLINE DAN RANDA. Judol dan Randa adalah dua bentuk perjudian yang sangat berbahaya. 
            Judi online dilakukan melalui platform digital, sementara randa adalah judi dadu tradisional. 
            Keduanya menyebabkan kerugian finansial besar, kehancuran keluarga, hukuman penjara, 
            kerusakan mental, dan isolasi sosial. Ingat, hanya bandar yang untung dari judi!
            """
        elif current_tab == 1:  # Dampak Negatif
            text_content = """
            DAMPAK NEGATIF JUDI sangat mengerikan. Secara ekonomi menyebabkan kebangkrutan dan utang. 
            Keluarga hancur berantakan, KDRT meningkat, anak-anak terlantar. 
            Kesehatan fisik dan mental rusak parah, stress, depresi, bahkan bunuh diri. 
            Hukumannya penjara 5-10 tahun dan denda ratusan juta. 95% penjudi bangkrut total!
            """
        else:  # Solusi & Bantuan
            text_content = """
            ADA SOLUSI untuk korban judi. Akui masalahnya, cari bantuan profesional, kelola keuangan, 
            bangun support system. Hubungi hotline bantuan di 1500-771 untuk Kementerian Sosial, 
            1198 untuk konseling psikologi. Ada panti rehabilitasi, bantuan hukum, dan pelatihan keterampilan. 
            Masih ada harapan untuk berubah!
            """
            
        if not text_content.strip():
            messagebox.showwarning("Peringatan", "Tidak ada konten untuk dibacakan!")
            return
            
        if self.is_speaking:
            messagebox.showwarning("Peringatan", "Sedang dalam proses berbicara!")
            return
            
        # Update UI state
        self.is_speaking = True
        self.stop_requested = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="🔊 SEDANG BERBICARA...", fg=THEME["accent_red"])
        
        self.add_log("Memulai edukasi tentang bahaya judi...")
        
        # Jalankan di thread terpisah
        thread = threading.Thread(target=self.speech_thread, args=(text_content,))
        thread.daemon = True
        thread.start()
        
    def stop_speech(self):
        """Stop current speech"""
        self.stop_requested = True
        self.add_log("Permintaan berhenti dikirim...")
        
    def speech_thread(self, text):
        """Thread untuk menjalankan text to speech"""
        try:
            # Jalankan speech
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Cek jika di-stop
            if self.stop_requested:
                self.add_log("Edukasi dihentikan oleh pengguna.")
            else:
                self.add_log("Edukasi selesai. Mari hindari judi dan mulai hidup sehat!")
                
        except Exception as e:
            self.add_log(f"Error selama proses: {e}")
            
        finally:
            # Reset UI state
            self.root.after(0, self.reset_ui_state)
            
    def reset_ui_state(self):
        """Reset UI state setelah speech selesai"""
        self.is_speaking = False
        self.stop_requested = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="✅ SIAP MENDENGARKAN", fg=THEME["accent_green"])

def main():
    """Main function"""
    root = tk.Tk()
    app = BahayaJudolApp(root)
    
    # Center window
    root.eval('tk::PlaceWindow . center')
    
    # Run application
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Aplikasi ditutup oleh pengguna")

if __name__ == "__main__":
    main()