import sys
import os
import platform
import subprocess
import socket
import shutil
import time
import tempfile
import logging
import webbrowser
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Optional: automatic driver management
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.utils import ChromeType
    WEBDRIVER_MANAGER = True
except Exception:
    WEBDRIVER_MANAGER = False

# --------------------------
# Logging (real-time to UI)
# --------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(message)s')

class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
    def emit(self, record):
        msg = self.format(record)
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, msg + '\n')
        self.widget.configure(state='disabled')
        self.widget.see(tk.END)
        self.widget.update()

# --------------------------
# New Tab Opening Utilities
# --------------------------
def open_new_tab_chrome(url="https://www.google.com"):
    """
    Opens a new tab in an existing Chrome window using webbrowser module.
    
    Args:
        url (str): The URL to open in the new tab
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        chrome_path = find_chrome_binary()
        
        if chrome_path:
            # Register Chrome browser
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            # Open new tab in existing window
            webbrowser.get('chrome').open_new_tab(url)
            logger.info(f"Opened new tab with URL: {url}")
            return True
        else:
            # Fallback: use default browser
            webbrowser.open_new_tab(url)
            logger.info(f"Opened new tab in default browser with URL: {url}")
            return True
            
    except Exception as e:
        logger.error(f"Error opening new tab: {e}")
        
        # Alternative method using subprocess
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run([chrome_path or "chrome", "--new-tab", url], check=True)
            elif system == "Darwin":
                subprocess.run(["open", "-a", "Google Chrome", url], check=True)
            elif system == "Linux":
                subprocess.run(["google-chrome", "--new-tab", url], check=True)
            logger.info(f"Opened new tab using subprocess with URL: {url}")
            return True
        except Exception as e2:
            logger.error(f"Both methods failed: {e2}")
            return False

def check_existing_chrome_instance():
    """
    Check if Chrome is already running with remote debugging enabled.
    
    Returns:
        int or None: Port number if found, None otherwise
    """
    try:
        # Common debugging ports to check
        common_ports = [9222, 9223, 9224, 9225]
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:  # Port is open
                    logger.info(f"Found existing Chrome debugging session on port {port}")
                    return port
            except:
                continue
        
        return None
    except Exception as e:
        logger.warning(f"Error checking for existing Chrome instances: {e}")
        return None

# --------------------------
# Original Utilities (Enhanced)
# --------------------------
def get_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def is_executable(p):
    return p and os.path.exists(p) and os.access(p, os.X_OK)

def which(cmd):
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for p in paths:
        candidate = os.path.join(p, cmd)
        if is_executable(candidate):
            return candidate
    return None

def find_chrome_binary():
    for env_key in ["CHROME", "GOOGLE_CHROME", "CHROME_PATH", "GOOGLE_CHROME_PATH"]:
        p = os.environ.get(env_key)
        if p and is_executable(p):
            return p
    system = platform.system().lower()
    if system == "windows":
        try:
            import winreg
            keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            ]
            for root, subkey in keys:
                try:
                    with winreg.OpenKey(root, subkey) as k:
                        val, _ = winreg.QueryValueEx(k, None)
                        if is_executable(val):
                            return val
                except OSError:
                    continue
        except Exception:
            pass
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        for p in candidates:
            if is_executable(p):
                return p
        return which("chrome.exe")
    elif system == "darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
        for p in candidates:
            if is_executable(p):
                return p
        return which("google-chrome")
    else:
        for cmd in ["google-chrome", "google-chrome-stable", "chrome"]:
            path_hit = which(cmd)
            if path_hit:
                return path_hit
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/google-chrome",
        ]
        for p in candidates:
            if is_executable(p):
                return p
    return None

def get_chrome_version(chrome_path):
    try:
        out = subprocess.check_output([chrome_path, "--version"], stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except Exception:
        return ""

def looks_like_chromium_version_string(ver_str):
    return "chromium" in ver_str.lower()

def start_google_chrome_debug(chrome_path, user_data_dir, port):
    args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-first-run-ui",
        "--start-maximized",
    ]
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

def setup_chrome():
    """
    Connect to existing Chrome instance only. Chrome must be running with remote debugging.
    
    Returns:
        tuple: (driver, None, None) - no profile_dir or chrome_proc since we don't create new instance
    """
    logger.info("Looking for existing Chrome instance...")
    
    debug_port = check_existing_chrome_instance()
    
    if debug_port is None:
        raise RuntimeError(
            "No existing Chrome instance found with remote debugging enabled.\n"
            "Please start Chrome manually with: chrome --remote-debugging-port=9222"
        )
    
    logger.info(f"Found existing Chrome instance on port {debug_port}")
    
    opts = ChromeOptions()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    
    if WEBDRIVER_MANAGER:
        service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
    else:
        service = ChromeService()
    
    try:
        driver = webdriver.Chrome(service=service, options=opts)
        driver.implicitly_wait(5)
        logger.info("Successfully connected to existing Chrome instance")
        return driver, None, None
    except Exception as e:
        logger.error(f"Failed to connect to Chrome: {e}")
        raise RuntimeError(
            f"Could not connect to Chrome on port {debug_port}.\n"
            "Make sure Chrome is running with remote debugging enabled."
        )

# --------------------------
# Enhanced Scraper
# --------------------------
def run_scraper(path, url, open_in_new_tab=True, use_existing_chrome=True):
    logger.info(f"Reading file: {path}")
    try:
        df = pd.read_excel(path, engine="openpyxl")
    except Exception as e:
        logger.error(f"Cannot read file: {e}")
        messagebox.showerror("Error", f"Cannot read file: {e}")
        return
    if df.empty:
        messagebox.showerror("Error", "Excel file is empty")
        return

    id_col = df.columns[0]
    if "hasDeath" not in df: df["hasDeath"] = ""

    # Open URL in new tab if requested
    if open_in_new_tab:
        logger.info("Opening URL in new Chrome tab...")
        if not open_new_tab_chrome(url):
            logger.warning("Failed to open new tab, will navigate in scraping session")
            open_in_new_tab = False
        else:
            time.sleep(2)  # Give time for tab to load

    driver, profile_dir, chrome_proc = None, None, None
    try:
        # Setup Chrome connection
        driver, profile_dir, chrome_proc = setup_chrome()
        
        # If we successfully opened a new tab, we need to switch to it
        if open_in_new_tab and len(driver.window_handles) > 1:
            logger.info("Switching to new tab...")
            driver.switch_to.window(driver.window_handles[-1])  # Switch to last opened tab
        
        # Navigate to URL (either in new tab or current window)
        if not open_in_new_tab or driver.current_url != url:
            driver.get(url)
        
        wait = WebDriverWait(driver, 10)

        for idx, row in df.iterrows():
            eid = str(row[id_col]).strip()
            if not eid or eid.lower() == "nan":
                continue
            logger.info(f"Processing ID: {eid}")
            try:
                # Step 1: enter ID
                box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id*="text_eartag"]')))
                box.clear()
                box.send_keys(eid)

                # Step 2: click search
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id*="button_search"]')))
                btn.click()

                # Step 3: DOB & Gender
                dob = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[id*="value_date_of_birth"]'))).text
                gender = driver.find_element(By.CSS_SELECTOR, 'span[id*="value_sex"]').text
                df.at[idx, "DOB"] = dob
                df.at[idx, "Gender"] = gender

                # Step 4: Holding info
                holding_name = driver.find_element(By.CSS_SELECTOR, 'span[id*="value_countyHoldingName"]').text
                holding_id = driver.find_element(By.CSS_SELECTOR, 'span[id*="value_countyHoldingId"]').text
                holding = f"{holding_name},{holding_id}"

                # Step 5: Movements (row-based instead of spans)
                rows = driver.find_elements(By.CSS_SELECTOR, 'table.dataTableEx tbody tr')
                for i, row_el in enumerate(rows):
                    try:
                        cells = row_el.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 5:
                            holding_id = cells[0].find_element(By.CSS_SELECTOR, "span[id*='value_countyHoldingId']").text
                            holding_name = cells[0].find_element(By.CSS_SELECTOR, "span[id*='value_countyHoldingName']").text
                            movement_on = cells[1].text
                            movement_on_date = cells[2].text
                            movement_off = cells[3].text
                            movement_off_date = cells[4].text

                            # Store into Excel
                            df.at[idx, f"Holding{i+1}"] = f"{holding_name},{holding_id}"
                            df.at[idx, f"MovementOn{i+1}"] = movement_on
                            df.at[idx, f"MovementOnDate{i+1}"] = movement_on_date
                            df.at[idx, f"MovementOff{i+1}"] = movement_off
                            df.at[idx, f"MovementOffDate{i+1}"] = movement_off_date
                    except Exception as e:
                        logger.warning(f"Movement row {i} failed for {eid}: {e}")

                # Step 6: Check for death
                spans = driver.find_elements(By.CSS_SELECTOR, "table.dataTableEx span")
                has_death = any("death" in s.text.lower() for s in spans if s.text.strip())
                df.at[idx, "hasDeath"] = has_death

                logger.info(f"✅ ID {eid} → DOB:{dob}, Gender:{gender}, Holding:{holding}, hasDeath={has_death}")

            except TimeoutException:
                logger.warning(f"Timeout for {eid}")
            except Exception as e:
                logger.error(f"Error on {eid}: {e}")

            out = path.replace(".xlsx", "_results.xlsx")
            try:
                df.to_excel(out, index=False, engine="openpyxl")
                logger.info(f"Progress saved → {out}")
            except Exception as e:
                logger.error(f"Failed to save results: {e}")

            time.sleep(1)

    finally:
        logger.info("Cleaning up...")
        try:
            if driver: 
                if open_in_new_tab and len(driver.window_handles) > 1:
                    # Close only the scraping tab, leave other tabs open
                    driver.close()
                    logger.info("Closed scraping tab, other tabs remain open")
                else:
                    driver.quit()
        except: pass
        try:
            # Only terminate if we created the Chrome process
            if chrome_proc and chrome_proc.poll() is None:
                chrome_proc.terminate()
        except: pass
        if profile_dir:
            shutil.rmtree(profile_dir, ignore_errors=True)
        logger.info("Done! Results saved.")

# --------------------------
# Enhanced GUI
# --------------------------
root = tk.Tk()
root.title("Enhanced Eartag Details Extractor (Google Chrome)")
root.geometry("800x600")
root.resizable(False, False)

# Nice font settings
label_font = ("Segoe UI", 10)
button_font = ("Segoe UI", 10, "bold")

# File selection row
tk.Label(root, text="Excel File (must contain column 'id'):", font=label_font).grid(row=0, column=0, sticky="w", padx=10, pady=8)
entry_file = tk.Entry(root, width=55, font=("Consolas", 10))
entry_file.grid(row=0, column=1, padx=5, pady=8)
tk.Button(
    root,
    text="Browse",
    font=button_font,
    command=lambda: entry_file.insert(
        0, filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    ),
).grid(row=0, column=2, padx=10, pady=8)

# URL input row
tk.Label(root, text="Target URL:", font=label_font).grid(row=1, column=0, sticky="w", padx=10, pady=8)
entry_url = tk.Entry(root, width=55, font=("Consolas", 10))
entry_url.grid(row=1, column=1, padx=5, pady=8)

# Instructions
instructions = tk.Label(root, 
    text="💡 Requirements: Chrome must be running with remote debugging enabled.\n"
         "Run this command first: chrome --remote-debugging-port=9222\n"
         "The scraper will automatically open a new tab and work in existing Chrome window.",
    font=("Segoe UI", 9), fg="blue", wraplength=750, justify="left")
instructions.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Start button
start_btn = tk.Button(root, text="▶ Start Extraction", bg="#28a745", fg="white", font=button_font, relief="raised", cursor="hand2")
start_btn.grid(row=3, column=1, pady=12)

# Logs box
tk.Label(root, text="Logs:", font=label_font).grid(row=4, column=0, sticky="w", padx=10)
log_widget = scrolledtext.ScrolledText(root, state="disabled", width=90, height=20, font=("Consolas", 9))
log_widget.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# Attach logger
text_handler = TextHandler(log_widget)
text_handler.setFormatter(formatter)
logger.addHandler(text_handler)

def start():
    f = entry_file.get().strip()
    u = entry_url.get().strip()
    if not os.path.isfile(f):
        messagebox.showerror("Error", "Select a valid Excel file")
        return
    if not u:
        messagebox.showerror("Error", "Enter a valid URL")
        return
    
    start_btn.config(state="disabled")
    root.update()
    
    try:
        run_scraper(f, u)
    except Exception as e:
        logger.error(f"Fatal: {e}")
        messagebox.showerror("Error", str(e))
    finally:
        start_btn.config(state="normal")

start_btn.config(command=start)

# Welcome message
logger.info("🚀 Eartag Details Extractor Ready!")
logger.info("📌 Make sure Chrome is running with: chrome --remote-debugging-port=9222")
logger.info("🔗 The scraper will automatically open new tabs in your existing Chrome window")

root.mainloop()