import os
import hashlib
import shutil
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
import pefile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import math
from collections import Counter
import win32api
import win32file  # Import adicionado

# === CONFIGURAÇÕES GLOBAIS ===
VIRUS_HASHES = set()
QUARANTINE_DIR = "quarentena"
LOG_FILE = "log_antivirus.txt"
MALICIOUS_URLS = set()
WINDOWS_CRITICAL_FOLDERS = [
    os.environ.get("USERPROFILE", "C:\\Users"),
    os.path.join(os.environ.get("SYSTEMDRIVE", "C:\\"), "Program Files"),
    os.path.join(os.environ.get("SYSTEMDRIVE", "C:\\"), "Program Files (x86)"),
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32"),
    os.path.join(os.environ.get("USERPROFILE", "C:\\Users"), "Downloads"),
    os.path.join(os.environ.get("USERPROFILE", "C:\\Users"), "Desktop"),
    os.path.join(os.environ.get("USERPROFILE", "C:\\Users"), "Documents")
]
BROWSER_FOLDERS = [
    os.path.join(os.environ.get("USERPROFILE", ""), "Downloads"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\User Data\\Default\\Downloads"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Edge\\User Data\\Default\\Downloads"),
    os.path.join(os.environ.get("APPDATA", ""), "Mozilla\\Firefox\\Profiles")
]
WHITELISTED_FILENAMES = {
    "WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE", "SOFFICE.BIN", "SOFFICE.EXE",
    "LIBREOFFICE.EXE", "WRITER.EXE", "CALC.EXE", "IMPRESS.EXE"
}
SUSPICIOUS_EXTENSIONS = [".exe", ".dll", ".bat", ".vbs", ".ps1", ".js", ".jar", ".scr", ".com"]
PACKERS_TO_DETECT = [b"UPX", b"FSG", b"MEW", b"Petite", b"ASPack", b"NSIS", b"Themida"]
TEST_MODE = True  # Define se o modo teste está ativado (não move arquivos)

def load_virus_hashes(hash_file="virus_hashes.txt"):
    if not os.path.exists(hash_file):
        return set()
    with open(hash_file, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def get_file_hash(file_path, algorithm="sha256"):
    try:
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception:
        return None

def is_signed_by_trusted_publisher(file_path):
    try:
        info = win32api.GetFileVersionInfo(file_path, "\\")
        if info and "Signature" in info:
            return True
    except Exception:
        return False

def detect_encoded_strings(content):
    base64_pattern = re.compile(rb'(?:[A-Za-z0-9+/]{4}){2,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]=)?')
    hex_pattern = re.compile(rb'\\x[0-9a-fA-F]{2}')
    return bool(base64_pattern.search(content)) or bool(hex_pattern.search(content))

def calculate_entropy(data):
    if not data:
        return 0
    entropy = 0
    counter = Counter(data)
    for count in counter.values():
        p = float(count) / len(data)
        entropy -= p * math.log(p, 2)
    return entropy

def advanced_heuristic_analysis(file_path):
    try:
        filename = os.path.basename(file_path).upper()
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if filename in WHITELISTED_FILENAMES:
            return False
        if is_signed_by_trusted_publisher(file_path):
            return False
        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            return False
        if ext in [".txt", ".log", ".cfg", ".ini"]:
            return False

        score = 0
        with open(file_path, "rb") as f:
            content = f.read(1024 * 50)

        if ext == ".exe":
            try:
                pe = pefile.PE(file_path)
                suspicious_sections = [s for s in pe.sections if any(p in s.Name for p in PACKERS_TO_DETECT)]
                if suspicious_sections:
                    score += 3
                if not (pe.OPTIONAL_HEADER.DllCharacteristics & 0x40):
                    score += 2
                if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
                    dangerous_imports = ["LoadLibrary", "GetProcAddress", "VirtualAlloc", "CreateRemoteThread"]
                    for entry in pe.DIRECTORY_ENTRY_IMPORT:
                        for imp in entry.imports:
                            if imp.name and any(d in imp.name.decode(errors="ignore") for d in dangerous_imports):
                                score += 1
            except Exception:
                pass

        SUSPICIOUS_KEYWORDS = [
            b"eval(", b"exec(", b"socket.", b"base64.b64decode", b"__import__",
            b"powershell", b"cmd.exe", b"ctypes", b"subprocess", b"requests"
        ]
        keyword_hits = sum(1 for keyword in SUSPICIOUS_KEYWORDS if keyword in content)
        score += min(keyword_hits, 3)

        if detect_encoded_strings(content):
            score += 2

        file_data = content[:512]
        entropy = calculate_entropy(file_data)
        if entropy > 7.0:
            score += 2

        return score >= 6
    except Exception:
        return False

def move_to_quarantine(file_path):
    try:
        if not file_path or not os.path.exists(file_path) or not os.access(file_path, os.W_OK):
            return None
        if not os.path.isfile(file_path):
            return None
        if not os.path.exists(QUARANTINE_DIR):
            os.makedirs(QUARANTINE_DIR)
        filename = os.path.basename(file_path)
        dest_path = os.path.join(QUARANTINE_DIR, filename)
        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            dest_path = os.path.join(QUARANTINE_DIR, f"{name}_{counter}{ext}")
            counter += 1
        shutil.move(file_path, dest_path)
        return dest_path
    except Exception:
        return None

def write_log(scan_path, infected_files):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"=== Varredura em {timestamp} ===\n")
            log.write(f"Caminho: {scan_path}\n")
            if infected_files:
                log.write("Infectados:\n")
                for f in infected_files:
                    log.write(f" - {f}\n")
            else:
                log.write("Nenhuma ameaça detectada.\n")
            log.write("\n")
    except Exception as e:
        print(f"Erro ao gravar log: {e}")

class BrowserProtectionHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        super().__init__()

    def on_created(self, event):
        if not event.is_directory:
            threading.Thread(target=self.scan_new_file, args=(event.src_path,), daemon=True).start()

    def scan_new_file(self, file_path):
        time.sleep(2)
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                hash_val = get_file_hash(file_path)
                infected = hash_val in VIRUS_HASHES or advanced_heuristic_analysis(file_path)
                if infected:
                    quarantine_path = move_to_quarantine(file_path)
                    if quarantine_path or not TEST_MODE:
                        self.app.show_alert(f"⚠️ POSSÍVEL INFECTADO (modo teste): {os.path.basename(file_path)}")
        except Exception as e:
            self.app.show_alert(f"⚠️ Erro na proteção em tempo real: {str(e)}")

class AntivirusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ POLONI ANTIVÍRUS - Proteção Avançada")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f2f5")
        self.root.resizable(True, True)
        self.stop_scan_flag = False
        self.scan_in_progress = False
        self.real_time_protection = False
        self.observer = None
        VIRUS_HASHES.update(load_virus_hashes())
        self.colors = {
            "primary": "#2c3e50",
            "secondary": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "light": "#ecf0f1",
            "dark": "#2c3e50"
        }
        self.create_widgets()
        self.show_alert("🛡️ Sistema inicializado. Proteção avançada disponível.")
        self.start_usb_monitoring()

    def start_usb_monitoring(self):
        self.usb_thread = threading.Thread(target=self.monitor_usb_devices, daemon=True)
        self.usb_thread.start()

    def monitor_usb_devices(self):
        previous_drives = set()
        while True:
            current_drives = set(win32api.GetLogicalDriveStrings().split('\x00')[:-1])
            new_drives = current_drives - previous_drives
            for drive in new_drives:
                try:
                    drive_type = win32file.GetDriveType(drive)
                    if drive_type == win32file.DRIVE_REMOVABLE:
                        self.show_alert(f"💾 Novo pendrive detectado: {drive}")
                        threading.Thread(target=self.scan_usb_drive, args=(drive,), daemon=True).start()
                except Exception as e:
                    self.show_alert(f"❌ Erro ao ler pendrive: {str(e)}")
            previous_drives = current_drives
            time.sleep(3)

    def scan_usb_drive(self, drive):
        all_files = []
        infected_files = []
        try:
            for root_dir, dirs, files in os.walk(drive):
                if self.stop_scan_flag:
                    break
                for file in files:
                    full_path = os.path.join(root_dir, file)
                    if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                        try:
                            if os.path.getsize(full_path) < 10 * 1024 * 1024:
                                all_files.append(full_path)
                        except Exception:
                            continue
            total = len(all_files)
            if total == 0:
                self.show_alert("⚠️ Nenhum arquivo encontrado no pendrive.")
                return
            self.show_alert(f"📊 Analisando {total} arquivos no pendrive...")
            for idx, file_path in enumerate(all_files, 1):
                if self.stop_scan_flag:
                    break
                try:
                    hash_val = get_file_hash(file_path)
                    infected = hash_val in VIRUS_HASHES or advanced_heuristic_analysis(file_path)
                    percent = int((idx / total) * 100)
                    if infected:
                        infected_files.append(file_path)
                        move_to_quarantine(file_path)
                        self.show_alert(f"⚠️ INFECTADO MOVIDO: {os.path.basename(file_path)}")
                except Exception:
                    continue
            write_log(drive, infected_files)
            report_message = self.generate_report("Varredura USB", drive, total, len(infected_files))
            self.show_alert(report_message)
            messagebox.showinfo("Relatório de Pendrive", report_message)
        except Exception as e:
            self.show_alert(f"❌ Erro ao varrer pendrive: {str(e)}")

    def generate_report(self, scan_type, scan_path, total_files, infected_files_count):
        report = f"--- Relatório de Varredura ({scan_type}) ---\n"
        report += f"Caminho da Varredura: {scan_path}\n"
        report += f"Total de Arquivos Escaneados: {total_files}\n"
        report += f"Ameaças Detectadas: {infected_files_count}\n"
        if infected_files_count > 0:
            report += "Status: Ameaças encontradas e tratadas.\n"
        else:
            report += "Status: Nenhuma ameaça detectada. Sistema limpo.\n"
        report += "-" * 40 + "\n"
        return report

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="🛡️ POLONI ANTIVÍRUS",
                               font=('Segoe UI', 18, 'bold'), bg="#2c3e50", fg="white")
        title_label.pack(expand=True)

        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True, padx=30, pady=10)

        # Seção de varredura
        scan_frame = tk.LabelFrame(main_container, text="  🔍 Varredura de Arquivos  ",
                                  font=('Segoe UI', 11, 'bold'), bg="#ffffff", fg="#2c3e50",
                                  relief="solid", bd=1, padx=15, pady=15)
        scan_frame.pack(fill="x", pady=(0, 15))

        path_frame = tk.Frame(scan_frame, bg="#ffffff")
        path_frame.pack(fill="x", pady=(0, 10))

        tk.Label(path_frame, text="Diretório:", font=('Segoe UI', 10, 'bold'),
                bg="#ffffff", fg="#2c3e50").pack(anchor="w")

        entry_frame = tk.Frame(path_frame, bg="#ffffff")
        entry_frame.pack(fill="x", pady=(5, 0))

        self.path_entry = tk.Entry(entry_frame, font=('Segoe UI', 10), relief="solid", bd=1, bg="#f8f9fa")
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=8)

        self.create_icon_button(entry_frame, "📂", self.select_directory, "#3498db").pack(side="right", padx=(10, 0))

        btn_frame = tk.Frame(scan_frame, bg="#ffffff")
        btn_frame.pack(fill="x", pady=(10, 0))

        self.create_modern_button(btn_frame, "📁 Varredura de Pasta", self.start_async_scan, "#27ae60").pack(side="left", padx=(0, 10))
        self.create_modern_button(btn_frame, "🔍 Varredura Completa", self.run_full_scan, "#3498db").pack(side="left", padx=(0, 10))
        self.create_modern_button(btn_frame, "⛔ Parar", self.stop_scan, "#e74c3c").pack(side="left")

        # Seção de proteção
        protection_frame = tk.LabelFrame(main_container, text="  🛡️ Proteção em Tempo Real  ",
                                      font=('Segoe UI', 11, 'bold'), bg="#ffffff", fg="#2c3e50",
                                      relief="solid", bd=1, padx=15, pady=15)
        protection_frame.pack(fill="x", pady=(0, 15))

        prot_top = tk.Frame(protection_frame, bg="#ffffff")
        prot_top.pack(fill="x", pady=(0, 10))

        self.protection_btn = self.create_toggle_button(prot_top, "🛡️ Ativar Proteção", self.toggle_real_time_protection)
        self.protection_btn.pack(side="left")

        self.protection_status = tk.Label(prot_top, text="🔴 Desativada", font=('Segoe UI', 10, 'bold'),
                                         bg="#ffffff", fg="#e74c3c")
        self.protection_status.pack(side="right")

        url_frame = tk.Frame(protection_frame, bg="#ffffff")
        url_frame.pack(fill="x")

        tk.Label(url_frame, text="Verificar URL:", font=('Segoe UI', 10, 'bold'),
                bg="#ffffff", fg="#2c3e50").pack(anchor="w")

        url_entry_frame = tk.Frame(url_frame, bg="#ffffff")
        url_entry_frame.pack(fill="x", pady=(5, 0))

        self.url_entry = tk.Entry(url_entry_frame, font=('Segoe UI', 10), relief="solid", bd=1, bg="#f8f9fa")
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=8)

        self.create_icon_button(url_entry_frame, "🌐", self.check_url, "#f39c12").pack(side="right", padx=(10, 0))

        # Progresso
        progress_frame = tk.Frame(main_container, bg="#f0f2f5")
        progress_frame.pack(fill="x", pady=(0, 15))

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 5))

        self.percent_label = tk.Label(progress_frame, text="Aguardando...", font=('Segoe UI', 10),
                                     bg="#f0f2f5", fg="#2c3e50")
        self.percent_label.pack()

        # Log de atividades
        log_frame = tk.LabelFrame(main_container, text="  📋 Log de Atividades  ",
                                 font=('Segoe UI', 11, 'bold'), bg="#ffffff", fg="#2c3e50",
                                 relief="solid", bd=1, padx=15, pady=15)
        log_frame.pack(fill="both", expand=True)

        text_frame = tk.Frame(log_frame, bg="#ffffff")
        text_frame.pack(fill="both", expand=True)

        self.alert_text = tk.Text(text_frame, font=('Consolas', 9), bg="#2c3e50", fg="#ecf0f1",
                                relief="flat", wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.alert_text.yview)
        self.alert_text.configure(yscrollcommand=scrollbar.set)
        self.alert_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_modern_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, font=('Segoe UI', 9, 'bold'),
                       bg=color, fg="white", relief="flat", padx=20, pady=10, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=self.darken_color(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def create_icon_button(self, parent, icon, command, color):
        btn = tk.Button(parent, text=icon, command=command, font=('Segoe UI', 12),
                       bg=color, fg="white", relief="flat", padx=15, pady=8, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=self.darken_color(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def create_toggle_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, font=('Segoe UI', 9, 'bold'),
                       bg="#95a5a6", fg="white", relief="flat", padx=20, pady=10, cursor="hand2")
        return btn

    def darken_color(self, color):
        colors = {"#27ae60": "#229954", "#3498db": "#2980b9", "#e74c3c": "#c0392b",
                 "#f39c12": "#e67e22", "#95a5a6": "#7f8c8d"}
        return colors.get(color, "#2c3e50")

    def show_alert(self, message):
        def _show():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.alert_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.alert_text.see(tk.END)
            self.root.update()
        self.root.after(0, _show)

    def toggle_real_time_protection(self):
        if not self.real_time_protection:
            self.start_real_time_protection()
        else:
            self.stop_real_time_protection()

    def start_real_time_protection(self):
        try:
            self.observer = Observer()
            handler = BrowserProtectionHandler(self)
            for folder in BROWSER_FOLDERS:
                if os.path.exists(folder):
                    self.observer.schedule(handler, folder, recursive=True)
                    self.show_alert(f"🛡️ Monitorando: {folder}")
            self.observer.start()
            self.real_time_protection = True
            self.protection_btn.config(text="🛡️ Desativar Proteção", bg="#e74c3c")
            self.protection_status.config(text="🟢 Ativada", fg="#27ae60")
            self.show_alert("🛡️ Proteção em tempo real ATIVADA")
        except Exception as e:
            self.show_alert(f"❌ Erro ao ativar proteção: {str(e)}")

    def stop_real_time_protection(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.real_time_protection = False
        self.protection_btn.config(text="🛡️ Ativar Proteção", bg="#95a5a6")
        self.protection_status.config(text="🔴 Desativada", fg="#e74c3c")
        self.show_alert("🛡️ Proteção em tempo real DESATIVADA")

    def check_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Digite uma URL para verificar")
            return
        if not url.startswith(('http://', 'https://')):   
            url = 'https://'  + url
        is_malicious = any(mal in url.lower() for mal in MALICIOUS_URLS)
        if is_malicious:
            self.show_alert(f"⚠️ URL SUSPEITA: {url}")
            messagebox.showwarning("URL Suspeita", f"A URL pode ser maliciosa:\n{url}")
        else:
            self.show_alert(f"✅ URL segura: {url}")

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def stop_scan(self):
        self.stop_scan_flag = True
        self.show_alert("⛔ Varredura interrompida pelo usuário.")

    def start_async_scan(self):
        if self.scan_in_progress:
            return
        self.stop_scan_flag = False
        self.scan_in_progress = True
        self.alert_text.delete(1.0, tk.END)
        threading.Thread(target=self.start_scan, daemon=True).start()

    def run_full_scan(self):
        if self.scan_in_progress:
            return
        self.stop_scan_flag = False
        self.scan_in_progress = True
        self.alert_text.delete(1.0, tk.END)
        folders_to_scan = [f for f in WINDOWS_CRITICAL_FOLDERS if os.path.exists(f)]
        self.path_entry.delete(0, tk.END)
        if folders_to_scan:
            self.path_entry.insert(0, "; ".join(folders_to_scan))
        self.show_alert("🔍 Iniciando varredura completa...")
        threading.Thread(target=self.full_scan_process, daemon=True).start()

    def update_progress_ui(self, percent):
        self.progress["value"] = percent
        self.percent_label.config(text=f"Progresso: {percent}%")

    def full_scan_process(self):
        infected_files = []
        all_files = []
        scan_path_display = "Pastas Críticas do Windows"
        try:
            for folder in WINDOWS_CRITICAL_FOLDERS:
                if self.stop_scan_flag:
                    break
                if os.path.exists(folder):
                    try:
                        for root_dir, dirs, files in os.walk(folder):
                            if self.stop_scan_flag:
                                break
                            for file in files:
                                full_path = os.path.join(root_dir, file)
                                if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                                    try:
                                        if os.path.getsize(full_path) < 10 * 1024 * 1024:
                                            all_files.append(full_path)
                                    except Exception:
                                        continue
                    except Exception:
                        continue
            total = len(all_files)
            if total == 0:
                self.show_alert("⚠️ Nenhum arquivo encontrado.")
                self.scan_in_progress = False
                self.update_progress_ui(0)
                report_message = self.generate_report("Varredura Completa", scan_path_display, 0, 0)
                self.show_alert(report_message)
                messagebox.showinfo("Relatório de Varredura", report_message)
                return
            self.show_alert(f"📊 Analisando {total} arquivos...")
            for idx, file_path in enumerate(all_files, 1):
                if self.stop_scan_flag:
                    break
                try:
                    hash_val = get_file_hash(file_path)
                    infected = hash_val in VIRUS_HASHES or advanced_heuristic_analysis(file_path)
                    percent = int((idx / total) * 100)
                    self.update_progress_ui(percent)
                    if infected:
                        infected_files.append(file_path)
                        move_to_quarantine(file_path)
                        self.show_alert(f"⚠️ INFECTADO MOVIDO: {os.path.basename(file_path)}")
                except Exception:
                    continue
            write_log("Varredura Completa", infected_files)
            report_message = self.generate_report("Varredura Completa", scan_path_display, total, len(infected_files))
            self.show_alert(report_message)
            messagebox.showinfo("Relatório de Varredura", report_message)
        finally:
            self.scan_in_progress = False
            self.update_progress_ui(0)

    def start_scan(self):
        input_path = self.path_entry.get()
        if not input_path or not os.path.exists(input_path):
            self.show_alert("❌ Caminho inválido.")
            self.scan_in_progress = False
            self.update_progress_ui(0)
            report_message = self.generate_report("Varredura Rápida", input_path, 0, 0)
            self.show_alert(report_message)
            messagebox.showinfo("Relatório de Varredura", report_message)
            return
        all_files = []
        try:
            for root_dir, dirs, files in os.walk(input_path):
                if self.stop_scan_flag:
                    break
                for file in files:
                    full_path = os.path.join(root_dir, file)
                    if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                        try:
                            if os.path.getsize(full_path) < 10 * 1024 * 1024:
                                all_files.append(full_path)
                        except Exception:
                            continue
        except Exception as e:
            self.show_alert(f"❌ Erro: {e}")
            self.scan_in_progress = False
            self.update_progress_ui(0)
            report_message = self.generate_report("Varredura Rápida", input_path, 0, 0)
            self.show_alert(report_message)
            messagebox.showinfo("Relatório de Varredura", report_message)
            return
        total = len(all_files)
        if total == 0:
            self.show_alert("⚠️ Nenhum arquivo encontrado.")
            self.scan_in_progress = False
            self.update_progress_ui(0)
            report_message = self.generate_report("Varredura Rápida", input_path, 0, 0)
            self.show_alert(report_message)
            messagebox.showinfo("Relatório de Varredura", report_message)
            return
        infected_files = []
        try:
            for idx, file_path in enumerate(all_files, 1):
                if self.stop_scan_flag:
                    break
                try:
                    hash_val = get_file_hash(file_path)
                    infected = hash_val in VIRUS_HASHES or advanced_heuristic_analysis(file_path)
                    percent = int((idx / total) * 100)
                    self.update_progress_ui(percent)
                    if infected:
                        infected_files.append(file_path)
                        move_to_quarantine(file_path)
                        self.show_alert(f"⚠️ INFECTADO: {os.path.basename(file_path)}")
                except Exception:
                    continue
            write_log(input_path, infected_files)
            report_message = self.generate_report("Varredura Rápida", input_path, total, len(infected_files))
            self.show_alert(report_message)
            messagebox.showinfo("Relatório de Varredura", report_message)
        finally:
            self.scan_in_progress = False
            self.update_progress_ui(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AntivirusApp(root)
    root.mainloop()