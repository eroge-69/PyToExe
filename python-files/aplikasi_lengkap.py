# =======================================================================================
# APLIKASI LIVECHAT DOWNLOADER v8.1 (Versi Streamlined)
# Dibuat oleh Gemini
# =======================================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
import shutil
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# --- KONFIGURASI ---
LOGIN_URL = "https://accounts.livechat.com/"
ARCHIVES_URL = "https://my.livechatinc.com/archives"
DOWNLOAD_FOLDER = "Downloaded_Transcripts"
COMBINED_FOLDER = "Combined_Archives"
HISTORY_FILE = "download_history.json"

# --- FUNGSI PENGGABUNGAN ---
def combine_all(log_function):
    log_function("Memulai proses 'Gabungkan Semua Jadi 1 File'...")
    os.makedirs(COMBINED_FOLDER, exist_ok=True)
    
    if not os.path.exists(DOWNLOAD_FOLDER):
        log_function(f"Folder '{DOWNLOAD_FOLDER}' tidak ditemukan.")
        return

    txt_files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.txt')]
    if not txt_files:
        log_function("Tidak ada file transkrip baru untuk digabungkan.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_filename = f"Gabungan_Total_{timestamp}.txt"
    output_filepath = os.path.join(COMBINED_FOLDER, output_filename)
    
    log_function(f"Menggabungkan {len(txt_files)} file ke dalam '{output_filename}'...")
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        for file_path in sorted(txt_files):
            filename = os.path.basename(file_path)
            outfile.write(f"===== ISI DARI FILE: {filename} =====\n\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as infile: outfile.write(infile.read() + "\n\n")
            except Exception as e: log_function(f"-> Gagal membaca {filename}: {e}")
            
    log_function(f"✅ File '{output_filename}' berhasil dibuat.")
    archive_originals_dir = os.path.join(COMBINED_FOLDER, "originals_total", timestamp)
    os.makedirs(archive_originals_dir, exist_ok=True)
    for file_path in txt_files:
        try: shutil.move(file_path, archive_originals_dir)
        except Exception as e: log_function(f"-> Gagal memindahkan {os.path.basename(file_path)}: {e}")
    log_function("'Gabungkan Semua' selesai.")


# --- LOGIKA BOT ---

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    try:
        with open(HISTORY_FILE, 'r') as f: return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError): return set()

def save_history(downloaded_ids_set):
    with open(HISTORY_FILE, 'w') as f: json.dump(list(downloaded_ids_set), f, indent=4)

def wait_for_new_file(timeout=15):
    files_before = set(os.listdir(DOWNLOAD_FOLDER))
    start_time = time.time()
    while time.time() - start_time < timeout:
        if len(set(os.listdir(DOWNLOAD_FOLDER))) > len(files_before):
            return True
        time.sleep(0.1)
    return False

def download_task(driver, log_function, update_gui_callback):
    try:
        log_function("Memulai proses download dari bawah ke atas...")
        log_function("Mengambil semua data chat yang telah Anda muat di layar...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_chat_ids = [item['id'].replace('archive-item-', '') for item in soup.select('li[id^="archive-item-"]')]
        if not all_chat_ids:
            log_function("Tidak ada chat yang terdeteksi di layar.")
            return

        downloaded_history = load_history()
        new_chats = [cid for cid in all_chat_ids if cid not in downloaded_history]

        if not new_chats:
            log_function("Semua chat yang terlihat sudah ada dalam riwayat unduhan.")
            return

        log_function(f"Ditemukan {len(new_chats)} transkrip baru untuk diunduh.")
        total_chats = len(new_chats)
        
        for i, chat_id in enumerate(reversed(new_chats)):
            log_function(f"[{i+1}/{total_chats}] Memproses dari bawah: ID {chat_id}...")
            try:
                chat_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, f"archive-item-{chat_id}")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", chat_element)
                chat_element.click()
                
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='chat-menu-trigger-button']"))).click()
                download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-test='download-transcript-menu-item']")))
                download_button.click()

                if wait_for_new_file():
                    downloaded_history.add(chat_id)
                else:
                    log_function(f"-> Peringatan: Gagal konfirmasi download untuk {chat_id}.")
            except Exception as e:
                log_function(f"❌ Gagal memproses {chat_id}. Error: {type(e).__name__}")
        
        save_history(downloaded_history)
        log_function("================== DOWNLOAD BATCH INI SELESAI ==================")

    except Exception as e:
        log_function(f"Terjadi error saat proses download: {e}")
    finally:
        log_function("Proses download selesai. Browser tetap terbuka.")
        update_gui_callback()

def login_and_prepare_browser(app_instance, email, password):
    try:
        app_instance.log("Mempersiapkan browser...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"download.default_directory": os.path.abspath(DOWNLOAD_FOLDER)})
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        app_instance.driver = driver
        app_instance.log("Membuka halaman login...")
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']"))).send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))).send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        app_instance.log("Login berhasil, membuka halaman Archives...")
        driver.get(ARCHIVES_URL)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[id^="archive-item-"]')))
        app_instance.log("✅ Browser SIAP. Silakan filter & scroll manual di browser.")
        app_instance.log("Jika sudah siap, klik 'Mulai Download'.")
        app_instance.root.after(0, app_instance.on_login_success)
    except Exception as e:
        app_instance.log(f"Gagal login atau membuka browser: {e}")
        if 'driver' in locals() and locals()['driver']: driver.quit()
        app_instance.root.after(0, app_instance.reset_gui)

# --- APLIKASI GUI ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("LiveChat Downloader v8.1 (Streamlined)")
        self.root.geometry("800x520")
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        self.driver = None

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        login_frame = ttk.LabelFrame(main_frame, text="Info Login", padding="10")
        login_frame.pack(fill="x", pady=5)
        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(login_frame, width=40)
        self.email_entry.grid(row=0, column=1, sticky="ew")
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew")
        login_frame.columnconfigure(1, weight=1)

        action_frame = ttk.LabelFrame(main_frame, text="Langkah Download", padding="10")
        action_frame.pack(fill="x", pady=10)
        self.login_button = ttk.Button(action_frame, text="1. Login & Buka Browser", command=self.start_login_thread)
        self.login_button.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
        self.download_button = ttk.Button(action_frame, text="2. Mulai Download", command=self.start_download_thread, state="disabled", style="Accent.TButton")
        self.download_button.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
        
        utility_frame = ttk.LabelFrame(main_frame, text="Tugas Tambahan (Setelah Download)", padding="10")
        utility_frame.pack(fill="x", pady=(0, 10))
        self.combine_all_button = ttk.Button(utility_frame, text="Gabungkan Semua File Menjadi 1", command=self.start_combine_thread)
        self.combine_all_button.pack(fill="x", expand=True, padx=5, ipady=8)
        
        self.quit_button = ttk.Button(main_frame, text="Tutup Browser & Keluar", command=self.on_closing)
        self.quit_button.pack(fill="x", padx=5, ipady=8)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log Aktivitas", padding="10")
        log_frame.pack(fill="both", expand=True)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#28a745", font=('Helvetica', 10, 'bold'))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin menutup browser (jika ada) dan keluar dari aplikasi?"):
            if self.driver and self.is_driver_active():
                try: self.driver.quit()
                except: pass
            self.root.destroy()

    def log(self, message):
        self.root.after(0, self._update_log, message)
            
    def _update_log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")
            
    def start_login_thread(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Email dan Password harus diisi.")
            return
        self.set_buttons_state("disabled", login_btn_state="disabled")
        self.login_button.config(text="LOGIN...")
        threading.Thread(target=login_and_prepare_browser, args=(self, email, password), daemon=True).start()

    def start_download_thread(self):
        if not self.driver or not self.is_driver_active():
            messagebox.showerror("Error", "Browser tidak aktif atau sudah ditutup. Silakan login kembali.")
            self.reset_gui()
            return
        self.set_buttons_state("disabled", login_btn_state="disabled")
        self.download_button.config(text="DOWNLOADING...")
        threading.Thread(target=download_task, args=(self.driver, self.log, lambda: self.root.after(0, self.on_download_finish)), daemon=True).start()

    def start_combine_thread(self):
        self.set_buttons_state("disabled", login_btn_state="disabled")
        threading.Thread(target=self.run_combine, args=(combine_all,), daemon=True).start()

    def run_combine(self, target_function):
        target_function(self.log)
        self.root.after(0, self.on_task_finish)

    def on_login_success(self):
        self.set_buttons_state("disabled", login_btn_state="disabled")
        self.login_button.config(text="Browser Siap")
        self.download_button.config(state="normal")
        self.quit_button.config(state="normal")
        self.combine_all_button.config(state="normal")

    def on_download_finish(self):
        self.on_task_finish()
        self.download_button.config(text="2. Mulai Download Berikutnya")
    
    def on_task_finish(self):
        messagebox.showinfo("Selesai", "Tugas telah selesai.")
        is_browser_active = self.driver and self.is_driver_active()
        
        self.set_buttons_state("normal")
        if is_browser_active:
            self.login_button.config(state="disabled", text="Browser Siap")
        else:
            self.reset_gui()

    def set_buttons_state(self, state, login_btn_state="normal"):
        self.login_button.config(state=login_btn_state)
        self.download_button.config(state=state)
        self.combine_all_button.config(state=state)
        self.quit_button.config(state=state)

    def reset_gui(self):
        self.driver = None
        self.login_button.config(state="normal", text="1. Login & Buka Browser")
        self.set_buttons_state("disabled", login_btn_state="normal")
        self.combine_all_button.config(state="normal")
        
    def is_driver_active(self):
        try:
            _ = self.driver.window_handles
            return True
        except:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()