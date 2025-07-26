import requests
import threading
import time
import tkinter as tk
from tkinter import messagebox

def send_spam(webhook_url, message, amount, status_label):
    def spam():
        try:
            requests.post(webhook_url, json={'content': message})
        except Exception as e:
            print(f"Error: {e}")

    for i in range(amount):
        threading.Thread(target=spam).start()
        time.sleep(0.1)
    
    status_label.config(text="✅ Spamming complete!")

def start_spamming():
    webhook_url = webhook_entry.get()
    message = message_entry.get()
    try:
        amount = int(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Amount must be an integer.")
        return

    if not webhook_url.startswith("http"):
        messagebox.showerror("Invalid Webhook", "Please enter a valid webhook URL.")
        return

    try:
        requests.post(webhook_url, json={'content': ""})
    except:
        messagebox.showerror("Invalid Webhook", "The webhook URL is not valid or is offline.")
        return

    status_label.config(text="🟡 Spamming in progress...")
    threading.Thread(target=send_spam, args=(webhook_url, message, amount, status_label)).start()

# --- GUI Setup ---

root = tk.Tk()
root.title("Webhook Spammer by Cisntsharp92 V1.0")
root.geometry("400x300")

tk.Label(root, text="Webhook URL:").pack(pady=5)
webhook_entry = tk.Entry(root, width=50)
webhook_entry.pack(pady=5)

tk.Label(root, text="Message to Send:").pack(pady=5)
message_entry = tk.Entry(root, width=50)
message_entry.pack(pady=5)

tk.Label(root, text="Amount:").pack(pady=5)
amount_entry = tk.Entry(root, width=20)
amount_entry.pack(pady=5)

tk.Button(root, text="Start Spamming", command=start_spamming, bg="red", fg="white").pack(pady=15)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
