import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import tldextract
import threading
import time
import pyperclip
from PyFunceble import DomainAvailabilityChecker
import requests
import json
from datetime import datetime

# Parameters
SLEEP_TIME = 0.1
GAP_DAYS = 1095  # 3 years

class DomainCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Перевірка статусу доменів")

        self.extractor = tldextract.TLDExtract()
        self.checker = DomainAvailabilityChecker()
        self.pause_event = threading.Event()
        self.stop_flag = False
        self.snapshot_cache = {}

        self.domains = []
        self.all_results = []

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(top_frame, text="Завантажити CSV", command=self.load_csv).pack(side="left")
        tk.Button(top_frame, text="Почати перевірку", command=self.start_checking).pack(side="left", padx=5)
        self.pause_btn = tk.Button(top_frame, text="Пауза", command=self.toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=5)
        self.stop_btn = tk.Button(top_frame, text="Зупинити", command=self.stop_checking, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        tk.Button(top_frame, text="Скопіювати (3+ роки вік)", command=self.copy_filtered_available).pack(side="left", padx=5)
        tk.Button(top_frame, text="Зберегти у CSV", command=self.save_results).pack(side="left", padx=5)

        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=(0, 5))

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 10), expand=False)
        tk.Label(left_frame, text="Введіть домени (по одному на рядок):").pack(anchor="w")
        self.domain_text = tk.Text(left_frame, width=30)
        self.domain_text.pack(fill="y", expand=True)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        self.tree = ttk.Treeview(right_frame, columns=("domain", "status", "age"), show="headings")
        self.tree.heading("domain", text="Домен")
        self.tree.heading("status", text="Статус")
        self.tree.heading("age", text="Вік (роки)")
        self.tree.pack(fill="both", expand=True)

        self.log_var = tk.StringVar()
        self.log_label = tk.Label(self.root, textvariable=self.log_var, anchor="w", fg="gray")
        self.log_label.pack(fill="x", padx=10, pady=(0, 10))

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[["CSV files", "*.csv"]])
        if not file_path:
            return
        try:
            df = pd.read_csv(file_path, header=None)
            self.domains = df[0].dropna().astype(str).tolist()
            self.log_var.set(f"Завантажено {len(self.domains)} доменів.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати файл: {e}")

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_btn.config(text="Пауза")
            self.log_var.set("Продовжено перевірку")
        else:
            self.pause_event.set()
            self.pause_btn.config(text="Продовжити")
            self.log_var.set("Призупинено перевірку")

    def stop_checking(self):
        self.stop_flag = True
        self.pause_event.clear()
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.log_var.set("Перевірку зупинено користувачем.")

    def start_checking(self):
        manual_input = self.domain_text.get("1.0", tk.END).strip().splitlines()
        manual_domains = [d.strip() for d in manual_input if d.strip()]

        all_domains = manual_domains + self.domains
        if not all_domains:
            messagebox.showwarning("Увага", "Список доменів порожній. Завантажте CSV або введіть домени.")
            return

        self.tree.delete(*self.tree.get_children())
        self.all_results.clear()

        self.all_domains = all_domains
        self.pause_event.clear()
        self.stop_flag = False
        self.pause_btn.config(state="normal", text="Пауза")
        self.stop_btn.config(state="normal")
        self.progress["maximum"] = len(all_domains)
        self.progress["value"] = 0
        threading.Thread(target=self.check_domains_thread, daemon=True).start()

    def check_domains_thread(self):
        unique = set()
        for i, line in enumerate(self.all_domains, 1):
            while self.pause_event.is_set():
                time.sleep(0.1)

            if self.stop_flag:
                break

            extracted = self.extractor(line)
            domain = f"{extracted.domain}.{extracted.suffix}".lower()

            if not domain or domain in unique:
                continue
            unique.add(domain)

            self.log_var.set(f"Перевіряється {i}/{len(self.all_domains)}: {domain}")
            self.root.update_idletasks()

            try:
                self.checker.set_subject(domain)
                domain_details = self.checker.get_status()
                status = "Available" if domain_details.status == "INACTIVE" else "Taken"

                if status == "Available":
                    age_days, has_gap, has_snapshots = self.analyze_wayback(domain)
                    if has_snapshots and not has_gap:
                        age_years = round(age_days / 365.0, 1)
                        self.all_results.append((domain, status, age_years))
                        self.tree.insert("", "end", values=(domain, status, age_years))

            except Exception:
                continue

            self.progress["value"] = i
            time.sleep(SLEEP_TIME)

        available = len(self.all_results)
        self.log_var.set(f"Перевірку завершено. Доступні з історією без пробілів: {available}.")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    def copy_filtered_available(self):
        rows = [(self.tree.item(i)['values'][0], self.tree.item(i)['values'][2]) for i in self.tree.get_children()]
        domains = [domain for domain, age in rows if float(age) >= 3.0]
        pyperclip.copy("\n".join(domains))
        self.log_var.set(f"Скопійовано {len(domains)} доменів з віком >= 3 роки.")

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[["CSV files", "*.csv"]])
        if not file_path:
            return

        rows = [(self.tree.item(i)['values'][0], self.tree.item(i)['values'][1], self.tree.item(i)['values'][2]) for i in self.tree.get_children()]
        df = pd.DataFrame(rows, columns=["Domain", "Status", "AgeYears"])
        try:
            df.to_csv(file_path, index=False)
            self.log_var.set(f"Результати збережено у {file_path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")

    def get_snapshots(self, domain):
        if domain in self.snapshot_cache:
            return self.snapshot_cache[domain]
        try:
            cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp"
            response = requests.get(cdx_url, timeout=15)
            response.raise_for_status()
            data = json.loads(response.text)
            timestamps = sorted(list(set([row[0] for row in data[1:]])))
            self.snapshot_cache[domain] = timestamps
            return timestamps
        except:
            return []

    def check_history_length(self, timestamps):
        if not timestamps:
            return False, 0
        first = datetime.strptime(timestamps[0], "%Y%m%d%H%M%S")
        last = datetime.strptime(timestamps[-1], "%Y%m%d%H%M%S")
        delta = last - first
        return delta.days >= GAP_DAYS, delta.days

    def check_gaps(self, timestamps):
        if not timestamps:
            return True
        for i in range(len(timestamps) - 1):
            start = datetime.strptime(timestamps[i], "%Y%m%d%H%M%S")
            end = datetime.strptime(timestamps[i + 1], "%Y%m%d%H%M%S")
            if (end - start).days > GAP_DAYS:
                return True
        return False

    def analyze_wayback(self, domain):
        try:
            timestamps = self.get_snapshots(domain)
            if not timestamps:
                return 0, True, False
            has_enough, age = self.check_history_length(timestamps)
            has_gap = self.check_gaps(timestamps)
            return age, has_gap, True
        except:
            return 0, True, False

if __name__ == "__main__":
    root = tk.Tk()
    app = DomainCheckerGUI(root)
    root.mainloop()