import imaplib
import email
import os
import subprocess
import platform
import time
from pathlib import Path
import win32print
import win32api

# --- EDIT THESE CREDENTIALS AND KEYWORDS ---
# Gmail settings
GMAIL_HOST = 'imap.gmail.com'
GMAIL_USER = 'farmaciazenatto@gmail.com'  # Your Gmail address
GMAIL_PASSWORD = 'Brugim@_76!'  # App password (if 2FA) or regular password
GMAIL_KEYWORDS = ['promemoria', 'ricette', 'ricetta']  # Subject keywords to match

# Custom IMAP settings
IMAP_HOST = 'imapmail.virgilio.it'  # e.g., imapmail.virgilio.it
IMAP_USER = 'f.zenatto@virgilio.it'  # Your IMAP email
IMAP_PASSWORD = 'Brugimacl@si5!'  # IMAP password
IMAP_KEYWORDS = ['promemoria', 'ricette', 'ricetta', 'Invio documenti di fatturazione']  # Subject keywords to match
# --- END OF EDIT SECTION ---

# Temp folder for PDFs
download_dir = Path('./temp_pdfs')
download_dir.mkdir(exist_ok=True)

# List of accounts: (name, host, user, password, keywords, folder)
accounts = [
    ('Gmail', GMAIL_HOST, GMAIL_USER, GMAIL_PASSWORD, GMAIL_KEYWORDS, '[Gmail]/All Mail'),
    ('IMAP', IMAP_HOST, IMAP_USER, IMAP_PASSWORD, IMAP_KEYWORDS, 'INBOX')
]

def print_pdf(filename):
    """Print PDF using win32print on Windows, or system command on other platforms.
    Returns True if printing succeeds, False otherwise."""
    system = platform.system()
    try:
        if system == 'Windows':
            # Use win32print to send to default printer
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(0, "print", str(filename), None, ".", 0)
            print(f"Printed via win32print: {filename}")
            return True
        elif system == 'Darwin':  # macOS
            result = subprocess.run(['lpr', filename], check=True, capture_output=True, text=True)
            print(f"Printed via lpr: {filename}")
            return True
        elif system == 'Linux':
            result = subprocess.run(['lp', filename], check=True, capture_output=True, text=True)
            print(f"Printed via lp: {filename}")
            return True
        else:
            print(f"Printing not supported on {system}; open {filename} manually.")
            return False
    except Exception as e:
        print(f"Printing error for {filename}: {e}")
        return False

def connect_with_retry(host, user, password, folder, retries=3, timeout=30):
    """Attempt to connect to IMAP server with retries and timeout."""
    for attempt in range(retries):
        try:
            # Connect with timeout
            mailbox = imaplib.IMAP4_SSL(host, timeout=timeout)
            mailbox.login(user, password)
            mailbox.select(folder)
            return mailbox
        except Exception as e:
            print(f"Connection attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            else:
                raise Exception(f"Failed to connect to {host} after {retries} attempts: {e}")

for name, host, user, password, keywords, folder in accounts:
    try:
        print(f"Connecting to {name} ({host})...")
        mailbox = connect_with_retry(host, user, password, folder)
        # Build search query for multiple keywords (OR condition)
        search_terms = ' OR '.join(f'SUBJECT "{keyword}"' for keyword in keywords)
        search_query = f'(UNSEEN {search_terms})'
        *, data = mailbox.uid('search', None, search_query)
        if not data[0]:
            print(f"No matching emails in {name}.")
            mailbox.logout()
            continue
        email_uids = data[0].split()
        for uid in email_uids:
            *, msg_data = mailbox.uid('fetch', uid, '(RFC822)')
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            # Download only PDF attachments
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart' or not part.get('Content-Disposition'):
                    continue
                filename = part.get_filename()
                if filename and filename.lower().endswith('.pdf'):
                    filepath = download_dir / filename
                    if not filepath.exists():
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        if print_pdf(str(filepath)):
                            try:
                                os.remove(str(filepath))
                                print(f"Deleted file: {filepath}")
                            except Exception as e:
                                print(f"Error deleting {filepath}: {e}")
                        else:
                            print(f"File not deleted due to printing failure: {filepath}")
                    else:
                        print(f"PDF already exists: {filename}")
            # Mark as seen to avoid reprocessing
            mailbox.uid('store', uid, '+FLAGS', '\Seen')
        mailbox.close()
        mailbox.logout()
        print(f"Processed {name} successfully.\n")
    except Exception as e:
        print(f"Error with {name}: {e}")

print("Script complete.")