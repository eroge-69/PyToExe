import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import base64
import requests
import os
import time
from datetime import datetime
import threading

# --- API CONFIG ---
API_URL_MEDIA = "http://82.29.165.149:4500/api/send-media/"
API_URL_TEXT = "http://82.29.165.149:4500/api/send/"
API_KEY = "domansahug"
SESSION_KEY = "omayasuites"

# --- LOG FOLDER ---
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

class WhatsAppSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Bulk Sender")
        self.root.geometry("800x680")
        self.root.resizable(False, False)

        self.contacts_file = None
        self.media_file = None
        self.cancel_sending = False  # flag for cancel

        # --- Message Frame ---
        frame_message = tk.LabelFrame(root, text="Message", padx=10, pady=10)
        frame_message.pack(fill="x", padx=10, pady=5)
        self.msg_entry = tk.Text(frame_message, height=5, width=90)
        self.msg_entry.pack()

        # --- File Selection Frame ---
        frame_files = tk.LabelFrame(root, text="Files", padx=10, pady=10)
        frame_files.pack(fill="x", padx=10, pady=5)

        # CSV selection
        csv_frame = tk.Frame(frame_files)
        csv_frame.pack(fill="x", pady=5)
        tk.Button(csv_frame, text="Select Contacts CSV", command=self.load_csv, width=25).pack(side="left")
        self.csv_label = tk.Label(csv_frame, text="No file selected", anchor="w")
        self.csv_label.pack(side="left", padx=10)

        # Media selection (optional)
        media_frame = tk.Frame(frame_files)
        media_frame.pack(fill="x", pady=5)
        tk.Button(media_frame, text="Select Media File (Optional)", command=self.load_media, width=25).pack(side="left")
        self.media_label = tk.Label(media_frame, text="No media selected", anchor="w")
        self.media_label.pack(side="left", padx=10)

        # --- Action Buttons Frame ---
        frame_actions = tk.Frame(root)
        frame_actions.pack(pady=10)
        self.send_button = tk.Button(frame_actions, text="Send to All", command=self.confirm_send, bg="green", fg="white", width=20)
        self.send_button.pack(side="left", padx=5)
        self.cancel_button = tk.Button(frame_actions, text="Cancel Sending", command=self.cancel_send, bg="red", fg="white", width=20)
        self.cancel_button.pack(side="left", padx=5)
        self.clear_button = tk.Button(frame_actions, text="Clear All", command=self.clear_all, bg="orange", fg="white", width=20)
        self.clear_button.pack(side="left", padx=5)

        # --- Logs Frame ---
        frame_logs = tk.LabelFrame(root, text="Logs", padx=10, pady=10)
        frame_logs.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area = scrolledtext.ScrolledText(frame_logs, height=18, width=100, state="disabled", wrap="word")
        self.log_area.pack()

    # --- Logging ---
    def log(self, message):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state="disabled")
        self.root.update()

    def save_log_excel(self, contact, status, response_code):
        today = datetime.now().strftime("%Y-%m-%d")
        logfile = os.path.join(LOG_FOLDER, f"logs_{today}.xlsx")
        log_entry = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Contact": contact,
            "Status": status,
            "ResponseCode": response_code
        }
        if os.path.exists(logfile):
            df_existing = pd.read_excel(logfile)
            df_new = pd.concat([df_existing, pd.DataFrame([log_entry])], ignore_index=True)
        else:
            df_new = pd.DataFrame([log_entry])
        df_new.to_excel(logfile, index=False)

    # --- Load Files ---
    def load_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file:
            self.contacts_file = file
            self.csv_label.config(text=file)
            self.log(f"✅ Contacts file selected: {file}")

    def load_media(self):
        file = filedialog.askopenfilename(filetypes=[
            ("All Supported", "*.jpg *.jpeg *.png *.gif *.pdf *.mp4"),
            ("Images", "*.jpg *.jpeg *.png *.gif"),
            ("Documents", "*.pdf"),
            ("Videos", "*.mp4")
        ])
        if file:
            self.media_file = file
            self.media_label.config(text=file)
            self.log(f"✅ Media file selected: {file}")

    # --- Clear Inputs ---
    def clear_all(self):
        self.msg_entry.delete("1.0", tk.END)
        self.contacts_file = None
        self.media_file = None
        self.csv_label.config(text="No file selected")
        self.media_label.config(text="No media selected")
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.configure(state="disabled")
        self.cancel_sending = False
        self.log("🔄 Cleared all inputs and logs.")

    # --- Cancel Sending ---
    def cancel_send(self):
        self.cancel_sending = True
        self.log("❌ Sending will be cancelled after current message...")

    # --- Confirm Send ---
    def confirm_send(self):
        if not self.contacts_file:
            messagebox.showerror("Error", "Please select contacts CSV")
            return

        df = pd.read_csv(self.contacts_file)
        if df.empty or df.shape[1] < 1:
            messagebox.showerror("Error", "CSV must contain at least one column with contacts")
            return
        contacts = df.iloc[:, 0].dropna().astype(str).tolist()
        base_message = self.msg_entry.get("1.0", tk.END).strip()

        media_text = os.path.basename(self.media_file) if self.media_file else "No media"
        confirm = messagebox.askyesno(
            "Confirm Send",
            f"You are about to send this message to {len(contacts)} contacts.\n\n"
            f"Message:\n{base_message}\n\n"
            f"Media: {media_text}\n\n"
            "Do you want to proceed?"
        )
        if not confirm:
            self.log("❌ Sending cancelled by user.")
            return

        self.cancel_sending = False
        threading.Thread(target=self.send_messages, args=(contacts, base_message), daemon=True).start()

    # --- Send Messages ---
    def send_messages(self, contacts, base_message):
        media_base64 = None
        mime_type = None
        filename = None
        use_media = bool(self.media_file)

        if use_media:
            with open(self.media_file, "rb") as f:
                media_bytes = f.read()
            media_base64 = base64.b64encode(media_bytes).decode("utf-8")
            if self.media_file.endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif self.media_file.endswith(".png"):
                mime_type = "image/png"
            elif self.media_file.endswith(".gif"):
                mime_type = "image/gif"
            elif self.media_file.endswith(".pdf"):
                mime_type = "application/pdf"
            elif self.media_file.endswith(".mp4"):
                mime_type = "video/mp4"
            else:
                mime_type = "application/octet-stream"
            filename = os.path.basename(self.media_file)
            base64_data = f"data:{mime_type};base64,{media_base64}"

        self.log(f"✅ Starting sending to {len(contacts)} contacts...")

        for idx, contact in enumerate(contacts, start=1):
            if self.cancel_sending:
                self.log("❌ Sending cancelled by user.")
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{base_message}\n\nSent at: {timestamp}"
            headers = {"Accept": "application/json", "x-api-key": API_KEY}

            try:
                if use_media:
                    # Media endpoint
                    payload = {
                        "number": "91" + contact,
                        "caption": message,
                        "mimeType": mime_type,
                        "filename": filename,
                        "mediaBase64": base64_data
                    }
                    response = requests.post(API_URL_MEDIA + SESSION_KEY, json=payload, headers=headers)
                else:
                    # Text-only endpoint
                    payload = {
                        "number": "91" + contact,
                        "message": message
                    }
                    response = requests.post(API_URL_TEXT + SESSION_KEY, json=payload, headers=headers)

                status_code = response.status_code
                status = "Sent" if status_code == 200 else "Failed"
                self.log(f"[{idx}/{len(contacts)}] {status} to {contact}: Status {status_code}")
                self.save_log_excel(contact, status, status_code)
            except Exception as e:
                self.log(f"[{idx}/{len(contacts)}] Failed for {contact}: {e}")
                self.save_log_excel(contact, "Failed", str(e))

            if idx < len(contacts) and not self.cancel_sending:
                self.log("⏳ Waiting 30 seconds before next contact...")
                for _ in range(30):
                    if self.cancel_sending:
                        break
                    time.sleep(1)

        if not self.cancel_sending:
            self.log("✅ All messages sent successfully!")
            messagebox.showinfo("Done", "All messages sent successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppSenderApp(root)
    root.mainloop()
