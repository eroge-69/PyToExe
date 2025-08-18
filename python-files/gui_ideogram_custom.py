#!/usr/bin/env python3
"""
Ideogram Automation — CUSTOM (no auto-open, uses existing profile)
- Do NOT auto-open Chrome on start.
- Use an existing Chrome user-data-dir + profile-directory to avoid repeated verification.
- Adds common anti-detection flags for Selenium/Chrome.
- Build with PyInstaller (build script included).

Usage:
1) Edit prompts.txt (one prompt per line).
2) Option A (recommended): Build EXE using build_exe.bat or run this script with Python.
3) In GUI enter:
   - Prompts file path
   - Pre-delay (seconds) - how long to wait before launching Chrome using profile
   - Delay per prompt (seconds)
   - Chrome user-data-dir (e.g., C:\\Users\\<YOU>\\AppData\\Local\\Google\\Chrome\\User Data)
   - Profile-directory (e.g., Default)
4) Click Start. The script will wait pre-delay seconds, then launch Chrome using the provided profile.
   If verification appears, complete it once manually; after that saved profile should work.
"""

import threading, time, tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

IDEOGRAM_CREATE_URL = "https://ideogram.ai/create"

def read_prompts(path: Path):
    txt = path.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in txt.splitlines()]
    return [ln for ln in lines if ln and not ln.lstrip().startswith("#")]

def build_driver(profile_path: str | None, profile_dir: str | None):
    chrome_options = Options()
    # Anti-detection options
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if profile_path:
        chrome_options.add_argument(f'--user-data-dir={profile_path}')
    if profile_dir:
        chrome_options.add_argument(f'--profile-directory={profile_dir}')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver

def wait_for_prompt_box(driver, timeout=120):
    wait = WebDriverWait(driver, timeout)
    selectors = [
        (By.CSS_SELECTOR, "div[contenteditable='true']"),
        (By.TAG_NAME, "textarea"),
        (By.XPATH, "//textarea[contains(@placeholder, 'Describe') or contains(@placeholder, 'prompt')]"),
        (By.XPATH, "//*[@role='textbox']"),
    ]
    last = None
    for by, sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((by, sel)))
            wait.until(EC.element_to_be_clickable((by, sel)))
            return el
        except Exception as e:
            last = e
    raise last or TimeoutError("Prompt input box not found")

def find_generate_button(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)
    candidates = [
        (By.XPATH, "//button[.//text()[contains(., 'Generate')]]"),
        (By.XPATH, "//button[contains(., 'Generate')]"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(@class,'generate') or contains(@aria-label,'Generate')]"),
    ]
    last = None
    for by, sel in candidates:
        try:
            return wait.until(EC.element_to_be_clickable((by, sel)))
        except Exception as e:
            last = e
    raise last or TimeoutError("Generate button not found")

def smart_type(el, text):
    try:
        el.clear()
    except Exception:
        pass
    el.send_keys(Keys.CONTROL, 'a')
    el.send_keys(Keys.BACKSPACE)
    el.send_keys(text)

def take_screenshot(driver, outdir: Path, prefix: str):
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    driver.save_screenshot(str(fp))
    return fp

def run_automation(prompts_file: str, pre_delay: int, delay_s: int, profile_path: str | None, profile_dir: str | None, log_cb):
    try:
        p = Path(prompts_file)
        if not p.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_file}")
        prompts = read_prompts(p)
        if not prompts:
            raise ValueError("No prompts found (file empty or only comments).")

        outdir = Path("ideogram_runs") / datetime.now().strftime("%Y%m%d")

        # Pre-wait for manual actions if needed
        for s in range(pre_delay, 0, -1):
            log_cb(f"Pre-start delay: {s}s...", replace=True)
            time.sleep(1)
        log_cb(" ")

        log_cb("Launching Chrome with provided profile (if supplied)...")
        driver = build_driver(profile_path, profile_dir)
        driver.get(IDEOGRAM_CREATE_URL)
        log_cb("If verification appears, please complete it manually once. Then rerun the app using same profile.")

        prompt_box = wait_for_prompt_box(driver, timeout=120)
        log_cb("Prompt box detected. Starting automation...")

        for idx, prompt in enumerate(prompts, start=1):
            short = prompt[:80] + ("..." if len(prompt)>80 else "")
            log_cb(f"[{idx}/{len(prompts)}] Submitting: {short}")
            try:
                prompt_box.click()
            except Exception:
                pass
            smart_type(prompt_box, prompt)

            try:
                find_generate_button(driver, 30).click()
            except Exception:
                try:
                    prompt_box.send_keys(Keys.ENTER)
                except Exception:
                    pass

            log_cb(f"Saved screenshot: {take_screenshot(driver, outdir, f'before_wait_{idx}').name}")

            wait_seconds = max(5, int(delay_s))
            for s in range(wait_seconds, 0, -1):
                log_cb(f"Waiting {s}s...", replace=True)
                time.sleep(1)
            log_cb(" ")

            log_cb(f"Saved screenshot: {take_screenshot(driver, outdir, f'after_wait_{idx}').name}")

            try:
                prompt_box = wait_for_prompt_box(driver, timeout=30)
            except Exception:
                try:
                    driver.get(IDEOGRAM_CREATE_URL)
                    prompt_box = wait_for_prompt_box(driver, timeout=120)
                except Exception as e:
                    log_cb(f"Stopped: could not find prompt box again. {e}")
                    break

        log_cb("Done. Check ideogram_runs/<today>/ for screenshots.")
    except Exception as e:
        log_cb(f"ERROR: {e}")
        try:
            messagebox.showerror("Automation Error", str(e))
        except Exception:
            pass

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ideogram Automation - CUSTOM")
        self.geometry("700x480")
        self.prompts_var = tk.StringVar(value="prompts.txt")
        self.pre_delay_var = tk.StringVar(value="10")
        self.delay_var = tk.StringVar(value="30")
        self.profile_path_var = tk.StringVar(value="")
        self.profile_dir_var = tk.StringVar(value="Default")
        self.running = False

        row = 0
        tk.Label(self, text="Prompts file:").grid(row=row, column=0, sticky="w", padx=10, pady=6)
        tk.Entry(self, textvariable=self.prompts_var, width=55).grid(row=row, column=1, sticky="we", padx=5)
        tk.Button(self, text="Browse", command=self.browse_prompts).grid(row=row, column=2, padx=10); row+=1

        tk.Label(self, text="Initial pre-start delay (seconds):").grid(row=row, column=0, sticky="w", padx=10, pady=6)
        tk.Entry(self, textvariable=self.pre_delay_var, width=15).grid(row=row, column=1, sticky="w", padx=5); row+=1

        tk.Label(self, text="Delay per prompt (seconds):").grid(row=row, column=0, sticky="w", padx=10, pady=6)
        tk.Entry(self, textvariable=self.delay_var, width=15).grid(row=row, column=1, sticky="w", padx=5); row+=1

        tk.Label(self, text="Chrome user-data-dir (profile path):").grid(row=row, column=0, sticky="w", padx=10, pady=6)
        tk.Entry(self, textvariable=self.profile_path_var, width=55).grid(row=row, column=1, sticky="we", padx=5)
        tk.Button(self, text="Browse", command=self.browse_profile).grid(row=row, column=2, padx=10); row+=1

        tk.Label(self, text="Chrome profile-directory (e.g., Default):").grid(row=row, column=0, sticky="w", padx=10, pady=6)
        tk.Entry(self, textvariable=self.profile_dir_var, width=20).grid(row=row, column=1, sticky="w", padx=5); row+=1

        self.start_btn = tk.Button(self, text="Start (pre-delay & run)", command=self.on_start, height=2)
        self.start_btn.grid(row=row, column=0, padx=10, pady=10, sticky="we")
        tk.Button(self, text="Quit", command=self.destroy, height=2).grid(row=row, column=2, padx=10, pady=10, sticky="we"); row+=1

        tk.Label(self, text="Log:").grid(row=row, column=0, sticky="nw", padx=10)
        self.log = tk.Text(self, height=14, wrap="word"); self.log.grid(row=row, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(row, weight=1)

    def browse_prompts(self):
        p = filedialog.askopenfilename(title="Select prompts file", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if p: self.prompts_var.set(p)

    def browse_profile(self):
        p = filedialog.askdirectory(title="Select Chrome user data directory")
        if p: self.profile_path_var.set(p)

    def log_cb(self, text, replace=False):
        if replace:
            try: self.log.delete("end-2l", "end-1l")
            except Exception: pass
        self.log.insert("end", text + "\\n"); self.log.see("end"); self.update_idletasks()

    def on_start(self):
        if self.running: return
        try:
            pre_delay_int = int(self.pre_delay_var.get().strip())
            delay_int = int(self.delay_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Delay", "Delays should be numbers (e.g., 10, 30)."); return
        self.running = True; self.start_btn.config(state="disabled")
        threading.Thread(target=self._run_thread, args=(self.prompts_var.get().strip(), pre_delay_int, delay_int, self.profile_path_var.get().strip() or None, self.profile_dir_var.get().strip() or None), daemon=True).start()

    def _run_thread(self, prompts, pre_delay, delay, profile_path, profile_dir):
        try:
            run_automation(prompts, pre_delay, delay, profile_path, profile_dir, self.log_cb)
        finally:
            self.running = False; self.start_btn.config(state="normal")

if __name__ == "__main__":
    App().mainloop()
