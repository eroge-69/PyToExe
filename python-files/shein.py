import tkinter as tk
from tkinter import ttk, scrolledtext
import re
from playwright.sync_api import sync_playwright
import time
import threading

class EmailCheckerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("@FWbebo Email Checker")
        self.root.geometry("800x600")
        self.root.configure(bg='white')
        
        # Configure style
        style = ttk.Style()
        style.configure('Modern.TButton', padding=10, font=('Helvetica', 10))
        style.configure('Modern.TLabel', padding=10, font=('Helvetica', 12))
        
        # Title
        title_label = ttk.Label(
            root, 
            text="@FWbebo Email Checker", 
            style='Modern.TLabel',
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Email Input Section
        input_frame = ttk.LabelFrame(root, text="Email Input", padding=10)
        input_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.email_input = scrolledtext.ScrolledText(
            input_frame, 
            height=10,
            font=('Helvetica', 10)
        )
        self.email_input.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Check Button
        self.check_button = ttk.Button(
            root,
            text="Check Emails",
            command=self.start_checking,
            style='Modern.TButton'
        )
        self.check_button.pack(pady=10)
        
        # Results Section
        results_frame = ttk.LabelFrame(root, text="Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=10,
            font=('Helvetica', 10)
        )
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.is_checking = False

    def save_email(self, email: str, filename="FWbebo.txt"):
        try:
            with open(filename, "a") as f:
                f.write(email + "\n")
        except Exception as e:
            self.log_result(f"Error saving email: {e}")

    def check_email(self, page, email: str):
        self.log_result(f"Checking email: {email}")
        
        # Navigate freshly to the login page
        page.goto("https://us.shein.com/user/auth/login?direction=nav")
        try:
            page.wait_for_load_state("load", timeout=10000)
        except Exception as e:
            self.log_result(f"[!] Warning: wait_for_load_state timeout or error: {e}")

        # Fill email and click continue
        page.get_by_role("textbox", name="Email Address:").click()
        page.get_by_role("textbox", name="Email Address:").fill(email)
        time.sleep(1)  # Small delay to ensure input is registered
        page.get_by_role("button", name="Continue", exact=True).click()

        try:
            page.wait_for_selector(".page__login-newUI-emailPannel", timeout=5000)
            container_text = page.locator(".page__login-newUI-emailPannel").inner_text()

            if "Sign In With Your Account" in container_text:
                self.log_result(f"[+] {email} is VALID (login page).")
                self.save_email(email)
            elif "Create Your shein Account" in container_text:
                self.log_result(f"[-] {email} is INVALID (registration page).")
            else:
                self.log_result(f"[-] {email} - Unknown state, no clear indicators found.")
        except Exception as e:
            self.log_result(f"[-] {email} - Timeout or error while checking: {e}")

        time.sleep(2)

    def log_result(self, message):
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()

    def check_emails(self):
        raw_input = self.email_input.get("1.0", tk.END).strip()
        emails = re.split(r"[,\s]+", raw_input)
        emails = [e for e in emails if e]

        self.check_button.configure(state='disabled')
        self.log_result("Starting email checks...")

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=False)
                
                for email in emails:
                    if not self.is_checking:
                        break
                        
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
            self.log_result(f"Error during checking: {e}")
        finally:
            self.is_checking = False
            self.check_button.configure(state='normal')
            self.log_result("Done checking all emails.")

    def start_checking(self):
        if not self.is_checking:
            self.is_checking = True
            self.results_text.delete("1.0", tk.END)
            threading.Thread(target=self.check_emails, daemon=True).start()

def main():
    root = tk.Tk()
    app = EmailCheckerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
