import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from ringcentral import SDK
import time
import os

# === CONFIGURATION ===
CLIENT_ID = 'e6wKvkFN9STfw9O0yK8pfo'
CLIENT_SECRET = 'YMIor3Eb0DTccLYu87C5BL8qFWfT9aDbBfZLfIaQRExA'
SERVER_URL = 'https://platform.ringcentral.com'
USERNAME = '+16282305518'
EXTENSION = ''
PASSWORD = 'Alfie007!'

def load_contacts(file_path):
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        if 'PhoneNumber' not in df.columns:
            raise ValueError("Spreadsheet must contain a 'PhoneNumber' column.")
        return df
    except Exception as e:
        messagebox.showerror("Error loading file", str(e))
        return pd.DataFrame()

def send_messages(contacts_df, message, media_path=None):
    try:
        rcsdk = SDK(CLIENT_ID, CLIENT_SECRET, SERVER_URL)
        platform = rcsdk.platform()
        platform.login(USERNAME, EXTENSION, PASSWORD)

        for _, row in contacts_df.iterrows():
            to_number = row['PhoneNumber']
            personalized_message = message
            if 'Name' in row:
                personalized_message = message.replace('{name}', str(row['Name']))

            body = {
                'from': {'phoneNumber': USERNAME},
                'to': [{'phoneNumber': to_number}],
                'text': personalized_message
            }

            if media_path:
                files = [media_path]
                endpoint = '/restapi/v1.0/account/~/extension/~/mms'
                response = platform.post(endpoint, body, files=files)
            else:
                response = platform.post('/restapi/v1.0/account/~/extension/~/sms', body)

            print(f"Sent to {to_number}: {response.json()['id']}")
            time.sleep(1)
        messagebox.showinfo("Success", "Messages sent successfully.")
    except Exception as e:
        messagebox.showerror("Error sending messages", str(e))

class MessagingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RingCentral Bulk Sender")

        self.file_path = ""
        self.media_path = None

        tk.Label(root, text="Message (use {name} for personalization):").pack()
        self.message_entry = tk.Text(root, height=5, width=60)
        self.message_entry.pack()

        tk.Button(root, text="Upload Contacts (.csv or .xlsx)", command=self.upload_file).pack(pady=5)
        tk.Button(root, text="Attach Image (optional MMS)", command=self.attach_media).pack(pady=5)
        tk.Button(root, text="Send Messages", command=self.send).pack(pady=10)

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Spreadsheets", "*.xlsx *.csv")])
        if self.file_path:
            messagebox.showinfo("File Selected", os.path.basename(self.file_path))

    def attach_media(self):
        self.media_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.gif")])
        if self.media_path:
            messagebox.showinfo("Media Selected", os.path.basename(self.media_path))

    def send(self):
        if not self.file_path:
            messagebox.showwarning("Missing File", "Please upload a contacts spreadsheet.")
            return
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Empty Message", "Please enter a message.")
            return

        contacts_df = load_contacts(self.file_path)
        if not contacts_df.empty:
            send_messages(contacts_df, message, self.media_path)

if __name__ == '__main__':
    root = tk.Tk()
    app = MessagingApp(root)
    root.mainloop()
