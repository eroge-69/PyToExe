#!/usr/bin/env python3
"""
Email Sender Script with Dynamic Content Replacement
Sends HTML emails to multiple recipients using various methods.
"""

import smtplib
import os
import time
import subprocess
import tempfile
import random
import string
import base64
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self):
        self.config_dir = Path("config")
        self.logs_dir = Path("logs")
        self.log_file = self.logs_dir / "delivery_log.txt"
        
        # Initialize dynamic data
        self.dynamic_data = {}
        self._load_dynamic_data()
        
    def _load_dynamic_data(self):
        """Load and generate dynamic data for placeholders."""
        # Basic placeholders
        self.dynamic_data["##IP##"] = self._generate_random_ip()
        self.dynamic_data["[-IP-]"] = self._generate_random_ip()
        
        # Link from config (if exists)
        config_link = self.read_config("link.txt")
        self.dynamic_data["##LINK##"] = config_link if config_link else "https://example.com"
        self.dynamic_data["[-LINK-]"] = config_link if config_link else "https://example.com"
        
        # Current date and time
        now = datetime.now()
        self.dynamic_data["##DATE##"] = now.strftime("%Y-%m-%d")
        self.dynamic_data["[-DATE-]"] = now.strftime("%Y-%m-%d")
        self.dynamic_data["##TIME##"] = now.strftime("%H:%M:%S")
        self.dynamic_data["[-TIME-]"] = now.strftime("%H:%M:%S")
        self.dynamic_data["[-Time-]"] = now.strftime("%H:%M:%S")
        
        # Time components
        self.dynamic_data["[-Seconds-]"] = str(now.second)
        self.dynamic_data["[-Minutes-]"] = str(now.minute)
        self.dynamic_data["[-Hours-]"] = str(now.hour)
        self.dynamic_data["[-LongTime-]"] = f"{now.hour} hours, {now.minute} minutes, {now.second} seconds"
        self.dynamic_data["[-LongDate-]"] = now.strftime("%A, %B %d, %Y")
        self.dynamic_data["[-ShortDate-]"] = now.strftime("%B")
        self.dynamic_data["[-DATETIME-]"] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.dynamic_data["[-DATEJP-]"] = now.strftime("%Y %m %d %H:%M:%S")
        
        # Random numbers and characters (1-10)
        for i in range(1, 11):
            self.dynamic_data[f"[-CHAR{i}-]"] = random.choice(string.ascii_letters)
            self.dynamic_data[f"[-NUMBER{i}-]"] = str(random.randint(0, 9))
        
        # Random numbers and text (10 characters)
        self.dynamic_data["##NUMBER10##"] = ''.join(random.choices(string.digits, k=10))
        self.dynamic_data["[-NUMBER10-]"] = ''.join(random.choices(string.digits, k=10))
        self.dynamic_data["##CHAR10##"] = ''.join(random.choices(string.ascii_letters, k=10))
        self.dynamic_data["[-CHAR10-]"] = ''.join(random.choices(string.ascii_letters, k=10))
        self.dynamic_data["##TEXT10##"] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.dynamic_data["[-RANDOM-]"] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Random data with configurable length
        self.dynamic_data["[-random_number_10-]"] = ''.join(random.choices(string.digits, k=10))
        self.dynamic_data["[-random_letter_10-]"] = ''.join(random.choices(string.ascii_letters, k=10))
        self.dynamic_data["[-random_letterupp_10-]"] = ''.join(random.choices(string.ascii_uppercase, k=10))
        self.dynamic_data["[-random_letterlow_10-]"] = ''.join(random.choices(string.ascii_lowercase, k=10))
        self.dynamic_data["[-random_letternumber_10-]"] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.dynamic_data["[-random_letternumberlow_10-]"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.dynamic_data["[-random_letternumberupp_10-]"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Device data
        self.dynamic_data["##APPLE_PHONE##"] = self._get_apple_phone_data()
        self.dynamic_data["[-APPLE_PHONE-]"] = self._get_apple_phone_data()
        self.dynamic_data["##APPLE_APPS##"] = self._get_apple_apps_data()
        self.dynamic_data["[-APPLE_APPS-]"] = self._get_apple_apps_data()
        self.dynamic_data["##APPLE_MACBOOK##"] = self._get_apple_macbook_data()
        self.dynamic_data["[-APPLE_MACBOOK-]"] = self._get_apple_macbook_data()
        self.dynamic_data["##ANDROID_OS##"] = self._get_android_os_data()
        self.dynamic_data["[-ANDROID_OS-]"] = self._get_android_os_data()
        self.dynamic_data["##ANDROID_PHONE##"] = self._get_android_phone_data()
        self.dynamic_data["[-ANDROID_BROWSER-]"] = self._get_android_browser_data()
        
        # Location data
        self.dynamic_data["##COUNTRY##"] = self._get_random_country()
        self.dynamic_data["[-random_country-]"] = self._get_random_country()
        self.dynamic_data["[-RANDOM_COUNTRY-]"] = self._get_random_country()
        self.dynamic_data["##COUNTRY_STATE##"] = self._get_random_country_state()
        self.dynamic_data["[-City-]"] = self._get_random_city()
        self.dynamic_data["[-Company-]"] = self._get_random_company()
        
        # User agent
        self.dynamic_data["##USERAGENT##"] = self._get_random_user_agent()
        
        # Fake data
        self.dynamic_data["[-FAKE_NAME-]"] = self._get_fake_name()
        self.dynamic_data["[-FAKE_ADDRESS-]"] = self._get_fake_address()
        self.dynamic_data["[-FAKE_DOB-]"] = self._get_fake_dob()
        self.dynamic_data["[-FAKE_PHONE-]"] = self._get_fake_phone()
        self.dynamic_data["[-FAKE_MAIL-]"] = self._get_fake_email()
        self.dynamic_data["[-FAKE_CARD-]"] = self._get_fake_credit_card()
        self.dynamic_data["[-VIN_NUMBER-]"] = self._get_fake_vin()
        self.dynamic_data["[-BUSINESS_EMAIL-]"] = self._get_fake_business_email()
        self.dynamic_data["[-INSTITUTE-]"] = self._get_fake_institute()
        self.dynamic_data["[-COMPANY_ADDRESS-]"] = self._get_fake_company_address()
        self.dynamic_data["[-JOB_TITLE-]"] = self._get_fake_job_title()
        
        # Random email
        self.dynamic_data["[-random_email-]"] = self._get_random_email()
        
        # SMTP data (will be filled later)
        smtp_config = self.read_config("smtp.txt")
        if smtp_config:
            smtp_parts = smtp_config.split('|')
            if len(smtp_parts) >= 2:
                self.dynamic_data["[-SMTPDOMAIN-]"] = smtp_parts[0]
                self.dynamic_data["[-SMTPUSER-]"] = smtp_parts[2]
                self.dynamic_data["[-DOMAINSENDER-]"] = smtp_parts[0]
        else:
            self.dynamic_data["[-SMTPDOMAIN-]"] = "smtp.example.com"
            self.dynamic_data["[-SMTPUSER-]"] = "user@example.com"
            self.dynamic_data["[-DOMAINSENDER-]"] = "smtp.example.com"
        
        # Sender email
        sender_email = self.read_config("from_email.txt")
        self.dynamic_data["[-Sender_Email-]"] = sender_email if sender_email else "noreply@example.com"
        
        # Email link
        self.dynamic_data["[-EMAIL_LINK-]"] = f"mailto:{sender_email}" if sender_email else "mailto:noreply@example.com"
        
        # Root domain
        if sender_email:
            domain = sender_email.split('@')[1] if '@' in sender_email else "example.com"
            self.dynamic_data["[-ROOTDOMAIN-]"] = domain.split('.')[0] if '.' in domain else domain
        else:
            self.dynamic_data["[-ROOTDOMAIN-]"] = "example"
        
        # Random hex
        self.dynamic_data["[-RNDHEX-]"] = ''.join(random.choices(string.hexdigits.lower(), k=32))
        self.dynamic_data["[-RND-]"] = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
    def _generate_random_ip(self):
        """Generate a random IP address."""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _get_apple_phone_data(self):
        """Get random Apple phone data."""
        phones = [
            "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15 Plus", "iPhone 15",
            "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14 Plus", "iPhone 14",
            "iPhone 13 Pro Max", "iPhone 13 Pro", "iPhone 13", "iPhone 13 mini"
        ]
        return random.choice(phones)
    
    def _get_apple_apps_data(self):
        """Get random Apple apps data."""
        apps = [
            "Safari", "Mail", "Messages", "FaceTime", "Photos", "Camera",
            "Maps", "Weather", "Notes", "Calendar", "App Store", "iTunes"
        ]
        return random.choice(apps)
    
    def _get_apple_macbook_data(self):
        """Get random Apple MacBook data."""
        macbooks = [
            "MacBook Pro 16-inch", "MacBook Pro 14-inch", "MacBook Pro 13-inch",
            "MacBook Air 15-inch", "MacBook Air 13-inch", "MacBook Pro M3",
            "MacBook Air M2", "MacBook Pro M2"
        ]
        return random.choice(macbooks)
    
    def _get_android_os_data(self):
        """Get random Android OS data."""
        android_versions = [
            "Android 14", "Android 13", "Android 12", "Android 11",
            "Android 10", "Android 9", "Android 8", "Android 7"
        ]
        return random.choice(android_versions)
    
    def _get_android_phone_data(self):
        """Get random Android phone data."""
        phones = [
            "Samsung Galaxy S24", "Samsung Galaxy S23", "Samsung Galaxy S22",
            "Google Pixel 8", "Google Pixel 7", "Google Pixel 6",
            "OnePlus 12", "OnePlus 11", "OnePlus 10",
            "Xiaomi 14", "Xiaomi 13", "Xiaomi 12"
        ]
        return random.choice(phones)
    
    def _get_android_browser_data(self):
        """Get random Android browser data."""
        browsers = [
            "Chrome", "Firefox", "Samsung Internet", "Opera", "Edge",
            "Brave", "DuckDuckGo", "Vivaldi"
        ]
        return random.choice(browsers)
    
    def _get_random_country(self):
        """Get random country."""
        countries = [
            "United States", "Canada", "United Kingdom", "Germany", "France",
            "Australia", "Japan", "South Korea", "India", "Brazil",
            "Mexico", "Spain", "Italy", "Netherlands", "Sweden"
        ]
        return random.choice(countries)
    
    def _get_random_country_state(self):
        """Get random country state."""
        states = [
            "California", "Texas", "Florida", "New York", "Illinois",
            "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan",
            "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts"
        ]
        return random.choice(states)
    
    def _get_random_city(self):
        """Get random city."""
        cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
            "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte"
        ]
        return random.choice(cities)
    
    def _get_random_company(self):
        """Get random company."""
        companies = [
            "Apple Inc.", "Microsoft Corporation", "Google LLC", "Amazon.com Inc.",
            "Tesla Inc.", "Meta Platforms Inc.", "Netflix Inc.", "Adobe Inc.",
            "Salesforce Inc.", "Oracle Corporation", "Intel Corporation", "Cisco Systems"
        ]
        return random.choice(companies)
    
    def _get_random_user_agent(self):
        """Get random user agent."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/118.0 Firefox/118.0"
        ]
        return random.choice(user_agents)
    
    def _get_fake_name(self):
        """Get random fake name."""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _get_fake_address(self):
        """Get random fake address."""
        streets = ["Main St", "Oak Ave", "Pine Rd", "Elm St", "Maple Dr"]
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        states = ["NY", "CA", "IL", "TX", "AZ"]
        return f"{random.randint(100, 9999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"
    
    def _get_fake_dob(self):
        """Get random fake date of birth."""
        year = random.randint(1960, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month:02d}/{day:02d}/{year}"
    
    def _get_fake_phone(self):
        """Get random fake phone number."""
        return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    def _get_fake_email(self):
        """Get random fake email."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@{random.choice(domains)}"
    
    def _get_fake_credit_card(self):
        """Get random fake credit card number."""
        return f"{random.randint(4000, 4999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    
    def _get_fake_vin(self):
        """Get random fake VIN number."""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=17))
    
    def _get_fake_business_email(self):
        """Get random fake business email."""
        companies = ["company", "corp", "inc", "llc", "enterprise"]
        domains = ["com", "net", "org"]
        username = ''.join(random.choices(string.ascii_lowercase, k=6))
        company = random.choice(companies)
        domain = random.choice(domains)
        return f"{username}@{company}.{domain}"
    
    def _get_fake_institute(self):
        """Get random fake institute."""
        institutes = [
            "Harvard University", "Stanford University", "MIT", "Yale University",
            "Princeton University", "Columbia University", "University of Chicago",
            "Duke University", "Northwestern University", "Johns Hopkins University"
        ]
        return random.choice(institutes)
    
    def _get_fake_company_address(self):
        """Get random fake company address."""
        companies = ["Tech Corp", "Innovation Inc", "Global Solutions", "Digital Systems"]
        streets = ["Business Blvd", "Corporate Ave", "Enterprise Rd", "Commerce St"]
        cities = ["New York", "Los Angeles", "Chicago", "Houston"]
        states = ["NY", "CA", "IL", "TX"]
        return f"{random.choice(companies)}, {random.randint(100, 9999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"
    
    def _get_fake_job_title(self):
        """Get random fake job title."""
        titles = [
            "Software Engineer", "Product Manager", "Data Analyst", "Marketing Specialist",
            "Sales Representative", "Human Resources Manager", "Financial Analyst",
            "Project Manager", "Business Analyst", "Customer Success Manager"
        ]
        return random.choice(titles)
    
    def _get_random_email(self):
        """Get random email address."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"{username}@{random.choice(domains)}"
    
    def _replace_dynamic_content(self, content, recipient):
        """Replace dynamic placeholders in content."""
        # Email-specific placeholders
        email_parts = recipient.split('@')
        username = email_parts[0] if len(email_parts) > 1 else recipient
        domain = email_parts[1] if len(email_parts) > 1 else "unknown"
        
        # Generate domain name (remove .com, .org, etc.)
        domain_name = domain.split('.')[0] if '.' in domain else domain
        
        # Email censored (show first 3 chars, then ***, then @domain)
        email_censored = f"{username[:3]}***@{domain}" if len(username) > 3 else f"{username}***@{domain}"
        
        # Email base64 encoded
        email_b64 = base64.b64encode(recipient.encode()).decode()
        
        # Update dynamic data with email-specific values
        email_data = {
            "##EMAIL##": recipient,
            "[-EMAIL-]": recipient,
            "##EMAIL_CENSORED##": email_censored,
            "##EMAILB64##": email_b64,
            "[-EMAILB64-]": email_b64,
            "##UNAME##": username,
            "[-UNAME-]": username,
            "##UDOMAIN##": domain,
            "[-UDOMAIN-]": domain,
            "##NAMEDOMAIN##": domain_name
        }
        
        # Combine all dynamic data
        all_data = {**self.dynamic_data, **email_data}
        
        # Replace all placeholders
        for placeholder, value in all_data.items():
            content = content.replace(placeholder, str(value))
        
        # Handle configurable length placeholders (e.g., [-CHAR$5$-])
        char_pattern = r'\[-CHAR\$(\d+)\$\-\]'
        number_pattern = r'\[-NUMBER\$(\d+)\$\-\]'
        random_pattern = r'\[-RANDOM\$(\d+)\$\-\]'
        
        # Replace CHAR$n$ patterns
        content = re.sub(char_pattern, lambda m: ''.join(random.choices(string.ascii_letters, k=int(m.group(1)))), content)
        
        # Replace NUMBER$n$ patterns
        content = re.sub(number_pattern, lambda m: ''.join(random.choices(string.digits, k=int(m.group(1)))), content)
        
        # Replace RANDOM$n$ patterns
        content = re.sub(random_pattern, lambda m: ''.join(random.choices(string.ascii_letters + string.digits, k=int(m.group(1)))), content)
        
        return content
    
    def read_config(self, filename):
        """Read configuration from a file."""
        filepath = self.config_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def read_recipients(self):
        """Read recipient list from file."""
        recipients = self.read_config("recipient.txt")
        if recipients:
            return [email.strip() for email in recipients.split('\n') if email.strip()]
        return []
    
    def log_delivery(self, recipient, status, message=""):
        """Log email delivery status."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp}|{recipient}|{status}|{message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def send_email_smtp(self, recipient):
        """Send email using SMTP configuration."""
        try:
            smtp_config = self.read_config("smtp.txt")
            if not smtp_config:
                return False, "SMTP configuration not found"
            
            # Parse SMTP configuration
            smtp_parts = smtp_config.split('|')
            if len(smtp_parts) != 4:
                return False, "Invalid SMTP configuration format"
            
            smtp_host, smtp_port, smtp_user, smtp_pass = smtp_parts
            smtp_port = int(smtp_port)
            
            # Create message
            msg = self._create_email_message(recipient)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            return True, "Email sent successfully via SMTP"
            
        except Exception as e:
            return False, f"SMTP error: {str(e)}"
    
    def send_email_system_mail(self, recipient):
        """Send email using system mail command."""
        try:
            # Create message
            msg = self._create_email_message(recipient)
            
            # Convert message to string
            email_content = msg.as_string()
            
            # Use system mail command
            result = subprocess.run(
                ['mail', '-s', msg['Subject'], '-a', 'Content-Type: text/html', recipient],
                input=email_content,
                text=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                return True, "Email sent successfully via system mail"
            else:
                return False, f"System mail error: {result.stderr}"
                
        except FileNotFoundError:
            return False, "System mail command not available"
        except Exception as e:
            return False, f"System mail error: {str(e)}"
    
    def preview_email(self, recipient):
        """Preview email content without sending."""
        try:
            msg = self._create_email_message(recipient)
            
            # Extract HTML content
            html_content = ""
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        html_content = payload.decode('utf-8')
                    else:
                        html_content = str(payload)
                    break
            
            if not html_content:
                html_content = self.read_config("html_letter.html") or "<p>No content</p>"
            
            # Create temporary file for preview
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            print(f"\n📧 Email Preview for {recipient}:")
            print(f"From: {msg['From']}")
            print(f"Subject: {msg['Subject']}")
            print(f"Preview saved to: {temp_file}")
            
            # Try to open in default browser
            try:
                subprocess.run(['open', temp_file], check=False)
            except:
                pass
            
            return True, f"Email preview created: {temp_file}"
            
        except Exception as e:
            return False, f"Preview error: {str(e)}"
    
    def _create_email_message(self, recipient):
        """Create email message object with dynamic content replacement."""
        from_name = self.read_config("from_name.txt") or "Email Sender"
        from_email = self.read_config("from_email.txt") or "noreply@example.com"
        subject = self.read_config("subject.txt") or "Message"
        html_content = self.read_config("html_letter.html") or "<p>No content</p>"
        
        # Replace dynamic content
        html_content = self._replace_dynamic_content(html_content, recipient)
        subject = self._replace_dynamic_content(subject, recipient)
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        return msg
    
    def send_email(self, recipient, method="auto"):
        """Send email using specified method."""
        if method == "auto":
            # Try SMTP first, then system mail, then preview
            success, message = self.send_email_smtp(recipient)
            if success:
                print(f"✓ {message} to {recipient}")
                self.log_delivery(recipient, "SUCCESS", "SMTP")
                return True
            
            success, message = self.send_email_system_mail(recipient)
            if success:
                print(f"✓ {message} to {recipient}")
                self.log_delivery(recipient, "SUCCESS", "System Mail")
                return True
            
            # Fall back to preview mode
            print(f"⚠️  Could not send email to {recipient}: {message}")
            print("Creating email preview instead...")
            success, message = self.preview_email(recipient)
            if success:
                print(f"✓ {message}")
                self.log_delivery(recipient, "PREVIEW", message)
                return True
            else:
                print(f"✗ Failed to create preview: {message}")
                self.log_delivery(recipient, "FAILED", message)
                return False
        
        elif method == "smtp":
            success, message = self.send_email_smtp(recipient)
            if success:
                print(f"✓ {message} to {recipient}")
                self.log_delivery(recipient, "SUCCESS", "SMTP")
            else:
                print(f"✗ Failed to send email to {recipient}: {message}")
                self.log_delivery(recipient, "FAILED", message)
            return success
        
        elif method == "system":
            success, message = self.send_email_system_mail(recipient)
            if success:
                print(f"✓ {message} to {recipient}")
                self.log_delivery(recipient, "SUCCESS", "System Mail")
            else:
                print(f"✗ Failed to send email to {recipient}: {message}")
                self.log_delivery(recipient, "FAILED", message)
            return success
        
        elif method == "preview":
            success, message = self.preview_email(recipient)
            if success:
                print(f"✓ {message}")
                self.log_delivery(recipient, "PREVIEW", message)
            else:
                print(f"✗ Failed to create preview: {message}")
                self.log_delivery(recipient, "FAILED", message)
            return success
        
        else:
            print(f"✗ Unknown method: {method}")
            return False
    
    def send_bulk_emails(self, method="auto"):
        """Send emails to all recipients."""
        recipients = self.read_recipients()
        
        if not recipients:
            print("No recipients found in config/recipient.txt")
            return
        
        print(f"Starting to send emails to {len(recipients)} recipients using method: {method}")
        print("-" * 50)
        
        successful = 0
        failed = 0
        
        for i, recipient in enumerate(recipients, 1):
            print(f"[{i}/{len(recipients)}] Processing {recipient}...")
            
            # Regenerate dynamic data for each email
            self._load_dynamic_data()
            
            if self.send_email(recipient, method):
                successful += 1
            else:
                failed += 1
            
            # Add delay between emails to avoid rate limiting
            if i < len(recipients) and method != "preview":
                time.sleep(2)
        
        print("-" * 50)
        print(f"Email processing completed!")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Check {self.log_file} for detailed logs.")

def main():
    """Main function."""
    print("GX40 Sender V.4.2 - Email Sender with Dynamic Content")
    print("=" * 60)
    
    # Check for required configuration files
    required_files = [
        "from_name.txt", 
        "from_email.txt",
        "subject.txt",
        "html_letter.html",
        "recipient.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not (Path("config") / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("Error: Missing required configuration files:")
        for file in missing_files:
            print(f"  - config/{file}")
        print("\nPlease create all required configuration files before running the script.")
        return
    
    # Check if SMTP configuration exists
    smtp_exists = (Path("config") / "smtp.txt").exists()
    if not smtp_exists:
        print("⚠️  SMTP configuration not found (config/smtp.txt)")
        print("The script will use alternative methods:")
        print("  1. System mail command (if available)")
        print("  2. Email preview mode")
    
    # Initialize and run email sender
    sender = EmailSender()
    
    # Show configuration
    recipients = sender.read_recipients()
    print(f"Found {len(recipients)} recipients:")
    for recipient in recipients:
        print(f"  - {recipient}")
    
    print(f"\nFrom: {sender.read_config('from_name.txt')} <{sender.read_config('from_email.txt')}>")
    print(f"Subject: {sender.read_config('subject.txt')}")
    
    # Show available placeholders
    print("\n📋 Available Dynamic Placeholders:")
    print("Basic Placeholders:")
    print("  ##IP## / [-IP-] - Random IP Address")
    print("  ##LINK## / [-LINK-] - Link from config/link.txt")
    print("  ##DATE## / [-DATE-] - Current date")
    print("  ##TIME## / [-TIME-] - Current time")
    print("  ##EMAIL## / [-EMAIL-] - Target email")
    print("  ##UNAME## / [-UNAME-] - Username from email")
    print("  ##UDOMAIN## / [-UDOMAIN-] - Domain from email")
    print("  ##EMAILB64## / [-EMAILB64-] - Email (base64)")
    
    print("\nRandom Data:")
    print("  [-CHAR1-] to [-CHAR10-] - Random characters")
    print("  [-NUMBER1-] to [-NUMBER10-] - Random numbers")
    print("  [-random_number_10-] - Random 10-digit number")
    print("  [-random_letter_10-] - Random 10-letter string")
    print("  [-random_letterupp_10-] - Random uppercase letters")
    print("  [-random_letterlow_10-] - Random lowercase letters")
    print("  [-random_letternumber_10-] - Random letters and numbers")
    print("  [-CHAR$n$-] / [-NUMBER$n$-] / [-RANDOM$n$-] - Configurable length")
    
    print("\nTime & Date:")
    print("  [-Seconds-] / [-Minutes-] / [-Hours-] - Time components")
    print("  [-LongTime-] / [-LongDate-] / [-ShortDate-] - Formatted time/date")
    print("  [-DATETIME-] / [-DATEJP-] - Date and time formats")
    
    print("\nDevice Data:")
    print("  [-APPLE_PHONE-] / [-APPLE_APPS-] / [-APPLE_MACBOOK-] - Apple devices")
    print("  [-ANDROID_OS-] / [-ANDROID_BROWSER-] - Android data")
    
    print("\nLocation Data:")
    print("  [-random_country-] / [-City-] / [-Company-] - Location info")
    
    print("\nFake Data:")
    print("  [-FAKE_NAME-] / [-FAKE_ADDRESS-] / [-FAKE_DOB-] - Personal info")
    print("  [-FAKE_PHONE-] / [-FAKE_MAIL-] / [-FAKE_CARD-] - Contact info")
    print("  [-VIN_NUMBER-] / [-BUSINESS_EMAIL-] / [-INSTITUTE-] - Business data")
    print("  [-COMPANY_ADDRESS-] / [-JOB_TITLE-] - Professional info")
    
    print("\nSystem Data:")
    print("  [-SMTPDOMAIN-] / [-SMTPUSER-] / [-Sender_Email-] - SMTP info")
    print("  [-EMAIL_LINK-] / [-ROOTDOMAIN-] / [-DOMAINSENDER-] - Email links")
    print("  [-RND-] / [-RNDHEX-] - Random strings")
    
    # Choose sending method
    if smtp_exists:
        print("\nSending methods available:")
        print("1. Auto (try SMTP → System Mail → Preview)")
        print("2. SMTP only")
        print("3. System Mail only")
        print("4. Preview only")
        
        method_choice = input("\nChoose method (1-4, default=1): ").strip()
        method_map = {
            "1": "auto",
            "2": "smtp", 
            "3": "system",
            "4": "preview"
        }
        method = method_map.get(method_choice, "auto")
    else:
        print("\nSending methods available:")
        print("1. Auto (try System Mail → Preview)")
        print("2. System Mail only")
        print("3. Preview only")
        
        method_choice = input("\nChoose method (1-3, default=1): ").strip()
        method_map = {
            "1": "auto",
            "2": "system",
            "3": "preview"
        }
        method = method_map.get(method_choice, "auto")
    
    response = input(f"\nDo you want to proceed with {method} method? (y/N): ")
    if response.lower() in ['y', 'yes']:
        sender.send_bulk_emails(method)
    else:
        print("Email sending cancelled.")

if __name__ == "__main__":
    main() 