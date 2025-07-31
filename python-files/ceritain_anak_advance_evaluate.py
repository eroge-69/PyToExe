import tkinter as tk
from tkinter import messagebox, ttk
import os
from datetime import datetime
import google.generativeai as genai
import pandas as pd
import io
import json
import subprocess
import webbrowser
import threading


class StoryGeneratorApp:
    def open_api_key_link(self):
        """Membuka link Gemini API Key di browser default."""
        webbrowser.open_new("https://aistudio.google.com/apikey")

    def open_branding_link(self, event=None):
        """Membuka link branding di browser default."""
        webbrowser.open_new(
            "lynk.id/agitasi101")  # Ganti dengan URL website Anda

    # --- FUNGSI BARU UNTUK SCROLLBAR ---
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __init__(self, root):
        self.root = root
        root.title("CeritAIn Anak - Advance")
        self.root.geometry("420x850")  # Ukuran jendela disesuaikan

        self.api_key = tk.StringVar()
        self.api_key_file = "gemini_api_key.txt"

        # Variabel untuk pilihan karakter
        self.character_type = tk.StringVar(value="Hewan")  # Default: Hewan
        self.selected_animal = tk.StringVar()
        self.selected_human_char = tk.StringVar()
        self.custom_character = tk.StringVar()

        # Variabel untuk pilihan pesan moral
        self.selected_moral = tk.StringVar()
        self.custom_moral = tk.StringVar()

        # Variabel untuk pilihan gaya cerita
        self.selected_story_style = tk.StringVar()
        self.custom_story_style = tk.StringVar()

        # Variabel untuk pilihan lokasi/setting
        self.selected_location = tk.StringVar(
            value="Hutan Ajaib")  # <-- Variabel lokasi ini
        self.custom_location = tk.StringVar()

        # Variabel untuk pilihan panjang narasi
        self.narration_length = tk.StringVar(value="Narasi Singkat")

        # Variabel untuk pilihan rentang usia
        self.selected_age_range = tk.StringVar(
            value="4-6 Tahun")  # Default: 4-6 Tahun
        self.custom_age_range = tk.StringVar()

        # Variabel untuk output file
        self.output_txt = tk.BooleanVar(value=True)  # Default: generate TXT
        self.output_xlsx = tk.BooleanVar(value=True)  # Default: generate XLSX
        # NEW: Variabel untuk opsi prompt gambar
        self.generate_image_prompts = tk.BooleanVar(
            value=True)  # Default: aktif

        # --- TAMBAHAN UNTUK SCROLLBAR ---
        # Buat Canvas
        self.canvas = tk.Canvas(root)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Buat Scrollbar dan hubungkan ke Canvas
        self.scrollbar = ttk.Scrollbar(
            root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))

        # Buat frame di dalam Canvas yang akan berisi semua widget
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")

        self.create_widgets()
        # Untuk scroll dengan mouse wheel
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.load_api_key()

    def show_progress_popup(self, title, message):
        # Buat jendela pop-up
        self.progress_popup = tk.Toplevel(self.root)
        self.progress_popup.title(title)
        # Membuat pop-up selalu di atas jendela utama
        self.progress_popup.transient(self.root)
        self.progress_popup.grab_set()  # Mencegah interaksi dengan jendela utama
        self.progress_popup.resizable(False, False)

        # Pusatkan pop-up di layar
        self.progress_popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - \
            (self.progress_popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - \
            (self.progress_popup.winfo_height() // 2)
        self.progress_popup.geometry(f"+{x}+{y}")

        # Label pesan
        self.progress_message_label = tk.Label(
            self.progress_popup, text=message, pady=10, padx=20)
        self.progress_message_label.pack()

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_popup, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.start(10)  # Mulai animasi progress bar

    def update_progress_message(self, message):
        if hasattr(self, 'progress_message_label') and self.progress_message_label.winfo_exists():
            self.progress_message_label.config(text=message)
            self.progress_popup.update_idletasks()

    def hide_progress_popup(self):
        if hasattr(self, 'progress_popup') and self.progress_popup.winfo_exists():
            self.progress_bar.stop()
            self.progress_popup.destroy()

    def create_widgets(self):

        # --- Branding Text dengan Hyperlink ---
        self.branding_label = tk.Label(
            self.scrollable_frame,
            text="by Agitasi101",
            font=("Arial", 8, "bold underline"),
            fg="blue",
            cursor="hand2"
        )
        self.branding_label.pack(pady=2, padx=10)
        self.branding_label.bind("<Button-1>", self.open_branding_link)
        # --- End Branding Text ---

        # --- Frame untuk API Key ---
        api_frame = tk.LabelFrame(
            self.scrollable_frame, text="Gemini API Key", padx=10, pady=2)
        api_frame.pack(pady=2, padx=10, fill="x")

        get_api_key_button = tk.Button(
            api_frame,
            text="Get Gemini API Key",
            command=self.open_api_key_link,
            bg="#007bff",
            fg="white",
            font=("Arial", 9, "bold")
        )
        get_api_key_button.grid(row=0, column=0, padx=5,
                                pady=5, sticky="ew", columnspan=3)

        tk.Label(api_frame, text="API Key:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        api_entry = tk.Entry(
            api_frame, textvariable=self.api_key, width=40, show="*")
        api_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        paste_button = tk.Button(
            api_frame, text="Paste", command=self.paste_api_key)
        paste_button.grid(row=1, column=2, padx=5, pady=5)
        api_frame.grid_columnconfigure(1, weight=1)

        # --- Tambahan Tombol Clear API Key ---

        clear_api_button = tk.Button(
            api_frame, text="Clear API Key", command=self.clear_api_key)
        # Baris baru untuk tombol clear, ambil 2 kolom
        clear_api_button.grid(row=2, column=1, padx=5,
                              pady=5, sticky="ew", columnspan=3)
        # --- End Tambahan ---

        # --- Frame untuk Pemilihan Karakter ---
        char_frame = tk.LabelFrame(
            self.scrollable_frame, text="Pilih Tokoh Utama", padx=10, pady=2)
        char_frame.pack(pady=2, padx=10, fill="x")

        tk.Radiobutton(char_frame, text="Hewan", variable=self.character_type, value="Hewan",
                       command=self.toggle_character_options).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(char_frame, text="Tokoh Manusia/Fantasi", variable=self.character_type, value="Tokoh",
                       command=self.toggle_character_options).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        # Agar radio button tidak terlalu lebar
        char_frame.grid_columnconfigure(1, weight=1)

        # Dropdown untuk Hewan
        self.animal_label = tk.Label(char_frame, text="Nama Hewan:")
        self.animal_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        animals = ["Kelinci", "Beruang", "Kucing",
                   "Anjing", "Gajah", "Monyet", "Burung Hantu"]
        self.animal_dropdown = ttk.Combobox(
            char_frame, textvariable=self.selected_animal, values=animals, state="readonly")
        self.animal_dropdown.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.animal_dropdown.set(animals[0])

        # Dropdown untuk Tokoh Manusia/Fantasi
        self.human_char_label = tk.Label(char_frame, text="Jenis Tokoh:")
        self.human_char_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        human_chars = ["Anak Laki-laki", "Anak Perempuan", "Putri",
                       "Pangeran", "Penyihir Baik", "Robot", "Astronot"]
        self.human_char_dropdown = ttk.Combobox(
            char_frame, textvariable=self.selected_human_char, values=human_chars, state="readonly")
        self.human_char_dropdown.grid(
            row=2, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.human_char_dropdown.set(human_chars[0])

        # Custom Character Entry
        self.custom_char_label = tk.Label(char_frame, text="Karakter Kustom:")
        self.custom_char_label.grid(
            row=3, column=0, padx=5, pady=5, sticky="w")
        self.custom_char_entry = tk.Entry(
            char_frame, textvariable=self.custom_character, width=40, state="disabled")
        self.custom_char_entry.grid(
            row=3, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        tk.Radiobutton(char_frame, text="Lainnya (input manual)", variable=self.character_type, value="Kustom",
                       command=self.toggle_character_options).grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        self.toggle_character_options()  # Atur status awal

        # --- Frame untuk Pilihan Pesan Moral ---
        moral_frame = tk.LabelFrame(
            self.scrollable_frame, text="Pilih Pesan Moral", padx=10, pady=2)
        moral_frame.pack(pady=2, padx=10, fill="x")

        tk.Label(moral_frame, text="Pesan Moral:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        morals = ["Persahabatan", "Kejujuran", "Sopan Santun", "Keberanian", "Kemandirian", "Kesabaran",
                  "Mengelola Emosi", "Kerja Sama", "Menghargai Perbedaan", "Menolong Sesama", "Lainnya (input manual)"]
        self.moral_dropdown = ttk.Combobox(
            moral_frame, textvariable=self.selected_moral, values=morals, state="readonly")
        self.moral_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.moral_dropdown.set("Persahabatan")
        self.moral_dropdown.bind("<<ComboboxSelected>>", self.on_moral_select)
        moral_frame.grid_columnconfigure(1, weight=1)

        self.custom_moral_label = tk.Label(moral_frame, text="Moral Kustom:")
        self.custom_moral_label.grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.custom_moral_entry = tk.Entry(
            moral_frame, textvariable=self.custom_moral, width=40, state="disabled")
        self.custom_moral_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        self.on_moral_select(None)  # Atur status awal

        # --- Frame untuk Pilihan Gaya Cerita ---
        style_frame = tk.LabelFrame(
            self.scrollable_frame, text="Pilih Gaya Cerita", padx=10, pady=2)
        style_frame.pack(pady=2, padx=10, fill="x")

        tk.Label(style_frame, text="Gaya Cerita:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        styles = ["Lucu & Jenaka", "Petualangan Seru", "Edukasi & Pembelajaran",
                  "Fantasi & Ajaib", "Inspiratif & Positif", "Lainnya (input manual)"]
        self.style_dropdown = ttk.Combobox(
            style_frame, textvariable=self.selected_story_style, values=styles, state="readonly")
        self.style_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.style_dropdown.set("Petualangan Seru")
        self.style_dropdown.bind("<<ComboboxSelected>>", self.on_style_select)
        style_frame.grid_columnconfigure(1, weight=1)

        self.custom_style_label = tk.Label(style_frame, text="Gaya Kustom:")
        self.custom_style_label.grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.custom_style_entry = tk.Entry(
            style_frame, textvariable=self.custom_story_style, width=40, state="disabled")
        self.custom_style_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        self.on_style_select(None)  # Atur status awal

        # --- Frame BARU untuk Pilihan Lokasi/Setting ---
        location_frame = tk.LabelFrame(
            self.scrollable_frame, text="Pilih Lokasi Cerita", padx=2, pady=2)  # Sesuaikan pady/padx
        location_frame.pack(pady=2, padx=10, fill="x")  # Sesuaikan pady

        tk.Label(location_frame, text="Lokasi Cerita:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        locations = ["Hutan Ajaib", "Desa Damai", "Kota Sibuk", "Pulau Terpencil", "Bawah Laut",
                     "Luar Angkasa", "Istana Megah", "Sekolah Ceria", "Rumah Nenek", "Lainnya (input manual)"]
        self.location_dropdown = ttk.Combobox(
            location_frame, textvariable=self.selected_location, values=locations, state="readonly")
        self.location_dropdown.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        self.location_dropdown.set("Hutan Ajaib")
        self.location_dropdown.bind(
            "<<ComboboxSelected>>", self.on_location_select)
        location_frame.grid_columnconfigure(1, weight=1)

        self.custom_location_label = tk.Label(
            location_frame, text="Lokasi Kustom:")
        self.custom_location_label.grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.custom_location_entry = tk.Entry(
            location_frame, textvariable=self.custom_location, width=40, state="disabled")
        self.custom_location_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        self.on_location_select(None)  # Atur status awal

        # --- Frame BARU untuk Pilihan Panjang Narasi ---
        narration_frame = tk.LabelFrame(
            self.scrollable_frame, text="Pilih Panjang Narasi", padx=2, pady=2)
        narration_frame.pack(pady=2, padx=10, fill="x")

        tk.Radiobutton(narration_frame, text="Narasi Singkat", variable=self.narration_length,
                       value="Narasi Singkat").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(narration_frame, text="Narasi Detail", variable=self.narration_length,
                       value="Narasi Detail").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        narration_frame.grid_columnconfigure(1, weight=1)

        # --- Frame untuk Pilihan Rentang Usia ---
        age_frame = tk.LabelFrame(
            self.scrollable_frame, text="Rentang Usia Target", padx=10, pady=2)
        age_frame.pack(pady=2, padx=10, fill="x")

        tk.Label(age_frame, text="Usia Target:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        ages = ["2-4 Tahun", "4-6 Tahun",
                "6-8 Tahun", "Lainnya (input manual)"]
        self.age_dropdown = ttk.Combobox(
            age_frame, textvariable=self.selected_age_range, values=ages, state="readonly")
        self.age_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.age_dropdown.set("4-6 Tahun")
        self.age_dropdown.bind("<<ComboboxSelected>>", self.on_age_select)
        age_frame.grid_columnconfigure(1, weight=1)

        self.custom_age_label = tk.Label(age_frame, text="Usia Kustom:")
        self.custom_age_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.custom_age_entry = tk.Entry(
            age_frame, textvariable=self.custom_age_range, width=40, state="disabled")
        self.custom_age_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        self.on_age_select(None)  # Atur status awal

        # --- Frame untuk Opsi Output File ---
        output_frame = tk.LabelFrame(
            self.scrollable_frame, text="Jenis File Output", padx=10, pady=2)
        output_frame.pack(pady=2, padx=10, fill="x")

        tk.Checkbutton(output_frame, text=".txt", variable=self.output_txt).grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Checkbutton(output_frame, text=".xlsx", variable=self.output_xlsx).grid(
            row=0, column=1, padx=5, pady=5, sticky="w")
        # NEW: Checkbutton untuk prompt gambar
        tk.Checkbutton(output_frame, text="Saran Prompt Gambar", variable=self.generate_image_prompts).grid(
            row=0, column=2, padx=5, pady=5, sticky="w")
        output_frame.grid_columnconfigure(1, weight=1)

        # --- Tombol Generate dan Status ---
        process_frame = tk.Frame(self.scrollable_frame, padx=0, pady=2)
        process_frame.pack(pady=2, padx=10, fill="x")

        self.generate_button = tk.Button(process_frame, text="Generate Cerita!",
                                         command=self.generate_story_threaded,  # <<< UBAH KE FUNGSI INI
                                         height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.generate_button.pack(pady=2, fill="x")

        self.status_label = tk.Label(
            self.scrollable_frame, text="", fg="blue", wraplength=580)
        self.status_label.pack(pady=2, padx=10)

    def paste_api_key(self):
        try:
            # Gunakan self.root untuk clipboard_get
            clipboard_content = self.root.clipboard_get()
            if clipboard_content:
                self.api_key.set(clipboard_content)
                # Panggil save_api_key secara otomatis, tanpa menampilkan messagebox
                self.save_api_key(show_message=False)
                messagebox.showinfo(
                    "API Key", "API Key berhasil ditempel dan disimpan.")
            else:
                messagebox.showwarning(
                    "Clipboard Kosong", "Tidak ada teks di clipboard untuk ditempel.")
        except tk.TclError:
            messagebox.showwarning(
                "Clipboard Kosong", "Tidak ada teks di clipboard untuk ditempel.")
        except Exception as e:
            messagebox.showerror(
                "Error Paste", f"Terjadi kesalahan saat menempel dari clipboard: {e}")

    # --- FUNGSI BARU UNTUK API KEY MANAGEMENT ---
    def load_api_key(self):
        """Memuat API Key dari file lokal."""
        if os.path.exists(self.api_key_file):
            try:
                with open(self.api_key_file, "r") as f:
                    key = f.read().strip()
                    if key:
                        self.api_key.set(key)
                        # messagebox.showinfo("API Key Loaded", "API Key berhasil dimuat dari file.")
            except Exception as e:
                messagebox.showwarning(
                    "Load API Key Error", f"Gagal memuat API Key dari file: {e}")

    def save_api_key(self, show_message=True):  # <--- TAMBAHKAN show_message=True
        """Menyimpan API Key ke file lokal."""
        key = self.api_key.get().strip()
        if key:
            try:
                with open(self.api_key_file, "w") as f:
                    f.write(key)
                if show_message:  # <--- KONDISI UNTUK MENAMPILKAN MESSAGEBOX
                    messagebox.showinfo(
                        "API Key Saved", "API Key berhasil disimpan.")
            except Exception as e:
                messagebox.showerror("Save API Key Error",
                                     f"Gagal menyimpan API Key: {e}")
        elif show_message:  # <--- KONDISI UNTUK MENAMPILKAN MESSAGEBOX JIKA INPUT KOSONG
            messagebox.showwarning(
                "Input Kosong", "Masukkan API Key terlebih dahulu sebelum menyimpan.")

    def clear_api_key(self):
        """Menghapus API Key dari input dan file lokal."""
        self.api_key.set("")  # Kosongkan input field
        if os.path.exists(self.api_key_file):
            try:
                os.remove(self.api_key_file)  # Hapus file
                messagebox.showinfo(
                    "API Key Dihapus", "API Key berhasil dihapus dari aplikasi dan file.")
            except Exception as e:
                messagebox.showerror("Clear API Key Error",
                                     f"Gagal menghapus file API Key: {e}")
        else:
            messagebox.showinfo("API Key Dihapus",
                                "Input API Key sudah kosong.")
    # --- END FUNGSI BARU ---

    # --- FUNGSI PEMBANTU BARU ---
    def _get_selected_value(self, selected_var, custom_var, error_msg):
        """
        Fungsi pembantu untuk mengambil nilai dari StringVar,
        menangani kasus 'Lainnya (input manual)', dan menampilkan error jika kosong.
        """
        value = selected_var.get().strip()
        if value == "Lainnya (input manual)":
            value = custom_var.get().strip()

        # Tambahkan pemeriksaan tambahan jika custom_var ternyata kosong setelah dipilih "Lainnya"
        if not value and selected_var.get() == "Lainnya (input manual)":
            messagebox.showerror("Input Error", "Mohon isi detail untuk 'Lainnya (input manual)' di " + error_msg.lower(
            ).replace("pilih atau masukkan ", "").replace("cerita.", "").replace("target.", "").strip() + ".")
            return None  # Menandakan error
        elif not value:  # Untuk kasus jika pilihan bukan "Lainnya" tapi somehow kosong
            messagebox.showerror("Input Error", error_msg)
            return None  # Menandakan error

        return value
    # --- END FUNGSI PEMBANTU BARU ---

    def toggle_character_options(self):
        char_type = self.character_type.get()
        # Nonaktifkan semua terlebih dahulu
        self.animal_label.config(state="disabled")
        self.animal_dropdown.config(state="disabled")
        self.human_char_label.config(state="disabled")
        self.human_char_dropdown.config(state="disabled")
        self.custom_char_label.config(state="disabled")
        self.custom_char_entry.config(state="disabled")

        if char_type == "Hewan":
            self.animal_label.config(state="normal")
            self.animal_dropdown.config(state="readonly")
        elif char_type == "Tokoh":
            self.human_char_label.config(state="normal")
            self.human_char_dropdown.config(state="readonly")
        elif char_type == "Kustom":
            self.custom_char_label.config(state="normal")
            self.custom_char_entry.config(state="normal")

    def on_moral_select(self, event):
        if self.selected_moral.get() == "Lainnya (input manual)":
            self.custom_moral_entry.config(state="normal")
        else:
            self.custom_moral_entry.config(state="disabled")
            self.custom_moral.set("")

    def on_style_select(self, event):
        if self.selected_story_style.get() == "Lainnya (input manual)":
            self.custom_style_entry.config(state="normal")
        else:
            self.custom_style_entry.config(state="disabled")
            self.custom_story_style.set("")

    def on_location_select(self, event):
        if self.selected_location.get() == "Lainnya (input manual)":
            self.custom_location_entry.config(state="normal")
        else:
            self.custom_location_entry.config(state="disabled")
            self.custom_location.set("")

    def on_age_select(self, event):
        if self.selected_age_range.get() == "Lainnya (input manual)":
            self.custom_age_entry.config(state="normal")
        else:
            self.custom_age_entry.config(state="disabled")
            self.custom_age_range.set("")

    def generate_story_threaded(self):
        """Fungsi pembantu yang menjalankan generate_story_logic di thread terpisah."""
        self.show_progress_popup(
            "Menggenerasi Cerita", "Sedang menghubungkan ke Gemini API...")
        # Nonaktifkan tombol generate agar tidak diklik berkali-kali
        self.generate_button.config(state="disabled")

        # Jalankan logika generate di thread terpisah
        threading.Thread(target=self._generate_story_logic,
                         daemon=True).start()

    def _generate_story_logic(self):
        """Logika inti untuk menggenerasi cerita, berjalan di thread terpisah."""
        api_key = self.api_key.get().strip()
        generate_txt = self.output_txt.get()
        generate_xlsx = self.output_xlsx.get()
        # NEW: Get state of image prompt generation
        generate_img_prompts = self.generate_image_prompts.get()

        if not api_key:
            self.hide_progress_popup()
            messagebox.showerror(
                "Input Error", "Masukkan Gemini API Key Anda.")
            self.generate_button.config(state="normal")  # Aktifkan kembali
            return

        chosen_character = ""
        char_type = self.character_type.get()
        if char_type == "Hewan":
            chosen_character = self.selected_animal.get().strip()
            if not chosen_character:
                self.hide_progress_popup()
                messagebox.showerror(
                    "Input Error", "Pilih nama hewan untuk tokoh utama.")
                self.generate_button.config(state="normal")
                return
        elif char_type == "Tokoh":
            chosen_character = self.selected_human_char.get().strip()
            if not chosen_character:
                self.hide_progress_popup()
                messagebox.showerror("Input Error", "Pilih jenis tokoh utama.")
                self.generate_button.config(state="normal")
                return
        elif char_type == "Kustom":
            chosen_character = self.custom_character.get().strip()
            if not chosen_character:
                self.hide_progress_popup()
                messagebox.showerror(
                    "Input Error", "Masukkan karakter kustom untuk tokoh utama.")
                self.generate_button.config(state="normal")
                return

        # Ini validasi tambahan, mungkin redundant jika yang di atas sudah ada, tapi untuk memastikan
        if not chosen_character:
            self.hide_progress_popup()
            messagebox.showerror(
                "Input Error", "Pilih atau masukkan tokoh utama cerita.")
            self.generate_button.config(state="normal")
            return

        chosen_moral = self._get_selected_value(
            self.selected_moral, self.custom_moral, "Pilih atau masukkan pesan moral cerita.")
        if chosen_moral is None:
            self.hide_progress_popup()
            self.generate_button.config(state="normal")
            return

        chosen_style = self._get_selected_value(
            self.selected_story_style, self.custom_story_style, "Pilih atau masukkan gaya cerita.")
        if chosen_style is None:
            self.hide_progress_popup()
            self.generate_button.config(state="normal")
            return

        chosen_location = self._get_selected_value(
            self.selected_location, self.custom_location, "Pilih atau masukkan lokasi cerita.")
        if chosen_location is None:
            self.hide_progress_popup()
            self.generate_button.config(state="normal")
            return

        chosen_narration_length = self.narration_length.get()

        chosen_age_range = self._get_selected_value(
            self.selected_age_range, self.custom_age_range, "Pilih atau masukkan rentang usia target.")
        if chosen_age_range is None:
            self.hide_progress_popup()
            self.generate_button.config(state="normal")
            return

        if not generate_txt and not generate_xlsx:
            self.hide_progress_popup()
            messagebox.showerror(
                "Input Error", "Pilih setidaknya satu jenis file output (.txt atau .xlsx).")
            self.generate_button.config(state="normal")
            return

        self.status_label.config(text="")  # Kosongkan status label utama

        try:
            self.update_progress_message("Mengonfigurasi Gemini API...")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            self.update_progress_message("Membangun prompt untuk Gemini...")
            prompt_parts = [f"""
            Anda adalah seorang penulis cerita anak yang kreatif dan ahli.
            Buatlah cerita anak dengan gaya **{chosen_style}** untuk anak-anak berusia **{chosen_age_range}**.
            **SANGAT PENTING:** Tokoh utama dan satu-satunya karakter sentral cerita ini adalah **{chosen_character}**. Fokuskan alur pada karakter ini.
            Cerita ini berlatar di **{chosen_location}**.
            Cerita ini harus mengandung pesan moral tentang **{chosen_moral}**.

            Panjang cerita sekitar 10 hingga 14 paragraf pendek (setiap paragraf dianggap sebagai satu 'halaman' buku).
            Pastikan bahasanya sangat sederhana, mudah dimengerti, menarik, dan sesuai untuk rentang usia tersebut.
            Gunakan kalimat pendek dan langsung.
            """]

            if chosen_narration_length == "Narasi Detail":
                prompt_parts.append("""
            Untuk setiap halaman/paragraf, tambahkan lebih banyak detail:
            - Gunakan kalimat yang sedikit lebih bervariasi namun tetap mudah dipahami.
            - Sertakan beberapa dialog sederhana antar karakter.
            - Berikan deskripsi yang lebih kaya tentang lingkungan, perasaan karakter, dan aksi yang terjadi.
            - Cerita harus terasa lebih 'penuh' dan mendalam di setiap halamannya.
            """)
            else:  # Narasi Singkat
                prompt_parts.append("""
            Setiap paragraf/halaman harus singkat dan langsung ke inti cerita.
            Hindari detail yang berlebihan.
            """)

            # Start building the JSON structure instruction dynamically
            json_structure_keys = [
                "'title': Judul cerita yang menarik.",
                "'pages': Sebuah list/array dari string, di mana setiap string adalah satu paragraf/halaman cerita.",
                "'moral_summary': Ringkasan singkat pesan moral dari cerita (maksimal 2 kalimat)."
            ]

            json_example_parts = [
                "\"title\": \"Petualangan Si Kelinci Pemberani\",",
                "\"pages\": [\"Di sebuah hutan yang hijau, hiduplah seekor kelinci kecil bernama Kiki.\", \"Kiki sangat suka melompat-lompat dan mencari wortel.\", \"Suatu hari, Kiki ingin tahu apa yang ada di balik bukit.\", \"Dia berjalan dan berjalan, melewati bunga-bunga indah.\", \"Tiba-tiba, Kiki melihat seekor burung kecil jatuh dari sarangnya.\", \"Burung itu menangis 'cuit, cuit' karena kakinya sakit.\", \"Kiki tidak takut. Dia ingat pesan ibunya untuk selalu menolong.\", \"Dengan hati-hati, Kiki menggendong burung itu ke sarangnya.\", \"Ibu burung sangat senang dan berterima kasih kepada Kiki.\", \"Kiki merasa senang karena sudah berani menolong.\", \"Sejak itu, Kiki tahu bahwa berani itu berarti melakukan hal baik, bukan hanya tidak takut.\"],",
                "\"moral_summary\": \"Cerita ini mengajarkan tentang keberanian untuk menolong sesama. Kita harus berani berbuat baik.\","
            ]

            if generate_img_prompts:  # NEW: Only add image prompt instructions if enabled
                json_structure_keys.append(f"""
                'image_prompts': Sebuah list/array dari string, di mana setiap string adalah saran prompt gambar yang SANGAT DESKRIPTIF untuk ilustrasi halaman yang sesuai. Prompt harus fokus pada karakter utama, aksi, dan detail visual adegan di halaman tersebut, cocok untuk digunakan di tool image generation AI.
                **SANGAT PENTING untuk 'image_prompts':** Pastikan ada SATU prompt gambar untuk setiap halaman cerita (sesuai jumlah elemen di 'pages'). Setiap prompt harus selalu menyertakan deskripsi visual yang konsisten untuk karakter utama **{chosen_character}** di awal prompt. Contoh: "Ilustrasi buku anak: Seorang {chosen_character} [deskripsi visual singkat, misal: 'dengan bulu cokelat muda dan topi merah'] melakukan aksi..." atau "Ilustrasi buku anak: Karakter utama {chosen_character} [deskripsi visual singkat] sedang..."
                Prioritaskan konsistensi penampilan karakter utama di setiap prompt gambar.
                """)
                json_example_parts.append("""
                \"image_prompts\": [
                    \"Ilustrasi buku anak: Seekor **kelinci kecil bernama Kiki dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas**, sedang berdiri di hutan yang hijau cerah, dikelilingi pohon-pohon tinggi dan sinar matahari menembus dedaunan. Gaya kartun lembut, warna hangat.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas**, sedang melompat-lompat dengan gembira di ladang wortel yang subur, wortel oranye mencuat dari tanah. Ekspresi ceria, latar belakang detail dan berwarna-warni.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** melihat ke atas bukit yang misterius, matahari terbit di baliknya menciptakan siluet indah. Penuh rasa ingin tahu, petualangan menunggu. Gaya realistis tapi ramah anak.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** berjalan menyusuri jalan setapak di hutan, dikelilingi bunga-bunga liar berwarna-warni seperti ungu, merah, dan kuning yang mekar di sisi jalan. Kupu-kupu beterbangan di sekelilingnya. Penuh kedamaian.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** terkejut melihat seekor burung kecil jatuh dari sarangnya. Ekspresi khawatir. Detail sarang dan ranting. Gaya ekspresif.\",
                    \"Ilustrasi buku anak: Burung kecil yang terluka menangis 'cuit, cuit' dengan ekspresi sedih. Kaki burung terlihat sedikit menekuk, menunjukkan sakit. **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** melihatnya dengan empati. Close-up.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** dengan wajah penuh tekad, mengingat nasihat ibunya. Dia mendekati burung kecil yang terluka, menunjukkan keberanian dan niat menolong. Latar belakang fokus pada keduanya.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** dengan hati-hati menggendong burung kecil yang lembut di antara kedua tangannya, membawanya kembali ke sarang di atas pohon. Aksi lembut dan penuh kasih. Pohon dengan daun lebat.\",
                    \"Ilustrasi buku anak: Ibu burung (burung dewasa dengan bulu yang sama) tersenyum bahagia dan berterima kasih kepada **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas**, mungkin dengan menyentuh hidung Kiki dengan paruhnya. Kiki tersenyum lega. Pemandangan sarang yang aman.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** berdiri tegak dengan senyum bangga dan senang, merasakan kehangatan karena telah membantu. Sinar matahari menyinarinya, menunjukkan perasaan positif. Suasana cerah.\",
                    \"Ilustrasi buku anak: **Kiki si kelinci dengan bulu cokelat muda, mata besar yang ramah, dan telinga panjang yang khas** bermain bersama burung kecil yang sudah sembuh di hutan, menunjukkan bahwa keberanian sejati adalah berbuat baik. Mereka bermain di samping pohon yang teduh. Tema persahabatan.\"
                ]
                """)

            prompt_parts.append(f"""
            Berikan output dalam format JSON dengan kunci berikut:
            {', '.join(json_structure_keys)}

            Contoh format JSON yang diharapkan:
            {{
              {', '.join(json_example_parts)}
            }}
            """)

            prompt = os.linesep.join([s for s in '\n'.join(
                prompt_parts).splitlines() if s.strip()])  # Join all parts

            self.update_progress_message(
                "Mengirim permintaan ke Gemini (ini mungkin butuh beberapa detik)...")
            response = model.generate_content([prompt], stream=False)
            response.resolve()

            raw_json_text = response.text.strip()
            if raw_json_text.startswith("```json"):
                raw_json_text = raw_json_text[7:]
            if raw_json_text.endswith("```"):
                raw_json_text = raw_json_text[:-3]

            self.update_progress_message("Memproses respons dari Gemini...")
            story_data = json.loads(raw_json_text)
            title = story_data.get('title', 'Cerita Tanpa Judul')
            pages = story_data.get('pages', [])
            moral_summary = story_data.get(
                'moral_summary', 'Tidak ada ringkasan moral.')

            # NEW: Handle image_prompts based on whether they were requested
            image_prompts = []
            if generate_img_prompts:
                # Get image_prompts, provide placeholder list if not found
                image_prompts = story_data.get('image_prompts', [
                                               'Saran prompt gambar tidak tersedia untuk halaman ini.'] * len(pages))
                # If Gemini failed to provide the correct number, fill with placeholder
                if len(image_prompts) != len(pages):
                    print(
                        f"Peringatan: Jumlah prompt gambar ({len(image_prompts)}) tidak sesuai dengan jumlah halaman ({len(pages)}). Menyesuaikan.")
                    if len(image_prompts) < len(pages):
                        image_prompts.extend(
                            ['Saran prompt gambar tidak tersedia untuk halaman ini.'] * (len(pages) - len(image_prompts)))
                    else:
                        image_prompts = image_prompts[:len(pages)]
            # If not generating image prompts, image_prompts will remain an empty list.

            if not pages:
                raise ValueError(
                    "Generasi cerita gagal: Tidak ada halaman cerita yang dihasilkan.")

            output_directory = os.getcwd()
            self.update_progress_message("Menyimpan hasil cerita...")
            self.save_story_results(
                output_directory, title, pages, moral_summary, image_prompts, generate_txt, generate_xlsx, generate_img_prompts)  # NEW: Pass generate_img_prompts

            # NEW: Adjust status label based on whether image prompts were generated
            status_text = "Cerita berhasil digenerate dan disimpan!"
            if generate_img_prompts:
                status_text = "Cerita & Saran Prompt Gambar berhasil digenerate dan disimpan!"
            self.status_label.config(text=status_text, fg="green")

            self.open_output_directory(output_directory)

        except json.JSONDecodeError as e:
            self.status_label.config(
                text="Error parsing JSON dari API.", fg="red")
            messagebox.showerror(
                "JSON Error", f"Gagal membaca respons dari Gemini. Mungkin formatnya tidak sesuai harapan. Error: {e}\n\nRespons mentah:\n{raw_json_text}")
            print(f"Detail Error JSON: {e}\nRaw JSON: {raw_json_text}")
        except Exception as e:
            self.status_label.config(
                text="Terjadi kesalahan fatal saat menggenerasi cerita.", fg="red")
            messagebox.showerror(
                "Error Generasi", f"Terjadi kesalahan saat menggenerasi cerita:\n{e}\n\nPastikan API Key benar dan koneksi internet stabil.")
            print(f"Detail Error: {e}")
        finally:
            self.hide_progress_popup()
            # Pastikan tombol diaktifkan kembali
            self.generate_button.config(state="normal")

    # Ubah parameter fungsi untuk menerima image_prompts dan generate_img_prompts
    # NEW: Added generate_img_prompts
    def save_story_results(self, output_directory, title, pages, moral_summary, image_prompts, save_txt, save_xlsx, generate_img_prompts):
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        safe_title = "".join(c for c in title if c.isalnum()
                             or c in (' ', '.', '_')).rstrip()
        # Ambil 50 karakter pertama dari judul
        base_filename = f"{timestamp}_{safe_title[:50].strip()}"

        output_messages = []

        # Output TXT
        if save_txt:
            txt_filename = os.path.join(
                output_directory, f"{base_filename}.txt")
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(
                    f"===== Laporan Cerita Anak - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n\n")
                f.write(f"Judul Cerita: {title}\n")
                f.write(f"Pesan Moral: {moral_summary}\n\n")
                # Adjusted title if image prompts are not generated
                if generate_img_prompts:
                    f.write("--- Isi Cerita & Saran Prompt Gambar ---\n")
                else:
                    f.write("--- Isi Cerita ---\n")

                for i, page in enumerate(pages):
                    f.write(f"Halaman {i+1}:\n{page}\n")
                    if generate_img_prompts:  # Only write image prompt section if enabled
                        if i < len(image_prompts):  # Pastikan ada prompt untuk halaman ini
                            f.write(
                                f"\nSaran Prompt Gambar untuk Halaman {i+1}:\n")
                            # Tambahkan prompt gambar
                            f.write(f"'{image_prompts[i]}'\n\n")
                        else:  # Fallback if prompt was requested but missing for a specific page
                            f.write(
                                "\nSaran Prompt Gambar tidak tersedia untuk halaman ini.\n\n")
                    else:  # If image prompts were not requested at all, just add a new line for spacing
                        f.write("\n")
                f.write("--------------------\n")
            output_messages.append(f"File TXT: {txt_filename}")

        # Output XLSX
        if save_xlsx:
            xlsx_filename = os.path.join(
                output_directory, f"{base_filename}.xlsx")

            # Siapkan data untuk DataFrame
            data_for_df = []
            for i, page_content in enumerate(pages):
                row_data = {
                    "Judul Cerita": title,
                    "Pesan Moral": moral_summary,
                    "Nomor Halaman": i + 1,
                    "Isi Halaman": page_content,
                }
                if generate_img_prompts:  # NEW: Only add this column if enabled
                    row_data["Saran Prompt Gambar"] = image_prompts[i] if i < len(
                        image_prompts) else "Tidak tersedia"
                data_for_df.append(row_data)

            df = pd.DataFrame(data_for_df)
            df.to_excel(xlsx_filename, index=False, engine='openpyxl')
            output_messages.append(f"File XLSX: {xlsx_filename}")

        # NEW: Adjust success message based on whether image prompts were generated
        success_message_part = "Cerita"
        if generate_img_prompts:
            success_message_part += " dan saran prompt gambar"

        messagebox.showinfo(
            "Sukses", f"Proses Selesai. {success_message_part} telah disimpan:\n\n" + "\n".join(output_messages))

    def open_output_directory(self, path):
        """Membuka direktori output di file explorer."""
        try:
            if os.path.exists(path):
                if os.name == 'nt':  # For Windows
                    os.startfile(path)
                elif os.uname().sysname == 'Darwin':  # For macOS
                    subprocess.Popen(['open', path])
                else:  # For Linux/Unix
                    subprocess.Popen(['xdg-open', path])
            else:
                messagebox.showwarning(
                    "Direktori Tidak Ditemukan", f"Direktori output tidak ditemukan: {path}")
        except Exception as e:
            messagebox.showerror(
                "Error Membuka Direktori", f"Gagal membuka direktori output: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StoryGeneratorApp(root)
    root.mainloop()
