import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from playwright.sync_api import sync_playwright
import time
import threading
import random

def random_delay(min_seconds=0.8, max_seconds=1.5):
    """Generate a random delay to simulate human-like behavior"""
    time_to_sleep = random.uniform(min_seconds, max_seconds)
    time.sleep(time_to_sleep)

def get_random_user_agent():
    """Return a random user agent string to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

class EmailCheckerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("@FWbebo Email Checker")
        self.root.geometry("1000x700")
        self.root.configure(bg='#111111')
        
        # Configure modern style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       background='#111111', 
                       foreground='#ff0000',
                       font=('Segoe UI', 28, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#111111',
                       foreground='#ffffff',
                       font=('Segoe UI', 12))
        
        style.configure('Modern.TButton',
                       background='#ff0000',
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Modern.TButton',
                 background=[('active', '#cc0000'),
                           ('pressed', '#990000')])
        
        style.configure('Clear.TButton',
                       background='#333333',
                       foreground='white',
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Clear.TButton',
                 background=[('active', '#444444'),
                           ('pressed', '#222222')])
        
        style.configure('Stop.TButton',
                       background='#ff6600',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Stop.TButton',
                 background=[('active', '#cc5500'),
                           ('pressed', '#994400')])
        
        style.configure('Modern.TLabelframe',
                       background='#111111',
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.TLabelframe.Label',
                       background='#111111',
                       foreground='#ffffff',
                       font=('Segoe UI', 12, 'bold'))
        
        # Main container
        main_frame = tk.Frame(root, bg='#111111')
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#111111')
        header_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ttk.Label(
            header_frame, 
            text="@FWbebo", 
            style='Title.TLabel'
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Email Validation System - Headless Mode",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Content container
        content_frame = tk.Frame(main_frame, bg='#111111')
        content_frame.pack(fill='both', expand=True)
        
        # Left panel - Email Input
        left_panel = ttk.LabelFrame(content_frame, text="📧 Email Input", 
                                   style='Modern.TLabelframe', padding=20)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Input instructions
        input_instruction = ttk.Label(
            left_panel,
            text="Enter emails (one per line, or separated by commas/spaces):",
            font=('Segoe UI', 10),
            background='#111111',
            foreground='#ffffff'
        )
        input_instruction.pack(anchor='w', pady=(0, 10))
        
        # Email input with modern styling
        input_container = tk.Frame(left_panel, bg='#1a1a1a', relief='solid', bd=1)
        input_container.pack(fill='both', expand=True, pady=(0, 15))
        
        self.email_input = scrolledtext.ScrolledText(
            input_container,
            height=12,
            font=('Consolas', 10),
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='#ff0000',
            selectbackground='#ff0000',
            selectforeground='#ffffff',
            relief='flat',
            padx=15,
            pady=15,
            wrap='word'
        )
        self.email_input.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Button container
        button_frame = tk.Frame(left_panel, bg='#111111')
        button_frame.pack(fill='x', pady=(10, 0))
        
        self.check_button = ttk.Button(
            button_frame,
            text="🚀 Start Checking",
            command=self.start_checking,
            style='Modern.TButton'
        )
        self.check_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="🛑 Stop Checking",
            command=self.stop_checking,
            style='Stop.TButton',
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=(0, 10))
        
        self.clear_input_button = ttk.Button(
            button_frame,
            text="Clear Input",
            command=self.clear_input,
            style='Clear.TButton'
        )
        self.clear_input_button.pack(side='left')
        
        # Right panel - Results
        right_panel = ttk.LabelFrame(content_frame, text="📊 Results", 
                                    style='Modern.TLabelframe', padding=20)
        right_panel.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Status bar
        status_frame = tk.Frame(right_panel, bg='#111111')
        status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to check emails (Headless Mode)",
            font=('Segoe UI', 10),
            background='#111111',
            foreground='#ffffff'
        )
        self.status_label.pack(side='left')
        
        self.progress_label = ttk.Label(
            status_frame,
            text="",
            font=('Segoe UI', 10, 'bold'),
            background='#111111',
            foreground='#ff0000'
        )
        self.progress_label.pack(side='right')
        
        # Results display with modern styling
        results_container = tk.Frame(right_panel, bg='#1a1a1a', relief='solid', bd=1)
        results_container.pack(fill='both', expand=True, pady=(0, 15))
        
        self.results_text = scrolledtext.ScrolledText(
            results_container,
            height=12,
            font=('Consolas', 10),
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='#ff0000',
            selectbackground='#ff0000',
            selectforeground='#ffffff',
            relief='flat',
            padx=15,
            pady=15,
            wrap='word'
        )
        self.results_text.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Results button container
        results_button_frame = tk.Frame(right_panel, bg='#111111')
        results_button_frame.pack(fill='x')
        
        self.clear_results_button = ttk.Button(
            results_button_frame,
            text="Clear Results",
            command=self.clear_results,
            style='Clear.TButton'
        )
        self.clear_results_button.pack(side='left')
        
        self.save_results_button = ttk.Button(
            results_button_frame,
            text="💾 Save Results",
            command=self.save_results,
            style='Modern.TButton'
        )
        self.save_results_button.pack(side='right')
        
        self.is_checking = False
        self.stop_requested = False
        self.total_emails = 0
        self.checked_emails = 0
        self.valid_emails = []
        self.invalid_emails = []
        
        # Add sample text to input
        sample_text = "# Paste your emails here\n# One per line or separated by commas\n# Example:\nexample1@gmail.com\nexample2@yahoo.com"
        self.email_input.insert('1.0', sample_text)
        self.email_input.bind('<FocusIn>', self.clear_sample_text)

    def clear_sample_text(self, event):
        current_text = self.email_input.get('1.0', tk.END).strip()
        if current_text.startswith('# Paste your emails here'):
            self.email_input.delete('1.0', tk.END)
    
    def clear_input(self):
        self.email_input.delete('1.0', tk.END)
    
    def clear_results(self):
        self.results_text.delete('1.0', tk.END)
        self.valid_emails = []
        self.invalid_emails = []
        self.update_status("Results cleared")
    
    def save_results(self):
        try:
            with open("email_check_results.txt", "w") as f:
                f.write("=== EMAIL CHECK RESULTS ===\n\n")
                f.write(f"Total Checked: {self.checked_emails}\n")
                f.write(f"Valid: {len(self.valid_emails)}\n")
                f.write(f"Invalid: {len(self.invalid_emails)}\n\n")
                f.write("VALID EMAILS:\n")
                for email in self.valid_emails:
                    f.write(f"✓ {email}\n")
                f.write("\nINVALID EMAILS:\n")
                for email in self.invalid_emails:
                    f.write(f"✗ {email}\n")
            messagebox.showinfo("Success", "Results saved to email_check_results.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {e}")
    
    def update_status(self, message):
        self.status_label.configure(text=message)
        self.root.update()
    
    def update_progress(self):
        if self.total_emails > 0:
            progress_text = f"{self.checked_emails}/{self.total_emails}"
            self.progress_label.configure(text=progress_text)
        self.root.update()
    
    def log_result(self, message, color_tag=None):
        # Configure text tags for colored output
        self.results_text.tag_configure("valid", foreground="#00ff00")
        self.results_text.tag_configure("invalid", foreground="#ff0000")
        self.results_text.tag_configure("info", foreground="#ffffff")
        self.results_text.tag_configure("warning", foreground="#ffff00")
        
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        if color_tag:
            self.results_text.insert(tk.END, formatted_message, color_tag)
        else:
            self.results_text.insert(tk.END, formatted_message)
        
        self.results_text.see(tk.END)
        self.root.update()

    def save_email(self, email: str, filename="FWbebo.txt"):
        try:
            with open(filename, "a") as f:
                f.write(email + "\n")
        except Exception as e:
            self.log_result(f"Error saving email: {e}")
    
    def remove_email_from_input(self, email_to_remove):
        """Remove the checked email from the input field"""
        try:
            current_text = self.email_input.get("1.0", tk.END).strip()
            lines = current_text.split('\n')
            
            # Remove the email from lines
            updated_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check if this line contains the email to remove
                    emails_in_line = re.split(r"[,\s]+", line)
                    filtered_emails = [e.strip() for e in emails_in_line if e.strip() != email_to_remove and '@' in e.strip()]
                    if filtered_emails:
                        updated_lines.append(' '.join(filtered_emails))
                elif line.startswith('#'):
                    updated_lines.append(line)
            
            # Update the input field
            self.email_input.delete("1.0", tk.END)
            if updated_lines:
                self.email_input.insert("1.0", '\n'.join(updated_lines))
                
        except Exception as e:
            self.log_result(f"Error removing email from input: {e}", "warning")

    def stop_checking(self):
        """Stop the email checking process"""
        self.stop_requested = True
        self.log_result("🛑 Stop requested by user...", "warning")
        self.update_status("Stopping email validation...")

    def check_email(self, page, email: str):
        # Check if stop was requested
        if self.stop_requested:
            return "stop"
            
        self.log_result(f"🔍 Checking: {email}", "info")
        self.update_status(f"Checking: {email}")
        
        try:
            # Navigate freshly to the login page with random delay
            self.log_result(f"🌐 Navigating to Shein login page...", "info")
            page.goto("https://us.shein.com/user/auth/login?direction=nav")
            
            try:
                page.wait_for_load_state("load", timeout=15000)
                random_delay(1.0, 2.0)  # Wait for page to fully settle
            except Exception as e:
                self.log_result(f"⚠️ Page load warning: {e}", "warning")

            # Check if stop was requested during page load
            if self.stop_requested:
                return "stop"

            # Simulate human-like interaction with the email field
            try:
                self.log_result(f"📧 Entering email address...", "info")
                email_input_field = page.get_by_role("textbox", name="Email Address:")
                
                # Hover over the field first (human-like behavior)
                email_input_field.hover()
                random_delay(0.5, 1.0)
                
                # Click to focus
                email_input_field.click()
                random_delay(0.3, 0.7)
                
                # Clear any existing content and fill email
                email_input_field.fill("")
                random_delay(0.2, 0.5)
                email_input_field.fill(email)
                random_delay(0.8, 1.2)  # Wait after filling email
                
            except Exception as e:
                self.log_result(f"❌ Error during email input for {email}: {e}", "invalid")
                self.invalid_emails.append(email)
                return "continue"

            # Check if stop was requested during email input
            if self.stop_requested:
                return "stop"

            # Simulate human-like interaction with the continue button
            try:
                self.log_result(f"🔄 Clicking continue button...", "info")
                continue_button = page.get_by_role("button", name="Continue", exact=True)
                
                # Hover over the button first
                continue_button.hover()
                random_delay(0.5, 1.0)
                
                # Click the button
                continue_button.click()
                random_delay(1.5, 2.5)  # Wait for response
                
            except Exception as e:
                self.log_result(f"❌ Error clicking continue button for {email}: {e}", "invalid")
                self.invalid_emails.append(email)
                return "continue"

            # Check if stop was requested during button click
            if self.stop_requested:
                return "stop"

            # Wait for and analyze the response
            try:
                self.log_result(f"⏳ Waiting for authentication response...", "info")
                page.wait_for_selector(".page__login-newUI-emailPannel", timeout=8000)
                random_delay(0.5, 1.0)  # Let the page settle
                
                container_text = page.locator(".page__login-newUI-emailPannel").inner_text()

                if "Sign In With Your Account" in container_text:
                    self.log_result(f"✅ {email} - VALID (existing account)", "valid")
                    self.save_email(email)
                    self.valid_emails.append(email)
                elif "Create Your shein Account" in container_text:
                    self.log_result(f"❌ {email} - INVALID (new registration)", "invalid")
                    self.invalid_emails.append(email)
                else:
                    self.log_result(f"❓ {email} - Unknown state: {container_text[:100]}...", "warning")
                    self.invalid_emails.append(email)
                    
            except Exception as e:
                # Check for timeout errors that indicate potential blocking
                error_str = str(e)
                if "Timeout" in error_str and "page__login-newUI-emailPannel" in error_str:
                    self.log_result(f"🚫 {email} - TIMEOUT ERROR: Shein may be blocking requests", "invalid")
                    self.log_result(f"🔒 DETECTION ALERT: Please connect to a VPN and try again", "warning")
                    self.log_result(f"⚠️ Stopping email checking to prevent further blocking", "warning")
                    self.invalid_emails.append(email)
                    return "stop"  # Signal to stop checking
                
                # Check if we got an authentication error
                try:
                    page_content = page.content()
                    if "Authentication service unavailable" in page_content:
                        self.log_result(f"🚫 {email} - Authentication service blocked (bot detected)", "invalid")
                        self.log_result(f"🔒 DETECTION ALERT: Please connect to a VPN and try again", "warning")
                        self.log_result(f"⚠️ Stopping email checking to prevent further blocking", "warning")
                        self.invalid_emails.append(email)
                        return "stop"  # Signal to stop checking
                    else:
                        self.log_result(f"❌ {email} - Timeout/Error: {e}", "invalid")
                except:
                    self.log_result(f"❌ {email} - Timeout/Error: {e}", "invalid")
                self.invalid_emails.append(email)

        except Exception as e:
            self.log_result(f"❌ {email} - Critical error: {e}", "invalid")
            self.invalid_emails.append(email)
        
        finally:
            self.checked_emails += 1
            self.update_progress()
            # Remove the checked email from input
            self.remove_email_from_input(email)
            random_delay(2.0, 4.0)  # Random delay between checks
            
        return "continue"

    def check_emails(self):
        raw_input = self.email_input.get("1.0", tk.END).strip()
        
        # Filter out comments and empty lines
        lines = raw_input.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        raw_clean = ' '.join(clean_lines)
        
        emails = re.split(r"[,\s]+", raw_clean)
        emails = [e.strip() for e in emails if e.strip() and '@' in e]

        if not emails:
            messagebox.showwarning("No Emails", "Please enter valid email addresses to check.")
            return

        # Reset counters and flags
        self.total_emails = len(emails)
        self.checked_emails = 0
        self.valid_emails = []
        self.invalid_emails = []
        self.stop_requested = False

        self.check_button.configure(state='disabled', text="⏳ Checking...")
        self.stop_button.configure(state='normal')
        self.clear_input_button.configure(state='disabled')
        
        self.log_result("=" * 50, "info")
        self.log_result(f"🚀 Starting email validation for {self.total_emails} emails (Headless Mode)", "info")
        self.log_result("=" * 50, "info")
        self.update_status("Initializing headless browser...")

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,  # Changed to True for headless mode
                    args=[
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-extensions-except',
                        '--disable-plugins-discovery',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--window-size=1280,800'
                    ]
                )
                
                for i, email in enumerate(emails, 1):
                    if not self.is_checking or self.stop_requested:
                        self.log_result("❌ Checking cancelled by user", "warning")
                        break
                    
                    self.update_status(f"Processing email {i}/{self.total_emails}")
                    
                    context = browser.new_context(
                        user_agent=get_random_user_agent(),
                        viewport={"width": 1280, "height": 800},
                        locale="en-US",
                        extra_http_headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )
                    page = context.new_page()
                    page.add_init_script(path="stealth.js")
                    
                    result = self.check_email(page, email)
                    context.close()
                    
                    # If we got a stop signal, break the loop
                    if result == "stop" or self.stop_requested:
                        self.log_result("🛑 Email checking stopped", "warning")
                        break

                browser.close()
                
        except Exception as e:
            self.log_result(f"💥 Critical error during checking: {e}", "invalid")
        finally:
            self.is_checking = False
            self.stop_requested = False
            self.check_button.configure(state='normal', text="🚀 Start Checking")
            self.stop_button.configure(state='disabled')
            self.clear_input_button.configure(state='normal')
            
            # Final summary
            self.log_result("=" * 50, "info")
            self.log_result(f"✅ Validation complete!", "info")
            self.log_result(f"📊 Summary: {len(self.valid_emails)} valid, {len(self.invalid_emails)} invalid", "info")
            self.log_result("=" * 50, "info")
            self.update_status("Validation complete (Headless Mode)")

    def start_checking(self):
        if not self.is_checking:
            self.is_checking = True
            self.stop_requested = False
            threading.Thread(target=self.check_emails, daemon=True).start()

def main():
    root = tk.Tk()
    app = EmailCheckerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
