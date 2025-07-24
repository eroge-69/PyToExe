
import os
import hashlib
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = "config_monitor.json"

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        config = {
            "project_folder": input("🟡 مسیر پوشه پروژه را وارد کنید: ").strip('" '),
            "database_folder": input("🔵 مسیر پوشه دیتابیس را وارد کنید: ").strip('" ')
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return config

def scan_database_files(database_folder):
    db_files = {}
    for root, _, files in os.walk(database_folder):
        for file in files:
            file_path = os.path.join(root, file)
            db_files[file] = get_file_hash(file_path)
    return db_files

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, database_files):
        self.database_files = database_files

    def on_created(self, event):
        if not event.is_directory:
            self.check_conflict(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.check_conflict(event.dest_path)

    def check_conflict(self, file_path):
        filename = os.path.basename(file_path)
        if filename in self.database_files:
            try:
                new_hash = get_file_hash(file_path)
                db_hash = self.database_files[filename]
                if new_hash != db_hash:
                    print(f"⚠️ تضاد نام با محتوای متفاوت برای فایل: {filename}")
                    print(f"   ↪ فایل پروژه: {file_path}")
            except Exception as e:
                print(f"❌ خطا در خواندن فایل {file_path}: {e}")

def main():
    print("🔍 در حال اجرای مانیتور زنده پوشه پروژه...")
    config = load_or_create_config()
    project_folder = config["project_folder"]
    database_folder = config["database_folder"]

    if not os.path.isdir(project_folder) or not os.path.isdir(database_folder):
        print("❌ مسیرها معتبر نیستند.")
        return

    db_files = scan_database_files(database_folder)
    event_handler = FileMonitorHandler(db_files)
    observer = Observer()
    observer.schedule(event_handler, path=project_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
