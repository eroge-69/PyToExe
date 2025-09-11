import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import messagebox, ttk


SMTP_SETTINGS = {
    "Gmail": ("smtp.gmail.com", 587),
    "Yahoo": ("smtp.mail.yahoo.com", 587),
    "Outlook": ("smtp.office365.com", 587),
    "Apple Mail": ("smtp.mail.me.com", 587),
    "ProtonMail": ("smtp.protonmail.com", 587),  # requires Bridge
}


def send_emails():
    sender_email = entry_sender.get()
    sender_password = entry_password.get()
    recipient_email = entry_recipient.get()
    subject = entry_subject.get()
    message = text_message.get("1.0", tk.END).strip()
    count = int(entry_count.get())
    provider = provider_combo.get()

    if not sender_email or not sender_password or not recipient_email or not subject or not message:
        messagebox.showerror("Error", "All fields must be filled!")
        return

    if count < 1 or count > 100:
        messagebox.showerror("Error", "Email count must be between 1 and 100!")
        return

    smtp_server, port = SMTP_SETTINGS.get(provider, (None, None))
    if not smtp_server:
        messagebox.showerror("Error", "Unsupported provider!")
        return

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, sender_password)

        for i in range(count):
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            server.sendmail(sender_email, recipient_email, msg.as_string())
            status_label.config(text=f"Sent {i+1}/{count} emails...", fg="green")
            root.update_idletasks()

        server.quit()
        messagebox.showinfo("Success", f"✅ Sent {count} emails to {recipient_email}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI Setup
root = tk.Tk()
root.title("Multi-Provider Email Sender")
root.geometry("500x500")

tk.Label(root, text="Email Provider:").pack()
provider_combo = ttk.Combobox(root, values=list(SMTP_SETTINGS.keys()), state="readonly")
provider_combo.pack()
provider_combo.current(0)

tk.Label(root, text="Your Email:").pack()
entry_sender = tk.Entry(root, width=50)
entry_sender.pack()

tk.Label(root, text="Password / App Password:").pack()
entry_password = tk.Entry(root, width=50, show="*")
entry_password.pack()

tk.Label(root, text="Recipient Email:").pack()
entry_recipient = tk.Entry(root, width=50)
entry_recipient.pack()

tk.Label(root, text="Subject:").pack()
entry_subject = tk.Entry(root, width=50)
entry_subject.pack()

tk.Label(root, text="Message:").pack()
text_message = tk.Text(root, width=60, height=10)
text_message.pack()

tk.Label(root, text="Number of Emails (1–100):").pack()
entry_count = tk.Entry(root, width=10)
entry_count.insert(0, "1")
entry_count.pack()

send_button = tk.Button(root, text="Send Emails", command=send_emails, bg="blue", fg="white")
send_button.pack(pady=10)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
