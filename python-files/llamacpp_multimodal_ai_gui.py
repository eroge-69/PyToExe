# GUI Python Tkinter untuk Multichat AI
# Fitur sesuai permintaan: tanpa Gradio/Flask, chat tab hanya aktif setelah model dijalankan dari tab utama
# Author: Satria Novian and Contributor: @chatgpt

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading, subprocess, json, os, time, re, requests
import base64
import mimetypes
import cv2
import tempfile
import torch
import pytesseract
from PIL import Image, ImageTk
from transformers import AutoProcessor, AutoModelForCausalLM
from docx import Document

class MultichatAI:
    def __init__(self, root):
        self.root = root
        self.root.title("LLaMA.cpp Server Multimodal AI GUI")

        self.model_running = False
        self.server_process = None
        self.chat_tabs = []
        self.contexts = {}
        self.memory_modes = self.load_memory_modes()
        self.tab_system_prompts = {}  # Untuk menyimpan system prompt setiap tab
        self.tab_settings = {}  # Simpan pengaturan per tab, key = tab_index
        self.stop_chunk_generation_flags = {}
        self.ctx_size = 4096  # default context size

        self.llama_port = 5001
        self.server_url = f"http://127.0.0.1:{self.llama_port}/completion"

        self.setup_main_tab()

    def setup_main_tab(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill='both', expand=True)

        self.main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text="Main Tab")

        load_btn = ttk.Button(self.main_tab, text="Load GGUF Model", command=self.load_model)
        load_btn.pack(pady=5)
        
        change_model_btn = ttk.Button(self.main_tab, text="Change GGUF Model", command=self.change_model)
        change_model_btn.pack(pady=5)
        
        ctx_btn = ttk.Button(self.main_tab, text="Pengaturan Ctx Size", command=self.ctx_settings_dialog)
        ctx_btn.pack(pady=5)

        run_server_btn = ttk.Button(self.main_tab, text="Run llama-server.exe", command=self.run_server)
        run_server_btn.pack(pady=5)
        
        custom_server_btn = ttk.Button(self.main_tab, text="Run LLaMA Server (Custom Multimodal)", command=self.run_server_custom)
        custom_server_btn.pack(pady=5)

        new_tab_btn = ttk.Button(self.main_tab, text="New Chat Tab", command=self.create_chat_tab)
        new_tab_btn.pack(pady=5)

    def load_model(self):
        filepath = filedialog.askopenfilename(title="Select GGUF model")
        if filepath:
            messagebox.showinfo("Model Loaded", f"Loaded model: {os.path.basename(filepath)}")
            self.model_path = filepath
            
    def change_model(self):
        if not self.model_running:
            self.load_model()
        else:
            confirm = messagebox.askyesno("Restart Required", "Server is running.\nDo you want to stop and load a new model?")
            if confirm:
                self.stop_server()
                time.sleep(1)
                self.load_model()
                messagebox.showinfo("Next Step", "Now click 'Run llama-server.exe' again.")

    def run_server(self):
        if hasattr(self, 'model_path'):
            try:
                self.server_process = subprocess.Popen(["llama-server.exe", "--model", self.model_path, "--port", str(self.llama_port)])
                self.model_running = True
                messagebox.showinfo("Success", "llama-server.exe started")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Load model first")
            
    def stop_server(self):
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()
            self.model_running = False
            messagebox.showinfo("Server Stopped", "llama-server.exe has been stopped.")
            
    def run_server_with_ctx(self):
        if hasattr(self, 'model_path'):
            try:
                self.server_process = subprocess.Popen([
                    "llama-server.exe",
                    "--model", self.model_path,
                    "--port", str(self.llama_port),
                    "--ctx-size", str(self.ctx_size)
                ])
                self.model_running = True
                messagebox.showinfo("Success", f"llama-server.exe started with ctx size {self.ctx_size}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Load model first")
            
    def run_server_custom(self):
        if not hasattr(self, 'model_path'):
            messagebox.showwarning("Warning", "Pilih model terlebih dahulu.")
            return

        def launch_server_with_ctx(ctx_value):
            try:
                model_dir = os.path.dirname(self.model_path)
                model_basename = os.path.basename(self.model_path)
                model_prefix = model_basename.split("-")[0].lower()  # contoh: gemma, internvl3, llava

                mmproj_path = ""
                needs_mmproj = not model_prefix.startswith("internvl3")  # model native multimodal

                if needs_mmproj:
                    mmproj_name = model_basename.replace(".gguf", ".mmproj-model.gguf")
                    mmproj_path_full = os.path.join(model_dir, mmproj_name)

                    if os.path.isfile(mmproj_path_full):
                        mmproj_path = mmproj_path_full
                    else:
                        for file in os.listdir(model_dir):
                            if file.endswith(".gguf") and "mmproj" in file.lower() and model_prefix in file.lower():
                                mmproj_path = os.path.join(model_dir, file)
                                print(f"[INFO] Using fallback mmproj file: {file}")
                                break

                args = [
                    "llama-server.exe",
                    "--model", self.model_path,
                    "--port", str(self.llama_port),
                    "--ctx-size", str(ctx_value)
                ]

                if mmproj_path:
                    args += ["--mmproj", mmproj_path]
                    print(f"[INFO] Using mmproj: {mmproj_path}")
                else:
                    if needs_mmproj:
                        print(f"[WARNING] mmproj not found for {model_prefix}. Model may not support image input.")
                    else:
                        print(f"[INFO] Model {model_prefix} is natively multimodal. Skipping mmproj.")

                self.server_process = subprocess.Popen(args)
                self.model_running = True

                messagebox.showinfo(
                    "Success",
                    f"llama-server.exe started\nModel: {model_prefix}\nMultimodal: {'Yes (native)' if not needs_mmproj else ('Yes (with mmproj)' if mmproj_path else 'No')}\nCtx Size: {ctx_value}"
                )

            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server:\n{str(e)}")

        # === Tkinter Window for Custom Ctx ===
        ctx_window = tk.Toplevel(self.root)
        ctx_window.title("Custom Context Size")

        tk.Label(ctx_window, text="Context Size (1024 - 327680):").pack(pady=5)
        ctx_entry = tk.Entry(ctx_window)
        ctx_entry.insert(0, "4096")
        ctx_entry.pack(pady=5)

        def on_run():
            try:
                ctx_val = int(ctx_entry.get())
                if ctx_val < 1024 or ctx_val > 327680:
                    raise ValueError
                ctx_window.destroy()
                launch_server_with_ctx(ctx_val)
            except ValueError:
                messagebox.showerror("Invalid Input", "Masukkan angka ctx-size antara 1024 hingga 327680.")

        def on_reset():
            ctx_entry.delete(0, tk.END)
            ctx_entry.insert(0, "4096")

        button_frame = tk.Frame(ctx_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Reset Default", command=on_reset).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Save & Jalankan", command=on_run).grid(row=0, column=1, padx=5)

    def create_chat_tab(self):
        if not self.model_running:
            messagebox.showwarning("Server not running", "Start llama-server.exe first")
            return

        tab = ttk.Frame(self.tab_control)
        tab_index = len(self.chat_tabs)

        chat_display = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=20)
        chat_display.pack(fill='both', expand=True)

        prompt_frame = ttk.Frame(tab)
        prompt_frame.pack(fill='x')
        
        image_frame = ttk.Frame(tab)
        image_frame.pack(fill='x', padx=5, pady=2)

        image_path_var = tk.StringVar(value="")
        image_label = ttk.Label(image_frame, textvariable=image_path_var)
        image_label.pack(side='left', padx=5)
        image_path_var.set("No image selected")

        # Load model BLIP untuk captioning
        model_id = "microsoft/git-large-coco"
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda")
        
        def upload_multiple_images_multimodal():
            global upload_mode
            upload_mode = "embedding"
            try:
                file_paths = filedialog.askopenfilenames(
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
                )
                if not file_paths:
                    return

                formatted_prompt = ""
                global latest_image_embeddings
                latest_image_embeddings = []

                # Clear image previews jika sudah ada
                if hasattr(self, 'img_previews'):
                    for img_widget in self.img_previews:
                        img_widget.destroy()
                self.img_previews = []

                for idx, file_path in enumerate(file_paths):
                    image = Image.open(file_path).convert("RGB")
                    inputs = processor(images=image, return_tensors="pt")
                    pixel_values = inputs["pixel_values"].to("cuda", dtype=torch.float16)

                    with torch.no_grad():
                        vision_outputs = model.get_input_embeddings()(inputs["pixel_values"])
                        # GIT tidak punya vision_model terpisah, jadi embedding diambil dari input embeddings
                        generated_ids = model.generate(pixel_values=pixel_values, max_new_tokens=50)
                        caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

                    latest_image_embeddings.append(vision_outputs.squeeze(0))

                    # Tambahkan caption ke prompt
                    formatted_prompt += f"[Image {idx+1} Caption: {caption}]\n"

                    # Tampilkan preview image
                    thumbnail = image.copy()
                    thumbnail.thumbnail((100, 100))
                    tk_image = ImageTk.PhotoImage(thumbnail)

                    img_label = ttk.Label(tab, image=tk_image)
                    img_label.image = tk_image
                    img_label.pack(side="left")
                    self.img_previews.append(img_label)

                # Tambahkan baris terakhir ke prompt
                formatted_prompt += "\nUser: "

                # Masukkan prompt ke UI
                prompt_entry.delete("1.0", "end")
                prompt_entry.insert("end", formatted_prompt)

                messagebox.showinfo("Sukses", f"{len(file_paths)} gambar diproses.")

            except Exception as e:
                messagebox.showerror("Gagal Memuat Gambar", str(e))

        upload_multi_btn = ttk.Button(image_frame, text="Upload Banyak Gambar + Caption", command=upload_multiple_images_multimodal)
        upload_multi_btn.pack(side='left')
        
        def upload_multiple_images_internvl():
            global upload_mode
            upload_mode = "embedding"
            try:
                file_paths = filedialog.askopenfilenames(
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
                )
                if not file_paths:
                    return

                formatted_prompt = ""
                global latest_image_embeddings
                latest_image_embeddings = []

                # Clear image previews jika ada sebelumnya
                if hasattr(self, 'img_previews'):
                    for img_widget in self.img_previews:
                        img_widget.destroy()
                self.img_previews = []

                for idx, file_path in enumerate(file_paths):
                    image = Image.open(file_path).convert("RGB")
                    inputs = processor(images=image, return_tensors="pt")
                    pixel_values = inputs["pixel_values"].to("cuda", dtype=torch.float16)

                    with torch.no_grad():
                        vision_outputs = model.get_input_embeddings()(inputs["pixel_values"])
                        # GIT tidak punya vision_model terpisah, jadi embedding diambil dari input embeddings
                        generated_ids = model.generate(pixel_values=pixel_values, max_new_tokens=50)
                        caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

                    latest_image_embeddings.append(vision_outputs.squeeze(0))

                    # Tambahkan format prompt untuk InternVL
                    formatted_prompt += f"<image {idx+1}>\n"
                    formatted_prompt += f"Caption: {caption}\n"

                    # Tampilkan preview image di GUI
                    thumbnail = image.copy()
                    thumbnail.thumbnail((100, 100))
                    tk_image = ImageTk.PhotoImage(thumbnail)

                    img_label = ttk.Label(tab, image=tk_image)
                    img_label.image = tk_image
                    img_label.pack(side="left")
                    self.img_previews.append(img_label)

                # Baris akhir untuk input user
                formatted_prompt += "User: "

                # Inject ke prompt_entry (Text widget)
                prompt_entry.delete("1.0", "end")
                prompt_entry.insert("end", formatted_prompt)

                messagebox.showinfo("Berhasil", f"{len(file_paths)} gambar berhasil diproses dengan format InternVL.")

            except Exception as e:
                messagebox.showerror("Gagal Memuat Gambar", str(e))
                
        upload_internvl_btn = ttk.Button(image_frame, text="Upload InternVL (Image + Caption + User)", command=upload_multiple_images_internvl)
        upload_internvl_btn.pack(side='left')

        def upload_video_internvl():
            global upload_mode
            upload_mode = "embedding"
            try:
                video_path = filedialog.askopenfilename(
                    filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")]
                )
                if not video_path:
                    return

                # ==== Ekstraksi frame dari video ====
                cap = cv2.VideoCapture(video_path)
                frame_interval = 30  # Ambil 1 frame setiap 30 frame video
                frame_count = 0
                extracted_frames = []

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if frame_count % frame_interval == 0:
                        temp_img_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
                        cv2.imwrite(temp_img_path, frame)
                        extracted_frames.append(temp_img_path)
                    frame_count += 1
                cap.release()

                formatted_prompt = ""
                global latest_image_embeddings
                latest_image_embeddings = []

                # Clear preview lama
                if hasattr(self, 'img_previews'):
                    for img_widget in self.img_previews:
                        img_widget.destroy()
                self.img_previews = []

                # ==== Proses setiap frame ====
                for idx, frame_path in enumerate(extracted_frames):
                    image = Image.open(frame_path).convert("RGB")
                    inputs = processor(images=image, return_tensors="pt")
                    pixel_values = inputs["pixel_values"].to("cuda", dtype=torch.float16)

                    with torch.no_grad():
                        vision_outputs = model.get_input_embeddings()(inputs["pixel_values"])
                        # GIT tidak punya vision_model terpisah, jadi embedding diambil dari input embeddings
                        generated_ids = model.generate(pixel_values=pixel_values, max_new_tokens=50)
                        caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

                    latest_image_embeddings.append(vision_outputs.squeeze(0))

                    # Format prompt InternVL
                    formatted_prompt += f"<image {idx+1}>\n"
                    formatted_prompt += f"Caption: {caption}\n"

                    # Preview di GUI
                    thumbnail = image.copy()
                    thumbnail.thumbnail((100, 100))
                    tk_image = ImageTk.PhotoImage(thumbnail)

                    img_label = ttk.Label(tab, image=tk_image)
                    img_label.image = tk_image
                    img_label.pack(side="left")
                    self.img_previews.append(img_label)

                formatted_prompt += "User: "

                # Masukkan ke prompt_entry
                prompt_entry.delete("1.0", "end")
                prompt_entry.insert("end", formatted_prompt)

                messagebox.showinfo("Berhasil", f"{len(extracted_frames)} frame berhasil diproses menggunakan microsoft/git-large-coco.")

            except Exception as e:
                messagebox.showerror("Gagal Memuat Video", str(e))

        # Tombol upload video
        upload_video_btn = ttk.Button(image_frame, text="Upload Video (InternVL)", command=upload_video_internvl)
        upload_video_btn.pack(side='left')
        
        def reset_images():
            global latest_image_embeddings
            latest_image_embeddings = []

            # Hapus preview gambar
            if hasattr(self, 'img_previews'):
                for img_widget in self.img_previews:
                    img_widget.destroy()
                self.img_previews = []

            # Reset label jadi No image selected
            image_path_var.set("")  
            image_label.config(text="No image selected")

            # Kosongkan prompt entry
            prompt_entry.delete("1.0", "end")

            messagebox.showinfo("Reset", "Gambar dan prompt berhasil direset.")
        
        reset_btn = ttk.Button(image_frame, text="Reset Gambar", command=reset_images)
        reset_btn.pack(side='left', padx=5)
        
        def upload_txt_for_data_analysis():
            global upload_mode
            upload_mode = "text_analysis"
            try:
                file_paths = filedialog.askopenfilenames(
                    filetypes=[("Text Files", "*.txt")]
                )
                if not file_paths:
                    return

                formatted_prompt = ""

                # Kita proses tiap file txt yang dipilih (bisa multi file)
                for idx, file_path in enumerate(file_paths):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()

                    # Format prompt content + user sesuai permintaan
                    formatted_prompt += f"<data_analysis {idx+1}>\n"
                    formatted_prompt += f"Prompt Content:\n{content}\n"
                    formatted_prompt += "User: \n\n"

                # Masukkan ke prompt_entry (Text widget)
                prompt_entry.delete("1.0", "end")
                prompt_entry.insert("end", formatted_prompt)

                messagebox.showinfo("Berhasil", f"{len(file_paths)} file txt berhasil diproses dengan format data analysis.")

            except Exception as e:
                messagebox.showerror("Gagal Memuat File TXT", str(e))


        # Contoh tombol untuk upload file txt di GUI
        upload_txt_btn = ttk.Button(image_frame, text="Upload Data Analysis TXT", command=upload_txt_for_data_analysis)
        upload_txt_btn.pack(side='left')
        
        def upload_docx_for_data_analysis():
            global upload_mode
            upload_mode = "text_analysis"
            try:
                file_paths = filedialog.askopenfilenames(
                    filetypes=[("Word Documents", "*.docx")]
                )
                if not file_paths:
                    return

                formatted_prompt = ""

                for idx, file_path in enumerate(file_paths):
                    doc = Document(file_path)

                    # ===== Ambil semua teks =====
                    all_text = []
                    for para in doc.paragraphs:
                        if para.text.strip():
                            all_text.append(para.text.strip())

                    # ===== Ambil semua tabel =====
                    all_tables = []
                    for table in doc.tables:
                        table_data = []
                        for row in table.rows:
                            row_data = [cell.text.strip() for cell in row.cells]
                            table_data.append(row_data)
                        all_tables.append(table_data)

                    # ===== OCR Gambar/Grafik =====
                    image_texts = []
                    images = [
                        part for part in doc.part.related_parts.values()
                        if part.content_type.startswith("image")
                    ]
                    for img_part in images:
                        img_bytes = img_part.blob
                        image = Image.open(BytesIO(img_bytes))
                        try:
                            ocr_text = pytesseract.image_to_string(image, lang="eng+ind")  # OCR bahasa Inggris + Indonesia
                            if ocr_text.strip():
                                image_texts.append(ocr_text.strip())
                        except Exception as ocr_err:
                            image_texts.append(f"[Gagal OCR: {ocr_err}]")

                    # ===== Format ke prompt =====
                    formatted_prompt += f"<data_analysis {idx+1}>\n"
                    formatted_prompt += f"File: {os.path.basename(file_path)}\n\n"

                    # Gabung teks dari paragraf
                    formatted_prompt += "Teks Dokumen:\n"
                    formatted_prompt += "\n".join(all_text) + "\n\n"

                    # Gabung tabel
                    if all_tables:
                        formatted_prompt += "Tabel:\n"
                        for t_idx, table in enumerate(all_tables, start=1):
                            formatted_prompt += f"  Tabel {t_idx}:\n"
                            for row in table:
                                formatted_prompt += "    " + " | ".join(row) + "\n"
                        formatted_prompt += "\n"

                    # Gabung hasil OCR dari gambar/grafik
                    if image_texts:
                        formatted_prompt += "Teks dari Gambar/Grafik (OCR):\n"
                        for g_idx, g_text in enumerate(image_texts, start=1):
                            formatted_prompt += f"  Gambar {g_idx}:\n"
                            formatted_prompt += f"    {g_text}\n"
                        formatted_prompt += "\n"

                    # Tutup dengan user prompt
                    formatted_prompt += "User:\n\n"

                # Masukkan ke prompt_entry (Text widget)
                prompt_entry.delete("1.0", "end")
                prompt_entry.insert("end", formatted_prompt)

                messagebox.showinfo("Berhasil", f"{len(file_paths)} file DOCX berhasil diproses untuk data analysis (termasuk OCR gambar/grafik).")

            except Exception as e:
                messagebox.showerror("Gagal Memuat File DOCX", str(e))

        # Contoh tombol untuk upload DOCX di GUI
        upload_docx_btn = ttk.Button(image_frame, text="Upload Data Analysis DOCX", command=upload_docx_for_data_analysis)
        upload_docx_btn.pack(side='left')

        prompt_entry = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, height=4)
        prompt_entry.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        send_btn = ttk.Button(prompt_frame, text="Kirim Prompt")
        send_btn.pack(side='left')

        chunk_delay = tk.DoubleVar(value=1.0)
        chunk_chk = tk.BooleanVar()
        chunk_cb = ttk.Checkbutton(prompt_frame, text="Generate per Chunk", variable=chunk_chk)
        chunk_cb.pack(side='left', padx=5)

        delay_spin = ttk.Spinbox(prompt_frame, from_=0.1, to=10.0, increment=0.1, textvariable=chunk_delay, width=5)
        delay_spin.pack(side='left')

        file_btn = ttk.Button(tab, text="Impor Prompt", command=lambda: self.import_prompt(prompt_entry))
        file_btn.pack(pady=2)

        setting_btn = ttk.Button(tab, text="Pengaturan", command=lambda: self.show_settings(tab_index))
        setting_btn.pack(pady=2)
        
        manual_chunk_var = tk.BooleanVar()

        manual_cb = ttk.Checkbutton(tab, text="Manual Generate Delay", variable=manual_chunk_var)
        manual_cb.pack()

        # --- Run Chunk Resume button ---
        run_chunk_btn = ttk.Button(tab, text="Run Chunk Resume", command=lambda d=chat_display, idx=tab_index: self.run_chunk_resume(d, idx))
        run_chunk_btn.pack(pady=2)
        
        reset_btn = ttk.Button(tab, text="🧹 Reset Chat Display", command=lambda idx=tab_index: self.reset_chat_display_only(idx))
        reset_btn.pack(pady=2)
        
        load_ctx_btn = ttk.Button(tab, text="📥 Load Chat Context", command=lambda idx=tab_index: self.load_chat_context(idx))
        load_ctx_btn.pack(pady=2)

        reset_ctx_btn = ttk.Button(tab, text="🧹 Reset Chat Context", command=lambda idx=tab_index: self.reset_chat_context(idx))
        reset_ctx_btn.pack(pady=2)

        close_btn = ttk.Button(tab, text="❌", command=lambda: self.close_tab(tab))
        close_btn.pack(anchor='ne')

        # --- Memory Mode Controls per Tab ---
        mem_mode_var = tk.StringVar()

        # --- Dropdown: pilih memory mode yang sudah tersimpan ---
        memory_mode_list = list(self.load_memory_modes().keys())

        self.mem_dropdown = ttk.Combobox(tab, textvariable=mem_mode_var, values=memory_mode_list, state="readonly")
        self.mem_dropdown.pack(pady=2)

        def on_memory_mode_selected(event):
            selected_mode = mem_mode_var.get()
            chat_display.insert(tk.END, f"[Selected Memory Mode: {selected_mode}]\n")
            chat_display.see(tk.END)

        self.mem_dropdown.bind("<<ComboboxSelected>>", on_memory_mode_selected)
        
        # Variabel untuk menyimpan status auto-refresh
        self.auto_refresh_var = tk.BooleanVar(value=True)  # default aktif

        # Checklist Auto-Refresh
        auto_refresh_cb = ttk.Checkbutton(tab, text="Auto-Refresh Memory Mode", variable=self.auto_refresh_var, command=lambda: self.load_memory_modes() if self.auto_refresh_var.get() else None)
        auto_refresh_cb.pack(pady=2)
        
        # Tombol Load Manual dari dropdown
        load_mem_btn = ttk.Button(tab, text="Load Selected Memory Mode", command=lambda m=mem_mode_var, d=chat_display: self.load_selected_memory_mode(m.get(), d))
        load_mem_btn.pack(pady=2)
        
        # Tombol Edit System Prompt
        prompt_btn = ttk.Button(tab, text="🛠 Prompt System", command=lambda idx=tab_index: self.edit_system_prompt(idx))
        prompt_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Set default system prompt untuk tab ini
        self.tab_system_prompts[tab_index] = (
            "You are a helpful and intelligent assistant. "
            "Respond clearly, concisely, and follow the user's instructions precisely.\n"
        )
        
        # ==== Kontrol Jumlah Context Lines ====
        def show_context_setting():
            ctx_win = tk.Toplevel(self.root)
            ctx_win.title("Pengaturan Panjang Context")
            ctx_win.geometry("300x120")

            lbl = ttk.Label(ctx_win, text="Jumlah Baris Context Terakhir:")
            lbl.pack(pady=5)

            ctx_var = tk.StringVar(value=str(self.chat_tabs[tab_index].get('context_lines', 4)))
            ctx_entry = ttk.Entry(ctx_win, textvariable=ctx_var, width=10)
            ctx_entry.pack(pady=5)

            def save_context_setting():
                try:
                    value = int(ctx_var.get())
                    if value < 0:
                        raise ValueError("Harus >= 0")
                    self.chat_tabs[tab_index]['context_lines'] = value
                    messagebox.showinfo("Disimpan", f"Jumlah context diset ke {value} baris terakhir.")
                    ctx_win.destroy()
                except ValueError as ve:
                    messagebox.showerror("Error", f"Input tidak valid: {ve}")

            save_btn = ttk.Button(ctx_win, text="Simpan", command=save_context_setting)
            save_btn.pack(pady=5)

        ctx_btn = ttk.Button(tab, text="🎛️ Context Setting", command=show_context_setting)
        ctx_btn.pack(pady=2)

        # ==== STOP BUTTON ====
        self.stop_chunk_generation_flags[tab_index] = False
        
        # Tombol Stop Chunk
        def stop_chunking():
            self.stop_chunk_generation_flags[tab_index] = True
            print(f"Stop Chunk ditekan di Tab {tab_index+1}")
            chat_display.insert(tk.END, "\n[Stopped by user]\n")
            chat_display.see(tk.END)
    
        stop_btn = ttk.Button(prompt_frame, text="Stop Chunk", command=stop_chunking)
        stop_btn.pack(side='left', padx=5)
        
        stop_event = threading.Event()
        
        stop_btn = tk.Button(tab, text="⛔ Stop Prompt", fg="red")

        def make_stop_prompt(chat_display, stop_event):
            def stop():
                chat_display.insert(tk.END, "\n[⛔ Prompt dihentikan oleh pengguna]\n")
                chat_display.see(tk.END)
                stop_event.set()
            return stop

        stop_btn.config(command=make_stop_prompt(chat_display, stop_event))
        stop_btn.pack(anchor='e', padx=5, pady=2)

        send_btn.config(command=lambda: self.send_prompt(prompt_entry, chat_display, chunk_chk.get(), chunk_delay.get(), tab_index, mem_mode_var.get(), stop_event))
        
        # Inisialisasi default setting untuk tab ini
        self.tab_settings[tab_index] = {
            "max_tokens": "512",
            "temperature": "0.7",
            "top_p": "0.9",
            "repeat_penalty": "1.1"
        }

        self.tab_control.add(tab, text=f"Chat {tab_index+1}")
        self.tab_control.select(tab)
        self.chat_tabs.append({
            'tab': tab,
            'chat_display': chat_display,
            'prompt_entry': prompt_entry,
            'context': [],
            'context_file': f"chat_context_{tab_index+1}.json",
            'history_file': f"chat_history_{tab_index+1}.txt",
            'chunk_file': f"chunk_{tab_index+1}.txt",
            'chunk_resume_file': f"chunk_resume_{tab_index+1}.json",
            'stop_event': stop_event,
            'stop_chunk_generation': False,
            'config': {}
        })
        
        chat_display.tag_configure("user_input", foreground="blue", font=('Courier', 10, 'bold'))

        def on_double_click(event, d=chat_display, tab_idx=tab_index, mem_var=mem_mode_var, stop_evt=stop_event):
            try:
                index = d.index("@%s,%s" % (event.x, event.y))
                line = d.get(f"{index} linestart", f"{index} lineend")
                if line.startswith("You:"):
                    old_prompt = line[4:].strip()

                    edit_win = tk.Toplevel(self.root)
                    edit_win.title("Edit Prompt")
                    edit_win.geometry("400x200")

                    edit_box = tk.Text(edit_win, wrap=tk.WORD)
                    edit_box.insert(tk.END, old_prompt)
                    edit_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

                    def send_edited():
                        new_prompt = edit_box.get("1.0", tk.END).strip()
                        if new_prompt:
                            stop_evt.clear()  # Reset stop
                            self.send_prompt(
                                entry=None,
                                display=d,
                                use_chunk=chunk_chk.get(),
                                delay=chunk_delay.get(),
                                tab_index=tab_idx,
                                memory_mode=mem_var.get(),
                                stop_event=stop_evt,
                                prompt_override=new_prompt  # Custom param (lihat bawah)
                            )
                            edit_win.destroy()

                    send_btn = ttk.Button(edit_win, text="Kirim Ulang Prompt", command=send_edited)
                    send_btn.pack(pady=5)

            except Exception as e:
                messagebox.showerror("Error", f"Gagal edit prompt: {e}")

        chat_display.bind("<Double-Button-1>", on_double_click)

    def send_prompt(self, entry, display, use_chunk, delay, tab_index, memory_mode, stop_event, prompt_override=None):
        stop_event.clear()
        
        prompt = prompt_override if prompt_override is not None else entry.get("1.0", tk.END).strip()

        if entry:
            entry.delete("1.0", tk.END)

        if not prompt:
            return
            
        # ✅ Keyword pemicu manual auto chunk resume (per tab)
        if prompt.lower() in ["run auto chunk resume", "lanjutkan chunking", "resume chunk sekarang"]:
            display.insert(tk.END, "[🧠] Memulai Auto Chunk Resume berdasarkan perintah prompt...\n")
            self.run_chunk_resume(display, tab_index)
            return

        # ✅ Update memory mode jika sesuai format (dan hentikan supaya tidak masuk ke chat)
        if prompt.startswith("update memory:"):
            self.update_memory_mode_injection(prompt)
            display.insert(tk.END, f"[💾] Memory Mode diperbarui dari prompt: {prompt}\n")
            return  # ← stop di sini, jangan kirim ke server

        default_system_prompt = (
            "You are a helpful and intelligent assistant. "
            "Respond clearly, concisely, and follow the user's instructions precisely.\n"
        )
        system_prompt = self.tab_system_prompts.get(tab_index, default_system_prompt)

        # Ambil riwayat chat terakhir
        chat_lines = display.get("1.0", tk.END).strip().split("\n")
        last_lines = [line for line in chat_lines if line.startswith("You:") or line.startswith("AI:")]
        ctx_lines = self.chat_tabs[tab_index].get('context_lines', 4)
        last_context = "\n".join(last_lines[-ctx_lines:])

        # --- Tambahkan memory jika ada (terhubung ke sistem memory mode) ---
        self.load_memory_modes()  # Pastikan memory_modes terbaru dari file
        memory_context = self.memory_modes.get(memory_mode, "")
        memory_block = f"{memory_context}\n" if memory_context else ""

        # Deteksi multimodal berdasarkan upload_mode
        upload_mode = globals().get("upload_mode", "text")
        is_multimodal = (upload_mode == "embedding")
        
        # Gunakan langsung karena sudah clean
        prompt_cleaned = prompt

        # Bangun prompt
        full_prompt = f"{system_prompt}{memory_block}{last_context}\nUser: {prompt_cleaned}\nAssistant:"

        display.insert(tk.END, f"You: {prompt}\n", "user_input")
        display.see(tk.END)

        self.save_chat_history(tab_index, f"You: {prompt}\n")

        threading.Thread(target=self.query_server, args=(full_prompt, display, use_chunk, delay, tab_index, stop_event, system_prompt, prompt, is_multimodal, upload_mode)).start()

    def query_server(self, full_prompt, display, use_chunk, delay, tab_index, stop_event, system_prompt, prompt, is_multimodal, upload_mode):
        try:
            headers = {"Content-Type": "application/json"}
            settings = self.tab_settings.get(tab_index, {})
            payload = {
                "prompt": full_prompt,
                "stream": False,
                "temperature": float(settings.get("temperature", 0.7)),
                "top_p": float(settings.get("top_p", 0.9)),
                "n_predict": int(settings.get("max_tokens", 512)),
                "repeat_penalty": float(settings.get("repeat_penalty", 1.1)),
                "stop": []
            }
            
            # Deteksi multimodal embedding
            if is_multimodal:
                print(f"Upload mode: {upload_mode}")
                if upload_mode == "embedding":
                    global latest_image_embeddings
                    if 'latest_image_embeddings' in globals() and latest_image_embeddings:
                        if len(latest_image_embeddings) == 1:
                            payload["image_embedding"] = latest_image_embeddings[0].tolist()
                        else:
                            payload["image_embeddings"] = [emb.tolist() for emb in latest_image_embeddings]

                        print(f"[DEBUG] {len(latest_image_embeddings)} image_embedding(s) dimasukkan ke payload (mode: embedding)")
                    else:
                        # Jika tidak ada embeddings, langsung fallback ke prompt teks
                        payload["prompt"] = full_prompt
                        print("[DEBUG] latest_image_embeddings tidak ditemukan, fallback ke prompt teks (mode: teks)")
                else:
                    # Upload mode selain "embedding", fallback ke prompt teks biasa
                    print("[DEBUG] Mode upload tidak dikenali, fallback ke prompt teks biasa.")
                    # Tetap kirim prompt teks biasa ke payload
                    payload["prompt"] = full_prompt  
            else:
                # Mode bukan multimodal, prompt biasa
                payload["prompt"] = full_prompt
                    
            response = requests.post(self.server_url, json=payload, headers=headers)
            result = response.json()
            output = result.get("content", "[No response]")
            
            stop_event.clear()

            if re.search(r'(\d+)\s*words\s+and\s+(\d+)\s*words\s+per\s+paragraph', prompt.lower()):
                use_chunk = True

            if use_chunk:
                self.chat_tabs[tab_index]['stop_chunk_generation'] = False
                stop_event.clear()
                words = output.split()
                chunk = 50
                chunk_lines = []
                chunk_resume = []  # Untuk file chunk_resume.json

                for i in range(0, len(words), chunk):
                    part = ' '.join(words[i:i+chunk])
                    display.insert(tk.END, f"AI: {part}\n")
                    display.see(tk.END)
                    self.save_chat_context(tab_index, f"AI: {part}\n")
                    self.save_chat_history(tab_index, f"AI: {part}\n")
                    chunk_lines.append(f"AI: {part}\n")
                    chunk_resume.append({"chunk_index": i // chunk, "content": part})
                    if self.stop_chunk_generation_flags.get(tab_index, False):
                        display.insert(tk.END, f"\n[Stopped by user]\n")
                        break
                    time.sleep(delay)

                # Simpan file apa pun hasil chunk_lines dan chunk_resume sampai saat break
                try:
                    with open(self.chat_tabs[tab_index]['chunk_file'], 'w', encoding='utf-8') as f:
                        f.writelines(chunk_lines)

                    chunk_resume_path = self.chat_tabs[tab_index]['chunk_resume_file']
                    with open(chunk_resume_path, 'w', encoding='utf-8') as json_file:
                        json.dump(chunk_resume, json_file, indent=2, ensure_ascii=False)

                    display.insert(tk.END, "[ℹ️] Progress chunk disimpan, kamu bisa lanjutkan dengan Run Chunk Resume.\n")
                except Exception as e:
                    display.insert(tk.END, f"[Error saat simpan chunk]: {e}\n")

            else:
                if stop_event.is_set():
                    display.insert(tk.END, "\n[⛔ Prompt dihentikan sebelum ditampilkan]\n")
                    display.see(tk.END)
                    return
                display.insert(tk.END, f"AI: {output}\n")
                display.see(tk.END)
                self.save_chat_context(tab_index, f"AI: {output}\n")
                self.save_chat_history(tab_index, f"AI: {output}\n")

        except Exception as e:
            display.insert(tk.END, f"[Error]: {str(e)}\n")
            display.see(tk.END)

    def save_chat_context(self, tab_index, line):
        ctx_file = self.chat_tabs[tab_index]['context_file']
        context = self.chat_tabs[tab_index].get('context', [])
        context.append(line.strip())
        self.chat_tabs[tab_index]['context'] = context
        with open(ctx_file, 'w', encoding='utf-8') as f:
            json.dump({"context": context}, f, ensure_ascii=False, indent=2)

    def save_chat_history(self, tab_index, line):
        hist_file = self.chat_tabs[tab_index]['history_file']
        with open(hist_file, 'a', encoding='utf-8') as f:
            f.write(line)

    def import_prompt(self, entry):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    entry.delete("1.0", tk.END)  # Hapus isi lama dulu
                    entry.insert(tk.END, content)  # Masukkan di akhir
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file: {e}")

    def update_memory_mode_injection(self, prompt):
        """
        Update memory mode dari string prompt berformat:
        update memory: <nama> = <isi>
        """
        m = re.match(r"update memory:\s*(.*?)\s*=\s*(.*)", prompt)
        if m:
            name, content = m.groups()
            self.memory_modes[name] = content
            with open("memory_mode.json", "w", encoding='utf-8') as f:
                json.dump(self.memory_modes, f)

    def load_memory_modes(self):
        """Selalu load memory_mode.json versi terbaru dan update ke self.memory_modes."""
        try:
            with open("memory_mode.json", "r", encoding="utf-8") as f:
                self.memory_modes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory_modes = {}

        # Jika ada dropdown memory, langsung perbarui nilainya
        if hasattr(self, "mem_dropdown") and isinstance(self.mem_dropdown, ttk.Combobox):
            self.mem_dropdown["values"] = list(self.memory_modes.keys())

        return self.memory_modes
        
    def update_memory_mode(self, key, value):
        """Update memory_mode.json lalu refresh dropdown & pilih mode terbaru."""
        # Load data terbaru dulu
        self.load_memory_modes()

        # Simpan / update memory mode
        self.memory_modes[key] = value
        with open("memory_mode.json", "w", encoding="utf-8") as f:
            json.dump(self.memory_modes, f, indent=4, ensure_ascii=False)

        # Refresh dropdown setelah update (kalau auto-refresh aktif)
        if getattr(self, "auto_refresh_var", None) and self.auto_refresh_var.get():
            self.load_memory_modes()

        # Set dropdown ke mode yang baru diupdate
        if hasattr(self, "mem_dropdown") and isinstance(self.mem_dropdown, ttk.Combobox):
            self.mem_dropdown.set(key)  # otomatis pilih mode baru

        # Optional: Tampilkan info di chat display
        if hasattr(self, "chat_display"):
            self.chat_display.insert(tk.END, f"[✅ Memory Mode Updated: {key}]\n")
            self.chat_display.see(tk.END)
        
    def load_selected_memory_mode(self, name, display):
        """Load a single memory mode by name into the chat display."""
        self.load_memory_modes()  # Pastikan sinkron dengan file terbaru
    
        if not name:  # Jika nama kosong
            display.insert(tk.END, "[⚠] No memory mode selected.\n")
            display.see(tk.END)
            return

        if name in self.memory_modes:
            content = self.memory_modes[name]
            display.insert(tk.END, f"[Memory Mode Loaded: {name}]\n{content}\n\n")
        else:
            display.insert(tk.END, f"[❌] Memory Mode '{name}' not found.\n")
    
        display.see(tk.END)

    def run_chunk_resume(self, display, tab_index):
        try:
            chunk_resume_path = self.chat_tabs[tab_index]['chunk_resume_file']
            with open(chunk_resume_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                display.insert(tk.END, "\n[Chunk Resume Loaded]\n")
                for item in data:
                    display.insert(tk.END, f"AI (Chunk {item['chunk_index']}): {item['content']}\n")
                display.see(tk.END)
        except Exception as e:
            display.insert(tk.END, f"\n[Failed to load chunk_resume.json]: {e}\n")
            
    def check_and_run_chunk_resume(self, display, tab_index, enable_chunk_resume):
        # File resume per tab
        chunk_resume_path = self.chat_tabs[tab_index]['chunk_resume_file']

        if enable_chunk_resume.get() and os.path.exists(chunk_resume_path):
            try:
                with open(chunk_resume_path, "r", encoding="utf-8") as f:
                    resume_data = json.load(f)

                # Cek jika resume_data valid dan berisi list chunk
                if isinstance(resume_data, list) and len(resume_data) > 0:
                    # Mulai thread run chunk resume (tampilkan chunk yang sudah tersimpan)
                    threading.Thread(target=self.run_chunk_resume, args=(display, tab_index), daemon=True).start()
                    return True
                else:
                    messagebox.showwarning("Resume Gagal", "Data resume tidak valid atau kosong.")
                    return False
            except Exception as e:
                messagebox.showwarning("Resume Gagal", f"Data resume rusak: {e}")
                return False
        return False

    def close_tab(self, tab):
        index = self.tab_control.index(tab)
        self.tab_control.forget(index)
        del self.chat_tabs[index]

    def show_settings(self, tab_index):
        current_settings = self.tab_settings.get(tab_index, {
            "max_tokens": "512",
            "temperature": "0.7",
            "top_p": "0.9",
            "repeat_penalty": "1.1"
        })

        settings_window = tk.Toplevel(self.root)
        settings_window.title(f"Settings - Tab {tab_index + 1}")

        tk.Label(settings_window, text="Max Tokens:").grid(row=0, column=0)
        max_tokens_var = tk.StringVar(value=current_settings.get("max_tokens", "512"))
        tk.Entry(settings_window, textvariable=max_tokens_var).grid(row=0, column=1)

        tk.Label(settings_window, text="Temperature:").grid(row=1, column=0)
        temperature_var = tk.StringVar(value=current_settings.get("temperature", "0.7"))
        tk.Entry(settings_window, textvariable=temperature_var).grid(row=1, column=1)

        tk.Label(settings_window, text="Top-p:").grid(row=2, column=0)
        top_p_var = tk.StringVar(value=current_settings.get("top_p", "0.9"))
        tk.Entry(settings_window, textvariable=top_p_var).grid(row=2, column=1)
        
        tk.Label(settings_window, text="Repeat Penalty:").grid(row=3, column=0)
        repeat_penalty_var = tk.StringVar(value=current_settings.get("repeat_penalty", "1.1"))
        tk.Entry(settings_window, textvariable=repeat_penalty_var).grid(row=3, column=1)

        def save_local_settings():
            self.tab_settings[tab_index] = {
                "max_tokens": max_tokens_var.get(),
                "temperature": temperature_var.get(),
                "top_p": top_p_var.get(),
                "repeat_penalty": repeat_penalty_var.get()
            }
            messagebox.showinfo("Saved", f"Settings saved for Tab {tab_index + 1}")
            settings_window.destroy()

        tk.Button(settings_window, text="Save", command=save_local_settings).grid(row=4, columnspan=2)
        
    def edit_system_prompt(self, tab_index):
        current_prompt = self.tab_system_prompts.get(tab_index, "You are a helpful assistant.\n")
        default_prompt = (
            "You are a helpful and intelligent assistant. "
            "Respond clearly, concisely, and follow the user's instructions precisely.\n"
        )

        prompt_win = tk.Toplevel(self.root)
        prompt_win.title(f"Edit System Prompt - Tab {tab_index + 1}")
        prompt_win.geometry("500x300")

        label = ttk.Label(prompt_win, text="Edit system prompt for this chat tab:")
        label.pack(pady=5)

        prompt_text = tk.Text(prompt_win, wrap=tk.WORD)
        prompt_text.insert(tk.END, current_prompt)
        prompt_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        def save_prompt():
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            self.tab_system_prompts[tab_index] = new_prompt
            messagebox.showinfo("Saved", "System prompt updated successfully.")
            prompt_win.destroy()

        def reset_prompt():
            prompt_text.delete("1.0", tk.END)
            prompt_text.insert(tk.END, default_prompt)

        btn_frame = ttk.Frame(prompt_win)
        btn_frame.pack(pady=5)

        save_btn = ttk.Button(btn_frame, text="💾 Save", command=save_prompt)
        save_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = ttk.Button(btn_frame, text="🔁 Reset Default", command=reset_prompt)
        reset_btn.pack(side=tk.LEFT, padx=5)

    def ctx_settings_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Pengaturan Ctx Size")

        tk.Label(win, text="Context Size:").grid(row=0, column=0, padx=10, pady=5)
        ctx_var = tk.StringVar(value=str(self.ctx_size))
        tk.Entry(win, textvariable=ctx_var).grid(row=0, column=1, padx=10, pady=5)

        def save_ctx():
            try:
                self.ctx_size = int(ctx_var.get())
                win.destroy()
                self.run_server_with_ctx()
            except ValueError:
                messagebox.showerror("Error", "Ctx size harus angka bulat")

        def reset_ctx():
            ctx_var.set("4096")

        tk.Button(win, text="💾 Save & Run Server", command=save_ctx).grid(row=1, column=0, pady=10)
        tk.Button(win, text="🔁 Reset Default", command=reset_ctx).grid(row=1, column=1, pady=10)
        
    def reset_chat_display_only(self, tab_index):
        try:
            tab_info = self.chat_tabs[tab_index]
            display_widget = tab_info['chat_display']
            display_widget.delete("1.0", tk.END)
            display_widget.insert(tk.END, "[Chat cleared from display only — history & context preserved]\n")
            display_widget.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset chat display: {e}")
            
    def load_chat_context(self, tab_index):
        try:
            ctx_file = self.chat_tabs[tab_index]['context_file']
            if os.path.exists(ctx_file):
                with open(ctx_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    context_lines = data.get("context", [])
                    display_widget = self.chat_tabs[tab_index]['chat_display']
                    display_widget.delete("1.0", tk.END)
                    display_widget.insert(tk.END, "\n[Chat context loaded from file]\n")
                    for line in context_lines:
                        display_widget.insert(tk.END, line + "\n")
                    display_widget.see(tk.END)
            else:
                messagebox.showinfo("No Context", "Context file not found for this tab.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load context: {e}")

    def reset_chat_context(self, tab_index):
        try:
            self.chat_tabs[tab_index]['context'] = []
            ctx_file = self.chat_tabs[tab_index]['context_file']
            with open(ctx_file, 'w', encoding='utf-8') as f:
                json.dump({"context": []}, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Context Reset", f"Context for Tab {tab_index + 1} has been cleared.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset context: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MultichatAI(root)
    root.mainloop()
