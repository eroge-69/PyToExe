import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import time
import threading
import re

class BrowserTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Window Tool")
        self.windows = []
        self.running = False
        
        # URL Entry
        tk.Label(root, text="URL:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Paste Button
        self.paste_button = tk.Button(root, text="Paste URL", command=self.paste_url)
        self.paste_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Browser Selection
        tk.Label(root, text="Browser:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.browser_var = tk.StringVar(value="Chrome")
        browsers = ["Chrome", "Firefox"]
        self.browser_menu = tk.OptionMenu(root, self.browser_var, *browsers)
        self.browser_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Number of Windows
        tk.Label(root, text="Number of Windows (1-1000):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.windows_entry = tk.Entry(root, width=10)
        self.windows_entry.insert(0, "1")
        self.windows_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Runtime Entry
        tk.Label(root, text="Runtime (seconds):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.runtime_entry = tk.Entry(root, width=10)
        self.runtime_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Start and Stop Buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_browsers)
        self.start_button.grid(row=4, column=1, padx=5, pady=10)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_browsers, state="disabled")
        self.stop_button.grid(row=4, column=2, padx=5, pady=10)
        
    def paste_url(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard)
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty or inaccessible")
    
    def validate_url(self, url):
        # Basic URL validation
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
        if browser == "Chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-gpu")
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        else:  # Firefox
            options = webdriver.FirefoxOptions()
            return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    
    def start_browsers(self):
        if self.running:
            messagebox.showwarning("Warning", "Tool is already running!")
            return
        
        # Validate URL
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        if not self.validate_url(url):
            messagebox.showerror("Error", "Invalid URL format")
            return
        
        # Validate number of windows
        try:
            num_windows = int(self.windows_entry.get())
            if not 1 <= num_windows <= 1000:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of windows must be between 1 and 1000")
            return
        
        # Validate runtime
        try:
            runtime = float(self.runtime_entry.get())
            if runtime <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid runtime in seconds")
            return
        
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start browser opening in a separate thread
        threading.Thread(target=self.open_browsers, args=(url, num_windows, runtime), daemon=True).start()
    
    def open_browsers(self, url, num_windows, runtime):
        try:
            for _ in range(num_windows):
                if not self.running:
                    break
                driver = self.get_driver()
                driver.get(url)
                self.windows.append(driver)
                time.sleep(0.1)  # Small delay to prevent overwhelming the system
            
            # Wait for runtime
            time.sleep(runtime)
            
            # Close all windows
            self.stop_browsers()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
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
        
if __name__ == "__main__":
    root = tk.Tk()
    app = BrowserTool(root)
    root.mainloop()