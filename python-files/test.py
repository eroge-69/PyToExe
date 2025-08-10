import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
import csv
import os
import threading
from datetime import datetime, timedelta
from collections import deque
import random
import subprocess
import sys

# Dependency check for PySocks, which is required by 'requests' for SOCKS support.
try:
    import socks
    PYSOCKS_INSTALLED = True
except ImportError:
    PYSOCKS_INSTALLED = False

class AdvancedEmailExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Email Extractor")
        self.root.geometry("1200x800")

        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 9))
        self.style.configure('TButton', font=('Arial', 9, 'bold'))
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        self.style.configure("Status.TFrame", background='#e0e0e0')
        self.style.configure("Status.TLabel", background='#e0e0e0', font=('Arial', 9))
        self.style.configure("Config.TFrame", background='#f7f7f7', relief='groove', borderwidth=1)
        self.style.configure("Config.TLabel", background='#f7f7f7')
        self.style.configure('Header.TLabel', background='#f0f0f0', font=('Arial', 10, 'bold'))


        self.running = False
        self.paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.lock = threading.Lock()
        self.url_queue = deque()
        self.task_item_map = {}
        self.unwanted_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
        
        # --- Proxy Manager Attributes ---
        self.good_proxies = [] # This will store the final list of good proxies
        self.proxies_to_check = [] # Temp list for proxies loaded into the manager
        self.active_proxies = []   # Temp list for proxies that pass the check
        self.is_checking_proxies = False
        self.proxies_checked_count = 0
        self.proxy_window = None 
        
        self.reset_metrics()
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        top_controls_frame = ttk.Frame(main_frame, padding=(0, 0, 0, 5))
        top_controls_frame.pack(fill=tk.X)
        self.control_button = ttk.Button(top_controls_frame, text="Start", command=self.start_extraction)
        self.control_button.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_button = ttk.Button(top_controls_frame, text="Stop", command=self.stop_extraction, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_controls_frame, text="Load URLs", command=self.load_urls).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_controls_frame, text="Proxy Manager", command=self.open_proxy_manager).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_controls_frame, text="Export as CSV", command=self.save_results).pack(side=tk.LEFT, padx=5)
        self._create_config_frame(main_frame)
        content_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_pane.pack(fill=tk.BOTH, expand=True)
        results_outer_frame = ttk.LabelFrame(content_pane, text="Found Items", padding="5")
        content_pane.add(results_outer_frame, weight=3)
        results_cols = ("#", "Item", "Url", "Title", "Type", "Country", "Depth")
        self.results_table = ttk.Treeview(results_outer_frame, columns=results_cols, show="headings")
        self.results_table.heading("#", text="#")
        self.results_table.heading("Item", text="Item")
        self.results_table.heading("Url", text="Url")
        self.results_table.heading("Title", text="Title")
        self.results_table.heading("Type", text="Type")
        self.results_table.heading("Country", text="Country")
        self.results_table.heading("Depth", text="Depth")
        self.results_table.column("#", width=50, anchor=tk.CENTER)
        self.results_table.column("Item", width=200)
        self.results_table.column("Url", width=250)
        self.results_table.column("Title", width=250)
        self.results_table.column("Type", width=80, anchor=tk.CENTER)
        self.results_table.column("Country", width=100, anchor=tk.CENTER)
        self.results_table.column("Depth", width=60, anchor=tk.CENTER)
        results_v_scroll = ttk.Scrollbar(results_outer_frame, orient=tk.VERTICAL, command=self.results_table.yview)
        results_h_scroll = ttk.Scrollbar(results_outer_frame, orient=tk.HORIZONTAL, command=self.results_table.xview)
        self.results_table.configure(yscroll=results_v_scroll.set, xscroll=results_h_scroll.set)
        results_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        results_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_table.pack(fill=tk.BOTH, expand=True)
        tasks_outer_frame = ttk.LabelFrame(content_pane, text="Active Tasks", padding="5")
        content_pane.add(tasks_outer_frame, weight=1)
        task_cols = ("Url", "Status")
        self.task_table = ttk.Treeview(tasks_outer_frame, columns=task_cols, show="headings")
        self.task_table.heading("Url", text="Url")
        self.task_table.heading("Status", text="Status")
        self.task_table.column("Url", width=250)
        self.task_table.column("Status", width=80, anchor=tk.CENTER)
        task_v_scroll = ttk.Scrollbar(tasks_outer_frame, orient=tk.VERTICAL, command=self.task_table.yview)
        self.task_table.configure(yscroll=task_v_scroll.set)
        task_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_table.pack(fill=tk.BOTH, expand=True)
        status_bar_frame = ttk.Frame(main_frame, style="Status.TFrame", padding=2)
        status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        self.parse_var = tk.StringVar(value="Ready")
        ttk.Label(status_bar_frame, textvariable=self.parse_var, style="Status.TLabel", anchor='w').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        separator = ttk.Separator(status_bar_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill='y', padx=5)
        self.time_var = tk.StringVar(value="Time: 00:00:00")
        ttk.Label(status_bar_frame, textvariable=self.time_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.queue_var = tk.StringVar(value="Queue: 0")
        ttk.Label(status_bar_frame, textvariable=self.queue_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.found_urls_var = tk.StringVar(value="Found Urls: 0")
        ttk.Label(status_bar_frame, textvariable=self.found_urls_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.processed_var = tk.StringVar(value="Processed: 0")
        ttk.Label(status_bar_frame, textvariable=self.processed_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.errors_var = tk.StringVar(value="Errors: 0")
        ttk.Label(status_bar_frame, textvariable=self.errors_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.found_items_var = tk.StringVar(value="Found Items: 0")
        ttk.Label(status_bar_frame, textvariable=self.found_items_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.filtered_var = tk.StringVar(value="Filtered: 0")
        ttk.Label(status_bar_frame, textvariable=self.filtered_var, style="Status.TLabel").pack(side=tk.LEFT, padx=5)

    def _create_config_frame(self, parent):
        config_frame = ttk.Frame(parent, padding=5, style="Config.TFrame")
        config_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(config_frame, text="SETTINGS:", font=('Arial', 9, 'bold'), style="Config.TLabel").pack(side=tk.LEFT, padx=(5,15))
        self.max_threads_var = tk.IntVar(value=50)
        ttk.Label(config_frame, text="Max Threads:", style="Config.TLabel").pack(side=tk.LEFT, padx=(5,0))
        ttk.Spinbox(config_frame, from_=1, to=200, textvariable=self.max_threads_var, width=5).pack(side=tk.LEFT, padx=(2,10))
        self.timeout_var = tk.IntVar(value=10)
        ttk.Label(config_frame, text="Timeout(s):", style="Config.TLabel").pack(side=tk.LEFT, padx=(5,0))
        ttk.Spinbox(config_frame, from_=3, to=60, textvariable=self.timeout_var, width=5).pack(side=tk.LEFT, padx=(2,10))
        self.max_depth_var = tk.IntVar(value=2)
        ttk.Label(config_frame, text="Crawl Depth:", style="Config.TLabel").pack(side=tk.LEFT, padx=(5,0))
        ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.max_depth_var, width=5).pack(side=tk.LEFT, padx=(2,10))
        self.max_pages_var = tk.IntVar(value=20)
        ttk.Label(config_frame, text="Pages per Site:", style="Config.TLabel").pack(side=tk.LEFT, padx=(5,0))
        ttk.Spinbox(config_frame, from_=1, to=1000, textvariable=self.max_pages_var, width=5).pack(side=tk.LEFT, padx=(2,10))
        self.use_proxies_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Use Proxies", variable=self.use_proxies_var, style="TCheckbutton").pack(side=tk.LEFT, padx=(15,0))

    def open_proxy_manager(self):
        if self.proxy_window and self.proxy_window.winfo_exists():
            self.proxy_window.lift()
            return
            
        self.proxy_window = tk.Toplevel(self.root)
        self.proxy_window.title("SOCKS Proxy Checker & Manager")
        self.proxy_window.geometry("650x500")
        self.proxy_window.transient(self.root)
        self.proxy_window.grab_set()

        main_frame = ttk.Frame(self.proxy_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        controls_frame = ttk.Frame(main_frame, padding="5", relief="groove", borderwidth=1)
        controls_frame.pack(fill=tk.X)

        self.proxy_load_btn = ttk.Button(controls_frame, text="Load Proxies (.txt)", command=self.load_proxies_from_file)
        self.proxy_load_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.proxy_type_var = tk.StringVar(value="socks5")
        ttk.Radiobutton(controls_frame, text="SOCKS5", variable=self.proxy_type_var, value="socks5").pack(side=tk.LEFT, padx=(10, 5), pady=5)
        ttk.Radiobutton(controls_frame, text="SOCKS4", variable=self.proxy_type_var, value="socks4").pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(controls_frame, text="Timeout(s):").pack(side=tk.LEFT, padx=(15, 2), pady=5)
        self.proxy_timeout_var = tk.IntVar(value=8)
        self.proxy_timeout_spinbox = ttk.Spinbox(controls_frame, from_=3, to=60, textvariable=self.proxy_timeout_var, width=5)
        self.proxy_timeout_spinbox.pack(side=tk.LEFT, pady=5)

        self.proxy_check_btn = ttk.Button(controls_frame, text="Check Proxies", command=self.start_proxy_check)
        self.proxy_check_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        log_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        log_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(log_frame, text="Results Log:", style='Header.TLabel').pack(anchor='w')
        self.proxy_log_area = scrolledtext.ScrolledText(log_frame, height=15, width=70, state=tk.DISABLED, font=("Courier New", 9))
        self.proxy_log_area.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        progress_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        progress_frame.pack(fill=tk.X)
        self.proxy_progress_var = tk.DoubleVar()
        self.proxy_progress_bar = ttk.Progressbar(progress_frame, variable=self.proxy_progress_var, orient=tk.HORIZONTAL, mode='determinate')
        self.proxy_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.proxy_progress_label_var = tk.StringVar(value="Checked: 0 / 0")
        ttk.Label(progress_frame, textvariable=self.proxy_progress_label_var).pack(side=tk.RIGHT, padx=(5, 0))
        
        action_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        action_frame.pack(fill=tk.X)
        self.proxy_save_btn = ttk.Button(action_frame, text="Save & Close", command=self.save_proxies_and_close)
        self.proxy_save_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        if not PYSOCKS_INSTALLED:
            self.root.after(100, self.prompt_for_install)

    def log_proxy_message(self, msg, tag=None):
        self.proxy_log_area.configure(state=tk.NORMAL)
        if tag:
            if tag not in self.proxy_log_area.tag_names():
                self.proxy_log_area.tag_config(tag, foreground="green" if tag == "LIVE" else "red")
            self.proxy_log_area.insert(tk.END, msg + "\n", tag)
        else:
            self.proxy_log_area.insert(tk.END, msg + "\n")
        self.proxy_log_area.configure(state=tk.DISABLED)
        self.proxy_log_area.see(tk.END)

    def load_proxies_from_file(self):
        if self.is_checking_proxies: return
        file_path = filedialog.askopenfilename(
            title="Select Proxy File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            parent=self.proxy_window
        )
        if not file_path: return
        
        try:
            with open(file_path, 'r') as f:
                self.proxies_to_check = [line.strip() for line in f if line.strip() and ':' in line]
            
            if not self.proxies_to_check:
                messagebox.showwarning("Empty File", "The selected file is empty or contains no valid proxies (ip:port).", parent=self.proxy_window)
                return

            self.log_proxy_message(f"--- Loaded {len(self.proxies_to_check)} proxies. Ready to check. ---")
            self.proxy_progress_label_var.set(f"Checked: 0 / {len(self.proxies_to_check)}")
            self.proxy_progress_var.set(0)
        except Exception as e:
            messagebox.showerror("File Read Error", f"Failed to load or read the file.\n\nError: {e}", parent=self.proxy_window)

    def start_proxy_check(self):
        if not PYSOCKS_INSTALLED:
            self.prompt_for_install()
            return
        if not self.proxies_to_check:
            messagebox.showwarning("No Proxies", "Please load a list of proxies from a file first.", parent=self.proxy_window)
            return
        if self.is_checking_proxies: return

        self.is_checking_proxies = True
        self.proxies_checked_count = 0
        self.active_proxies.clear()
        self.toggle_proxy_controls(False)
        
        mode = self.proxy_type_var.get()
        timeout = self.proxy_timeout_var.get()
        total_proxies = len(self.proxies_to_check)

        self.log_proxy_message(f"--- Starting check for {total_proxies} proxies (Mode: {mode.upper()}, Timeout: {timeout}s) ---")
        
        executor = ThreadPoolExecutor(max_workers=self.max_threads_var.get())
        for proxy in self.proxies_to_check:
            future = executor.submit(self.check_one_proxy, proxy, mode, timeout)
            future.add_done_callback(self.handle_proxy_check_result)
        executor.shutdown(wait=False)

    def check_one_proxy(self, proxy, mode, timeout):
        proxies = {"http": f"{mode}://{proxy}", "https": f"{mode}://{proxy}"}
        try:
            r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
            r.raise_for_status()
            return (proxy, "LIVE", f"[LIVE] {proxy} -> Success (Status: {r.status_code})")
        except requests.exceptions.ProxyError:
            return (proxy, "DEAD", f"[DEAD] {proxy} -> Proxy Error. Bad proxy or wrong SOCKS version.")
        except requests.exceptions.ConnectTimeout:
            return (proxy, "DEAD", f"[DEAD] {proxy} -> Connection Timed Out.")
        except requests.exceptions.RequestException as e:
            return (proxy, "DEAD", f"[DEAD] {proxy} -> Failed ({type(e).__name__})")
        except Exception as e:
            return (proxy, "DEAD", f"[DEAD] {proxy} -> An unexpected error occurred: {e}")

    def handle_proxy_check_result(self, future):
        try:
            proxy, status, message = future.result()
            self.root.after(0, self.update_proxy_ui_with_result, proxy, status, message)
        except Exception as e:
            self.root.after(0, self.log_proxy_message, f"Error processing result: {e}")

    def update_proxy_ui_with_result(self, proxy, status, message):
        self.proxies_checked_count += 1
        
        if status == "LIVE":
            self.active_proxies.append(proxy)
            self.log_proxy_message(message, "LIVE")
        else:
            self.log_proxy_message(message, "DEAD")

        total_proxies = len(self.proxies_to_check)
        self.proxy_progress_var.set((self.proxies_checked_count / total_proxies) * 100)
        self.proxy_progress_label_var.set(f"Checked: {self.proxies_checked_count} / {total_proxies}")

        if self.proxies_checked_count == total_proxies:
            self.on_proxy_check_complete()

    def on_proxy_check_complete(self):
        self.is_checking_proxies = False
        self.toggle_proxy_controls(True)
        self.log_proxy_message("---")
        self.log_proxy_message(f"--- Check Complete. Found {len(self.active_proxies)} LIVE proxies. ---", "LIVE")

    def toggle_proxy_controls(self, is_enabled):
        state = tk.NORMAL if is_enabled else tk.DISABLED
        try:
            if self.proxy_window and self.proxy_window.winfo_exists():
                self.proxy_load_btn.config(state=state)
                self.proxy_check_btn.config(state=state)
                self.proxy_save_btn.config(state=state)
                self.proxy_timeout_spinbox.config(state=state)
                for child in self.proxy_load_btn.master.winfo_children():
                    if isinstance(child, ttk.Radiobutton):
                        child.configure(state=state)
        except tk.TclError:
            pass

    def save_proxies_and_close(self):
        self.good_proxies.clear()
        for proxy_str in self.active_proxies:
            self.good_proxies.append((proxy_str, self.proxy_type_var.get()))
        
        if self.good_proxies:
            messagebox.showinfo("Proxies Saved", f"{len(self.good_proxies)} LIVE proxies have been saved for use.", parent=self.proxy_window)
        else:
            self.use_proxies_var.set(False)
            messagebox.showwarning("No Proxies Saved", "No LIVE proxies were found or saved. 'Use Proxies' option will be disabled.", parent=self.proxy_window)
        
        if self.proxy_window and self.proxy_window.winfo_exists():
            self.proxy_window.destroy()
            self.proxy_window = None

    def prompt_for_install(self):
        install = messagebox.askyesno(
            "Dependency Missing",
            "The 'PySocks' library is required to check SOCKS proxies.\n\n"
            "Would you like to attempt to install it automatically?",
            parent=self.proxy_window
        )
        if install:
            self.log_proxy_message("--- Attempting to install 'PySocks' via pip... ---")
            self.toggle_proxy_controls(False)
            threading.Thread(target=self._run_pip_install, daemon=True).start()

    def _run_pip_install(self):
        global PYSOCKS_INSTALLED
        try:
            command = [sys.executable, "-m", "pip", "install", "PySocks"]
            subprocess.run(command, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            PYSOCKS_INSTALLED = True
            self.root.after(0, self.on_install_success)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.root.after(0, self.on_install_failure, str(e))
    
    def on_install_success(self):
        messagebox.showinfo("Installation Successful", "'PySocks' has been installed. The proxy manager will now work correctly.", parent=self.proxy_window)
        self.log_proxy_message("--- 'PySocks' installed successfully. ---")
        self.toggle_proxy_controls(True)

    def on_install_failure(self, error_message):
        messagebox.showerror("Installation Failed", f"Could not install 'PySocks'.\nPlease run this command in your terminal:\n\npip install PySocks\n\nError: {error_message}", parent=self.proxy_window)
        self.log_proxy_message(f"--- 'PySocks' installation failed. Please install it manually. ---", "DEAD")
        self.toggle_proxy_controls(True)
        
    def reset_metrics(self):
        with self.lock:
            self.id_counter = 1
            self.processed_count = 0
            self.error_count = 0
            self.found_urls_count = 0
            self.filtered_count = 0
            self.start_time = None
            self.active_tasks_count = 0
            self.seen_emails = set()

    def start_extraction(self):
        if not self.url_queue:
            messagebox.showwarning("No Tasks", "Please load URLs first.")
            return
        if self.use_proxies_var.get() and not self.good_proxies:
            messagebox.showwarning("No Proxies", "Please add and check proxies in the Proxy Manager.")
            return
        self.running = True
        self.paused = False
        self.pause_event.set()
        self.toggle_controls(is_running=True)
        self.reset_metrics()
        self.results_table.delete(*self.results_table.get_children())
        self.task_table.delete(*self.task_table.get_children())
        self.task_item_map.clear()
        self.start_time = datetime.now()
        self.update_status_bar()
        self.update_timer()
        self.parse_var.set("Starting dispatcher...")
        self.executor = ThreadPoolExecutor(max_workers=self.max_threads_var.get())
        threading.Thread(target=self._task_dispatcher, daemon=True).start()
        
    def _task_dispatcher(self):
        self.parse_var.set("Running...")
        while self.url_queue and self.running:
            self.pause_event.wait()
            if not self.running: break
            url = self.url_queue.popleft()
            with self.lock:
                self.active_tasks_count += 1
            self.root.after(0, self.add_task_to_table, url)
            future = self.executor.submit(self.crawl_website, url, self.max_depth_var.get(), self.timeout_var.get(), self.max_pages_var.get(), self.use_proxies_var.get())
            future.add_done_callback(self.task_complete)
            self.root.after(10, self.update_status_bar)
        self.executor.shutdown(wait=True)
        if self.running:
            self.root.after(0, self.finish_extraction)
            
    def pause_extraction(self):
        if not self.running or self.paused: return
        self.paused = True
        self.pause_event.clear()
        self.parse_var.set("Paused...")
        self.control_button.config(text="Continue", command=self.continue_extraction)

    def continue_extraction(self):
        if not self.running or not self.paused: return
        self.paused = False
        self.pause_event.set()
        self.parse_var.set("Running...")
        self.control_button.config(text="Pause", command=self.pause_extraction)

    def finish_extraction(self):
        if not self.running: return
        self.running = False
        self.toggle_controls(is_running=False)
        self.parse_var.set(f"Extraction complete! Found {self.id_counter - 1} total items.")

    def stop_extraction(self):
        if not self.running: return
        self.running = False
        self.pause_event.set()
        self.parse_var.set("Stopping... finishing active tasks.")
        self.toggle_controls(is_running=False)

    def fetch_with_retries(self, session, url, timeout):
        """
        Attempts to fetch a URL. If proxies are enabled, it will rotate through
        the good_proxies list on failure. If all proxies fail, it will make
        one final attempt with a direct connection.
        """
        if self.use_proxies_var.get() and self.good_proxies:
            proxies_to_try = list(self.good_proxies)
            random.shuffle(proxies_to_try)

            for proxy_str, proxy_type in proxies_to_try:
                if not self.running: return None
                self.pause_event.wait()

                proxy_url = f"{proxy_type}://{proxy_str}"
                session.proxies = {'http': proxy_url, 'https': proxy_url}
                try:
                    response = session.get(url, timeout=timeout)
                    response.raise_for_status()
                    return response
                except requests.RequestException:
                    continue

        session.proxies = {}
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException:
            return None

    def crawl_website(self, start_url, max_depth, timeout_sec, max_pages, use_proxies):
        self.pause_event.wait()
        if not self.running: return "Stopped"
        
        self.root.after(0, self.update_task_status, start_url, "Processing")
        
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        if not re.match(r'https?://', start_url):
            start_url = 'https://' + start_url

        base_domain = urlparse(start_url).netloc
        country = self.get_country_from_tld(base_domain.split('.')[-1])
        urls_to_visit = deque([(start_url, 1)])
        visited_urls = {start_url}
        pages_processed_count = 0
            
        while urls_to_visit and self.running:
            self.pause_event.wait() 
            if not self.running: break
            if pages_processed_count >= max_pages: break
                
            current_url, depth = urls_to_visit.popleft()
                
            response = self.fetch_with_retries(session, current_url, timeout_sec)

            if not response:
                with self.lock: self.error_count += 1
                continue
            
            html_content = response.text
            pages_processed_count += 1
                    
            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue
                        
            soup = BeautifulSoup(html_content, 'html.parser')
            with self.lock: self.processed_count += 1
                    
            page_title = soup.title.string.strip() if soup.title else 'No Title'
            potential_emails = set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html_content))
            new_results = []
                    
            with self.lock:
                for email in potential_emails:
                    if not self.is_valid_email(email):
                        self.filtered_count += 1
                        continue
                    if (email.lower(), base_domain) not in self.seen_emails:
                        self.seen_emails.add((email.lower(), base_domain))
                        new_results.append({"id": self.id_counter, "email": email, "source_url": current_url, "title": page_title, "country": country, "depth": depth})
                        self.id_counter += 1
                                
            if new_results:
                self.root.after(0, self.update_results_table, new_results)
                        
            if depth < max_depth:
                page_links = set()
                for a_tag in soup.find_all('a', href=True):
                    link = urljoin(current_url, a_tag['href'])
                    parsed_link = urlparse(link)
                    if (parsed_link.netloc == base_domain and parsed_link.scheme in ['http', 'https'] and link not in visited_urls):
                        page_links.add(link)
                        visited_urls.add(link)
                with self.lock: self.found_urls_count += len(page_links)
                urls_to_visit.extend([(link, depth + 1) for link in page_links])

        self.root.after(0, self.update_task_status, start_url, "Complete")
        return "Complete"

    def is_valid_email(self, email):
        email_lower = email.lower()
        if any(email_lower.endswith(ext) for ext in self.unwanted_extensions):
            return False
        return bool(re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))

    def update_results_table(self, results):
        for res in results:
            self.results_table.insert("", tk.END, values=(res["id"], res["email"], res["source_url"], res["title"], "Email", res["country"], res["depth"]))

    def task_complete(self, future):
        with self.lock:
            self.active_tasks_count -= 1
        self.root.after(0, self.update_status_bar)

    def toggle_controls(self, is_running):
        state = tk.DISABLED if is_running else tk.NORMAL
        self.control_button.config(text="Pause" if is_running else "Start", command=self.pause_extraction if is_running else self.start_extraction)
        self.stop_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        config_frame = self.root.winfo_children()[0].winfo_children()[1]
        for child in config_frame.winfo_children():
            if isinstance(child, (ttk.Spinbox, ttk.Checkbutton, ttk.Radiobutton)):
                child.configure(state=state)
        for child in self.control_button.master.winfo_children():
            if isinstance(child, ttk.Button) and child not in [self.control_button, self.stop_button]:
                child.config(state=state)
        if not is_running:
            self.control_button.config(state=tk.NORMAL)
            self.paused = False

    def add_task_to_table(self, url):
        if not self.running: return
        item_id = self.task_table.insert("", tk.END, values=(url, "Queued"))
        self.task_item_map[url] = item_id

    def update_task_status(self, url, status):
        item_id = self.task_item_map.get(url)
        if item_id and self.task_table.exists(item_id):
            try:
                self.task_table.item(item_id, values=(url, status))
                if status in ["Complete", "Error", "Stopped"]:
                    self.root.after(2000, self.remove_task_from_table, item_id)
            except tk.TclError: pass

    def remove_task_from_table(self, item_id):
        try:
            if self.task_table.exists(item_id):
                self.task_table.delete(item_id)
        except tk.TclError: pass

    def update_status_bar(self):
        with self.lock:
            self.queue_var.set(f"Queue: {len(self.url_queue)}")
            self.found_items_var.set(f"Found Items: {self.id_counter - 1}")
            self.processed_var.set(f"Processed: {self.processed_count}")
            self.errors_var.set(f"Errors: {self.error_count}")
            self.found_urls_var.set(f"Found Urls: {self.found_urls_count}")
            self.filtered_var.set(f"Filtered: {self.filtered_count}")

    def update_timer(self):
        if self.running and not self.paused:
            elapsed = datetime.now() - self.start_time
            self.time_var.set(f"Time: {str(timedelta(seconds=int(elapsed.total_seconds())))}")
        if self.running:
            self.root.after(1000, self.update_timer)

    def load_urls(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path: return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.url_queue.clear()
                self.task_table.delete(*self.task_table.get_children())
                urls = [line.strip() for line in f if line.strip()]
                self.url_queue.extend(urls)
            self.parse_var.set(f"Loaded {len(self.url_queue)} URLs.")
            self.update_status_bar()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file: {e}")

    def save_results(self):
        items = self.results_table.get_children()
        if not items:
            messagebox.showwarning("No Results", "There is no data to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path: return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([self.results_table.heading(col)["text"] for col in self.results_table["columns"]])
                for item_id in items:
                    writer.writerow(self.results_table.item(item_id)["values"])
            self.parse_var.set(f"Successfully saved {len(items)} records.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}")

    def get_country_from_tld(self, tld):
        tld_map = {'de': 'Germany', 'at': 'Austria', 'ch': 'Switzerland', 'fr': 'France', 'it': 'Italy', 'es': 'Spain', 'uk': 'United Kingdom', 'us': 'USA', 'ca': 'Canada', 'au': 'Australia', 'jp': 'Japan', 'cn': 'China', 'in': 'India', 'ru': 'Russia', 'br': 'Brazil', 'nl': 'Netherlands', 'pl': 'Poland', 'be': 'Belgium', 'se': 'Sweden', 'no': 'Norway'}
        return tld_map.get(tld, tld.upper())

    def on_closing(self):
        self.running = False
        self.pause_event.set()
        if hasattr(self, 'executor') and self.executor:
            self.executor.shutdown(wait=False, cancel_futures=True)
        if self.proxy_window and self.proxy_window.winfo_exists():
            self.proxy_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedEmailExtractorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()