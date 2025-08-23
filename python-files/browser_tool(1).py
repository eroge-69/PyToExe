import tkinter as tk
from tkinter import messagebox, ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import time
import threading
import re
import logging
from datetime import datetime

class BrowserTool:
    def __init__(self, root):
        self.root = root
        self.root.title("GWP Browser Automation Tool")
        self.root.geometry("600x400")
        self.windows = []
        self.running = False
        
        # Configure logging
        logging.basicConfig(filename='browser_tool.log', level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Style configuration
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))
        
        # URL Entry
        ttk.Label(self.main_frame, text="URL:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.url_entry = ttk.Entry(self.main_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Paste Button
        self.paste_button = ttk.Button(self.main_frame, text="Paste URL", command=self.paste_url)
        self.paste_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Browser Selection
        ttk.Label(self.main_frame, text="Browser:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.browser_var = tk.StringVar(value="Chrome")
        browsers = ["Chrome", "Firefox"]
        self.browser_menu = ttk.OptionMenu(self.main_frame, self.browser_var, "Chrome", *browsers)
        self.browser_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Number of Windows
        ttk.Label(self.main_frame, text="Number of Windows (1-1000):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.windows_entry = ttk.Entry(self.main_frame, width=10)
        self.windows_entry.insert(0, "1")
        self.windows_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Runtime Entry
        ttk.Label(self.main_frame, text="Runtime (seconds):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.runtime_entry = ttk.Entry(self.main_frame, width=10)
        self.runtime_entry.insert(0, "60")
        self.runtime_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Start and Stop Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_browsers)
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_browsers, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.grid(row=5, column=0, columnspan=4, sticky="ew", pady=5)
        
        # Signature
        ttk.Label(self.main_frame, text="Built by GWP Automation", font=("Helvetica", 8, "italic")).grid(
            row=6, column=0, columnspan=4, pady=5)
        
        # Log initialization
        logging.info("Browser Tool initialized")
        
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()
        logging.info(message)
        
    def paste_url(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard)
            self.update_status("URL pasted successfully")
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty or inaccessible")
            self.update_status("Failed to paste URL")
            logging.error("Failed to paste URL: Clipboard empty or inaccessible")
    
    def validate_url(self, url):
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(url_pattern, url) is not None
    
    def get_driver(self):
        browser = self.browser_var.get()
        self.update_status(f"Initializing {browser} WebDriver...")
        try:
            if browser == "Chrome":
                options = webdriver.ChromeOptions()
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            else:  # Firefox
                options = webdriver.FirefoxOptions()
                return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        except Exception as e:
            self.update_status(f"Failed to initialize {browser} WebDriver")
            logging.error(f"Failed to initialize {browser} WebDriver: {str(e)}")
            raise
    
    def start_browsers(self):
        if self.running:
            messagebox.showwarning("Warning", "Tool is already running!")
            self.update_status("Operation aborted: Tool already running")
            return
        
        # Validate inputs
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            self.update_status("Operation aborted: No URL provided")
            logging.error("No URL provided")
            return
        if not self.validate_url(url):
            messagebox.showerror("Error", "Invalid URL format")
            self.update_status("Operation aborted: Invalid URL format")
            logging.error(f"Invalid URL format: {url}")
            return
        
        try:
            num_windows = int(self.windows_entry.get())
            if not 1 <= num_windows <= 1000:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of windows must be between 1 and 1000")
            self.update_status("Operation aborted: Invalid number of windows")
            logging.error(f"Invalid number of windows: {self.windows_entry.get()}")
            return
        
        try:
            runtime = float(self.runtime_entry.get())
            if runtime <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid runtime in seconds")
            self.update_status("Operation aborted: Invalid runtime")
            logging.error(f"Invalid runtime: {self.runtime_entry.get()}")
            return
        
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.update_status(f"Opening {num_windows} {self.browser_var.get()} windows...")
        
        # Start browser opening in a separate thread
        threading.Thread(target=self.open_browsers, args=(url, num_windows, runtime), daemon=True).start()
    
    def open_browsers(self, url, num_windows, runtime):
        try:
            start_time = time.time()
            for i in range(num_windows):
                if not self.running:
                    self.update_status("Operation stopped by user")
                    break
                driver = self.get_driver()
                driver.get(url)
                self.windows.append(driver)
                self.update_status(f"Opened window {i+1}/{num_windows}")
                time.sleep(0.1)  # Prevent system overload
                
            # Wait for runtime
            elapsed = time.time() - start_time
            remaining = max(0, runtime - elapsed)
            while remaining > 0 and self.running:
                self.update_status(f"Running... {int(remaining)} seconds remaining")
                time.sleep(1)
                remaining -= 1
            
            # Close all windows
            self.stop_browsers()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.update_status(f"Error: {str(e)}")
            logging.error(f"Error in open_browsers: {str(e)}")
            self.stop_browsers()
    
    def stop_browsers(self):
        self.running = False
        for driver in self.windows:
            try:
                driver.quit()
            except:
                pass
        self.windows = []
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.update_status("All windows closed")
        logging.info("All browser windows closed")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = BrowserTool(root)
    root.mainloop()