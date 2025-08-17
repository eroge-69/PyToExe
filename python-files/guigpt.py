#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TGJU Gold 18K Fetcher – GUI Edition
@author: <your-name>
"""
import threading, re, time, datetime as dt, tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests, pandas as pd, jdatetime
from bs4 import BeautifulSoup

BASE = "https://english.tgju.org/profile/geram18"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ────────────   کرالینگ   ────────────
def _parse_table(soup):
    out = []
    for r in soup.find_all("tr"):
        tds = [c.get_text(strip=True).replace(',', '') for c in r.find_all("td")]
        if len(tds) >= 6 and re.match(r"\d{4}-\d{2}-\d{2}", tds[0]):
            gdate = dt.date.fromisoformat(tds[0])
            high, low = int(tds[1]), int(tds[2])
            avg = (high + low) // 2
            out.append((gdate, low, high, avg))
    return out

def fetch_range(j_start: jdatetime.date, j_end: jdatetime.date, status_cb):
    """
    Crawl TGJU History pages until we’re past j_end or before j_start.
    Returns DataFrame with PersianDate, Min, Max, Avg, Trend.
    """
    status_cb("دریافت داده‌ها ...")
    data, page = [], 1
    while True:
        url = f"{BASE}?p={page}"
        html = requests.get(url, headers=HEADERS, timeout=15).text
        chunk = _parse_table(BeautifulSoup(html, "html.parser"))
        if not chunk:
            break
        data.extend(chunk); page += 1
        last_g = chunk[-1][0]
        if last_g < j_start.togregorian():
            break
        time.sleep(0.8)      # polite delay

    # به DataFrame
    df = pd.DataFrame(data, columns=["GDate", "Min", "Max", "Avg"])
    df["PDate"] = [jdatetime.date.fromgregorian(date=d) for d in df["GDate"]]
    df = df[df["PDate"].between(j_start, j_end)]
    df.sort_values("PDate", inplace=True)

    # روند
    df["Trend"] = df["Avg"].diff().apply(
        lambda x: "صعودی" if x > 0 else ("نزولی" if x < 0 else "بدون تغییر"))
    df = df[["PDate", "Min", "Max", "Avg", "Trend"]]
    df.columns = ["تاریخ", "حداقل", "حداکثر", "میانگین", "روند"]
    status_cb("پایان دریافت")
    return df

# ────────────   GUI   ────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TGJU Gold 18K Downloader")
        self.geometry("420x220")
        self.resizable(False, False)

        f = ttk.Frame(self, padding=12); f.pack(fill="both", expand=True)
        ttk.Label(f, text="تاریخ شروع (مثال 1403-01-01):").grid(row=0, column=0, sticky="e")
        ttk.Label(f, text="تاریخ پایان  (مثال 1404-05-31):").grid(row=1, column=0, sticky="e")

        self.ent_start = ttk.Entry(f, width=18); self.ent_start.grid(row=0, column=1)
        self.ent_end   = ttk.Entry(f, width=18); self.ent_end.grid(row=1, column=1)

        self.path_var = tk.StringVar()
        ttk.Button(f, text="محل ذخیره...", command=self.browse).grid(row=2, column=0, pady=10)
        ttk.Entry(f, textvariable=self.path_var, width=30).grid(row=2, column=1, sticky="we")

        self.btn = ttk.Button(f, text="دریافت", command=self.run_fetch)
        self.btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.status = ttk.Label(f, foreground="blue"); self.status.grid(row=4, column=0, columnspan=2)

    def browse(self):
        p = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                         filetypes=[("Excel file", "*.xlsx")],
                                         title="محل ذخیرهٔ فایل")
        if p: self.path_var.set(p)

    def show_status(self, msg):
        self.status["text"] = msg
        self.update_idletasks()

    def run_fetch(self):
        try:
            js = jdatetime.date.fromisoformat(self.ent_start.get().strip())
            je = jdatetime.date.fromisoformat(self.ent_end.get().strip())
        except ValueError:
            messagebox.showerror("خطا", "فرمت تاریخ نادرست است!")
            return
        if je < js:
            messagebox.showerror("خطا", "تاریخ پایان باید بزرگ‌تر یا مساوی تاریخ شروع باشد.")
            return
        if not self.path_var.get():
            messagebox.showerror("خطا", "محل ذخیره را تعیین کنید.")
            return

        self.btn["state"] = "disabled"
        threading.Thread(target=self._worker, args=(js, je, self.path_var.get()), daemon=True).start()

    def _worker(self, jstart, jend, path):
        try:
            df = fetch_range(jstart, jend, self.show_status)
            df.to_excel(path, index=False)
            messagebox.showinfo("پایان", f"فایل با موفقیت ذخیره شد:\n{path}")
        except Exception as e:
            messagebox.showerror("خطا", str(e))
        finally:
            self.btn["state"] = "normal"
            self.show_status("")

if __name__ == "__main__":
    App().mainloop()