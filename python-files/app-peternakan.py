import customtkinter as ctk
import sqlite3
from tkinter import messagebox, ttk
import datetime
import json
from PIL import Image
import os

# Konfigurasi tema
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"

class PeternakanApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Sistem Manajemen Peternakan")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)
        
        # Inisialisasi database
        self.init_database()
        
        # Setup UI
        self.setup_ui()
        
        # Timer untuk waktu realtime
        self.update_time()
        
    def init_database(self):
        """Inisialisasi database dan tabel jika belum ada"""
        self.conn = sqlite3.connect('peternakan.db')
        self.cursor = self.conn.cursor()
        
        # Buat tabel jika belum ada
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS hewan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jenis TEXT NOT NULL,
                jenis_hewan TEXT NOT NULL,
                identifikasi TEXT NOT NULL UNIQUE,
                tanggal_lahir TEXT,
                jenis_kelamin TEXT,
                berat REAL,
                kesehatan TEXT,
                catatan TEXT,
                tanggal_masuk TEXT NOT NULL
            )
        ''')
        
        # Tabel untuk logs
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waktu TEXT NOT NULL,
                aktivitas TEXT NOT NULL,
                detail TEXT
            )
        ''')
        self.conn.commit()
        
    def setup_ui(self):
        """Setup antarmuka pengguna"""
        # Frame utama
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header dengan judul dan waktu
        self.header_frame = ctk.CTkFrame(self.main_frame, height=80)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Sistem Manajemen Peternakan",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=20)
        
        self.time_label = ctk.CTkLabel(
            self.header_frame, 
            text="",
            font=ctk.CTkFont(size=16),
            fg_color="#2C3E50",
            corner_radius=10
        )
        self.time_label.pack(side="right", padx=20, pady=20)
        
        # Frame untuk konten utama
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        # Frame untuk form input (kiri)
        self.input_frame = ctk.CTkFrame(self.content_frame, width=400)
        self.input_frame.pack(side="left", fill="y", padx=(0, 20))
        self.input_frame.pack_propagate(False)
        
        # Frame untuk tabel data (kanan)
        self.table_frame = ctk.CTkFrame(self.content_frame)
        self.table_frame.pack(side="right", fill="both", expand=True)
        
        # Judul form input
        ctk.CTkLabel(
            self.input_frame, 
            text="Form Input Data Hewan",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Form input
        form_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Grid layout untuk form input
        form_frame.columnconfigure(1, weight=1)
        
        # Label dan input fields
        labels = [
            "Jenis*", "Jenis Hewan*", "Identifikasi*", 
            "Tanggal Lahir", "Jenis Kelamin", "Berat (kg)", 
            "Kesehatan", "Catatan"
        ]
        self.entries = {}
        
        for i, label in enumerate(labels):
            ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont(weight="bold")).grid(
                row=i, column=0, padx=10, pady=10, sticky="w"
            )
            
            if label == "Jenis*":
                options = ["Sapi", "Kambing"]
                entry = ctk.CTkComboBox(form_frame, values=options, state="readonly")
                entry.set("Pilih Jenis")
            elif label == "Jenis Hewan*":
                options = ["Perah", "Pedaging", "Lainnya"]
                entry = ctk.CTkComboBox(form_frame, values=options, state="readonly")
                entry.set("Pilih Jenis Hewan")
            elif label == "Jenis Kelamin":
                options = ["Jantan", "Betina"]
                entry = ctk.CTkComboBox(form_frame, values=options, state="readonly")
                entry.set("Pilih Jenis Kelamin")
            elif label == "Tanggal Lahir":
                entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
            else:
                entry = ctk.CTkEntry(form_frame, placeholder_text=f"Masukkan {label.lower()}")
                
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.entries[label.replace('*', '').strip().lower().replace(' ', '_')] = entry
        
        # Frame untuk tombol aksi
        self.button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)
        
        # Tombol aksi
        self.add_btn = ctk.CTkButton(
            self.button_frame, text="Tambah", command=self.add_hewan,
            fg_color="#2AA876", hover_color="#207A5A", width=100
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.update_btn = ctk.CTkButton(
            self.button_frame, text="Update", command=self.update_hewan,
            fg_color="#3B8ED0", hover_color="#2D70AC", width=100, state="disabled"
        )
        self.update_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            self.button_frame, text="Hapus", command=self.delete_hewan,
            fg_color="#E74C3C", hover_color="#C0392B", width=100, state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        # Frame untuk tombol khusus
        self.special_button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.special_button_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)
        
        self.clear_btn = ctk.CTkButton(
            self.special_button_frame, text="Bersihkan Form", command=self.clear_form,
            fg_color="#7F8C8D", hover_color="#616A6B", width=120
        )
        self.clear_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(
            self.special_button_frame, text="Simpan ke TXT", command=self.save_to_txt,
            fg_color="#3498DB", hover_color="#2980B9", width=120
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.logs_btn = ctk.CTkButton(
            self.special_button_frame, text="Lihat Logs", command=self.show_logs,
            fg_color="#9B59B6", hover_color="#8E44AD", width=120
        )
        self.logs_btn.pack(side="left", padx=5)
        
        # Pencarian
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Cari berdasarkan identifikasi atau jenis..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.search_hewan)
        
        self.search_btn = ctk.CTkButton(
            search_frame, 
            text="Cari", 
            command=self.search_hewan,
            width=100
        )
        self.search_btn.pack(side="right")
        
        # Treeview untuk menampilkan data
        columns = ("ID", "Jenis", "Jenis Hewan", "Identifikasi", "Tanggal Lahir", 
                  "Jenis Kelamin", "Berat", "Kesehatan", "Catatan", "Tanggal Masuk")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define headings
        column_widths = [50, 80, 100, 120, 100, 100, 80, 100, 150, 100]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[i], minwidth=50)
        
        # Scrollbar untuk treeview
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout treeview dan scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind event ketika item dipilih
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Load data awal
        self.load_data()
        
        # Tambah log aktivitas
        self.add_log("Aplikasi dimulai", "Sistem manajemen peternakan dijalankan")
    
    def update_time(self):
        """Update waktu realtime"""
        now = datetime.datetime.now()
        # Waktu lokal (WIB)
        wib_time = now.strftime("%d-%m-%Y %H:%M:%S WIB")
        # Waktu Moskow (+3 jam dari UTC)
        moscom_time = (now + datetime.timedelta(hours=3)).strftime("%H:%M:%S MOSCOM")
        
        time_text = f"{wib_time} | {moscom_time}"
        self.time_label.configure(text=time_text)
        
        # Update setiap detik
        self.window.after(1000, self.update_time)
    
    def add_log(self, aktivitas, detail=""):
        """Menambahkan log aktivitas"""
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO logs (waktu, aktivitas, detail) VALUES (?, ?, ?)",
            (waktu, aktivitas, detail)
        )
        self.conn.commit()
    
    def load_data(self, data=None):
        """Memuat data ke treeview"""
        # Hapus data lama
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Jika data tidak diberikan, ambil dari database
        if data is None:
            self.cursor.execute("SELECT * FROM hewan ORDER BY tanggal_masuk DESC")
            data = self.cursor.fetchall()
        
        # Masukkan data ke treeview
        for row in data:
            self.tree.insert("", "end", values=row)
    
    def add_hewan(self):
        """Menambahkan hewan baru"""
        # Ambil data dari form
        jenis = self.entries['jenis'].get().strip()
        jenis_hewan = self.entries['jenis_hewan'].get().strip()
        identifikasi = self.entries['identifikasi'].get().strip()
        tanggal_lahir = self.entries['tanggal_lahir'].get().strip()
        jenis_kelamin = self.entries['jenis_kelamin'].get().strip()
        
        try:
            berat = float(self.entries['berat'].get().strip()) if self.entries['berat'].get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Error", "Berat harus angka")
            return
        
        kesehatan = self.entries['kesehatan'].get().strip()
        catatan = self.entries['catatan'].get().strip()
        tanggal_masuk = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Validasi input
        if not jenis or jenis == "Pilih Jenis":
            messagebox.showerror("Error", "Jenis hewan harus dipilih")
            return
        
        if not jenis_hewan or jenis_hewan == "Pilih Jenis Hewan":
            messagebox.showerror("Error", "Jenis hewan harus dipilih")
            return
            
        if not identifikasi:
            messagebox.showerror("Error", "Identifikasi harus diisi")
            return
        
        # Coba tambahkan ke database
        try:
            self.cursor.execute(
                """INSERT INTO hewan 
                (jenis, jenis_hewan, identifikasi, tanggal_lahir, jenis_kelamin, berat, kesehatan, catatan, tanggal_masuk) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (jenis, jenis_hewan, identifikasi, tanggal_lahir, jenis_kelamin, berat, kesehatan, catatan, tanggal_masuk)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sukses", "Data hewan berhasil ditambahkan")
            self.add_log("Tambah hewan", f"{jenis} - {identifikasi} ditambahkan")
            self.clear_form()
            self.load_data()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Identifikasi sudah ada")
    
    def update_hewan(self):
        """Memperbarui data hewan"""
        # Dapatkan ID dari item yang dipilih
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih hewan yang akan diupdate")
            return
            
        hewan_id = self.tree.item(selected_item)['values'][0]
        
        # Ambil data dari form
        jenis = self.entries['jenis'].get().strip()
        jenis_hewan = self.entries['jenis_hewan'].get().strip()
        identifikasi = self.entries['identifikasi'].get().strip()
        tanggal_lahir = self.entries['tanggal_lahir'].get().strip()
        jenis_kelamin = self.entries['jenis_kelamin'].get().strip()
        
        try:
            berat = float(self.entries['berat'].get().strip()) if self.entries['berat'].get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Error", "Berat harus angka")
            return
        
        kesehatan = self.entries['kesehatan'].get().strip()
        catatan = self.entries['catatan'].get().strip()
        
        # Validasi input
        if not jenis or jenis == "Pilih Jenis":
            messagebox.showerror("Error", "Jenis hewan harus dipilih")
            return
        
        if not jenis_hewan or jenis_hewan == "Pilih Jenis Hewan":
            messagebox.showerror("Error", "Jenis hewan harus dipilih")
            return
            
        if not identifikasi:
            messagebox.showerror("Error", "Identifikasi harus diisi")
            return
        
        # Update database
        try:
            self.cursor.execute(
                """UPDATE hewan 
                SET jenis=?, jenis_hewan=?, identifikasi=?, tanggal_lahir=?, jenis_kelamin=?, 
                    berat=?, kesehatan=?, catatan=?
                WHERE id=?""",
                (jenis, jenis_hewan, identifikasi, tanggal_lahir, jenis_kelamin, 
                 berat, kesehatan, catatan, hewan_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Sukses", "Data hewan berhasil diupdate")
            self.add_log("Update hewan", f"{jenis} - {identifikasi} diupdate")
            self.clear_form()
            self.load_data()
            self.toggle_buttons(False)
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Identifikasi sudah ada")
    
    def delete_hewan(self):
        """Menghapus hewan"""
        # Dapatkan ID dari item yang dipilih
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih hewan yang akan dihapus")
            return
            
        hewan_id = self.tree.item(selected_item)['values'][0]
        jenis = self.tree.item(selected_item)['values'][1]
        identifikasi = self.tree.item(selected_item)['values'][3]
        
        # Konfirmasi penghapusan
        if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus {jenis} - {identifikasi}?"):
            self.cursor.execute("DELETE FROM hewan WHERE id=?", (hewan_id,))
            self.conn.commit()
            
            messagebox.showinfo("Sukses", "Data hewan berhasil dihapus")
            self.add_log("Hapus hewan", f"{jenis} - {identifikasi} dihapus")
            self.clear_form()
            self.load_data()
            self.toggle_buttons(False)
    
    def search_hewan(self, event=None):
        """Mencari hewan berdasarkan identifikasi atau jenis"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.load_data()
            return
            
        self.cursor.execute(
            "SELECT * FROM hewan WHERE identifikasi LIKE ? OR jenis LIKE ? OR jenis_hewan LIKE ?",
            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')
        )
        
        results = self.cursor.fetchall()
        self.load_data(results)
    
    def on_item_select(self, event):
        """Event handler ketika item dipilih di treeview"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        # Dapatkan data dari item yang dipilih
        data = self.tree.item(selected_item)['values']
        
        # Isi form dengan data yang dipilih
        self.entries['jenis'].set(data[1])
        self.entries['jenis_hewan'].set(data[2])
        self.entries['identifikasi'].delete(0, 'end')
        self.entries['identifikasi'].insert(0, data[3])
        
        self.entries['tanggal_lahir'].delete(0, 'end')
        self.entries['tanggal_lahir'].insert(0, data[4] if data[4] else "")
        
        self.entries['jenis_kelamin'].set(data[5] if data[5] else "Pilih Jenis Kelamin")
        
        self.entries['berat'].delete(0, 'end')
        self.entries['berat'].insert(0, str(data[6]) if data[6] else "")
        
        self.entries['kesehatan'].delete(0, 'end')
        self.entries['kesehatan'].insert(0, data[7] if data[7] else "")
        
        self.entries['catatan'].delete(0, 'end')
        self.entries['catatan'].insert(0, data[8] if data[8] else "")
        
        # Aktifkan tombol update dan delete
        self.toggle_buttons(True)
    
    def toggle_buttons(self, state):
        """Mengaktifkan atau menonaktifkan tombol update dan delete"""
        if state:
            self.update_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
        else:
            self.update_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
    
    def clear_form(self):
        """Mengosongkan form input"""
        for key, entry in self.entries.items():
            if isinstance(entry, ctk.CTkComboBox):
                if key == 'jenis':
                    entry.set("Pilih Jenis")
                elif key == 'jenis_hewan':
                    entry.set("Pilih Jenis Hewan")
                elif key == 'jenis_kelamin':
                    entry.set("Pilih Jenis Kelamin")
            else:
                entry.delete(0, 'end')
        
        # Deselect item di treeview
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        self.toggle_buttons(False)
        self.add_log("Form dibersihkan", "Form input dikosongkan")
    
    def save_to_txt(self):
        """Menyimpan data ke file TXT"""
        try:
            # Dapatkan semua data
            self.cursor.execute("SELECT * FROM hewan")
            data = self.cursor.fetchall()
            
            # Buat nama file dengan timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_hewan_{timestamp}.txt"
            
            # Tulis data ke file
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("DATA HEWAN TERNAK\n")
                file.write("=" * 50 + "\n")
                file.write(f"Diekspor pada: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=" * 50 + "\n\n")
                
                for row in data:
                    file.write(f"ID: {row[0]}\n")
                    file.write(f"Jenis: {row[1]}\n")
                    file.write(f"Jenis Hewan: {row[2]}\n")
                    file.write(f"Identifikasi: {row[3]}\n")
                    file.write(f"Tanggal Lahir: {row[4]}\n")
                    file.write(f"Jenis Kelamin: {row[5]}\n")
                    file.write(f"Berat: {row[6]} kg\n")
                    file.write(f"Kesehatan: {row[7]}\n")
                    file.write(f"Catatan: {row[8]}\n")
                    file.write(f"Tanggal Masuk: {row[9]}\n")
                    file.write("-" * 30 + "\n")
            
            messagebox.showinfo("Sukses", f"Data berhasil disimpan ke {filename}")
            self.add_log("Ekspor data", f"Data diekspor ke {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan data: {str(e)}")
    
    def show_logs(self):
        """Menampilkan jendela logs"""
        logs_window = ctk.CTkToplevel(self.window)
        logs_window.title("Log Aktivitas")
        logs_window.geometry("800x500")
        logs_window.transient(self.window)
        logs_window.grab_set()
        
        # Frame untuk logs
        logs_frame = ctk.CTkFrame(logs_window)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview untuk logs
        columns = ("Waktu", "Aktivitas", "Detail")
        tree = ttk.Treeview(logs_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200, minwidth=100)
        
        tree.column("Waktu", width=150)
        tree.column("Aktivitas", width=150)
        tree.column("Detail", width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load logs
        self.cursor.execute("SELECT * FROM logs ORDER BY id DESC")
        logs = self.cursor.fetchall()
        
        for log in logs:
            tree.insert("", "end", values=(log[1], log[2], log[3]))
        
        # Tombol tutup
        ctk.CTkButton(
            logs_window, 
            text="Tutup", 
            command=logs_window.destroy,
            width=100
        ).pack(pady=10)
    
    def run(self):
        """Menjalankan aplikasi"""
        self.window.mainloop()
        
    def __del__(self):
        """Cleanup ketika aplikasi ditutup"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    app = PeternakanApp()
    app.run()