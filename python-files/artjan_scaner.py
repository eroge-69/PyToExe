import os
import hashlib
import threading
import json
from tkinter import *
from tkinter import messagebox, filedialog

VERSION = "1.1.0"
LICENSE_FILE = "license.json"

# Пример хешей вирусов (реально — нужна база)
MALICIOUS_HASHES = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # пустой файл (пример)
}

VALID_LICENSE_KEYS = {
    "PRO-6723-JHDJ-7349": True,
    "PRO-4243-GHDH-7437": True,
    "PRO-3467-JKDF-3798": True,
    "PRO-3748-HJFJ-7477": True,
    "PRO-7387-HFHJ-4757": True,
}

class ArtJanScanner:
    def __init__(self, root):
        self.root = root
        self.license_key = None
        self.is_pro = False
        self.infected_files = []
        self.checked_files = 0
        self.load_license()
        self.setup_ui()

    def setup_ui(self):
        self.root.title(f"ArtJan Anti-Miner {VERSION}")
        self.root.geometry("800x600")
        self.root.configure(bg="#e6e6e6")

        header = Frame(self.root, bg="#00a0e3", height=80)
        header.pack(fill=X)
        Label(header, text="ARTJAN", font=("Arial", 24, "bold"), fg="white", bg="#00a0e3").pack(side=LEFT, padx=20)

        main = Frame(self.root, bg="#e6e6e6")
        main.pack(fill=BOTH, expand=True, padx=20, pady=20)

        Label(main, text="Антивирусный сканер майнеров", font=("Arial", 16), bg="#e6e6e6").pack(pady=10)

        Button(main, text="Выбрать папку для сканирования", command=self.select_folder,
               bg="#007acc", fg="white", font=("Arial", 14)).pack(pady=5)

        self.scan_button = Button(main, text="Начать сканирование", command=self.start_scan,
               bg="#00a0e3", fg="white", font=("Arial", 14))
        self.scan_button.pack(pady=10)
        self.scan_button.config(state=DISABLED)

        self.buy_button = Button(main, text="Купить PRO версию (500₽)", bg="#28a745", fg="white",
                                 font=("Arial", 12, "bold"), command=self.open_buy_window)
        self.buy_button.pack(pady=5)

        self.status = Label(main, text="Готов к работе", font=("Arial", 12), bg="#e6e6e6")
        self.status.pack(pady=10)

        self.license_label = Label(main, text="", font=("Arial", 12), bg="#e6e6e6")
        self.license_label.pack(pady=5)

        self.results_box = Text(main, height=18, bg="#fff", state=DISABLED)
        self.results_box.pack(fill=BOTH, expand=True, pady=10)

        self.update_license_label()

    def update_license_label(self):
        if self.is_pro:
            self.license_label.config(text="Полная версия активирована ✅", fg="green")
            self.buy_button.config(state=DISABLED)
        else:
            self.license_label.config(text="Бесплатная версия (демо) ⚠️", fg="orange")
            self.buy_button.config(state=NORMAL)

    def load_license(self):
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, "r") as f:
                    data = json.load(f)
                    key = data.get("license_key", "")
                    if key in VALID_LICENSE_KEYS:
                        self.license_key = key
                        self.is_pro = True
            except:
                self.is_pro = False

    def save_license(self, key):
        with open(LICENSE_FILE, "w") as f:
            json.dump({"license_key": key}, f)
        self.license_key = key
        self.is_pro = True
        self.update_license_label()

    def open_buy_window(self):
        top = Toplevel(self.root)
        top.title("Активация PRO версии")
        top.geometry("450x300")
        
        Label(top, text="Введите лицензионный ключ:", font=("Arial", 12)).pack(pady=10)

        entry = Entry(top, width=30, font=("Arial", 14))
        entry.pack(pady=10)

        payment_info = (
            "Для покупки PRO переведите 500₽ на один из кошельков:\n\n"
            "USDT (TRC20): 0xf29Ca1253BEeD9bA8B0be2747357C3c738597Ef5\n"
            "BTC: bc1q2wt3hflnn856cxqr9va6a9eqhzyav9rgmlqgxm\n\n"
            "После оплаты введите полученный ключ."
        )
        Label(top, text=payment_info, font=("Arial", 10), justify=LEFT, fg="blue").pack(pady=5)

        def activate():
            key = entry.get().strip()
            if key in VALID_LICENSE_KEYS:
                self.save_license(key)
                messagebox.showinfo("Успех", "Полная версия активирована!")
                top.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный лицензионный ключ.")

        Button(top, text="Активировать", command=activate, bg="#28a745", fg="white", font=("Arial", 12)).pack(pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_to_scan = folder
            self.status.config(text=f"Выбрана папка: {folder}", fg="black")
            self.scan_button.config(state=NORMAL)

    def start_scan(self):
        self.infected_files.clear()
        self.checked_files = 0
        self.results_box.config(state=NORMAL)
        self.results_box.delete(1.0, END)
        self.results_box.config(state=DISABLED)
        self.scan_button.config(state=DISABLED)
        if self.is_pro:
            self.status.config(text="Полная проверка (PRO)...", fg="blue")
            threading.Thread(target=self.full_scan, daemon=True).start()
        else:
            self.status.config(text="Быстрая проверка (демо)...", fg="orange")
            threading.Thread(target=self.quick_scan, daemon=True).start()

    def quick_scan(self):
        count = 0
        for rootdir, _, files in os.walk(self.folder_to_scan):
            for file in files:
                if count >= 10:
                    break
                filepath = os.path.join(rootdir, file)
                if self.check_file_hash(filepath):
                    self.infected_files.append(filepath)
                self.checked_files += 1
                count += 1
                self.update_scan_progress(filepath)
            if count >= 10:
                break
        self.report_results()

    def full_scan(self):
        for rootdir, _, files in os.walk(self.folder_to_scan):
            for file in files:
                filepath = os.path.join(rootdir, file)
                if self.check_file_hash(filepath):
                    self.infected_files.append(filepath)
                self.checked_files += 1
                self.update_scan_progress(filepath)
        self.report_results()

    def check_file_hash(self, filepath):
        try:
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            return file_hash in MALICIOUS_HASHES
        except:
            return False

    def update_scan_progress(self, filepath):
        self.results_box.config(state=NORMAL)
        self.results_box.insert(END, f"[✓] Проверено: {filepath}\n")
        self.results_box.see(END)
        self.results_box.config(state=DISABLED)

    def report_results(self):
        self.results_box.config(state=NORMAL)
        self.results_box.insert(END, f"\nВсего проверено файлов: {self.checked_files}\n\n")
        if self.infected_files:
            self.status.config(text=f"Найдено угроз: {len(self.infected_files)}", fg="red")
            self.results_box.insert(END, "🔴 Обнаружены угрозы:\n")
            for f in self.infected_files:
                self.results_box.insert(END, f"{f}\n")
            if self.is_pro:
                for f in self.infected_files:
                    try:
                        os.remove(f)
                        self.results_box.insert(END, f"Удалено: {f}\n")
                    except Exception as e:
                        self.results_box.insert(END, f"Не удалось удалить: {f} ({e})\n")
        else:
            self.status.config(text="Угроз не обнаружено ✅", fg="green")
            self.results_box.insert(END, "✅ Проверка завершена, угроз не обнаружено.\n")
        self.results_box.config(state=DISABLED)
        self.scan_button.config(state=NORMAL)

if __name__ == "__main__":
    root = Tk()
    app = ArtJanScanner(root)
    root.mainloop()
