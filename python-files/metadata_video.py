import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import google.generativeai as genai
import google.api_core.exceptions
import pandas as pd
import os
import datetime
import threading
import queue
import random
import time

# =================================================================================================
# === KUMPULAN CONTOH PROMPT (Tampilan: Indonesia, Nilai untuk AI: Inggris)                     ===
# =================================================================================================
PROMPT_DATA = {
    "Gaya": [
        {"display": "Foto Sangat Nyata", "value": "ultra realistic photo"},
        {"display": "Gaya Film Sinematik", "value": "cinematic film still"},
        {"display": "Potret Fashion", "value": "fashion portrait"},
        {"display": "Fotografi Dokumenter", "value": "documentary photography"},
        {"display": "Lukisan Cat Minyak", "value": "oil painting"},
        {"display": "Seni Anime (Screenshot)", "value": "anime screenshot"},
        {"display": "Seni Gaya Ghibli", "value": "ghibli style art"},
        {"display": "Pemandangan Kota Cyberpunk", "value": "cyberpunk cityscape"},
        {"display": "Seni Fantasi", "value": "fantasy art"},
        {"display": "Render 3D", "value": "3D render"}
    ],
    "Subjek": [
        {"display": "Elang yang Gagah", "value": "a majestic eagle"},
        {"display": "Wanita Muda Berambut Perak", "value": "a young woman with silver hair"},
        {"display": "Robot Antik Membaca Buku", "value": "a vintage robot reading a book"},
        {"display": "Penyihir Tua Merapal Mantra", "value": "an old wizard casting a spell"},
        {"display": "Ksatria Berbaju Zirah", "value": "a knight in shining armor"},
        {"display": "Android yang Sedang Berpikir", "value": "a thoughtful android"}
    ],
    "Setting": [
        {"display": "di Hutan Lebat", "value": "in a dense jungle"},
        {"display": "di Jalan Penuh Neon di Tokyo", "value": "on a neon-lit street in Tokyo"},
        {"display": "di dalam Perpustakaan yang Nyaman", "value": "inside a cozy library"},
        {"display": "di Koloni Mars Masa Depan", "value": "on a futuristic Mars colony"},
        {"display": "di Hutan Ajaib", "value": "in an enchanted forest"},
        {"display": "di Kota Pasca-Kiamat", "value": "in a post-apocalyptic city"},
        {"display": "di Pantai yang Tenang saat Senja", "value": "on a tranquil beach at sunset"}
    ],
    "Komposisi": [
        {"display": "Tangkapan Jarak Dekat (Close-up)", "value": "close-up shot"},
        {"display": "Tangkapan Sangat Lebar (Wide Shot)", "value": "extreme wide shot"},
        {"display": "Sudut Pandang Rendah (Low Angle)", "value": "low angle shot"},
        {"display": "Sudut Pandang dari Atas (Top-down)", "value": "top-down view"},
        {"display": "Aturan Sepertiga (Rule of Thirds)", "value": "rule of thirds composition"},
        {"display": "Simetris", "value": "symmetrical"}
    ],
    "Pencahayaan": [
        {"display": "Pencahayaan Sinematik", "value": "cinematic lighting"},
        {"display": "Cahaya Alami yang Lembut", "value": "soft natural light"},
        {"display": "Cahaya Studio yang Dramatis", "value": "dramatic studio lighting"},
        {"display": "Cahaya Neon Berpendar", "value": "neon glow"},
        {"display": "Cahaya Senja (Golden Hour)", "value": "golden hour lighting"},
        {"display": "Cahaya Subuh (Blue Hour)", "value": "blue hour lighting"}
    ],
    "Warna": [
        {"display": "Warna-warni Cerah", "value": "vibrant colors"},
        {"display": "Hitam Putih Monokromatik", "value": "monochromatic black and white"},
        {"display": "Palet Warna Pastel", "value": "pastel color palette"},
        {"display": "Nuansa Warna Bumi (Earthy)", "value": "earthy tones"},
        {"display": "Warna Neon Cyberpunk", "value": "cyberpunk neon colors"},
        {"display": "Nada Sepia", "value": "sepia tone"}
    ],
    "Kualitas": [
        {"display": "Sangat Detail", "value": "highly detailed"},
        {"display": "Detail yang Rumit", "value": "intricate details"},
        {"display": "Kualitas Mahakarya", "value": "masterpiece"},
        {"display": "Resolusi 4K", "value": "4K resolution"},
        {"display": "Fokus Tajam", "value": "sharp focus"},
        {"display": "Sangat Realistis (Hyperrealistic)", "value": "hyperrealistic"}
    ],
    "ParameterTeknis": [
        {"display": "Kamera Sony a7 IV, Lensa 85mm f/1.4", "value": "shot on Sony a7 IV, 85mm f/1.4 lens"},
        {"display": "Render Unreal Engine 5", "value": "Unreal Engine 5 render"},
        {"display": "Render Octane", "value": "Octane Render"},
        {"display": "Cahaya Volumetrik", "value": "volumetric lighting"},
        {"display": "Difoto dengan Film (Kodak Portra 400)", "value": "shot on film, kodak portra 400"}
    ]
}

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#3B4252", foreground="#ECEFF4", relief='solid', borderwidth=1,
                         font=("Poppins", 10, "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Tools (Generator Metadata & Prompt)")
        self.geometry("1100x800")
        self.minsize(900, 700)
        
        self.style = ttk.Style(self)
        self.configure(bg="#2E3440")
        self.style.theme_use('clam')
        self.configure_styles()

        self.image_paths = []
        self.video_paths = []
        self.result_queue = queue.Queue()
        self._create_widgets()
        self.check_queue()

    def configure_styles(self):
        self.style.configure('TFrame', background='#2E3440')
        self.style.configure('TLabel', background='#2E3440', foreground='#ECEFF4', font=('Poppins', 11))
        self.style.configure('TButton', background='#5E81AC', foreground='#ECEFF4', font=('Poppins', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#81A1C1'), ('disabled', '#4C566A')])
        self.style.configure('TEntry', fieldbackground='#3B4252', foreground='#ECEFF4', bordercolor='#4C566A', insertcolor='#ECEFF4')
        self.style.configure('Readonly.TEntry', fieldbackground='#2E3440', foreground='#D8DEE9', bordercolor='#4C566A', insertcolor='#D8DEE9')
        self.style.configure('TCombobox', fieldbackground='#3B4252', foreground='#ECEFF4', bordercolor='#4C566A', insertcolor='#ECEFF4', selectbackground='#3B4252', selectforeground='#ECEFF4', arrowcolor='#ECEFF4')
        self.style.configure('Treeview', background='#3B4252', fieldbackground='#3B4252', foreground='#ECEFF4', rowheight=28)
        self.style.map('Treeview', background=[('selected', '#5E81AC')])
        self.style.configure('Treeview.Heading', background='#434C5E', foreground='#ECEFF4', font=('Poppins', 11, 'bold'))
        self.style.configure('Horizontal.TProgressbar', background='#A3BE8C', troughcolor='#3B4252')
        self.style.configure("TNotebook", background='#2E3440', borderwidth=0)
        self.style.configure("TNotebook.Tab", background='#434C5E', foreground='#ECEFF4', padding=[10, 5], font=('Poppins', 10, 'bold'))
        self.style.map("TNotebook.Tab", background=[("selected", '#5E81AC')], foreground=[("selected", '#ECEFF4')])

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both")
        
        # --- Top frame for API Key (shared across tabs) ---
        api_frame = ttk.Frame(main_frame, padding="15 15 15 5")
        api_frame.pack(fill='x')
        
        ttk.Label(api_frame, text="🔑 Masukkan API Key:").pack(side='left', padx=(0, 10))
        self.api_entry = ttk.Entry(api_frame, width=35, show="*")
        self.api_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        ToolTip(self.api_entry, "Masukkan Gemini API Key Anda di sini. Digunakan untuk semua fitur.")
        self.check_limit_btn = ttk.Button(api_frame, text="📡 Cek Status & Limit", command=self.start_check_limit_thread)
        self.check_limit_btn.pack(side='left', padx=(0, 10))

        # --- Notebook for tabs ---
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both', padx=15, pady=(5,15))

        self.metadata_tab = ttk.Frame(notebook, padding="15")
        self.video_metadata_tab = ttk.Frame(notebook, padding="15")
        self.prompt_gen_tab = ttk.Frame(notebook, padding="15")
        
        notebook.add(self.metadata_tab, text='Generator Metadata Foto')
        notebook.add(self.video_metadata_tab, text='Generator Metadata Video')
        notebook.add(self.prompt_gen_tab, text='Generator Prompt')

        self._create_metadata_tab_content()
        self._create_video_metadata_tab_content()
        self._create_prompt_gen_tab_content()
        
    def _create_metadata_tab_content(self):
        tab = self.metadata_tab
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', pady=5)
        self.browse_btn = ttk.Button(top_frame, text="📂 Pilih Gambar", command=self.browse_files)
        self.browse_btn.pack(side='right', padx=(10, 0))

        center_frame = ttk.Frame(tab)
        center_frame.pack(expand=True, fill='both', pady=10)
        center_frame.columnconfigure(0, weight=3); center_frame.columnconfigure(1, weight=1); center_frame.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(center_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        columns = ('filename', 'title', 'keywords')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading('filename', text='Nama File'); self.tree.heading('title', text='Judul Hasil AI'); self.tree.heading('keywords', text='Kata Kunci Hasil AI')
        self.tree.column('filename', width=200, stretch=False); self.tree.column('title', width=300, stretch=True); self.tree.column('keywords', width=400, stretch=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set); self.tree.pack(side='left', expand=True, fill='both'); scrollbar.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

        right_panel = ttk.Frame(center_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_panel.columnconfigure(0, weight=1)
        ttk.Label(right_panel, text="Pratinjau Gambar", font=('Poppins', 12, 'bold')).grid(row=0, column=0, sticky='ew')
        self.preview_label = ttk.Label(right_panel, background='#3B4252', anchor='center')
        self.preview_label.grid(row=1, column=0, sticky='nsew', pady=5)
        right_panel.rowconfigure(1, weight=1)
        
        bottom_frame = ttk.Frame(tab)
        bottom_frame.pack(fill='x', pady=5)
        self.clear_btn = ttk.Button(bottom_frame, text="🗑️ Hapus Daftar", command=self.clear_list)
        self.clear_btn.pack(side='left')
        self.generate_btn = ttk.Button(bottom_frame, text="✨ Generate Metadata Foto", command=self.start_generation_thread, state='disabled')
        self.generate_btn.pack(side='right')

        status_frame = ttk.Frame(tab)
        status_frame.pack(fill='x', pady=5)
        self.status_label = ttk.Label(status_frame, text="Silakan pilih gambar...")
        self.status_label.pack(side='left')
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
    
    def _create_video_metadata_tab_content(self):
        tab = self.video_metadata_tab
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', pady=5)
        self.browse_video_btn = ttk.Button(top_frame, text="📂 Pilih Video", command=self.browse_videos)
        self.browse_video_btn.pack(side='right', padx=(10, 0))

        center_frame = ttk.Frame(tab)
        center_frame.pack(expand=True, fill='both', pady=10)
        center_frame.columnconfigure(0, weight=3); center_frame.columnconfigure(1, weight=1); center_frame.rowconfigure(0, weight=1)
        
        tree_frame = ttk.Frame(center_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        columns = ('filename', 'title', 'keywords')
        self.tree_video = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree_video.heading('filename', text='Nama File Video'); self.tree_video.heading('title', text='Judul Hasil AI'); self.tree_video.heading('keywords', text='Kata Kunci Hasil AI')
        self.tree_video.column('filename', width=200, stretch=False); self.tree_video.column('title', width=300, stretch=True); self.tree_video.column('keywords', width=400, stretch=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_video.yview)
        self.tree_video.configure(yscrollcommand=scrollbar.set); self.tree_video.pack(side='left', expand=True, fill='both'); scrollbar.pack(side='right', fill='y')

        right_panel = ttk.Frame(center_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(right_panel, text="Pratinjau Video", font=('Poppins', 12, 'bold')).pack()
        self.preview_label_video = ttk.Label(right_panel, background='#3B4252', text="Pratinjau video\ntidak tersedia", anchor='center', justify='center')
        self.preview_label_video.pack(expand=True, fill='both', pady=5)

        bottom_frame = ttk.Frame(tab)
        bottom_frame.pack(fill='x', pady=5)
        self.clear_video_btn = ttk.Button(bottom_frame, text="🗑️ Hapus Daftar Video", command=self.clear_video_list)
        self.clear_video_btn.pack(side='left')
        self.generate_video_btn = ttk.Button(bottom_frame, text="✨ Generate Metadata Video", command=self.start_video_generation_thread, state='disabled')
        self.generate_video_btn.pack(side='right')

        status_frame = ttk.Frame(tab)
        status_frame.pack(fill='x', pady=5)
        self.status_label_video = ttk.Label(status_frame, text="Silakan pilih video...")
        self.status_label_video.pack(side='left')
        self.progress_bar_video = ttk.Progressbar(status_frame, mode='indeterminate')
    
    def _create_prompt_gen_tab_content(self):
        tab = self.prompt_gen_tab
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill='x')
        
        self.prompt_elements = {}
        row = 0
        for key, data_list in PROMPT_DATA.items():
            label_text = key.replace("ParameterTeknis", "Parameter Teknis")
            ttk.Label(form_frame, text=f"{label_text}:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
            display_options = [item['display'] for item in data_list]
            combo = ttk.Combobox(form_frame, values=display_options, width=60)
            combo.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
            self.prompt_elements[key] = combo
            row += 1
        form_frame.columnconfigure(1, weight=1)
        
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill='x', pady=20)
        
        ttk.Label(control_frame, text="Jumlah Variasi:").pack(side='left', padx=(0,5))
        self.num_prompts_entry = ttk.Entry(control_frame, width=5)
        self.num_prompts_entry.insert(0, "5")
        self.num_prompts_entry.pack(side='left', padx=5)

        self.generate_prompt_btn = ttk.Button(control_frame, text="🚀 Buat Variasi Prompt Cemerlang", command=self.start_prompt_variations_generation)
        self.generate_prompt_btn.pack(side='left', padx=20)

        result_frame = ttk.Frame(tab)
        result_frame.pack(expand=True, fill='both', pady=10)
        ttk.Label(result_frame, text="Hasil Variasi Prompt (bisa di-copy):", font=('Poppins', 12, 'bold')).pack(anchor='w')
        self.prompt_result_text = tk.Text(result_frame, wrap='word', height=10, background="#3B4252", foreground="#ECEFF4", relief='flat', font=("Poppins", 10))
        text_scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.prompt_result_text.yview)
        self.prompt_result_text.configure(yscrollcommand=text_scrollbar.set)
        self.prompt_result_text.pack(side='left', expand=True, fill='both')
        text_scrollbar.pack(side='right', fill='y')

    def start_check_limit_thread(self):
        api_key = self.get_api_key()
        if not api_key:
            messagebox.showwarning("API Key Kosong", "Silakan masukkan Gemini API Key Anda terlebih dahulu.")
            return
        self.set_ui_state('disabled')
        self.status_label.config(text="📡 Mengecek status API Key...")
        self.status_label_video.config(text="...")
        thread = threading.Thread(target=self.run_check_limit_logic, args=(api_key,), daemon=True)
        thread.start()

    def run_check_limit_logic(self, api_key):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            model.count_tokens("test")
            self.result_queue.put(('limit_check_success', None))
        except google.api_core.exceptions.PermissionDenied:
            self.result_queue.put(('limit_check_error', "API Key tidak valid atau salah. Silakan periksa kembali."))
        except google.api_core.exceptions.ResourceExhausted:
            self.result_queue.put(('limit_check_error', "LIMIT TERCAPAI! Anda telah melebihi kuota permintaan (60 per menit). Coba lagi nanti."))
        except Exception as e:
            self.result_queue.put(('limit_check_error', f"Gagal terhubung: {e}"))

    def start_prompt_variations_generation(self):
        api_key = self.get_api_key()
        if not api_key: messagebox.showwarning("API Key Diperlukan", "Masukkan API Key Anda di atas."); return
        try:
            num_variations = int(self.num_prompts_entry.get())
            if num_variations <= 0: raise ValueError
        except ValueError: messagebox.showerror("Input Salah", "Jumlah variasi harus berupa angka positif."); return
        self.set_ui_state('disabled'); self.prompt_result_text.delete('1.0', 'end')
        self.prompt_result_text.insert('1.0', "Langkah 1: AI sedang membuat Master Prompt, mohon tunggu...")
        thread = threading.Thread(target=self.run_prompt_variations_logic, args=(api_key, num_variations), daemon=True)
        thread.start()

    def run_prompt_variations_logic(self, api_key, num_variations):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e: self.result_queue.put(('prompt_error', f"Gagal Konfigurasi API: {e}")); return
        user_input_values = {key: next((item['value'] for item in PROMPT_DATA[key] if item['display'] == combo.get()), combo.get()) for key, combo in self.prompt_elements.items() if combo.get()}
        if not user_input_values: self.result_queue.put(('prompt_error', "Isi minimal satu elemen untuk membuat prompt.")); return
        filled_elements = "\n".join([f"- {key}: {value}" for key, value in user_input_values.items()])
        master_prompt_meta = f"You are a world-class prompt engineer... Combine these into one flowing, natural-language sentence...\nElements:\n{filled_elements}"
        try:
            response = model.generate_content(master_prompt_meta)
            master_prompt = response.text.strip()
            self.result_queue.put(('prompt_status', f"Langkah 2: Master Prompt dibuat! Sekarang AI membuat {num_variations} variasi..."))
        except Exception as e: self.result_queue.put(('prompt_error', f"Gagal membuat Master Prompt: {e}")); return
        variations_meta_prompt = f'You are a creative muse... generate exactly {num_variations} creative variations of this master prompt: "{master_prompt}"... The final output must be a numbered list...'
        try:
            response_variations = model.generate_content(variations_meta_prompt)
            final_variations = [f"(buatkan gambar) {parts[1].strip() if len(parts) > 1 else line.strip()}" for line in response_variations.text.strip().splitlines() if (parts := line.split('.', 1))]
            self.result_queue.put(('prompt_result_list', final_variations))
        except Exception as e: self.result_queue.put(('prompt_error', f"Gagal membuat variasi: {e}"))

    def get_api_key(self): return self.api_entry.get()

    def browse_files(self):
        files = filedialog.askopenfilenames(title="Pilih satu atau lebih gambar", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")])
        if not files: return
        for file_path in files:
            if file_path not in self.image_paths: self.image_paths.append(file_path); self.tree.insert('', 'end', values=(os.path.basename(file_path), '', ''))
        self.generate_btn.config(state='normal'); self.status_label.config(text=f"{len(self.image_paths)} gambar dimuat.")

    def browse_videos(self):
        files = filedialog.askopenfilenames(title="Pilih satu atau lebih video", filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")])
        if not files: return
        for file_path in files:
            if file_path not in self.video_paths: self.video_paths.append(file_path); self.tree_video.insert('', 'end', values=(os.path.basename(file_path), '', ''))
        self.generate_video_btn.config(state='normal'); self.status_label_video.config(text=f"{len(self.video_paths)} video dimuat.")

    def on_item_select(self, event):
        if not (selected_item := self.tree.selection()): return
        img = Image.open(self.image_paths[self.tree.index(selected_item[0])])
        w, h = self.preview_label.winfo_width() or 220, self.preview_label.winfo_height() or 220
        img.thumbnail((w - 10, h - 10))
        photo = ImageTk.PhotoImage(img)
        self.preview_label.config(image=photo); self.preview_label.image = photo

    def clear_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.image_paths.clear(); self.preview_label.config(image='', text=''); self.generate_btn.config(state='disabled'); self.status_label.config(text="Silakan pilih gambar...")

    def clear_video_list(self):
        for item in self.tree_video.get_children(): self.tree_video.delete(item)
        self.video_paths.clear(); self.generate_video_btn.config(state='disabled'); self.status_label_video.config(text="Silakan pilih video...")

    def start_generation_thread(self):
        if not (api_key := self.get_api_key()): messagebox.showwarning("API Key Diperlukan", "Silakan masukkan Gemini API Key Anda."); return
        self.set_ui_state('disabled'); self.progress_bar.pack(side='right', expand=True, fill='x', padx=10); self.progress_bar.start(10)
        threading.Thread(target=self.run_generation_logic, args=(api_key,), daemon=True).start()

    def start_video_generation_thread(self):
        if not (api_key := self.get_api_key()): messagebox.showwarning("API Key Diperlukan", "Silakan masukkan Gemini API Key Anda."); return
        self.set_ui_state('disabled'); self.progress_bar_video.pack(side='right', expand=True, fill='x', padx=10); self.progress_bar_video.start(10)
        threading.Thread(target=self.run_video_generation_logic, args=(api_key,), daemon=True).start()

    def run_generation_logic(self, api_key):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e: self.result_queue.put(('error', f"Gagal Konfigurasi API: {e}")); return
        prompt = "You are an expert creative metadata specialist... Your goal is to create rich, human-like metadata...\n## Title Generation (Strict Rules)\n...MUST BE under 200 characters...\n## Keyword Generation (Strict Rules)\n...generate a comma-separated list of exactly 48 diverse keywords...\n## Final Output Format\nTitle: [Title here]\nKeywords: [Keywords here]"
        for i, path in enumerate(self.image_paths):
            self.result_queue.put(('status', f"Memproses {i + 1}/{len(self.image_paths)}: {os.path.basename(path)}..."))
            try:
                img = Image.open(path)
                response = model.generate_content([prompt, img], request_options={'timeout': 300})
                response.resolve()
                text_response = response.text
                title, keywords = ("Parsing Gagal", "Parsing Gagal")
                if "Title:" in text_response and "Keywords:" in text_response:
                    parts = text_response.split("Keywords:")
                    title = parts[0].replace("Title:", "").strip()
                    keywords = parts[1].strip()
                self.result_queue.put(('result', i, title, keywords))
            except Exception as e: self.result_queue.put(('result', i, "Gagal Generate", str(e)))
        self.result_queue.put(('done', 'img'))

    def run_video_generation_logic(self, api_key):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e: self.result_queue.put(('video_error', f"Gagal Konfigurasi API: {e}")); return
        
        video_prompt = "You are an expert creative metadata specialist for a stock video agency. Your goal is to create rich, human-like metadata for a video file.\n## Title Generation (Strict Rules)\nCreate one single, detailed sentence for the title, describing the main subjects, actions, setting, and overall cinematic mood. The title MUST BE under 200 characters.\n## Keyword Generation (Strict Rules)\nGenerate a comma-separated list of exactly 48 diverse keywords, including concepts, objects, actions, mood, and technical terms (e.g., 'slow motion', '4k', 'drone shot').\n## Final Output Format\nTitle: [Title here]\nKeywords: [Keywords here]"

        for i, path in enumerate(self.video_paths):
            video_file = None
            try:
                self.result_queue.put(('video_status', f"Mengupload {i+1}/{len(self.video_paths)}: {os.path.basename(path)}..."))
                video_file = genai.upload_file(path=path, display_name=os.path.basename(path))
                
                self.result_queue.put(('video_status', f"Menunggu {os.path.basename(path)} aktif..."))
                while video_file.state.name == "PROCESSING":
                    time.sleep(5)
                    video_file = genai.get_file(video_file.name)
                
                if video_file.state.name != "ACTIVE":
                    raise Exception(f"Upload file gagal atau macet, status: {video_file.state.name}")

                self.result_queue.put(('video_status', f"Menganalisis {os.path.basename(path)}..."))
                response = model.generate_content([video_prompt, video_file], request_options={'timeout': 600})
                
                text_response = response.text
                title, keywords = ("Parsing Gagal", "Parsing Gagal")
                if "Title:" in text_response and "Keywords:" in text_response:
                    parts = text_response.split("Keywords:")
                    title = parts[0].replace("Title:", "").strip()
                    keywords = parts[1].strip()
                self.result_queue.put(('video_result', i, title, keywords))

            except Exception as e:
                self.result_queue.put(('video_result', i, "Gagal Generate", str(e)))
            finally:
                if video_file:
                    self.result_queue.put(('video_status', f"Menghapus file {os.path.basename(path)} dari server..."))
                    genai.delete_file(video_file.name)
        self.result_queue.put(('done', 'video'))

    def check_queue(self):
        try:
            while True:
                msg = self.result_queue.get_nowait()
                msg_type, data = msg[0], msg[1:]
                
                # Image Tab Handlers
                if msg_type == 'status': self.status_label.config(text=data[0])
                elif msg_type == 'result':
                    item_id = self.tree.get_children()[data[0]]
                    self.tree.item(item_id, values=(os.path.basename(self.image_paths[data[0]]), data[1], data[2]))
                elif msg_type == 'error': self.on_generation_done('img', data[0])
                
                # Video Tab Handlers
                elif msg_type == 'video_status': self.status_label_video.config(text=data[0])
                elif msg_type == 'video_result':
                    item_id = self.tree_video.get_children()[data[0]]
                    self.tree_video.item(item_id, values=(os.path.basename(self.video_paths[data[0]]), data[1], data[2]))
                elif msg_type == 'video_error': self.on_generation_done('video', data[0])

                # Shared Handlers
                elif msg_type == 'done': self.on_generation_done(data[0])
                elif msg_type == 'limit_check_success':
                    self.set_ui_state('normal'); self.status_label.config(text="Status: OK"); self.status_label_video.config(text="Status: OK")
                    messagebox.showinfo("Berhasil", "Koneksi sukses! API Key Anda valid dan siap digunakan.\n\nInfo: Limit standar adalah 60 permintaan per menit.")
                elif msg_type == 'limit_check_error':
                    self.set_ui_state('normal'); self.status_label.config(text="Status: Gagal"); self.status_label_video.config(text="Status: Gagal")
                    messagebox.showerror("Gagal", data[0])
                
                # Prompt Gen Tab Handlers
                elif msg_type == 'prompt_status': self.prompt_result_text.delete('1.0', 'end'); self.prompt_result_text.insert('1.0', data[0])
                elif msg_type == 'prompt_result_list':
                    self.prompt_result_text.delete('1.0', 'end')
                    self.prompt_result_text.insert('1.0', "\n\n".join([f"{i+1}. {p}" for i, p in enumerate(data[0])]))
                    self.export_prompt_variations_to_excel(data[0]); self.set_ui_state('normal')
                elif msg_type == 'prompt_error':
                    self.prompt_result_text.delete('1.0', 'end'); self.prompt_result_text.insert('1.0', f"ERROR: {data[0]}"); self.set_ui_state('normal')
        except queue.Empty: pass
        finally: self.after(100, self.check_queue)

    def on_generation_done(self, gen_type, error_msg=None):
        if error_msg: messagebox.showerror("Error", error_msg)
        
        if gen_type == 'img':
            self.progress_bar.stop(); self.progress_bar.pack_forget()
            self.status_label.config(text=f"Selesai! {len(self.image_paths)} gambar diproses.")
            if not error_msg: self.export_metadata_to_excel(gen_type)
        elif gen_type == 'video':
            self.progress_bar_video.stop(); self.progress_bar_video.pack_forget()
            self.status_label_video.config(text=f"Selesai! {len(self.video_paths)} video diproses.")
            if not error_msg: self.export_metadata_to_excel(gen_type)
        self.set_ui_state('normal')

    def set_ui_state(self, state):
        widgets = [self.api_entry, self.browse_btn, self.generate_btn, self.clear_btn, self.tree, self.generate_prompt_btn, self.check_limit_btn, self.browse_video_btn, self.generate_video_btn, self.clear_video_btn, self.tree_video]
        for combo in self.prompt_elements.values(): widgets.append(combo)
        for widget in widgets:
            try: widget.config(state=state)
            except (tk.TclError, AttributeError): pass

    def export_metadata_to_excel(self, export_type):
        if export_type == 'img':
            if not self.image_paths: return
            tree, status_label = self.tree, self.status_label
        elif export_type == 'video':
            if not self.video_paths: return
            tree, status_label = self.tree_video, self.status_label_video
        else: return
        
        status_label.config(text="Mengekspor ke Excel...")
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_folder = f"metadata_{export_type}_output_{timestamp}"
            os.makedirs(output_folder, exist_ok=True)
            data = [list(tree.item(item_id, 'values')) for item_id in tree.get_children()]
            df = pd.DataFrame(data, columns=["Filename", "Title", "Keywords"])
            output_path = os.path.join(output_folder, f"metadata_{export_type}.xlsx")
            df.to_excel(output_path, index=False)
            messagebox.showinfo("Ekspor Berhasil", f"Data metadata berhasil disimpan di:\n{os.path.abspath(output_path)}")
            status_label.config(text="Ekspor berhasil!")
        except Exception as e:
            messagebox.showerror("Gagal Ekspor", f"Gagal menyimpan file Excel: {e}")
            status_label.config(text="Gagal ekspor.")

    def export_prompt_variations_to_excel(self, prompts):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"generated_prompt_variations_{timestamp}.xlsx"
            df = pd.DataFrame([[i, p] for i, p in enumerate(prompts, 1)], columns=["Nomor", "Generated Prompt"])
            df.to_excel(filename, index=False)
            messagebox.showinfo("Ekspor Berhasil", f"Variasi prompt disimpan sebagai:\n{os.path.abspath(filename)}")
        except Exception as e: messagebox.showerror("Gagal Ekspor", f"Gagal menyimpan file Excel: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()