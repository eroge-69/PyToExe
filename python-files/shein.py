import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from playwright.sync_api import sync_playwright
import time
import threading

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
            text="Email Validation System",
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
            text="Ready to check emails",
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

    def check_email(self, page, email: str):
        self.log_result(f"🔍 Checking: {email}", "info")
        self.update_status(f"Checking: {email}")
        
        try:
            # Navigate freshly to the login page
            page.goto("https://us.shein.com/user/auth/login?direction=nav")
            try:
                page.wait_for_load_state("load", timeout=10000)
            except Exception as e:
                self.log_result(f"⚠️ Page load warning: {e}", "warning")

            # Fill email and click continue
            page.get_by_role("textbox", name="Email Address:").click()
            page.get_by_role("textbox", name="Email Address:").fill(email)
            time.sleep(1)  # Small delay to ensure input is registered
            page.get_by_role("button", name="Continue", exact=True).click()

            try:
                page.wait_for_selector(".page__login-newUI-emailPannel", timeout=5000)
                container_text = page.locator(".page__login-newUI-emailPannel").inner_text()

                if "Sign In With Your Account" in container_text:
                    self.log_result(f"✅ {email} - VALID (existing account)", "valid")
                    self.save_email(email)
                    self.valid_emails.append(email)
                elif "Create Your shein Account" in container_text:
                    self.log_result(f"❌ {email} - INVALID (new registration)", "invalid")
                    self.invalid_emails.append(email)
                else:
                    self.log_result(f"❓ {email} - Unknown state", "warning")
                    self.invalid_emails.append(email)
            except Exception as e:
                self.log_result(f"❌ {email} - Timeout/Error: {e}", "invalid")
                self.invalid_emails.append(email)

        except Exception as e:
            self.log_result(f"❌ {email} - Critical error: {e}", "invalid")
            self.invalid_emails.append(email)
        
        finally:
            self.checked_emails += 1
            self.update_progress()
            time.sleep(2)

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

        # Reset counters
        self.total_emails = len(emails)
        self.checked_emails = 0
        self.valid_emails = []
        self.invalid_emails = []

        self.check_button.configure(state='disabled', text="⏳ Checking...")
        self.clear_input_button.configure(state='disabled')
        
        self.log_result("=" * 50, "info")
        self.log_result(f"🚀 Starting email validation for {self.total_emails} emails", "info")
        self.log_result("=" * 50, "info")
        self.update_status("Initializing browser...")

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=False)
                
                for i, email in enumerate(emails, 1):
                    if not self.is_checking:
                        self.log_result("❌ Checking cancelled by user", "warning")
                        break
                    
                    self.update_status(f"Processing email {i}/{self.total_emails}")
                    
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                        viewport={"width": 1280, "height": 800},
                        locale="en-US"
                    )
                    page = context.new_page()
                    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
                    
                    self.check_email(page, email)
                    context.close()

                browser.close()
                
        except Exception as e:
            self.log_result(f"💥 Critical error during checking: {e}", "invalid")
        finally:
            self.is_checking = False
            self.check_button.configure(state='normal', text="🚀 Start Checking")
            self.clear_input_button.configure(state='normal')
            
            # Final summary
            self.log_result("=" * 50, "info")
            self.log_result(f"✅ Validation complete!", "info")
            self.log_result(f"📊 Summary: {len(self.valid_emails)} valid, {len(self.invalid_emails)} invalid", "info")
            self.log_result("=" * 50, "info")
            self.update_status("Validation complete")

    def start_checking(self):
        if not self.is_checking:
            self.is_checking = True
            threading.Thread(target=self.check_emails, daemon=True).start()

def main():
    root = tk.Tk()
    app = EmailCheckerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
