import tkinter as tk
from tkinter import ttk
import threading
import requests
import random
import string
import config
from datetime import datetime
import os
import json
import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sys

# ---------------------------- UI ----------------------------
class MailerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mailer Progress")
        self.root.geometry("300x120")
        self.root.resizable(False, False)

        self.counter_label = ttk.Label(self.root, text="Progress: 0/0", font=("Arial", 12))
        self.counter_label.pack(pady=10)

        self.current_email_label = ttk.Label(self.root, text="Current: None", font=("Arial", 10))
        self.current_email_label.pack(pady=5)

        self.close_button = ttk.Button(self.root, text="Close", command=self.root.destroy, state="disabled")
        self.close_button.pack(pady=10)

    def update_progress(self, current_email, index, total):
        self.counter_label.config(text=f"Progress: {index}/{total}")
        self.current_email_label.config(text=f"Current: {current_email}")
        self.root.update_idletasks()

    def enable_close(self):
        self.close_button.config(state="normal")
        self.root.update_idletasks()

# ---------------------------- Helpers ----------------------------
def parse_custom_variables(variables_str):
    variables = {}
    if not variables_str:
        return variables
    variable_pairs = variables_str.split(',')
    for pair in variable_pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            variables[key.strip()] = value.strip()
    return variables

def replace_variables(text, dynamic_variables, custom_variables):
    for var, value in dynamic_variables.items():
        text = text.replace(var, value)
    for var, value in custom_variables.items():
        text = text.replace(var, value)
    return text

def fetch_batch_data(batch_id):
    try:
        url = config.API_URL
        params = {'api_key': config.API_KEY, 'api_pass': config.API_PASS, 'action': 'get_batch_id_to_shoot', 'id': batch_id}
        response = requests.get(url, params=params)
        response_data = response.json()
        if response_data.get("status") == "success" and response_data.get("data"):
            return response_data["data"]
        else:
            return []
    except Exception as e:
        print(f"Error fetching batch data: {e}")
        return []

def download_file(url, download_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return download_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def create_gmail_service(auth_json_path):
    try:
        creds = Credentials.from_authorized_user_file(auth_json_path, ["https://www.googleapis.com/auth/gmail.send"])
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Gmail service: {e}")
        return None

def send_email(service, sender, to, subject, body, attachment_path=None):
    try:
        message = MIMEMultipart()
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        if "<html" not in body.lower():
            body = f"<html><body>{body}</body></html>"

        message.attach(MIMEText(body, "html"))

        if attachment_path and os.path.exists(attachment_path):
            content_type, encoding = mimetypes.guess_type(attachment_path)
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            main_type, sub_type = content_type.split("/", 1)

            with open(attachment_path, "rb") as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent_result = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return sent_result
    except Exception as e:
        print(f"Error sending email to {to}: {e}")
        return None

# ---------------------------- Mailer Process ----------------------------
def mailer_process(batch_id, ui: MailerUI):
    batch_data_list = fetch_batch_data(batch_id)
    if not batch_data_list:
        print(f"No batch data found for batch ID {batch_id}")
        ui.enable_close()
        return

    for batch_data in batch_data_list:
        tmp_folder = "tmp"
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)

        g_auth_json_path = os.path.join(tmp_folder, f"{batch_data['id']}_g_auth.json")
        g_auth_json = json.loads(batch_data['g_auth_json'])
        with open(g_auth_json_path, 'w') as f:
            json.dump(g_auth_json, f)

        attachments_url = batch_data.get('attachments')
        attachment_path = None
        if attachments_url:
            ext = os.path.splitext(attachments_url)[1] or ".bin"
            attachment_path = os.path.join(tmp_folder, f"{batch_data['id']}_attachment{ext}")
            download_file(attachments_url, attachment_path)

        service = create_gmail_service(g_auth_json_path)
        if not service:
            continue

        original_subject = batch_data['subject'].replace("subject :", "").strip()
        original_content = batch_data['content'].replace("body :", "").strip()
        custom_variables = parse_custom_variables(batch_data.get('variables', ""))

        emails = [e.strip() for e in batch_data['emails'].split(',') if e.strip()]
        total_emails = len(emails)

        for idx, email in enumerate(emails, start=1):
            dynamic_variables = {
                "{{user}}": email.split("@")[0],
                "{{email}}": email,
                "{{date}}": datetime.now().strftime("%Y-%m-%d"),
                "{{time}}": datetime.now().strftime("%H:%M:%S"),
                "{{random_number}}": str(random.randint(10000, 99999)),
                "{{random_string}}": ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            }

            modified_subject = replace_variables(original_subject, dynamic_variables, custom_variables)
            modified_content = replace_variables(original_content, dynamic_variables, custom_variables)

            # Update UI
            ui.update_progress(email, idx, total_emails)
            send_email(service, "me", email, modified_subject, modified_content, attachment_path if attachment_path else None)

        # Cleanup
        try:
            if os.path.exists(g_auth_json_path):
                os.remove(g_auth_json_path)
            if attachment_path and os.path.exists(attachment_path):
                os.remove(attachment_path)
        except Exception as e:
            print(f"Error cleaning up files: {e}")

        # Mark batch complete
        try:
            url = config.API_URL
            params = {
                'api_key': config.API_KEY,
                'api_pass': config.API_PASS,
                'action': 'update_batch_id_to_shoot_complete',
                'id': batch_data['id']
            }
            requests.get(url, params=params)
        except Exception as e:
            print(f"Error updating batch complete: {e}")

    # Enable close button after all emails sent
    ui.enable_close()

# ---------------------------- Main ----------------------------
def main():
    if len(sys.argv) < 2:
        print("Error: Please provide batch ID as argument.")
        print("Usage: python mailer_ui.py <batch_id>")
        return

    batch_id = sys.argv[1]
    ui = MailerUI()

    threading.Thread(target=mailer_process, args=(batch_id, ui), daemon=True).start()

    ui.root.mainloop()


if __name__ == "__main__":
    main()
