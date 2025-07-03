import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def organize_files():
    """
    Mengatur file di direktori yang dipilih ke dalam subfolder berdasarkan ekstensinya.
    """
    source_dir = filedialog.askdirectory(title="Pilih Direktori untuk Diatur")
    if not source_dir:
        messagebox.showwarning("Peringatan", "Direktori tidak dipilih.")
        return

    try:
        # Dapatkan daftar semua item (file dan folder) di direktori sumber
        items = os.listdir(source_dir)
        files_moved_count = 0

        for item in items:
            item_path = os.path.join(source_dir, item)

            # Periksa apakah item tersebut adalah file
            if os.path.isfile(item_path):
                # Dapatkan nama file dan ekstensinya
                filename, file_extension = os.path.splitext(item)

                # Hapus titik dari ekstensi dan ubah menjadi huruf kecil
                # Jika tidak ada ekstensi (misal: file tanpa ekstensi), gunakan 'no_extension'
                if file_extension:
                    extension_name = file_extension[1:].lower()
                else:
                    extension_name = "no_extension"

                # Buat jalur untuk folder tujuan
                destination_folder = os.path.join(source_dir, extension_name)

                # Buat folder tujuan jika belum ada
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)

                # Pindahkan file ke folder tujuan
                shutil.move(item_path, os.path.join(destination_folder, item))
                files_moved_count += 1

        messagebox.showinfo("Selesai", f"Pengaturan file selesai! {files_moved_count} file dipindahkan.")

    except Exception as e:
        messagebox.showerror("Kesalahan", f"Terjadi kesalahan: {e}")

def create_gui():
    """
    Membuat antarmuka pengguna grafis (GUI) untuk aplikasi.
    """
    root = tk.Tk()
    root.title("Pengatur File")
    root.geometry("400x250") # Menyesuaikan ukuran jendela untuk copyright
    root.resizable(False, False) # Nonaktifkan perubahan ukuran jendela

    # Mengatur tema dan warna dasar
    root.configure(bg="#2c3e50") # Dark background
    text_color = "#ecf0f1" # Light text
    button_bg = "#3498db" # Blue button
    button_fg = "#ffffff" # White button text
    hover_bg = "#2980b9" # Darker blue on hover

    # Membuat label judul
    title_label = tk.Label(root, text="Pengatur File Otomatis", font=("Inter", 16, "bold"), bg=root.cget('bg'), fg=text_color)
    title_label.pack(pady=20)

    # Membuat tombol untuk memilih direktori dan memulai pengaturan
    organize_button = tk.Button(root, text="Pilih Direktori & Atur", command=organize_files,
                                font=("Inter", 12), bg=button_bg, fg=button_fg,
                                activebackground=hover_bg, activeforeground=button_fg,
                                relief=tk.RAISED, bd=3, padx=15, pady=8)
    organize_button.pack(pady=10)

    # Menambahkan sedikit efek hover
    def on_enter(e):
        e.widget['background'] = hover_bg

    def on_leave(e):
        e.widget['background'] = button_bg

    organize_button.bind("<Enter>", on_enter)
    organize_button.bind("<Leave>", on_leave)

    # Menambahkan label informasi di bagian bawah
    info_label = tk.Label(root, text="File akan dipindahkan ke subfolder berdasarkan ekstensinya.",
                          font=("Inter", 10), bg=root.cget('bg'), fg=text_color)
    info_label.pack(pady=10)

    # Menambahkan label copyright
    copyright_label = tk.Label(root, text="© Finuex 2025 v1.0.0", font=("Inter", 8), bg=root.cget('bg'), fg=text_color)
    copyright_label.pack(side=tk.BOTTOM, pady=5) # Menempatkan di bagian bawah jendela

    root.mainloop()

if __name__ == "__main__":
    create_gui()
