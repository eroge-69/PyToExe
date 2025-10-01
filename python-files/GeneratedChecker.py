import httpx, threading, queue, time
from urllib.parse import quote_plus
import customtkinter as ctk
from tkinter import filedialog, messagebox
import random, re

def random_user_agent():
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 14; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/128.0.6613.92 Mobile/15E148 Safari/604.1",
    ]
    return random.choice(uas)

def format_proxy(proxy):
    proxy = proxy.strip()
    if proxy.startswith(('http://','https://','socks')): return proxy
    elif '@' in proxy: return proxy
    elif proxy.count(':') == 3:
        ip, port, user, pwd = proxy.split(':'); return f'http://{user}:{pwd}@{ip}:{port}'
    elif proxy.count(':') == 1: return f'http://{proxy}'
    return proxy

def safe_split(combo, sep=":", maxsplit=1):
    parts = combo.split(sep, maxsplit)
    if len(parts) == 2: return parts
    return (combo, "")

class CheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PAIVPN Checker By CrackingTutrial Team")
        self.geometry("800x570")
        self.combos, self.proxies = [], []
        self.stats = {"hit":0,"fail":0,"retry":0,"expired":0,"free":0,"custom":0,"checked":0,"cpm":0}
        self.checked_times = []
        self.threads = 40
        self.stop_flag = threading.Event()
        self.proxy_on = ctk.BooleanVar(value=True)
        self.build_ui()
    def build_ui(self):
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("dark-blue")
        ctk.CTkLabel(self, text="PIAVPN Checker By CrackingTutorial", font=("Segoe UI Semibold", 22)).pack(pady=12)
        top = ctk.CTkFrame(self, fg_color="#1e1e1e"); top.pack(pady=8)
        ctk.CTkButton(top, text="Load Combos", command=self.load_combos).pack(side="left", padx=7, pady=7)
        ctk.CTkButton(top, text="Load Proxies", command=self.load_proxies).pack(side="left", padx=7, pady=7)
        ctk.CTkButton(top, text="Start", command=self.start_check).pack(side="left", padx=8, pady=7)
        ctk.CTkButton(top, text="Stop", command=self.stop_check).pack(side="left", padx=8, pady=7)
        ctk.CTkButton(top, text="Credits", command=self.show_credits).pack(side="left", padx=10, pady=7)
        self.output_box = ctk.CTkTextbox(self, width=730, height=270, font=("Consolas", 13))
        self.output_box.pack(pady=12)
        stats_bar = ctk.CTkFrame(self, fg_color="#1e1e1e")
        stats_bar.pack(pady=7)
        self.hit_lbl = ctk.CTkLabel(stats_bar, text="Hits: 0", text_color="#24e657", font=("Segoe UI Semibold", 16))
        self.fail_lbl = ctk.CTkLabel(stats_bar, text="Fails: 0", text_color="#f04747", font=("Segoe UI Semibold", 16))
        self.retry_lbl = ctk.CTkLabel(stats_bar, text="Retries: 0", text_color="#ffaa00", font=("Segoe UI Semibold", 16))
        self.expired_lbl = ctk.CTkLabel(stats_bar, text="Expired: 0", text_color="#ffff60", font=("Segoe UI Semibold", 16))
        self.free_lbl = ctk.CTkLabel(stats_bar, text="Free: 0", text_color="#3cb8e5", font=("Segoe UI Semibold", 16))
        self.cpm_lbl = ctk.CTkLabel(stats_bar, text="CPM: 0", text_color="#ffa500", font=("Segoe UI Semibold", 16))
        for w in [self.hit_lbl, self.fail_lbl, self.expired_lbl, self.free_lbl, self.retry_lbl, self.cpm_lbl]: w.pack(side="left", padx=14)
        self.after(1000, self.update_stats_loop)
    def update_stats_loop(self):
        self.hit_lbl.configure(text=f"Hits: {self.stats['hit']}")
        self.fail_lbl.configure(text=f"Fails: {self.stats['fail']}")
        self.retry_lbl.configure(text=f"Retries: {self.stats['retry']}")
        self.expired_lbl.configure(text=f"Expired: {self.stats['expired']}")
        self.free_lbl.configure(text=f"Free: {self.stats['free']}")
        self.cpm_lbl.configure(text=f"CPM: {self.stats['cpm']}")
        self.after(1000, self.update_stats_loop)
    def log(self, msg, color="white"):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", msg + "\n")
        self.output_box.see("end")
        self.output_box.configure(state="disabled")
    def load_combos(self):
        file = filedialog.askopenfilename(filetypes=[("Combo List", "*.txt"), ("All Files", "*.*")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                self.combos = [l.strip() for l in f if ":" in l]
    def load_proxies(self):
        file = filedialog.askopenfilename(filetypes=[("Proxy List", "*.txt"), ("All Files", "*.*")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                self.proxies = [l.strip() for l in f if l.strip()]
    def show_credits(self):
        messagebox.showinfo("Credits", "Made with Love ♥ by Yashvir Gaming\nTelegram: @therealyashvirgaming")
    def start_check(self):
        self.stop_flag.clear(); self.stats = dict(hit=0,fail=0,retry=0,expired=0,free=0,custom=0,checked=0,cpm=0); self.checked_times = []
        threading.Thread(target=self.run_checker, daemon=True).start()
    def stop_check(self):
        self.stop_flag.set()
    def run_checker(self):
        combo_q = queue.Queue()
        for combo in self.combos: combo_q.put(combo)
        proxy_q = queue.Queue()
        for p in self.proxies: proxy_q.put(p)
        threads = []
        def worker():
            while not self.stop_flag.is_set():
                try: combo = combo_q.get(timeout=2)
                except queue.Empty: break
                email, password = safe_split(combo)
                proxy_dict = None
                if self.proxy_on.get() and not proxy_q.empty():
                    proxy_raw = proxy_q.get()
                    proxy_url = format_proxy(proxy_raw)
                    proxy_dict = {"http://": proxy_url, "https://": proxy_url}
                    proxy_q.put(proxy_raw)
                result = self.check(email, password, proxy_dict)
                self.checked_times.append(time.time())
                if result["status"] in self.stats:
                    self.stats[result["status"]] += 1
                self.stats["checked"] += 1
                self.log(f"{email}:{password} | {result['status']} | {result.get('info','')}", color="green" if result["status"]=="success" else "red")
                # Write to file by status
                if result["status"]=="success":
                    with open("Success.txt","a",encoding="utf-8") as f: f.write(f"{email}:{password} | {result.get('info','')}\n")
                elif result["status"]=="expired":
                    with open("Expired.txt","a",encoding="utf-8") as f: f.write(f"{email}:{password} | {result.get('info','')}\n")
                elif result["status"]=="free":
                    with open("Free.txt","a",encoding="utf-8") as f: f.write(f"{email}:{password} | {result.get('info','')}\n")
                elif result["status"]=="custom":
                    with open("Custom.txt","a",encoding="utf-8") as f: f.write(f"{email}:{password} | {result.get('info','')}\n")
                self.checked_times = [t for t in self.checked_times if t > time.time()-60]
                self.stats["cpm"] = len(self.checked_times)
        for _ in range(self.threads):
            t = threading.Thread(target=worker, daemon=True); threads.append(t); t.start()
        for t in threads: t.join()
    def check(self, email, password, proxy_dict=None):
        try:
            return {"status":"fail"}
        except Exception as ex:
            print("Exception:", ex)
            return {"status":"retry"}

if __name__ == "__main__":
    app = CheckerApp()
    app.mainloop()