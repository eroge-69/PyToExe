import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import requests
import sys
import os
from multiprocessing.dummy import Pool
import queue
import time
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

class WordPressScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("WordPress Vulnerability Scanner v2.0 - By DENZ")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.scanning = False
        self.results_queue = queue.Queue()
        self.target = []
        
        # Telegram config (sama seperti original)
        self.telegram_token = "7609687193:AAGQNWSAyIAdy2otCOYLWF8vH1H52hfoyws"
        self.chat_id = "7640415872"
        
        # HTTP headers (sama seperti original)
        self.headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'referer': 'www.google.com'
        }
        
        # Disable warnings
        requests.packages.urllib3.disable_warnings()
        
        # Create GUI
        self.create_widgets()
        
        # Start result checker
        self.check_results()
        
        # Initialize counters
        self.scanned_count = 0
        self.vuln_count = 0
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors - Matrix theme
        style.configure('Title.TLabel', foreground='#00ff41', background='#0a0a0a', 
                       font=('Consolas', 18, 'bold'))
        style.configure('Header.TLabel', foreground='#00ff41', background='#0a0a0a', 
                       font=('Consolas', 11, 'bold'))
        style.configure('Custom.TFrame', background='#0a0a0a')
        style.configure('Custom.TButton', background='#1a1a2e', foreground='#00ff41',
                       font=('Consolas', 10, 'bold'))
        style.configure('Custom.TEntry', fieldbackground='#1a1a2e', foreground='#00ff41',
                       font=('Consolas', 10))
        style.configure('Custom.TLabelFrame', background='#0a0a0a', foreground='#00ff41',
                       font=('Consolas', 10, 'bold'))
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Banner - sama seperti original
        banner_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        banner_frame.pack(fill=tk.X, pady=(0, 20))
        
        banner_text = """
  [#] Create By ::
DENZ
        """
        banner_label = tk.Label(banner_frame, text=banner_text, 
                               fg='#00ff41', bg='#0a0a0a', font=('Consolas', 14, 'bold'),
                               justify=tk.CENTER)
        banner_label.pack()
        
        # Title
        title_label = ttk.Label(main_frame, text="WordPress Vulnerability Scanner", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text=" Configuration ", 
                                     style='Custom.TLabelFrame')
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Telegram settings frame
        telegram_frame = ttk.Frame(config_frame, style='Custom.TFrame')
        telegram_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(telegram_frame, text="Telegram Token:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.token_entry = ttk.Entry(telegram_frame, style='Custom.TEntry', width=50)
        self.token_entry.insert(0, self.telegram_token)
        self.token_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(telegram_frame, text="Chat ID:", style='Header.TLabel').grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(8, 0))
        self.chatid_entry = ttk.Entry(telegram_frame, style='Custom.TEntry', width=20)
        self.chatid_entry.insert(0, self.chat_id)
        self.chatid_entry.grid(row=1, column=1, sticky=tk.W, pady=(8, 0))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text=" Target Configuration ", 
                                   style='Custom.TLabelFrame')
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        file_inner_frame = ttk.Frame(file_frame, style='Custom.TFrame')
        file_inner_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(file_inner_frame, text="Sites File (sites.txt):", style='Header.TLabel').pack(anchor=tk.W)
        
        file_select_frame = ttk.Frame(file_inner_frame, style='Custom.TFrame')
        file_select_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path, 
                                   style='Custom.TEntry')
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(file_select_frame, text="Browse", command=self.browse_file,
                  style='Custom.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Scan", 
                                      command=self.start_scan, style='Custom.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Stop Scan", 
                                     command=self.stop_scan, style='Custom.TButton', 
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="🗑️ Clear Results", command=self.clear_results,
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="📁 Open Results", command=self.open_results,
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress and status frame
        progress_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_label = tk.Label(progress_frame, text="Ready to scan", 
                                    fg='#00ff41', bg='#0a0a0a', font=('Consolas', 11, 'bold'))
        self.status_label.pack()
        
        # Statistics frame
        stats_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = tk.Label(stats_frame, text="Scanned: 0 | Vulnerable: 0 | Threads: 50", 
                                   fg='#00ff41', bg='#0a0a0a', font=('Consolas', 11, 'bold'))
        self.stats_label.pack()
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text=" Scan Results ", 
                                      style='Custom.TLabelFrame')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame, bg='#0a0a0a', fg='#00ff41', 
            font=('Consolas', 10), insertbackground='#00ff41',
            selectbackground='#1a1a2e', selectforeground='#00ff41'
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for colors
        self.results_text.tag_configure("success", foreground="#00ff41")
        self.results_text.tag_configure("failed", foreground="#ff4444")
        self.results_text.tag_configure("error", foreground="#ffaa00")
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select sites.txt file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
    
    def open_results(self):
        if os.path.exists('vuln.txt'):
            os.startfile('vuln.txt')
        else:
            messagebox.showinfo("Info", "No results file found yet!")
    
    def update_status(self, message, color='#00ff41'):
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def log_result(self, message, tag="success"):
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.results_text.insert(tk.END, formatted_message, tag)
        self.results_text.see(tk.END)
        self.root.update()
    
    def update_stats(self):
        self.stats_label.config(text=f"Scanned: {self.scanned_count} | Vulnerable: {self.vuln_count} | Threads: 50")
    
    # Function to send message to Telegram (sama seperti original)
    def kirim_telegram(self, pesan):
        token = self.token_entry.get().strip()
        chat_id = self.chatid_entry.get().strip()
        
        if not token or not chat_id:
            return
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": pesan
        }
        try:
            requests.post(url, data=data, timeout=10)
        except:
            pass
    
    # Format URL (sama seperti original)
    def URLdomain(self, site):
        if 'http://' not in site and 'https://' not in site:
            site = 'http://' + site
        if site[-1] != '/':
            site = site + '/'
        return site
    
    # Fungsi untuk baca daftar direktori dari file (sama seperti original)
    def load_directories(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dirs = [line.strip() for line in f if line.strip()]
            return dirs
        except Exception as e:
            self.log_result(f"Error loading directories from {file_path}: {e}", "error")
            return []
    
    # Main scan function (EXACT sama seperti original)
    def exploit(self, url):
        if not self.scanning:
            return
            
        try:
            url = self.URLdomain(url)
            if 'www.' in url:
                username = url.replace('www.', '')
            else:
                username = url
            if '.' in username:
                username = username.split('.')[0]
            if 'http://' in username:
                username = username.replace('http://', '')
            else:
                username = username.replace('https://', '')
            up = username.title()

            # Load direktori dari file
            listdir = self.load_directories('path_2024.txt')

            # Tambahkan username dan variasinya ke listdir jika belum ada
            extras = [username, username.lower(), username.upper(), up]
            for extra in extras:
                if extra not in listdir:
                    listdir.append(extra)

            for directory in listdir:
                if not self.scanning:
                    break
                    
                inj = url + directory
                try:
                    check = requests.get(inj, headers=self.headers, verify=False, timeout=15).content
                    content = check.decode()
                    
                    # Check for WordPress Installation (EXACT sama seperti original)
                    if ('WordPress &rsaquo; Installation' in content or
                        'WordPress &rsaquo; installasi' in content or
                        'WordPress &rsaquo; Instalación' in content or
                        'WordPress &rsaquo; Installazione' in content or
                        'WordPress &rsaquo; インストール' in content or
                        'WordPress &rsaquo; Установка' in content or
                        'WordPress &rsaquo; 설치' in content or
                        'WordPress &rsaquo; installation' in content or
                        'WordPress &rsaquo; Installation' in content or
                        'WordPress &rsaquo; instalação' in content or
                        'WordPress &rsaquo; instalace' in content or
                        'WordPress &rsaquo; instalacija' in content or
                        'WordPress &rsaquo; instalācija' in content or
                        'WordPress &rsaquo; asennus' in content or
                        'WordPress &rsaquo; installationen' in content or
                        'WordPress &rsaquo; installatie' in content or
                        'WordPress &rsaquo; εγκατάσταση' in content or
                        'WordPress &rsaquo; inštalácia' in content or
                        'WordPress &rsaquo; инсталација' in content or
                        'WordPress &rsaquo; установка' in content or
                        'WordPress &rsaquo; התקשורת' in content or
                        'WordPress &rsaquo; التثبيت' in content or
                        'WordPress &rsaquo; instalacja' in content or
                        'WordPress &rsaquo; instalace' in content or
                        'WordPress &rsaquo; 配置文件' in content or
                        'WordPress &rsaquo; instalación' in content or
                        'WordPress &rsaquo; installatie' in content or
                        'WordPress &rsaquo; نصب' in content or
                        'WordPress &rsaquo; installation' in content or
                        'WordPress &rsaquo; instalacija' in content or
                        'WordPress &rsaquo; inštalace' in content or
                        'WordPress &rsaquo; Inštalácia' in content or
                        'WordPress &rsaquo; সেটআপ' in content):
                        
                        with open('vuln.txt', 'a') as f:
                            f.write(inj + ' \n')
                        self.results_queue.put(('vuln_install', inj))
                        self.kirim_telegram(f"[+] VULN WordPress Install Found:\n{inj}")
                        break
                        
                    # Check for WordPress Setup Configuration (EXACT sama seperti original)
                    elif ('WordPress &rsaquo; Setup Configuration File' in content or
                        'WordPress &rsaquo; Pengaturan File Konfigurasi' in content or
                        'Configuration de WordPress' in content or
                        'WordPress セットアップ設定ファイル' in content or
                        'WordPress 설정 구성 파일' in content or
                        'Archivo de configuración de WordPress' in content or
                        'Konfigurationsdatei von WordPress' in content or
                        'File di configurazione di WordPress' in content or
                        'Arquivo de configuração do WordPress' in content or
                        'Файл настройки WordPress' in content or
                        'WordPress 配置文件' in content or
                        'WordPress 設定ファイル' in content or
                        'WordPress تنظیم فایل پیکربندی' in content or
                        'Fichier de configuration WordPress' in content or
                        'Bestand met WordPress-configuratie' in content or
                        'WordPress konfigurasjonsfil' in content or
                        'Plik konfiguracyjny WordPress' in content or
                        'Ficheiro de configuração do WordPress' in content or
                        'Fichero de configuración de WordPress' in content or
                        'WordPress konfigurasjonsfil' in content or
                        'Dosya yapılandırması WordPress' in content or
                        'WordPress সেটআপ কনফিগারেশন ফাইল' in content or
                        'WordPress קונפיגורציית קובץ' in content or
                        'WordPress ملف التكوين' in content or
                        'WordPress কনফিগারেশন ফাইল' in content or
                        'WordPress कॉन्फ़िगरेशन फ़ाइल' in content or
                        'WordPress ಕಾನ್ಫಿಗರೇಶನ್ ಫೈಲ್' in content or
                        'WordPress കോൺഫിഗറേഷൻ ഫയൽ' in content or
                        'WordPress 設定ファイル' in content or
                        'WordPress ตั้งค่าการกำหนดค่าไฟล์' in content or
                        'WordPress設定ファイル' in content or
                        'WordPressตั้งค่าไฟล์' in content or
                        'WordPress konfiguracijos failas' in content or
                        'WordPress конфигурационен файл' in content or
                        'WordPress файл конфигурации' in content or
                        'WordPress सेटअप कॉन्फ़िगरेशन फ़ाइल' in content or
                        'WordPress設定ファイル' in content or
                        'WordPress opstillingskonfigurationsfil' in content or
                        'WordPress konfigurační soubor' in content or
                        'WordPress konfigurációs fájl' in content or
                        'WordPress конфігураційний файл' in content or
                        'WordPress setup-konfigurationsfil' in content or
                        'WordPress setup-konfigurationsfil' in content or
                        'WordPress setup-konfigurasjonsfil' in content or
                        'WordPress configuration file' in content):
                        
                        with open('vuln.txt', 'a') as f:
                            f.write(inj + '\n')
                        self.results_queue.put(('vuln_setup', inj))
                        self.kirim_telegram(f"[+] VULN WordPress Setup Found:\n{inj}")
                        break
                    else:
                        self.results_queue.put(('failed', inj))
                        
                except requests.exceptions.RequestException as e:
                    self.results_queue.put(('request_failed', f"{inj} - {str(e)}"))
                    
            self.results_queue.put(('complete', url))
            
        except Exception as e:
            self.results_queue.put(('error', f"{url} - {str(e)}"))
    
    def check_results(self):
        try:
            while True:
                result_type, message = self.results_queue.get_nowait()
                
                if result_type == 'vuln_install':
                    self.log_result(f" -| {message} --> [Successfully - Install Page]", "success")
                    self.vuln_count += 1
                elif result_type == 'vuln_setup':
                    self.log_result(f" -| {message} --> [Successfully - Setup Config]", "success")
                    self.vuln_count += 1
                elif result_type == 'failed':
                    self.log_result(f" -| {message} --> [Failed]", "failed")
                elif result_type == 'request_failed':
                    self.log_result(f" -| {message} --> [Request Failed]", "error")
                elif result_type == 'error':
                    self.log_result(f" -| {message} --> [Error]", "error")
                elif result_type == 'complete':
                    self.scanned_count += 1
                elif result_type == 'scan_finished':
                    self.scanning = False
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.progress.stop()
                    self.update_status(f"Scan completed! Found {self.vuln_count} vulnerabilities", '#00ff41')
                
                self.update_stats()
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_results)
    
    def start_scan(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select sites.txt file!")
            return
        
        try:
            # Load target sama seperti original logic
            with open(self.file_path.get(), 'r') as f:
                self.target = [i.strip() for i in f.readlines() if i.strip()]
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found. Please provide a valid file.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            return
        
        if not self.target:
            messagebox.showerror("Error", "No targets found in file!")
            return
        
        self.scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        self.scanned_count = 0
        self.vuln_count = 0
        self.update_stats()
        
        self.update_status("Scanning in progress...", '#ffff00')
        self.log_result(f"Starting scan with {len(self.target)} targets using 50 threads", "success")
        
        def scan_thread():
            try:
                # Start scanning with 50 threads (sama seperti original)
                mp = Pool(50)
                mp.map(self.exploit, self.target)
                mp.close()
                mp.join()
            except Exception as e:
                self.results_queue.put(('error', f"Scan error: {str(e)}"))
            finally:
                self.results_queue.put(('scan_finished', ''))
        
        thread = threading.Thread(target=scan_thread)
        thread.daemon = True
        thread.start()
    
    def stop_scan(self):
        self.scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.update_status("Scan stopped by user", '#ff4444')
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.scanned_count = 0
        self.vuln_count = 0
        self.update_stats()
        self.update_status("Results cleared", '#00ff41')

if __name__ == "__main__":
    root = tk.Tk()
    app = WordPressScanner(root)
    root.mainloop()
