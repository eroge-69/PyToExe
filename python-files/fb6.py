import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import os
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed

class AccountManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Account Manager")
        self.root.geometry("800x600")
        
        # Program state
        self.is_running = False
        self.is_paused = False
        self.current_thread = None
        
        # Settings
        self.min_delay = 1  # seconds
        self.max_delay = 5  # seconds
        self.concurrent_browsers = 3  # number of browsers running simultaneously
        
        # Create interface
        self.create_widgets()
        
        # Create folder for saving cookies
        self.cookies_dir = "cookies"
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)
    
    def create_widgets(self):
        # Accounts frame
        accounts_frame = ttk.LabelFrame(self.root, text="Accounts (email:pass)")
        accounts_frame.pack(fill="x", padx=10, pady=5)
        
        self.accounts_text = scrolledtext.ScrolledText(accounts_frame, height=8)
        self.accounts_text.pack(fill="x", padx=5, pady=5)
        
        # Accounts counter
        self.accounts_count_var = tk.StringVar(value="Number of accounts: 0")
        self.accounts_count_label = ttk.Label(accounts_frame, textvariable=self.accounts_count_var)
        self.accounts_count_label.pack(pady=5)
        
        # Add/Clear buttons for accounts
        accounts_buttons_frame = ttk.Frame(accounts_frame)
        accounts_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.add_btn = ttk.Button(accounts_buttons_frame, text="Add", command=self.add_accounts)
        self.add_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(accounts_buttons_frame, text="Clear", command=self.clear_accounts)
        self.clear_btn.pack(side="left", padx=5)
        
        # Active/Inactive accounts frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Active accounts
        active_frame = ttk.LabelFrame(status_frame, text="Active Accounts")
        active_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.active_listbox = tk.Listbox(active_frame)
        self.active_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Active accounts counter
        self.active_count_var = tk.StringVar(value="Number of active accounts: 0")
        self.active_count_label = ttk.Label(active_frame, textvariable=self.active_count_var)
        self.active_count_label.pack(pady=5)
        
        # Save active accounts button
        self.save_active_btn = ttk.Button(active_frame, text="Save", command=self.save_active_accounts)
        self.save_active_btn.pack(pady=5)
        
        # Inactive accounts
        inactive_frame = ttk.LabelFrame(status_frame, text="Inactive Accounts")
        inactive_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.inactive_listbox = tk.Listbox(inactive_frame)
        self.inactive_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Inactive accounts counter
        self.inactive_count_var = tk.StringVar(value="Number of inactive accounts: 0")
        self.inactive_count_label = ttk.Label(inactive_frame, textvariable=self.inactive_count_var)
        self.inactive_count_label.pack(pady=5)
        
        # General settings frame
        settings_frame = ttk.LabelFrame(self.root, text="General Settings")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Delay time
        ttk.Label(settings_frame, text="Delay time (seconds):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.min_delay_var = tk.StringVar(value="1")
        self.min_delay_spin = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.min_delay_var, width=8)
        self.min_delay_spin.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="to").grid(row=0, column=2, padx=5, pady=5)
        
        self.max_delay_var = tk.StringVar(value="5")
        self.max_delay_spin = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.max_delay_var, width=8)
        self.max_delay_spin.grid(row=0, column=3, padx=5, pady=5)
        
        # Number of concurrent browsers
        ttk.Label(settings_frame, text="Concurrent browsers:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        self.concurrent_var = tk.StringVar(value="3")
        self.concurrent_spin = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.concurrent_var, width=8)
        self.concurrent_spin.grid(row=1, column=1, padx=5, pady=5)
        
        # Additional options
        ttk.Label(settings_frame, text="Browser mode:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(settings_frame, text="Headless", variable=self.headless_var)
        self.headless_check.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Target URL
        ttk.Label(settings_frame, text="Target URL:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.target_url_var = tk.StringVar(value="https://www.facebook.com")
        self.target_url_entry = ttk.Entry(settings_frame, textvariable=self.target_url_var, width=30)
        self.target_url_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
        # Control buttons
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = ttk.Button(buttons_frame, text="Start", command=self.start_process)
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = ttk.Button(buttons_frame, text="Pause", command=self.pause_process, state="disabled")
        self.pause_btn.pack(side="left", padx=5)
        
        self.resume_btn = ttk.Button(buttons_frame, text="Resume", command=self.resume_process, state="disabled")
        self.resume_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="Stop", command=self.stop_process, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill="x", padx=10, pady=5)
        
        # Bind text change event in accounts field to update counter
        self.accounts_text.bind("<KeyRelease>", self.update_accounts_count)
    
    def update_accounts_count(self, event=None):
        """Update accounts counter in the first field"""
        accounts = self.get_accounts()
        self.accounts_count_var.set(f"Number of accounts: {len(accounts)}")
    
    def update_active_count(self):
        """Update active accounts counter"""
        count = self.active_listbox.size()
        self.active_count_var.set(f"Number of active accounts: {count}")
    
    def update_inactive_count(self):
        """Update inactive accounts counter"""
        count = self.inactive_listbox.size()
        self.inactive_count_var.set(f"Number of inactive accounts: {count}")
    
    def add_accounts(self):
        """Add accounts from file"""
        file_path = filedialog.askopenfilename(
            title="Select accounts file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    accounts_content = f.read()
                
                # Add content to text field
                current_content = self.accounts_text.get("1.0", tk.END).strip()
                if current_content:
                    accounts_content = current_content + "\n" + accounts_content
                
                self.accounts_text.delete("1.0", tk.END)
                self.accounts_text.insert("1.0", accounts_content)
                
                # Update counter
                self.update_accounts_count()
                
                messagebox.showinfo("Success", "Accounts added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def clear_accounts(self):
        """Clear all accounts from field"""
        if messagebox.askyesno("Confirm", "Do you want to clear all accounts?"):
            self.accounts_text.delete("1.0", tk.END)
            self.update_accounts_count()
    
    def save_active_accounts(self):
        """Save active accounts to text file"""
        if self.active_listbox.size() == 0:
            messagebox.showwarning("Warning", "No active accounts to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save active accounts",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i in range(self.active_listbox.size()):
                        f.write(self.active_listbox.get(i) + "\n")
                
                messagebox.showinfo("Success", f"Saved {self.active_listbox.size()} active accounts to file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def get_accounts(self):
        """Extract accounts from text field"""
        text = self.accounts_text.get("1.0", tk.END).strip()
        if not text:
            return []
        
        accounts = []
        for line in text.split('\n'):
            line = line.strip()
            if ':' in line:
                email, password = line.split(':', 1)
                accounts.append({'email': email.strip(), 'password': password.strip()})
        
        return accounts
    
    def update_settings(self):
        """Update settings from interface"""
        try:
            self.min_delay = max(1, int(self.min_delay_var.get()))
            self.max_delay = max(self.min_delay, int(self.max_delay_var.get()))
            self.concurrent_browsers = max(1, min(10, int(self.concurrent_var.get())))
            self.target_url = self.target_url_var.get().strip()
            if not self.target_url:
                messagebox.showerror("Error", "Please enter target URL")
                return False
        except ValueError:
            messagebox.showerror("Error", "Delay values and number of browsers must be integers")
            return False
        return True
    
    def start_process(self):
        """Start account processing"""
        if not self.update_settings():
            return
        
        accounts = self.get_accounts()
        if not accounts:
            messagebox.showwarning("Warning", "No accounts entered")
            return
        
        # Clear lists
        self.active_listbox.delete(0, tk.END)
        self.inactive_listbox.delete(0, tk.END)
        
        # Update counters
        self.update_active_count()
        self.update_inactive_count()
        
        # Update button states
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.status_var.set("Processing...")
        
        # Start process in separate thread
        self.is_running = True
        self.is_paused = False
        self.current_thread = threading.Thread(target=self.process_accounts, args=(accounts,))
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def pause_process(self):
        """Pause process"""
        self.is_paused = True
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")
        self.status_var.set("Paused")
    
    def resume_process(self):
        """Resume process"""
        self.is_paused = False
        self.resume_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.status_var.set("Processing...")
    
    def stop_process(self):
        """Stop process"""
        self.is_running = False
        self.is_paused = False
        
        # Update button states
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Stopped")
    
    def process_accounts(self, accounts):
        """Process accounts using multiple browsers simultaneously"""
        # Split accounts into groups based on number of concurrent browsers
        account_groups = [accounts[i:i + self.concurrent_browsers] 
                         for i in range(0, len(accounts), self.concurrent_browsers)]
        
        for group_index, account_group in enumerate(account_groups):
            if not self.is_running:
                break
            
            # Wait if process is paused
            while self.is_paused and self.is_running:
                time.sleep(0.5)
            
            if not self.is_running:
                break
            
            # Update current group status
            self.root.after(0, lambda: self.status_var.set(
                f"Processing group {group_index + 1} of {len(account_groups)}"
            ))
            
            # Process current group of accounts simultaneously
            with ThreadPoolExecutor(max_workers=self.concurrent_browsers) as executor:
                # Start processing all accounts in current group
                future_to_account = {
                    executor.submit(self.process_account, account): account 
                    for account in account_group
                }
                
                # Collect results
                for future in as_completed(future_to_account):
                    account = future_to_account[future]
                    try:
                        success = future.result()
                        # Update interface
                        self.root.after(0, self.update_account_list, account, success)
                    except Exception as e:
                        print(f"Error processing account {account['email']}: {str(e)}")
                        self.root.after(0, self.update_account_list, account, False)
            
            # Random delay between groups
            if group_index < len(account_groups) - 1:  # No delay after last group
                delay = self.get_random_delay()
                time.sleep(delay)
        
        # Reset program state after completion
        self.root.after(0, self.reset_ui)
    
    def get_random_delay(self):
        """Get random delay time"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def process_account(self, account):
        """Process individual account"""
        driver = None
        try:
            # Setup Chrome browser
            chrome_options = Options()
            
            # Add options to improve stability
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Control display mode (headless or normal)
            if self.headless_var.get():
                chrome_options.add_argument("--headless=new")  # Use new headless mode
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            
            # Use different ports for each browser to avoid conflicts
            chrome_options.add_argument("--remote-debugging-port=0")
            
            # Use webdriver_manager to automatically install and set ChromeDriver path
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Hide automation signs
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            driver.implicitly_wait(10)
            
            # Navigate to target page
            driver.get(self.target_url)
            time.sleep(3)  # Wait for page to load
            
            # Try to find login fields using different methods
            email_field = None
            password_field = None
            
            # Search for fields using different methods
            selectors = [
                ("input[type='email']", By.CSS_SELECTOR),
                ("input[type='text'][name*='mail']", By.CSS_SELECTOR),
                ("#email", By.CSS_SELECTOR),
                ("input[name='email']", By.CSS_SELECTOR),
                ("//input[contains(@id, 'email') or contains(@name, 'email')]", By.XPATH)
            ]
            
            for selector, by_method in selectors:
                try:
                    email_field = driver.find_element(by_method, selector)
                    if email_field:
                        break
                except:
                    continue
            
            # If email field not found, assume page doesn't have login form
            if not email_field:
                print(f"Email field not found in {self.target_url}")
                return False
            
            # Search for password field
            password_selectors = [
                ("input[type='password']", By.CSS_SELECTOR),
                ("#pass", By.CSS_SELECTOR),
                ("#password", By.CSS_SELECTOR),
                ("input[name='pass']", By.CSS_SELECTOR),
                ("input[name='password']", By.CSS_SELECTOR),
                ("//input[contains(@id, 'pass') or contains(@name, 'pass')]", By.XPATH)
            ]
            
            for selector, by_method in password_selectors:
                try:
                    password_field = driver.find_element(by_method, selector)
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                print(f"Password field not found in {self.target_url}")
                return False
            
            # Fill login credentials
            email_field.clear()
            email_field.send_keys(account['email'])
            
            password_field.clear()
            password_field.send_keys(account['password'])
            
            # Search for login button
            login_selectors = [
                ("button[type='submit']", By.CSS_SELECTOR),
                ("input[type='submit']", By.CSS_SELECTOR),
                ("#loginbutton", By.CSS_SELECTOR),
                ("button[name='login']", By.CSS_SELECTOR),
                ("//button[contains(text(), 'Login') or contains(text(), 'Log In')]", By.XPATH)
            ]
            
            login_button = None
            for selector, by_method in login_selectors:
                try:
                    login_button = driver.find_element(by_method, selector)
                    if login_button:
                        break
                except:
                    continue
            
            if login_button:
                login_button.click()
            else:
                # If no button found, press Enter in password field
                password_field.send_keys(Keys.RETURN)
            
            # Wait 30 seconds for two-factor authentication if required
            time.sleep(30)
            
            # Check if login was successful
            # Wait for page change or elements indicating successful login
            time.sleep(5)
            
            # Different methods to verify successful login
            success_indicators = [
                (By.ID, "logoutForm"),  # Logout form
                (By.XPATH, "//a[contains(@href, 'logout') or contains(@href, 'logoff')]"),  # Logout link
                (By.XPATH, "//*[contains(text(), 'Welcome')]"),  # Welcome message
                (By.XPATH, "//*[contains(text(), 'My Account')]"),  # My Account
            ]
            
            login_success = False
            for by, value in success_indicators:
                try:
                    element = driver.find_element(by, value)
                    if element:
                        login_success = True
                        break
                except:
                    continue
            
            # If no success indicators found, check URL
            if not login_success:
                current_url = driver.current_url
                # If URL is different from login page, login might be successful
                if "login" not in current_url.lower() and "signin" not in current_url.lower():
                    login_success = True
            
            if login_success:
                # Save cookies
                cookies = driver.get_cookies()
                self.save_cookies(account['email'], cookies)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error processing account {account['email']}: {str(e)}")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def save_cookies(self, email, cookies):
        """Save cookies to file"""
        try:
            # Clean filename from invalid characters
            safe_email = "".join(c for c in email if c.isalnum() or c in ('@', '.', '_', '-')).rstrip()
            cookie_file = os.path.join(self.cookies_dir, f"{safe_email}_cookies.json")
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            print(f"Cookies saved for account: {email}")
        except Exception as e:
            print(f"Error saving cookies for account {email}: {str(e)}")
    
    def update_account_list(self, account, success):
        """Update accounts list in interface"""
        account_str = f"{account['email']}:{account['password']}"
        
        if success:
            self.active_listbox.insert(tk.END, account_str)
            self.update_active_count()
            print(f"Account processed successfully: {account['email']}")
        else:
            self.inactive_listbox.insert(tk.END, account_str)
            self.update_inactive_count()
            print(f"Account processing failed: {account['email']}")
    
    def reset_ui(self):
        """Reset user interface after process completion"""
        self.is_running = False
        self.is_paused = False
        
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Processing completed")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManager(root)
    root.mainloop()
