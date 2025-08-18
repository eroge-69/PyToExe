import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import json

class EmailSender:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal Email Sender")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Email provider configurations
        self.providers = {
            "Gmail": {"smtp": "smtp.gmail.com", "port": 587, "tls": True},
            "Outlook/Hotmail": {"smtp": "smtp-mail.outlook.com", "port": 587, "tls": True},
            "Yahoo": {"smtp": "smtp.mail.yahoo.com", "port": 587, "tls": True},
            "Office365": {"smtp": "smtp.office365.com", "port": 587, "tls": True}
        }
        
        self.attachments = []
        self.setup_gui()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Universal Email Sender", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Provider selection
        ttk.Label(main_frame, text="Email Provider:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.provider_var = tk.StringVar(value="Gmail")
        provider_combo = ttk.Combobox(main_frame, textvariable=self.provider_var, 
                                     values=list(self.providers.keys()), state="readonly", width=30)
        provider_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Sender credentials
        ttk.Label(main_frame, text="Your Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sender_email = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.sender_email, width=35).grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="App Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.sender_password = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.sender_password, 
                                  show="*", width=35)
        password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Recipients
        ttk.Label(main_frame, text="To (separate with ;):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.to_emails = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.to_emails, width=35).grid(
            row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="CC (optional):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.cc_emails = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.cc_emails, width=35).grid(
            row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="BCC (optional):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.bcc_emails = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.bcc_emails, width=35).grid(
            row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Subject
        ttk.Label(main_frame, text="Subject:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.subject = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.subject, width=35).grid(
            row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Message body
        ttk.Label(main_frame, text="Message:").grid(row=8, column=0, sticky=(tk.W, tk.N), pady=5)
        self.message_text = tk.Text(main_frame, height=10, width=50, wrap=tk.WORD)
        self.message_text.grid(row=8, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), 
                              pady=5, padx=(10, 0))
        
        # Scrollbar for message
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.message_text.yview)
        scrollbar.grid(row=8, column=2, sticky=(tk.N, tk.S), pady=5)
        self.message_text.configure(yscrollcommand=scrollbar.set)
        
        # Attachments
        attachment_frame = ttk.Frame(main_frame)
        attachment_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(attachment_frame, text="Attachments:").pack(side=tk.LEFT)
        ttk.Button(attachment_frame, text="Add File", 
                  command=self.add_attachment).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(attachment_frame, text="Clear All", 
                  command=self.clear_attachments).pack(side=tk.LEFT, padx=5)
        
        # Attachment list
        self.attachment_listbox = tk.Listbox(main_frame, height=3)
        self.attachment_listbox.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                                   pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Send Email", command=self.send_email,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Help text
        help_text = """
Setup Instructions:
1. For Gmail: Enable 2FA and generate an App Password
2. For Outlook/Office365: Use your regular password or App Password
3. For Yahoo: Generate an App Password in Account Security
4. Separate multiple recipients with semicolons (;)
        """
        
        help_label = ttk.Label(main_frame, text=help_text, font=('Arial', 8), 
                              foreground='gray', justify=tk.LEFT)
        help_label.grid(row=13, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def add_attachment(self):
        file_path = filedialog.askopenfilename(
            title="Select file to attach",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            self.attachments.append(file_path)
            filename = os.path.basename(file_path)
            self.attachment_listbox.insert(tk.END, filename)
            self.status_var.set(f"Added attachment: {filename}")
    
    def clear_attachments(self):
        self.attachments = []
        self.attachment_listbox.delete(0, tk.END)
        self.status_var.set("Attachments cleared")
    
    def clear_form(self):
        # Clear all form fields
        self.sender_email.set("")
        self.sender_password.set("")
        self.to_emails.set("")
        self.cc_emails.set("")
        self.bcc_emails.set("")
        self.subject.set("")
        self.message_text.delete(1.0, tk.END)
        self.clear_attachments()
        self.status_var.set("Form cleared")
    
    def parse_emails(self, email_string):
        """Parse semicolon-separated email addresses"""
        if not email_string:
            return []
        return [email.strip() for email in email_string.split(';') if email.strip()]
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            provider_config = self.providers[self.provider_var.get()]
            
            if not self.sender_email.get() or not self.sender_password.get():
                messagebox.showerror("Error", "Please enter your email and password")
                return
            
            self.status_var.set("Testing connection...")
            self.root.update()
            
            # Create SMTP connection
            server = smtplib.SMTP(provider_config["smtp"], provider_config["port"])
            
            if provider_config["tls"]:
                context = ssl.create_default_context()
                server.starttls(context=context)
            
            server.login(self.sender_email.get(), self.sender_password.get())
            server.quit()
            
            self.status_var.set("Connection successful!")
            messagebox.showinfo("Success", "Connection test successful!")
            
        except smtplib.SMTPAuthenticationError:
            self.status_var.set("Authentication failed")
            messagebox.showerror("Error", "Authentication failed. Check your email and password.")
        except Exception as e:
            self.status_var.set(f"Connection failed: {str(e)}")
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
    
    def send_email(self):
        """Send the email"""
        try:
            # Validate inputs
            if not all([self.sender_email.get(), self.sender_password.get(), 
                       self.to_emails.get(), self.subject.get()]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            provider_config = self.providers[self.provider_var.get()]
            
            # Parse recipients
            to_list = self.parse_emails(self.to_emails.get())
            cc_list = self.parse_emails(self.cc_emails.get())
            bcc_list = self.parse_emails(self.bcc_emails.get())
            
            if not to_list:
                messagebox.showerror("Error", "Please enter at least one recipient")
                return
            
            self.status_var.set("Sending email...")
            self.root.update()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email.get()
            msg['To'] = '; '.join(to_list)
            if cc_list:
                msg['Cc'] = '; '.join(cc_list)
            msg['Subject'] = self.subject.get()
            
            # Add body
            body = self.message_text.get(1.0, tk.END).strip()
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            for file_path in self.attachments:
                try:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    msg.attach(part)
                except Exception as e:
                    messagebox.showwarning("Warning", 
                                         f"Could not attach {os.path.basename(file_path)}: {str(e)}")
            
            # Send email
            server = smtplib.SMTP(provider_config["smtp"], provider_config["port"])
            
            if provider_config["tls"]:
                context = ssl.create_default_context()
                server.starttls(context=context)
            
            server.login(self.sender_email.get(), self.sender_password.get())
            
            # All recipients
            all_recipients = to_list + cc_list + bcc_list
            server.send_message(msg, to_addrs=all_recipients)
            server.quit()
            
            self.status_var.set(f"Email sent successfully to {len(all_recipients)} recipients!")
            messagebox.showinfo("Success", 
                              f"Email sent successfully to {len(all_recipients)} recipients!")
            
            # Log the sent email
            self.log_sent_email(all_recipients)
            
        except smtplib.SMTPAuthenticationError:
            self.status_var.set("Authentication failed")
            messagebox.showerror("Error", "Authentication failed. Check your credentials.")
        except Exception as e:
            self.status_var.set(f"Failed to send email: {str(e)}")
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
    
    def log_sent_email(self, recipients):
        """Log sent email details"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "provider": self.provider_var.get(),
                "from": self.sender_email.get(),
                "to": recipients,
                "subject": self.subject.get(),
                "attachments": [os.path.basename(f) for f in self.attachments]
            }
            
            # Create logs directory if it doesn't exist
            if not os.path.exists("email_logs"):
                os.makedirs("email_logs")
            
            # Append to log file
            with open("email_logs/sent_emails.json", "a") as f:
                f.write(json.dumps(log_data) + "\n")
                
        except Exception as e:
            print(f"Could not log email: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = EmailSender()
    app.run()