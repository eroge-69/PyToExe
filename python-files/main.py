import os
import threading
import time
import json
import hashlib
import boto3
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from boto3.s3.transfer import TransferConfig
import schedule

LOG_FILE = "backup_log.txt"
CONFIG_FILE = "config.txt"
MANIFEST_FILE = "backup_manifest.json"

def sha256_checksum(filename, block_size=65536):
    if os.path.getsize(filename) < 1 * 1024 * 1024:
        with open(filename, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    else:
        sha256 = hashlib.sha256()
        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()

class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 Инкрементальный бэкап с хэшами")
        self.root.geometry("800x760")
        self.root.resizable(False, False)
        self.backup_thread = None
        self.cancel_backup = False
        self.files_total = 0
        self.files_uploaded = 0
        self.uploaded_bytes = 0
        self.total_bytes = 0
        self.source_folder = None

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("Accent.TButton",
            font=("Segoe UI Variable", 11, "bold"),
            padding=10,
            foreground="white",
            background="#4CAF50",
            borderwidth=0,
            focusthickness=3,
            focuscolor="#4CAF50"
        )
        self.style.map("Accent.TButton",
            background=[("active", "#45A049"), ("pressed", "#388E3C")])

        self.style.configure("Danger.TButton",
            font=("Segoe UI Variable", 11, "bold"),
            padding=10,
            foreground="white",
            background="#E53935",
            borderwidth=0)
        self.style.map("Danger.TButton",
            background=[("active", "#D32F2F"), ("pressed", "#B71C1C")])

        self.style.configure("TProgressbar", thickness=25)
        self.root.configure(bg="#f0f2f5")

        self.build_ui()
        self.load_last_folder()
        self.load_manifest()
        self.setup_scheduler()

        self.s3 = boto3.client(
            's3',
            endpoint_url='https://io.activecloud.com',
            aws_access_key_id="LY39JQ10C71CD5KUYJ5M",
            aws_secret_access_key="hsc5F6sZNooaGxBCKdgAnGFhWrGcqO0q6VCdp4BS",
            region_name="us-east-1",
        )
        self.bucket_name = "invelum-backup"
        self.ensure_bucket()

    def build_ui(self):
        frame_top = Frame(self.root, bg="#f0f2f5")
        frame_top.pack(fill=X, padx=25, pady=15)

        self.label_title = Label(frame_top, text="🛠 Инкрементальный бэкап с SHA256", font=("Segoe UI Variable", 20, "bold"), bg="#f0f2f5", fg="#222")
        self.label_title.pack(anchor=W)

        self.label_desc = Label(frame_top, text="Выберите папку и сделайте бэкап, загружая только изменённые файлы.",
                                font=("Segoe UI Variable", 11), bg="#f0f2f5", fg="#555")
        self.label_desc.pack(anchor=W, pady=(2, 10))

        frame_select = Frame(frame_top, bg="#f0f2f5")
        frame_select.pack(fill=X, pady=(0, 15))

        self.select_btn = ttk.Button(frame_select, text="📁 Выбрать папку", command=self.choose_folder, style="Accent.TButton")
        self.select_btn.pack(side=LEFT)

        self.folder_label = Label(frame_select, text="Папка не выбрана", bg="#f0f2f5", fg="#888", font=("Segoe UI Variable", 10))
        self.folder_label.pack(side=LEFT, padx=15, fill=X, expand=True)

        frame_buttons = Frame(frame_top, bg="#f0f2f5")
        frame_buttons.pack(fill=X)

        self.start_btn = ttk.Button(frame_buttons, text="🚀 Запустить бэкап", command=self.start_backup_thread, style="Accent.TButton", width=25)
        self.start_btn.pack(side=LEFT, padx=(0,10))

        self.cancel_btn = ttk.Button(frame_buttons, text="✖ Отменить", command=self.cancel_backup_process, style="Danger.TButton", width=15)
        self.cancel_btn.pack(side=LEFT)
        self.cancel_btn.config(state=DISABLED)

        frame_progress_file = Frame(self.root, bg="#f0f2f5")
        frame_progress_file.pack(fill=X, padx=25, pady=(10,0))

        self.progress_file_label = Label(frame_progress_file, text="Текущий файл:", bg="#f0f2f5", fg="#333", font=("Segoe UI Variable", 11))
        self.progress_file_label.pack(anchor=W)

        self.progress_file = ttk.Progressbar(frame_progress_file, orient="horizontal", mode="determinate", length=650)
        self.progress_file.pack(pady=6)

        self.progress_file_percent = Label(frame_progress_file, text="0.00%", bg="#f0f2f5", fg="#333", font=("Segoe UI Variable", 10))
        self.progress_file_percent.pack(anchor=E)

        frame_progress_total = Frame(self.root, bg="#f0f2f5")
        frame_progress_total.pack(fill=X, padx=25, pady=(15, 0))

        self.progress_total_label = Label(frame_progress_total, text="Общий прогресс:", bg="#f0f2f5", fg="#333", font=("Segoe UI Variable", 11))
        self.progress_total_label.pack(anchor=W)

        self.progress_total = ttk.Progressbar(frame_progress_total, orient="horizontal", mode="determinate", length=650)
        self.progress_total.pack(pady=6)

        self.progress_total_percent = Label(frame_progress_total, text="0 / 0 файлов", bg="#f0f2f5", fg="#333", font=("Segoe UI Variable", 10))
        self.progress_total_percent.pack(anchor=E)

        frame_stats = Frame(self.root, bg="#f0f2f5")
        frame_stats.pack(fill=X, padx=25, pady=(10, 15))

        self.stats_label = Label(frame_stats, text="Статистика: —", bg="#f0f2f5", fg="#666", font=("Segoe UI Variable", 10, "italic"))
        self.stats_label.pack(anchor=W)

        frame_log = Frame(self.root, bg="#ffffff", bd=1, relief="sunken")
        frame_log.pack(fill=BOTH, expand=True, padx=25, pady=(0, 20))

        log_label = Label(frame_log, text="📋 Журнал операций", font=("Segoe UI Variable", 13, "bold"), bg="#ffffff")
        log_label.pack(anchor=W, padx=10, pady=(10,0))

        self.status = Text(frame_log, height=14, wrap=WORD, font=("Consolas", 10), bg="#f9f9f9", relief=SOLID, bd=0)
        self.status.pack(fill=BOTH, expand=True, padx=10, pady=(5,10))

        self.status.tag_config("info", foreground="#555")
        self.status.tag_config("success", foreground="#2e7d32")
        self.status.tag_config("error", foreground="#d32f2f")
        self.status.tag_config("warning", foreground="#fbc02d")
        self.status.tag_config("newfile", foreground="#0288d1")
        self.status.tag_config("modified", foreground="#ef6c00")

        self.status_menu = Menu(self.root, tearoff=0)
        self.status_menu.add_command(label="Копировать", command=self.copy_log)
        self.status_menu.add_command(label="Очистить", command=self.clear_log)
        self.status.bind("<Button-3>", self.show_log_menu)

    def copy_log(self):
        try:
            text = self.status.get("1.0", END)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Копировать", "Журнал скопирован в буфер обмена")
        except Exception:
            pass

    def clear_log(self):
        self.status.delete("1.0", END)

    def show_log_menu(self, event):
        self.status_menu.tk_popup(event.x_root, event.y_root)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder = folder
            self.folder_label.config(text=folder, fg="#222")
            self.log(f"📂 Выбрана папка: {folder}", tag="info")
            self.save_last_folder(folder)
        else:
            self.log("❗ Папка не выбрана.", tag="warning")

    def save_last_folder(self, path):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(path)
        except Exception as e:
            self.log(f"⚠️ Не удалось сохранить путь: {e}", tag="error")

    def load_last_folder(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    path = f.read().strip()
                    if os.path.exists(path):
                        self.source_folder = path
                        self.folder_label.config(text=path, fg="#222")
                        self.log(f"📂 Загружен путь последней папки: {path}", tag="info")
        except Exception as e:
            self.log(f"⚠️ Не удалось загрузить путь: {e}", tag="error")

    def log(self, message, tag="info"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] {message}"
        self.status.insert(END, full_msg + "\n", tag)
        self.status.see(END)
        self.root.update_idletasks()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")

    def load_manifest(self):
        try:
            if os.path.exists(MANIFEST_FILE):
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    self.manifest = json.load(f)
                    self.log(f"📁 Загружен манифест с {len(self.manifest)} файлов.", tag="info")
            else:
                self.manifest = {}
        except Exception as e:
            self.manifest = {}
            self.log(f"⚠️ Не удалось загрузить манифест: {e}", tag="error")

    def save_manifest(self):
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, ensure_ascii=False, indent=2)
                self.log(f"💾 Манифест сохранён ({len(self.manifest)} файлов).", tag="success")
        except Exception as e:
            self.log(f"⚠️ Ошибка сохранения манифеста: {e}", tag="error")

    def ensure_bucket(self):
        try:
            buckets = self.s3.list_buckets()
            if not any(b['Name'] == self.bucket_name for b in buckets.get('Buckets', [])):
                self.s3.create_bucket(Bucket=self.bucket_name)
                self.log(f"🗃 Создан бакет: {self.bucket_name}", tag="success")
            else:
                self.log(f"🗃 Бакет {self.bucket_name} существует.", tag="info")
        except Exception as e:
            self.log(f"⚠️ Ошибка при проверке бакета: {e}", tag="error")

    def file_needs_upload(self, file_path):
        rel_path = os.path.relpath(file_path, self.source_folder)
        stat = os.stat(file_path)
        size, mtime = stat.st_size, stat.st_mtime
        prev = self.manifest.get(rel_path)

        if not prev:
            self.log(f"✨ Новый файл: {rel_path}", tag="newfile")
            return True

        # Быстрая проверка без хэша
        if prev['size'] != size or abs(prev['mtime'] - mtime) > 1:
            if size < 5 * 1024 * 1024:
                current_hash = sha256_checksum(file_path)
                if current_hash != prev['sha256']:
                    self.log(f"🔄 Изменён файл: {rel_path}", tag="modified")
                    return True
            else:
                return True

        return False

    def start_backup_thread(self):
        if not self.source_folder:
            self.log("⚠️ Папка не выбрана. Пожалуйста, выберите папку перед началом.", tag="warning")
            return
        if self.backup_thread and self.backup_thread.is_alive():
            self.log("⚠️ Бэкап уже запущен.", tag="warning")
            return
        self.load_manifest()
        self.cancel_backup = False
        self.backup_thread = threading.Thread(target=self.backup_folder, daemon=True)
        self.backup_thread.start()
        self.start_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)

    def cancel_backup_process(self):
        if self.backup_thread and self.backup_thread.is_alive():
            self.cancel_backup = True
            self.log("⏹ Пользователь отменил бэкап.", tag="warning")
            self.cancel_btn.config(state=DISABLED)

    def sync_deletions(self):
        local_files = set()
        for root_dir, _, files in os.walk(self.source_folder):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root_dir, file), self.source_folder).replace('\\', '/')
                local_files.add(rel_path)
        manifest_files = set(self.manifest.keys())
        to_delete = manifest_files - local_files
        if not to_delete:
            self.log("🗑 Нет файлов для удаления в S3.", tag="info")
            return
        self.log(f"🗑 Файлов для удаления из S3: {len(to_delete)}", tag="warning")
        for key in to_delete:
            try:
                self.s3.delete_object(Bucket=self.bucket_name, Key=key)
                self.log(f"❌ Удалён файл из S3: {key}", tag="success")
                self.manifest.pop(key, None)
            except Exception as e:
                self.log(f"⚠️ Ошибка при удалении {key} из S3: {e}", tag="error")

    def upload_one(self, file_path):
        if self.cancel_backup:
            return None
        rel_path = os.path.relpath(file_path, self.source_folder).replace('\\', '/')
        filesize = os.path.getsize(file_path)

        try:
            if filesize < 1024 * 1024:  # до 1МБ — быстрее так
                with open(file_path, 'rb') as f:
                    self.s3.put_object(Bucket=self.bucket_name, Key=rel_path, Body=f.read())
            else:
                config = TransferConfig(
                    multipart_threshold=8 * 1024 * 1024,
                    multipart_chunksize=8 * 1024 * 1024,
                    max_concurrency=32,
                    use_threads=True,
                )
                self.s3.upload_file(file_path, self.bucket_name, rel_path, Config=config)

            stat = os.stat(file_path)
            self.manifest[rel_path] = {
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                # большие файлы можно хэшировать позже фоном
                "sha256": sha256_checksum(file_path) if filesize < 5 * 1024 * 1024 else ""
            }
            return (rel_path, filesize)

        except Exception as e:
            self.log(f"❌ Ошибка загрузки {rel_path}: {e}", tag="error")
            return None

    def backup_folder(self):
        self.files_uploaded = 0
        self.uploaded_bytes = 0
        self.total_bytes = 0
        self.files_total = 0
        self.progress_file["value"] = 0
        self.progress_file_percent.config(text="0.00%")
        self.progress_total["value"] = 0
        self.progress_total_percent.config(text="0 / 0 файлов")
        self.stats_label.config(text="Статистика: —")
        self.status.delete("1.0", END)

        files_to_upload = []
        file_sizes = {}
        for root_dir, _, files in os.walk(self.source_folder):
            for file in files:
                full_path = os.path.join(root_dir, file)
                if self.cancel_backup:
                    self.finish_backup()
                    return
                if self.file_needs_upload(full_path):
                    files_to_upload.append(full_path)
                    file_sizes[full_path] = os.path.getsize(full_path)

        self.files_total = len(files_to_upload)
        self.total_bytes = sum(file_sizes.values())
        self.log(f"📦 Файлов для загрузки: {self.files_total}", tag="info")
        self.progress_total_percent.config(text=f"0 / {self.files_total} файлов")

        if self.files_total == 0:
            self.log("✅ Все файлы актуальны, загрузка не требуется.", tag="success")
            self.finish_backup()
            return

        with ThreadPoolExecutor(max_workers=128) as executor:
            futures = [executor.submit(self.upload_one, f) for f in files_to_upload]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    rel_path, filesize = result
                    self.files_uploaded += 1
                    self.uploaded_bytes += filesize
                    total_percent = (self.files_uploaded / self.files_total) * 100
                    self.progress_total["value"] = total_percent
                    self.progress_total_percent.config(text=f"{self.files_uploaded} / {self.files_total} файлов")
                    self.stats_label.config(text=f"Загружено {self.files_uploaded} из {self.files_total} файлов, {self.uploaded_bytes / 1024 / 1024:.2f} МБ из {self.total_bytes / 1024 / 1024:.2f} МБ")
                    self.log(f"✅ Загружено: {rel_path}", tag="success")

        self.sync_deletions()
        self.save_manifest()
        self.finish_backup()

    def finish_backup(self):
        self.progress_total["value"] = 100
        self.progress_total_percent.config(text=f"{self.files_uploaded} / {self.files_total} файлов")
        self.start_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        self.progress_file_label.config(text="Текущий файл: —")

    def setup_scheduler(self):
        def scheduled_job():
            self.log("⏰ Запущено по расписанию.", tag="info")
            self.start_backup_thread()

        schedule.every().day.at("12:15").do(scheduled_job)
        threading.Thread(target=self.run_schedule_loop, daemon=True).start()

    def run_schedule_loop(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    root = Tk()
    app = BackupApp(root)
    root.mainloop()
