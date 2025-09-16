import pandas as pd
import requests
from requests.exceptions import RequestException
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import os
import validators
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from fake_useragent import UserAgent
from urllib.parse import urlparse
import threading
from datetime import datetime

class URLCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Checker")
        self.root.geometry("900x700")
        self.driver = None
        self.processed_urls = set()
        self.ua = UserAgent()
        self.use_remote = False
        self.debug_port = '9222'
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        self.file_label = ttk.Label(file_frame, text="No Excel file selected")
        self.file_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Select Excel File", command=self.select_file).pack(side=tk.LEFT, padx=5)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.toggle_pause, state='disabled')
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_processing, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(control_frame, text="Save Progress", command=self.save_progress, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Scoreboard-style status display
        self.scoreboard_frame = ttk.LabelFrame(main_frame, text="Processing Status", padding="5")
        self.scoreboard_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(self.scoreboard_frame, text="Status: Idle", font=("Arial", 12, "bold"))
        self.status_label.pack()
        
        self.summary_frame = ttk.Frame(self.scoreboard_frame)
        self.summary_frame.pack(fill=tk.X, pady=5)
        
        self.urls_processed_label = ttk.Label(self.summary_frame, text="URLs Processed: 0/0", font=("Arial", 10))
        self.urls_processed_label.pack(side=tk.LEFT, padx=5)
        self.working_urls_label = ttk.Label(self.summary_frame, text="Working URLs: 0", font=("Arial", 10))
        self.working_urls_label.pack(side=tk.LEFT, padx=5)
        self.search_results_label = ttk.Label(self.summary_frame, text="Search Results: 0", font=("Arial", 10))
        self.search_results_label.pack(side=tk.LEFT, padx=5)
        self.errors_label = ttk.Label(self.summary_frame, text="Errors: 0", font=("Arial", 10))
        self.errors_label.pack(side=tk.LEFT, padx=5)
        self.avg_time_label = ttk.Label(self.summary_frame, text="Avg Time/URL: 0.00s", font=("Arial", 10))
        self.avg_time_label.pack(side=tk.LEFT, padx=5)
        self.est_time_label = ttk.Label(self.summary_frame, text="Est. Time Left: 0.00 min", font=("Arial", 10))
        self.est_time_label.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # Log area
        self.log_area = scrolledtext.ScrolledText(main_frame, height=20, width=100, state='disabled')
        self.log_area.pack(pady=10, fill=tk.BOTH, expand=True)

        self.input_file = None
        self.df = None
        self.output_file = None

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update_idletasks()

    def get_timestamped_filename(self, base_filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(base_filename)
        return f"{base}_{timestamp}_output{ext}"

    def select_file(self):
        self.input_file = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if self.input_file:
            self.file_label.config(text=f"Selected: {os.path.basename(self.input_file)}")
            self.output_file = self.get_timestamped_filename(os.path.splitext(self.input_file)[0] + '.xlsx')
            self.log(f"Excel file selected: {self.input_file}")
            self.log(f"Output will be saved to: {self.output_file}")
            try:
                temp_df = pd.read_excel(self.input_file)
                self.log(f"File validation successful. Found {len(temp_df)} rows with columns: {list(temp_df.columns)}")
                if len(temp_df.columns) > 0 and 'url' not in [col.lower() for col in temp_df.columns]:
                    messagebox.showwarning("Warning", "Column 'url' not found. Please ensure your Excel file has a column named 'url'.")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading Excel file: {e}")
                self.log(f"Error reading Excel file during validation: {e}")
                self.input_file = None
                self.file_label.config(text="No Excel file selected")
        else:
            self.file_label.config(text="No Excel file selected")
            self.log("No file selected.")

    def setup_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument(f"user-agent={self.ua.random}")

        try:
            if self.use_remote:
                self.log(f"Connecting to Chrome at http://127.0.0.1:{self.debug_port}...")
                self.driver = webdriver.Remote(
                    command_executor=f'http://127.0.0.1:{self.debug_port}',
                    options=chrome_options
                )
                self.log("Connected to existing Chrome debugging session.")
            else:
                self.log("Setting up Chrome browser...")
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
                self.log("Chrome browser started successfully.")
        except Exception as e:
            self.log(f"Failed to connect to remote Chrome: {e}")
            self.log("Falling back to local Chrome instance...")
            try:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
                self.log("Local Chrome instance started successfully.")
            except Exception as e2:
                self.log(f"Error starting local Chrome: {e2}")
                messagebox.showerror("Browser Error", f"Failed to start Chrome browser: {e2}")
                return False
        return True

    def is_hotel_page(self, url):
        return "/hotel/" in url.lower() and "searchresults" not in url.lower()

    def check_url(self, url):
        if not validators.url(url):
            return 'Invalid URL format', url, False
        
        parsed = urlparse(url)
        url_hash = f"{parsed.netloc}{parsed.path}"
        if url_hash in self.processed_urls:
            self.log(f"Skipping duplicate: {url}")
            return 'Duplicate', url, False
        self.processed_urls.add(url_hash)
        
        try:
            start_time = time.time()
            self.log(f"Loading URL: {url}")
            self.driver.get(url)
            
            max_wait = 5
            poll_interval = 0.5
            elapsed = 0
            final_url = url
            while elapsed < max_wait:
                current = self.driver.current_url
                if "searchresults" in current.lower():
                    self.driver.execute_script("window.stop();")
                    self.log(f"Early stop: Detected searchresults in {elapsed}s")
                    final_url = current
                    break
                final_url = current
                time.sleep(poll_interval)
                elapsed += poll_interval
            
            headers = {'User-Agent': self.ua.random}
            response = requests.head(final_url, headers=headers, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                response = requests.get(final_url, headers=headers, allow_redirects=True, timeout=5)
            status = response.status_code if "searchresults" not in final_url.lower() else "URL Link not working"
            
            is_hotel = self.is_hotel_page(final_url)
            load_time = time.time() - start_time
            self.log(f"URL: {url} | Load Time: {load_time:.2f}s | Status: {status} | Final URL: {final_url} | Is Hotel Page: {is_hotel}")
            return status, final_url, is_hotel
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log(f"URL: {url} | {error_msg}")
            return error_msg, url, False

    def update_scoreboard(self, index, total_rows):
        avg_time_per_url = self.total_process_time / self.urls_processed if self.urls_processed > 0 else 0
        remaining_urls = total_rows - index
        estimated_time_min = (remaining_urls * avg_time_per_url) / 60
        working_urls = self.urls_processed - self.search_results_count
        
        self.urls_processed_label.config(text=f"URLs Processed: {index}/{total_rows}")
        self.working_urls_label.config(text=f"Working URLs: {working_urls}")
        self.search_results_label.config(text=f"Search Results: {self.search_results_count}")
        self.errors_label.config(text=f"Errors: {self.error_count}")
        self.avg_time_label.config(text=f"Avg Time/URL: {avg_time_per_url:.2f}s")
        self.est_time_label.config(text=f"Est. Time Left: {estimated_time_min:.2f} min")
        self.status_label.config(text=f"Status: {'Paused' if self.is_paused else 'Processing'}")
        self.progress['value'] = index
        self.root.update_idletasks()

    def save_progress(self):
        if self.df is not None and len(self.df) > 0:
            try:
                timestamped_output_file = self.get_timestamped_filename(os.path.splitext(self.input_file)[0] + '.xlsx')
                self.df.to_excel(timestamped_output_file, index=False)
                self.log(f"Progress saved to {timestamped_output_file}")
                messagebox.showinfo("Success", f"Progress saved to {timestamped_output_file}")
            except Exception as e:
                self.log(f"Error saving progress: {e}")
                messagebox.showerror("Error", f"Error saving progress: {e}")
        else:
            messagebox.showwarning("Warning", "No data to save.")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.config(text="Resume" if self.is_paused else "Pause")
        self.status_label.config(text=f"Status: {'Paused' if self.is_paused else 'Processing'}")
        self.log(f"{'Paused' if self.is_paused else 'Resumed'} processing")

    def stop_processing(self):
        self.should_stop = True
        self.status_label.config(text="Status: Stopping...")
        self.log("Stopping processing...")

    def process_urls(self):
        if not self.input_file:
            self.log("No Excel file selected. Please select a file.")
            self.status_label.config(text="Status: Idle")
            self.is_running = False
            self.start_button.config(state='normal')
            return

        try:
            self.log("Reading Excel file...")
            self.df = pd.read_excel(self.input_file)
            self.log(f"Excel file read successfully. Shape: {self.df.shape}")
        except Exception as e:
            self.log(f"Error reading Excel file: {e}")
            messagebox.showerror("Error", f"Error reading Excel file: {e}")
            self.status_label.config(text="Status: Error")
            self.is_running = False
            self.start_button.config(state='normal')
            return

        url_col = None
        for col in self.df.columns:
            if col.lower() == 'url':
                url_col = col
                break
        
        if url_col is None:
            self.log("Error: Expected 'url' column not found")
            messagebox.showerror("Error", "Expected 'url' column not found. Please ensure your Excel file has a column named 'url'.")
            self.status_label.config(text="Status: Error")
            self.is_running = False
            self.start_button.config(state='normal')
            return

        self.df['Final URL'] = ''
        self.df['Response Status'] = ''
        self.df['Is Hotel Page'] = ''
        self.df['Is Working URL'] = False

        total_rows = len(self.df)
        self.progress['maximum'] = total_rows
        self.log(f"Total URLs to process: {total_rows}")

        if not self.setup_browser():
            self.status_label.config(text="Status: Browser Error")
            self.is_running = False
            self.start_button.config(state='normal')
            return

        self.start_time = time.time()
        self.log(f"Processing started at: {time.ctime(self.start_time)}")
        self.search_results_count = 0
        self.urls_same_count = 0
        self.urls_changed_count = 0
        self.hotel_pages_count = 0
        self.error_count = 0
        self.total_process_time = 0
        self.urls_processed = 0
        self.working_urls_count = 0

        try:
            for index, row in self.df.iterrows():
                if self.should_stop:
                    self.log("Processing stopped by user")
                    break

                while self.is_paused:
                    time.sleep(0.1)
                    if self.should_stop:
                        self.log("Processing stopped while paused")
                        break
                if self.should_stop:
                    break

                url = str(row[url_col]).strip() if pd.notna(row[url_col]) else ''
                if not url:
                    self.df.at[index, 'Final URL'] = ''
                    self.df.at[index, 'Response Status'] = 'Invalid URL'
                    self.df.at[index, 'Is Hotel Page'] = False
                    self.df.at[index, 'Is Working URL'] = False
                    self.log(f"Row {index+1}: Empty URL")
                    self.error_count += 1
                    self.update_scoreboard(index+1, total_rows)
                    continue

                self.log(f"Processing URL #{index+1}/{total_rows}: {url}")
                url_start_time = time.time()
                status, final_url, is_hotel = self.check_url(url)
                url_process_time = time.time() - url_start_time
                self.total_process_time += url_process_time
                self.urls_processed += 1

                self.df.at[index, 'Final URL'] = final_url
                self.df.at[index, 'Response Status'] = status
                self.df.at[index, 'Is Hotel Page'] = is_hotel
                is_working = "searchresults" not in final_url.lower()
                self.df.at[index, 'Is Working URL'] = is_working

                if "searchresults" in final_url.lower():
                    self.search_results_count += 1
                    self.df.at[index, 'Response Status'] = 'URL Link not working'
                else:
                    self.working_urls_count += 1
                if url == final_url:
                    self.urls_same_count += 1
                else:
                    self.urls_changed_count += 1
                if is_hotel:
                    self.hotel_pages_count += 1
                if isinstance(status, str) and ("Error" in status or "Invalid" in status or "Duplicate" in status):
                    self.error_count += 1

                self.update_scoreboard(index+1, total_rows)
                time.sleep(random.uniform(1, 2))

            finish_time = time.time()
            total_duration = finish_time - self.start_time
            self.log(f"Processing finished at: {time.ctime(finish_time)}")
            self.log(f"Total running duration: {total_duration:.2f} seconds")
            self.log("\n=== Processing Summary ===")
            self.log(f"Total URLs: {total_rows}")
            self.log(f"Working URLs: {self.working_urls_count}")
            self.log(f"Search results found (URL Link not working): {self.search_results_count}")
            self.log(f"URLs unchanged (Same URL): {self.urls_same_count}")
            self.log(f"URLs changed: {self.urls_changed_count}")
            self.log(f"Hotel pages: {self.hotel_pages_count}")
            self.log(f"Errors: {self.error_count}")
            self.log(f"Average time per URL: {self.total_process_time / self.urls_processed:.2f}s" if self.urls_processed > 0 else "No URLs processed")
            self.log(f"Total file processing time: {total_duration/60:.2f} minutes")

            self.save_progress()
            self.status_label.config(text="Status: Completed")
        except Exception as e:
            self.log(f"Unexpected error during processing: {e}")
            messagebox.showerror("Error", f"Unexpected error during processing: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.log("Browser closed.")
            self.is_running = False
            self.start_button.config(state='normal')
            self.pause_button.config(state='disabled')
            self.stop_button.config(state='disabled')
            self.save_button.config(state='normal')

    def start_processing(self):
        if self.is_running:
            return
        if not self.input_file:
            messagebox.showwarning("Warning", "Please select an Excel file first.")
            return
        self.is_running = True
        self.should_stop = False
        self.is_paused = False
        self.start_button.config(state='disabled')
        self.pause_button.config(state='normal', text="Pause")
        self.stop_button.config(state='normal')
        self.save_button.config(state='normal')
        self.progress['value'] = 0
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')
        self.log("Starting URL processing...")
        threading.Thread(target=self.process_urls, daemon=True).start()

    def on_closing(self):
        if self.driver:
            try:
                self.driver.quit()
                self.log("Browser closed on exit.")
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = URLCheckerApp(root)
    root.mainloop()