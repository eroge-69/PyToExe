#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meteogram Downloader GUI (old.meteo.pl)
--------------------------------------
- Wybór wielu ID (oddzielonych przecinkami)
- Zakres dat (YYYY-MM-DD do YYYY-MM-DD)
- Godzina modelu: 00 / 12 / obie
- "Tylko nowe" (nie nadpisuje istniejących plików)
- Wybór katalogu docelowego
- Pasek postępu + log w oknie + log do pliku
- Bezpieczne pobieranie w wątku roboczym (nie blokuje GUI)

Autor: ChatGPT (OpenAI)
Wersja: 1.0
"""

import os
import sys
import threading
import queue
import time
from datetime import datetime, timedelta

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception as e:
    print("Błąd importu Tkinter. Upewnij się, że masz Tkinter w Pythonie.", e)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Brak biblioteki 'requests'. Zainstaluj: pip install requests")
    sys.exit(1)

APP_TITLE = "Meteogram Downloader (old.meteo.pl)"
USER_AGENT = "meteogram-downloader-gui/1.0 Python-requests"
DEFAULT_TIMEOUT = 25
RETRY_COUNT = 3

class DownloaderThread(threading.Thread):
    def __init__(self, task_params, log_queue, progress_queue, stop_event):
        super().__init__(daemon=True)
        self.params = task_params
        self.log_q = log_queue
        self.prog_q = progress_queue
        self.stop_event = stop_event

    def log(self, msg):
        # Wysyła log do GUI
        self.log_q.put(msg)

    def set_progress(self, current, total):
        self.prog_q.put(("progress", current, total))

    def run(self):
        ids = [i.strip() for i in self.params["ids"].split(",") if i.strip()]
        from_date = self.params["from_date"]
        to_date = self.params["to_date"]
        hours_mode = self.params["hours_mode"]  # "00", "12", "both"
        out_dir = self.params["out_dir"]
        only_new = self.params["only_new"]

        try:
            start_dt = datetime.strptime(from_date, "%Y-%m-%d")
            end_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            self.log("BŁĄD: nieprawidłowy format daty. Użyj YYYY-MM-DD.")
            return

        if end_dt < start_dt:
            self.log("BŁĄD: Data 'Do' jest wcześniejsza niż 'Od'.")
            return

        # Godziny do pobierania
        hours = []
        if hours_mode == "00":
            hours = [0]
        elif hours_mode == "12":
            hours = [12]
        else:
            hours = [0, 12]

        # Oblicz łączną liczbę zadań
        total_tasks = 0
        tmp_dt = start_dt
        while tmp_dt <= end_dt:
            total_tasks += len(ids) * len(hours)
            tmp_dt += timedelta(days=1)

        if total_tasks == 0:
            self.log("Brak zadań do pobrania.")
            return

        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
        current_task = 0

        # Utwórz nadrzędny katalog
        os.makedirs(out_dir, exist_ok=True)
        log_file_path = os.path.join(out_dir, "meteogram_log.txt")
        try:
            log_file = open(log_file_path, "a", encoding="utf-8")
        except Exception:
            log_file = None

        def write_logfile(line):
            if log_file:
                try:
                    log_file.write(line + "\n")
                    log_file.flush()
                except Exception:
                    pass

        dt = start_dt
        while dt <= end_dt and not self.stop_event.is_set():
            date_str_file = dt.strftime("%Y%m%d")
            date_str_human = dt.strftime("%Y-%m-%d")
            for loc_id in ids:
                # Podkatalog per ID
                id_dir = os.path.join(out_dir, loc_id)
                os.makedirs(id_dir, exist_ok=True)

                for hour in hours:
                    current_task += 1
                    self.set_progress(current_task, total_tasks)

                    hour_str = f"{hour:02d}"
                    filename = f"{loc_id}_{date_str_file}{hour_str}.png"
                    url = f"https://old.meteo.pl/um/metco/{filename}"
                    dest_path = os.path.join(id_dir, filename)

                    if only_new and os.path.exists(dest_path):
                        msg = f"[SKIP] {date_str_human} {hour_str} UTC ID={loc_id} -> istnieje: {dest_path}"
                        self.log(msg)
                        write_logfile(msg)
                        continue

                    self.log(f"[GET ] {url}")
                    ok = False
                    for attempt in range(1, RETRY_COUNT + 1):
                        if self.stop_event.is_set():
                            break
                        try:
                            r = session.get(url, stream=True, timeout=DEFAULT_TIMEOUT)
                            if r.status_code == 404:
                                msg = f"[404 ] {url} (brak pliku)"
                                self.log(msg)
                                write_logfile(msg)
                                break
                            r.raise_for_status()
                            with open(dest_path, "wb") as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            msg = f"[SAVE] {dest_path}"
                            self.log(msg)
                            write_logfile(f"{msg} | URL: {url}")
                            ok = True
                            break
                        except Exception as e:
                            self.log(f"[ERR ] Próba {attempt}/{RETRY_COUNT} dla {url}: {e}")
                            time.sleep(1.0 * attempt)

                    if not ok and not self.stop_event.is_set():
                        write_logfile(f"[FAIL] {url}")

                    # mała przerwa z szacunku do serwera
                    time.sleep(0.3)

            dt += timedelta(days=1)

        if self.stop_event.is_set():
            self.log("Zatrzymano na żądanie użytkownika.")
        else:
            self.log("Zakończono pobieranie.")

        if log_file:
            log_file.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("780x540")
        self.minsize(740, 520)

        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = None

        self.create_widgets()
        self.after(100, self.poll_queues)

    def create_widgets(self):
        pad = {'padx': 8, 'pady': 6}

        frm = ttk.Frame(self)
        frm.pack(fill="x", **pad)

        # IDs
        ttk.Label(frm, text="ID lokalizacji (po przecinku):").grid(row=0, column=0, sticky="w")
        self.ids_var = tk.StringVar(value="2302")
        self.ids_entry = ttk.Entry(frm, textvariable=self.ids_var, width=50)
        self.ids_entry.grid(row=0, column=1, sticky="we", columnspan=3)
        frm.grid_columnconfigure(3, weight=1)

        # Dates
        ttk.Label(frm, text="Data od (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.from_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frm, textvariable=self.from_var, width=16).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Data do (YYYY-MM-DD):").grid(row=1, column=2, sticky="w")
        self.to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frm, textvariable=self.to_var, width=16).grid(row=1, column=3, sticky="w")

        # Hours
        ttk.Label(frm, text="Godzina modelu:").grid(row=2, column=0, sticky="w")
        self.hours_var = tk.StringVar()
        self.hours_combo = ttk.Combobox(frm, textvariable=self.hours_var, values=["00", "12", "both"], state="readonly", width=10)
        self.hours_combo.current(2)  # both jako domyślna
        self.hours_combo.grid(row=2, column=1, sticky="w")

        # Only new
        self.only_new_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Tylko nowe (nie nadpisuj)", variable=self.only_new_var).grid(row=2, column=2, sticky="w")

        # Output dir
        ttk.Label(frm, text="Katalog zapisu:").grid(row=3, column=0, sticky="w")
        self.out_var = tk.StringVar(value=os.path.join(os.path.abspath("."), "meteograms"))
        self.out_entry = ttk.Entry(frm, textvariable=self.out_var, width=50)
        self.out_entry.grid(row=3, column=1, sticky="we", columnspan=2)
        self.btn_browse = ttk.Button(frm, text="Wybierz…", command=self.choose_dir)
        self.btn_browse.grid(row=3, column=3, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", **pad)
        self.btn_start = ttk.Button(btn_frame, text="Pobierz meteogramy", command=self.start_download)
        self.btn_start.pack(side="left")
        self.btn_stop = ttk.Button(btn_frame, text="Zatrzymaj", command=self.stop_download, state="disabled")
        self.btn_stop.pack(side="left", padx=(8,0))

        # Progress
        prog_frame = ttk.Frame(self)
        prog_frame.pack(fill="x", **pad)
        self.progress = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        # Log
        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, **pad)
        self.log_text = tk.Text(log_frame, wrap="word", height=16)
        self.log_text.pack(fill="both", expand=True, side="left")
        yscroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        yscroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=yscroll.set)

        # Footer
        footer = ttk.Label(self, text="Uwaga: adresy obrazów są w formacie https://old.meteo.pl/um/metco/<ID>_<YYYYMMDD><HH>.png", foreground="#555")
        footer.pack(fill="x", padx=8, pady=(0,10))

    def choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.out_var.get(), title="Wybierz katalog docelowy")
        if d:
            self.out_var.set(d)

    def start_download(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("W trakcie", "Pobieranie już trwa.")
            return

        ids = self.ids_var.get().strip()
        if not ids:
            messagebox.showerror("Błąd", "Podaj co najmniej jedno ID.")
            return

        params = {
            "ids": ids,
            "from_date": self.from_var.get().strip(),
            "to_date": self.to_var.get().strip(),
            "hours_mode": self.hours_var.get().strip() or "both",
            "out_dir": self.out_var.get().strip(),
            "only_new": self.only_new_var.get()
        }

        # Reset UI
        self.log_text.delete("1.0", "end")
        self.progress["value"] = 0

        # Start worker
        self.stop_event.clear()
        self.worker_thread = DownloaderThread(params, self.log_queue, self.progress_queue, self.stop_event)
        self.worker_thread.start()
        self.btn_start["state"] = "disabled"
        self.btn_stop["state"] = "normal"

    def stop_download(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.stop_event.set()
            self.log("Zatrzymuję…")

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n")
        self.log_text.see("end")

    def poll_queues(self):
        # Log queue
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log(msg)
        except queue.Empty:
            pass

        # Progress queue
        try:
            while True:
                item = self.progress_queue.get_nowait()
                if item[0] == "progress":
                    cur, total = item[1], item[2]
                    if total > 0:
                        percent = int(cur * 100 / total)
                        self.progress["value"] = percent
        except queue.Empty:
            pass

        # Check worker end
        if self.worker_thread and not self.worker_thread.is_alive():
            self.btn_start["state"] = "normal"
            self.btn_stop["state"] = "disabled"

        self.after(100, self.poll_queues)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
