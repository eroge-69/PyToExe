import os
import json
import smtplib
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import tkinter as tk
from tkinter import filedialog

# --------------------- CONFIG: your accounts ---------------------
ACCOUNTS = {
    "Microsoft": {
        "email": "your_outlook@outlook.com",
        "password": "your-outlook-app-password",
        "smtp": "smtp.office365.com",
        "port": 587,
    },
    "Google 1": {
        "email": "ketanguptaboom@gmail.com",
        "password": "fzzo clch ehwv uyko",
        "smtp": "smtp.gmail.com",
        "port": 587,
    },
    "Google 2": {
        "email": "your_gmail2@gmail.com",
        "password": "your-gmail2-app-password",
        "smtp": "smtp.gmail.com",
        "port": 587,
    },
}

DRAFT_FILE = "draft.json"

# --------------------- UI helpers ---------------------
def hacker_popup(root, title, message, success=True):
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg="black")
    win.resizable(False, False)
    color = "lime" if success else "#ff3b3b"
    frame = tk.Frame(win, bg="black", bd=2, relief="solid", highlightbackground=color, highlightcolor=color, highlightthickness=2)
    frame.pack(padx=14, pady=14, fill="both")
    lbl = tk.Label(frame, text=message, fg=color, bg="black", font=("Courier New", 12, "bold"), justify="left")
    lbl.pack(padx=12, pady=10)
    btn = tk.Button(frame, text="OK", command=win.destroy, fg="black", bg=color, font=("Courier New", 11, "bold"), activebackground=color)
    btn.pack(pady=(4,10))
    # center on parent
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - win.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")
    win.grab_set()
    win.focus_set()

def set_enabled(widget, enabled=True):
    try:
        widget.config(state=("normal" if enabled else "disabled"))
    except Exception:
        pass

# --------------------- App ---------------------
class HackerMailer:
    def __init__(self, root):
        self.root = root
        self.root.title("QB64 Hacker Mail")
        self.root.configure(bg="black")
        self.attachments = []

        self.make_ui()
        self.log(">> QB64 Hacker Mail initialized.")

    def make_ui(self):
        ascii_art = ("""
 ██████╗ ██████╗  ██████╗ ██╗  ██╗
██╔═══██╗██╔══██╗██╔════╝ ██║  ██║
██║   ██║██████╔╝███████╗ ███████║
██║▄▄ ██║██╔══██╗██╔═══██╗╚════██║
╚██████╔╝██████╔╝╚██████╔╝     ██║
 ╚══▀▀═╝ ╚═════╝  ╚═════╝      ╚═╝"""
        )
        header = tk.Label(self.root, text=ascii_art, fg="lime", bg="black",
                          font=("Courier New", 10, "bold"), justify="left")
        header.pack(pady=(10, 6), anchor="w", padx=10)

        form = tk.Frame(self.root, bg="black")
        form.pack(fill="x", padx=12)

        # Account
        self.mk_label(form, "Account")
        self.account_var = tk.StringVar(value="Microsoft")
        self.account_menu = tk.OptionMenu(form, self.account_var, *ACCOUNTS.keys())
        self.stylize_button_like_menu(self.account_menu)
        self.account_menu.pack(fill="x", pady=3)

        # To
        self.mk_label(form, "To (receiver)")
        self.entry_to = self.mk_entry(form)
        # Subject
        self.mk_label(form, "Subject")
        self.entry_subject = self.mk_entry(form)
        # Message
        self.mk_label(form, "Message")
        self.text_body = tk.Text(form, height=8, bg="black", fg="lime",
                                 insertbackground="lime", font=("Courier New", 12),
                                 highlightthickness=1, highlightbackground="lime")
        self.text_body.pack(fill="x", pady=4)

        # Attachments row
        attach_row = tk.Frame(form, bg="black")
        attach_row.pack(fill="x", pady=(2, 0))
        self.btn_attach = tk.Button(attach_row, text="Attach File(s)",
                                    command=self.attach_files,
                                    fg="lime", bg="black", activeforeground="black",
                                    activebackground="lime", font=("Courier New", 11, "bold"),
                                    relief="solid", bd=1)
        self.btn_attach.pack(side="left", pady=6)

        self.btn_clear_attach = tk.Button(attach_row, text="Clear Attach",
                                          command=self.clear_attachments,
                                          fg="#ff3b3b", bg="black", activeforeground="black",
                                          activebackground="#ff3b3b", font=("Courier New", 11, "bold"),
                                          relief="solid", bd=1)
        self.btn_clear_attach.pack(side="left", padx=6)

        self.lbl_attach = tk.Label(form, text="No files attached", fg="#8aff8a",
                                   bg="black", font=("Courier New", 10), anchor="w", justify="left", wraplength=600)
        self.lbl_attach.pack(fill="x", pady=(2, 6))

        # Buttons row
        btns = tk.Frame(form, bg="black")
        btns.pack(fill="x", pady=6)
        self.btn_save = tk.Button(btns, text="Save Draft", command=self.save_draft,
                                  fg="black", bg="lime", activebackground="lime",
                                  font=("Courier New", 11, "bold"))
        self.btn_save.pack(side="left", padx=(0,6))
        self.btn_load = tk.Button(btns, text="Load Draft", command=self.load_draft,
                                  fg="black", bg="lime", activebackground="lime",
                                  font=("Courier New", 11, "bold"))
        self.btn_load.pack(side="left", padx=6)

        self.btn_send = tk.Button(btns, text="SEND EMAIL", command=self.send_with_animation,
                                  fg="black", bg="lime", activebackground="lime",
                                  font=("Courier New", 13, "bold"))
        self.btn_send.pack(side="right")

        # Status + Console
        self.status = tk.Label(self.root, text="READY", fg="lime", bg="black",
                               font=("Courier New", 11, "bold"), anchor="w")
        self.status.pack(fill="x", padx=12, pady=(2, 0))

        console_frame = tk.Frame(self.root, bg="black")
        console_frame.pack(fill="both", expand=True, padx=12, pady=(4, 10))
        self.console = tk.Text(console_frame, height=10, bg="black", fg="#8aff8a",
                               insertbackground="lime", font=("Courier New", 11),
                               highlightthickness=1, highlightbackground="lime", state="disabled")
        self.console.pack(side="left", fill="both", expand=True)
        scroll = tk.Scrollbar(console_frame, command=self.console.yview)
        scroll.pack(side="right", fill="y")
        self.console.config(yscrollcommand=scroll.set)

    def stylize_button_like_menu(self, widget):
        widget.configure(bg="black", fg="lime", activebackground="lime",
                         activeforeground="black", highlightthickness=1)
        try:
            widget["menu"].configure(bg="black", fg="lime", activebackground="lime", activeforeground="black")
        except Exception:
            pass

    def mk_label(self, parent, text):
        tk.Label(parent, text=text, fg="lime", bg="black",
                 font=("Courier New", 12, "bold"), anchor="w").pack(fill="x", pady=(6, 2))

    def mk_entry(self, parent):
        e = tk.Entry(parent, bg="black", fg="lime", insertbackground="lime",
                     font=("Courier New", 12), highlightthickness=1, highlightbackground="lime")
        e.pack(fill="x", pady=3)
        return e

    # ------------- Attachments -------------
    def attach_files(self):
        files = filedialog.askopenfilenames(title="Select file(s)")
        if files:
            self.attachments.extend(files)
            self.update_attach_label()
            self.log(f">> Added {len(files)} attachment(s).")

    def clear_attachments(self):
        self.attachments.clear()
        self.update_attach_label()
        self.log(">> Attachments cleared.")

    def update_attach_label(self):
        if self.attachments:
            names = [os.path.basename(f) for f in self.attachments]
            self.lbl_attach.config(text="Attachments: " + ", ".join(names))
        else:
            self.lbl_attach.config(text="No files attached")

    # ------------- Logging -------------
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = f"[{timestamp}] {msg}\n"
        self.console.config(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.config(state="disabled")

    def set_status(self, msg):
        self.status.config(text=msg)

    # ------------- Drafts -------------
    def save_draft(self):
        data = {
            "account": self.account_var.get(),
            "to": self.entry_to.get().strip(),
            "subject": self.entry_subject.get().strip(),
            "body": self.text_body.get("1.0", "end-1c"),
            "attachments": self.attachments,
        }
        with open(DRAFT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self.log(">> Draft saved.")
        hacker_popup(self.root, "Draft", "Draft saved successfully.", success=True)

    def load_draft(self):
        if not os.path.exists(DRAFT_FILE):
            hacker_popup(self.root, "Draft", "No draft found.", success=False)
            return
        with open(DRAFT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "account" in data and data["account"] in ACCOUNTS:
            self.account_var.set(data["account"])
        self.entry_to.delete(0, "end")
        self.entry_to.insert(0, data.get("to", ""))
        self.entry_subject.delete(0, "end")
        self.entry_subject.insert(0, data.get("subject", ""))
        self.text_body.delete("1.0", "end")
        self.text_body.insert("1.0", data.get("body", ""))
        self.attachments = data.get("attachments", [])
        self.update_attach_label()
        self.log(">> Draft loaded.")

    # ------------- Send + Animation -------------
    def send_with_animation(self):
        # Validate minimal fields
        to = self.entry_to.get().strip()
        subject = self.entry_subject.get().strip()
        body = self.text_body.get("1.0", "end-1c").strip()
        if not to or not subject or not body:
            hacker_popup(self.root, "Error", "Fill To, Subject, and Message.", success=False)
            return

        # Disable controls while "sending"
        self.toggle_controls(False)

        steps = [
            "Initializing secure channel...",
            "Loading account & headers...",
            "Encrypting payload...",
            "Establishing SMTP tunnel...",
            "Handshake OK. Authenticating...",
            "Transmitting email packets...",
        ]

        self.log(">> Begin send sequence.")
        self.play_steps_then_send(steps, 0)

    def play_steps_then_send(self, steps, idx):
        if idx < len(steps):
            msg = steps[idx]
            self.set_status(msg)
            self.log(".. " + msg)
            # typey effect: reveal char by char in status
            self.type_line(self.status, msg, 0, lambda: self.root.after(350, lambda: self.play_steps_then_send(steps, idx+1)))
        else:
            # After animation, actually send in background
            self.set_status("SENDING...")
            self.log(">> Dispatching to SMTP in background thread.")
            t = threading.Thread(target=self.send_email_worker, daemon=True)
            t.start()

    def type_line(self, label_widget, text, i, on_done):
        # Simple typing animation for status label
        label_widget.config(text=text[:i])
        if i < len(text):
            self.root.after(12, lambda: self.type_line(label_widget, text, i+1, on_done))
        else:
            on_done()

    def toggle_controls(self, enabled=True):
        for w in [self.account_menu, self.entry_to, self.entry_subject, self.text_body,
                  self.btn_attach, self.btn_clear_attach, self.btn_save, self.btn_load, self.btn_send]:
            set_enabled(w, enabled)

    def send_email_worker(self):
        acc_name = self.account_var.get()
        acc = ACCOUNTS[acc_name]
        sender_email = acc["email"]
        password = acc["password"]

        receiver_email = self.entry_to.get().strip()
        subject = self.entry_subject.get().strip()
        message_body = self.text_body.get("1.0", "end-1c")

        # Build message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message_body, "plain"))

        # Attach files
        for path in self.attachments:
            try:
                with open(path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
                msg.attach(part)
            except Exception as e:
                # log but continue
                self.root.after(0, lambda p=path, e=e: self.log(f"!! Failed to attach {os.path.basename(p)}: {e}"))

        # Send
        try:
            with smtplib.SMTP(acc["smtp"], acc["port"], timeout=30) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, [receiver_email], msg.as_string())

            # Success UI updates on main thread
            self.root.after(0, lambda: self.on_send_result(True, acc_name, receiver_email, subject))
        except Exception as e:
            self.root.after(0, lambda e=e: self.on_send_result(False, None, None, None, error=str(e)))

    def on_send_result(self, ok, acc_name, to_addr, subject, error=None):
        if ok:
            self.set_status("SENT ✓")
            self.log(f">> SENT via [{acc_name}] to <{to_addr}> | Subject: {subject}")
            hacker_popup(self.root, "Delivered", "Email sent successfully. ✓", success=True)
            # Optional: clear attachments after send
            self.attachments.clear()
            self.update_attach_label()
        else:
            self.set_status("FAILED ✗")
            self.log(f">> SEND FAILED: {error}")
            hacker_popup(self.root, "Error", f"Send failed:\n{error}", success=False)

        # Re-enable controls
        self.toggle_controls(True)

# --------------------- run ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HackerMailer(root)
    # Nice minimum size
    root.geometry("800x650")
    root.minsize(720, 560)
    root.mainloop()
